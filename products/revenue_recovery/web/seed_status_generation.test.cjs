"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "app.js"), "utf8");
const start = source.indexOf("async function seedDemo() {");
const end = source.indexOf('\ndocument.addEventListener("DOMContentLoaded"', start);
assert.ok(start >= 0 && end > start, "seedDemo function found");

function deferred() {
  let resolve;
  const promise = new Promise(r => { resolve = r; });
  return {promise, resolve};
}
function harness({hostname = "localhost", rejectAt = null, pauseAt = null} = {}) {
  const connection = {textContent: ""};
  const button = {disabled: false};
  const pending = deferred();
  const pendingPost = deferred();
  const posted = [];
  const ctx = vm.createContext({
    location: {hostname},
    FIXTURES: [
      {external_ref: "DEMO-HVAC-001", source: "website", need: "repair"},
      {external_ref: "DEMO-HVAC-002", source: "phone", need: "maintenance"},
      {external_ref: "DEMO-HVAC-003", source: "referral", need: "AC maintenance"}
    ],
    $: id => id === "connection" ? connection : button,
    fetch: async (url, options) => {
      assert.equal(url, "/api/demo/leads");
      assert.equal(options.method, "POST");
      assert.equal(options.credentials, "omit");
      const payload = JSON.parse(options.body);
      assert.equal(payload.synthetic, true);
      assert.deepEqual(Object.keys(payload).sort(), ["external_ref", "need", "source", "synthetic"]);
      posted.push(payload.external_ref);
      if (payload.external_ref === pauseAt) await pendingPost.promise;
      return {ok: payload.external_ref !== rejectAt};
    },
    refreshSequence: 0,
    refresh: () => {ctx.refreshSequence++; return pending.promise;}
  });
  vm.runInContext(source.slice(start, end), ctx);
  return {ctx, connection, button, pending, pendingPost, posted, run: () => vm.runInContext("seedDemo()", ctx)};
}
test("seed success may set status only when its own refresh remains latest", async () => {
  const h = harness();
  const work = h.run();
  await new Promise(resolve => setImmediate(resolve));
  h.pending.resolve(true);
  await work;
  assert.match(h.connection.textContent, /Three explicitly synthetic examples/);
  assert.deepEqual(h.posted, ["DEMO-HVAC-001", "DEMO-HVAC-002", "DEMO-HVAC-003"]);
  assert.equal(h.button.disabled, false);
});
test("newer refresh status cannot be overwritten by late seed success", async () => {
  const h = harness();
  const work = h.run();
  await new Promise(resolve => setImmediate(resolve));
  h.ctx.refreshSequence++;
  h.connection.textContent = "Newer user refresh owns status";
  h.pending.resolve(true);
  await work;
  assert.equal(h.connection.textContent, "Newer user refresh owns status");
  assert.equal(h.button.disabled, false);
});
test("failed seed refresh never reports successful load", async () => {
  const h = harness();
  const work = h.run();
  await new Promise(resolve => setImmediate(resolve));
  h.pending.resolve(false);
  await work;
  assert.doesNotMatch(h.connection.textContent, /Three explicitly synthetic examples/);
});

test("non-loopback host refuses synthetic seeding before any POST", async () => {
  const h = harness({hostname: "example.org"});
  await h.run();
  assert.deepEqual(h.posted, []);
  assert.equal(h.ctx.refreshSequence, 0);
  assert.match(h.connection.textContent, /local loopback demo/);
  assert.equal(h.button.disabled, false);
});
test("rejected synthetic POST stops remaining fixtures and never claims loaded", async () => {
  const h = harness({rejectAt: "DEMO-HVAC-002"});
  await h.run();
  assert.deepEqual(h.posted, ["DEMO-HVAC-001", "DEMO-HVAC-002"]);
  assert.equal(h.ctx.refreshSequence, 0);
  assert.match(h.connection.textContent, /seeding unavailable/);
  assert.doesNotMatch(h.connection.textContent, /Three explicitly synthetic examples loaded/);
  assert.equal(h.button.disabled, false);
});

test("user refresh during seed POST loop prevents stale seed from launching another refresh", async () => {
  const h = harness({pauseAt: "DEMO-HVAC-001"});
  const work = h.run();
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(h.posted, ["DEMO-HVAC-001"]);
  h.ctx.refreshSequence++;
  h.connection.textContent = "User refresh in progress";
  h.pendingPost.resolve();
  await work;
  assert.deepEqual(h.posted, ["DEMO-HVAC-001", "DEMO-HVAC-002", "DEMO-HVAC-003"]);
  assert.equal(h.ctx.refreshSequence, 1, "stale seed must not launch refresh");
  assert.equal(h.connection.textContent, "User refresh in progress");
  assert.equal(h.button.disabled, false);
});
