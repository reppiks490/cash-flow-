"use strict";
const {test} = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

// No browser, network, customer data, or third-party test dependencies.
const app = fs.readFileSync(path.join(__dirname, "app.js"), "utf8");
const lead = {synthetic:true,external_ref:"DEMO-HVAC-001",source:"website",need:"AC not cooling",status:"received"};
function deferred() {
  let resolve, reject;
  const promise = new Promise((yes, no) => {resolve = yes; reject = no;});
  return {promise, resolve, reject};
}
function preview(ref, message) {
  return {synthetic:true,preview:{
    synthetic:true,external_ref:ref,
    qualification:{result:"manual_review_required",qualified:false,consent_verified:false},
    followup:{status:"unsent_unapproved_draft",approved:false,transmitted:false,message},
    crm:{dry_run:true,transmitted:false},
    appointment:{confirmed:false},
    attribution:{verified_recovered_revenue_cents:0}
  }};
}
function harness() {
  const nodes = new Map();
  function element() {
    return {
      value:"",textContent:"",children:[],listeners:{},
      addEventListener(type, callback) {this.listeners[type] = callback;},
      replaceChildren() {this.children = [];},
      append(child) {this.children.push(child);},
      setAttribute() {}
    };
  }
  const document = {
    getElementById(id) {if (!nodes.has(id)) nodes.set(id, element()); return nodes.get(id);},
    createElement:element,
    addEventListener(type, callback) {if (type === "DOMContentLoaded") this.ready = callback;}
  };
  const requests = [];
  const context = vm.createContext({
    document, AbortController, setTimeout, clearTimeout,
    fetch(url) {const pending = deferred(); requests.push({url, ...pending}); return pending.promise;},
    location:{hostname:"localhost"},
    navigator:{clipboard:{writeText:async()=>{}}}
  });
  vm.runInContext(app, context, {filename:"app.js"});
  // Register the same input listener as browser startup, but avoid startup fetch.
  nodes.set("draft", element());
  nodes.get("draft").addEventListener("input", () => vm.runInContext("draftEditSequence += 1", context));
  vm.runInContext("render([FIXTURES[0], FIXTURES[1]], 'Fixture')", context);
  return {
    nodes, requests, context,
    select(index) {return vm.runInContext("selectLead(" + index + ")", context);},
    edit(text) {nodes.get("draft").value = text; nodes.get("draft").listeners.input();}
  };
}
test("delayed success cannot overwrite operator edits or status", async () => {
  const h = harness();
  const done = h.select(0);
  h.edit("Operator's exact unsent edit");
  const status = h.nodes.get("copyStatus").textContent;
  h.requests[0].resolve({ok:true,json:async()=>preview(lead.external_ref,"Server preview")});
  await done;
  assert.equal(h.nodes.get("draft").value,"Operator's exact unsent edit");
  assert.equal(h.nodes.get("copyStatus").textContent,status);
});
test("delayed failure cannot inject offline fallback over operator edits", async () => {
  const h = harness();
  const done = h.select(0);
  h.edit("Keep this human draft");
  const status = h.nodes.get("copyStatus").textContent;
  h.requests[0].reject(new Error("synthetic offline"));
  await done;
  assert.equal(h.nodes.get("draft").value,"Keep this human draft");
  assert.equal(h.nodes.get("copyStatus").textContent,status);
});
test("reselection ignores stale preview and accepts latest preview", async () => {
  const h = harness();
  const old = h.select(0);
  const current = h.select(1);
  h.requests[1].resolve({ok:true,json:async()=>preview("DEMO-HVAC-002","Latest safe preview")});
  await current;
  h.requests[0].resolve({ok:true,json:async()=>preview(lead.external_ref,"Old preview")});
  await old;
  assert.equal(h.nodes.get("draft").value,"Latest safe preview");
  assert.match(h.nodes.get("copyStatus").textContent,/DEMO-HVAC-002/);
});
test("new selection after previous manual edit accepts its own response", async () => {
  const h = harness();
  const old = h.select(0);
  h.edit("Earlier edit");
  const current = h.select(1);
  h.requests[1].resolve({ok:true,json:async()=>preview("DEMO-HVAC-002","New selected preview")});
  await current;
  h.requests[0].reject(new Error("old request failed"));
  await old;
  assert.equal(h.nodes.get("draft").value,"New selected preview");
  assert.match(h.nodes.get("copyStatus").textContent,/DEMO-HVAC-002/);
});
