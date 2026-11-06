"use strict";
// Execute with node --test; only node: built-ins, no network or real data.
const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const app = fs.readFileSync(path.join(__dirname, "app.js"), "utf8");
const base = Object.freeze({
  synthetic: true, external_ref: "DEMO-HVAC-001", source: "website",
  need: "AC not cooling", status: "received"
});

function harness(apiResponse) {
  const elements = new Map();
  function element() {
    return {
      textContent: "", value: "", children: [],
      append(...items) { this.children.push(...items); },
      replaceChildren(...items) { this.children = items; },
      setAttribute() {}, addEventListener() {}
    };
  }
  function get(id) {
    if (!elements.has(id)) elements.set(id, element());
    return elements.get(id);
  }
  const document = {
    getElementById: get,
    createElement: element,
    addEventListener() {}  // Do not trigger DOMContentLoaded or live requests.
  };
  const fetch = async (url) => {
    assert.equal(url, "/api/demo/leads", "malformed intake must not trigger other endpoints");
    return {ok: true, async json() { return apiResponse; }};
  };
  const context = vm.createContext({
    document, fetch, AbortController, setTimeout, clearTimeout,
  });
  vm.runInContext(app, context, {filename: "app.js"});
  return {context, elements, evaluate: code => vm.runInContext(code, context)};
}

function validate(row) {
  const h = harness({synthetic:true, leads:[]});
  return h.evaluate("safeLead(" + JSON.stringify(row) + ")");
}

test("all shared synthetic intake categories remain renderable", () => {
  for (const source of ["demo", "website", "phone", "referral"]) {
    for (const need of ["AC not cooling", "AC maintenance", "repair",
                         "maintenance", "estimate follow-up", "heating issue"]) {
      const result = validate({...base, source, need});
      assert.ok(result, source + "/" + need);
      assert.equal(result.source, source);
      assert.equal(result.need, need);
    }
  }
});

test("malformed or PII-bearing browser records are rejected before display", () => {
  for (const row of [
    {...base, synthetic:false},
    {...base, external_ref:"person@example.com"},
    {...base, external_ref:"DEMO-A\n"},
    {...base, external_ref:"CONTACT-1"},
    {...base, external_ref:"DEMO-" + "X".repeat(57)},
    {...base, source:"customer@example.com"},
    {...base, need:"Call Sam at 555-0100"},
    {...base, status:"paid"},
    {...base, email:"private@example.com"},
    {...base, status:42},
    null,
    []
  ]) {
    assert.equal(validate(row), null, "unsafe record must fail closed");
  }
});

test("a single unsafe record invalidates entire response and shows offline fixtures", async () => {
  const unsafe = {...base, email:"hidden@example.com"};
  const h = harness({synthetic:true, leads:[base, unsafe]});
  await h.evaluate("refresh()");
  assert.equal(h.elements.get("leadSource").textContent, "Offline fixtures");
  assert.equal(h.elements.get("leadCount").textContent, "3");
  assert.match(h.elements.get("connection").textContent, /Offline fixture mode/);
  assert.equal(h.elements.get("leadRows").children.length, 3);
});

test("oversize synthetic feed fails closed without attempting scorecard", async () => {
  const h = harness({synthetic:true, leads:Array(2001).fill(base)});
  await h.evaluate("refresh()");
  assert.equal(h.elements.get("leadSource").textContent, "Offline fixtures");
  assert.match(h.elements.get("connection").textContent, /demonstration only/);
});
