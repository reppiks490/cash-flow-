"use strict";
// Deliberately reordered synthetic read-only API promises. No network or real data.
const {test} = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const app = fs.readFileSync(path.join(__dirname, "app.js"), "utf8");
const leads = [
  {synthetic:true,external_ref:"DEMO-RACE-A",source:"website",need:"repair",status:"received"},
  {synthetic:true,external_ref:"DEMO-RACE-B",source:"phone",need:"maintenance",status:"received"}
];

function harness() {
  const elements = new Map();
  const listeners = new Map();
  const pending = {scenario: [], policy: []};
  const element = () => ({
    textContent:"", value:"", children:[],
    append(...x) { this.children.push(...x); },
    replaceChildren() { this.children=[]; },
    addEventListener(type, fn) { this.listeners ??= {}; this.listeners[type] = fn; }, setAttribute() {}
  });
  const get = id => {
    if (!elements.has(id)) elements.set(id, element());
    return elements.get(id);
  };
  const document = {getElementById:get,createElement:element,addEventListener(type, fn){ listeners.set(type, fn); }};
  const ok = value => ({ok:true, async json() {return value;}});
  const fetch = url => {
    if (url.startsWith("/api/demo/recovery/")) {
      const ref = url.split("/").at(-1);
      return Promise.resolve(ok({synthetic:true,preview:{
        synthetic:true,external_ref:ref,
        qualification:{result:"manual_review_required",qualified:false,consent_verified:false},
        followup:{status:"unsent_unapproved_draft",approved:false,transmitted:false,message:"UNSENT SYNTHETIC"},
        crm:{dry_run:true,transmitted:false},
        appointment:{confirmed:false},attribution:{verified_recovered_revenue_cents:0}
      }}));
    }
    if (url.startsWith("/api/demo/scenarios/")) {
      return new Promise(resolve => pending.scenario.push({resolve,url}));
    }
    if (url.startsWith("/api/demo/policy/")) {
      return new Promise(resolve => pending.policy.push({resolve,url}));
    }
    throw new Error("Unexpected endpoint " + url);
  };
  const sandbox = {document,fetch,AbortController,setTimeout,clearTimeout};
  vm.runInNewContext(app,sandbox,{timeout:1500});
  sandbox.render(leads,"Local synthetic API");
  get("scenarioChoice").value="review";
  get("policyChoice").value="unknown";
  return {sandbox,get,pending,init: () => listeners.get("DOMContentLoaded")()};
}

function scenarioReply(request, marker) {
  const ref = request.url.split("/").at(-2);
  const scenario = request.url.split("/").at(-1);
  request.resolve({ok:true,async json(){return {synthetic:true,scenario:{
    synthetic:true,external_ref:ref,scenario,
    events:[{synthetic:true,sequence:1,event_type:marker,
      source_evidence_verified:false,external_side_effect:false}],
    metrics:{actual_messages_sent:0,actual_bookings_confirmed:0,
      actual_jobs_closed:0,verified_recovered_revenue_cents:0,
      verified_rre_subscription_revenue_cents:0,verified_payment_receipts:0}
  }};}});
}

function policyReply(request, marker) {
  const ref = request.url.split("/").at(-2), mode=request.url.split("/").at(-1);
  request.resolve({ok:true,async json(){return {synthetic:true,policy:{
    synthetic:true,external_ref:ref,mode,
    suppressed: mode === "revoked_mock",
    consent_verified:false,operator_authorized:false,
    may_contact_real_person:false,actual_message_sent:false,
    reasons:[marker],draft:"UNSENT SYNTHETIC"
  }};}});
}

test("old scenario response cannot overwrite new A -> B -> A selection", async () => {
  const h=harness();
  await h.sandbox.selectLead(0);
  const old=h.sandbox.loadScenario();
  await h.sandbox.selectLead(1);
  await h.sandbox.selectLead(0);
  const newest=h.sandbox.loadScenario();
  assert.equal(h.pending.scenario.length,2);
  scenarioReply(h.pending.scenario[1],"latest_evidence");
  await newest;
  scenarioReply(h.pending.scenario[0],"stale_evidence");
  await old;
  assert.match(h.get("auditEvents").textContent,/latest evidence/);
  assert.doesNotMatch(h.get("auditEvents").textContent,/stale evidence/);
});

test("old policy response cannot overwrite new A -> B -> A selection", async () => {
  const h=harness();
  await h.sandbox.selectLead(0);
  const old=h.sandbox.loadPolicy();
  await h.sandbox.selectLead(1);
  await h.sandbox.selectLead(0);
  assert.match(h.get("policyEvents").textContent,/DEMO-RACE-A selected/);
  const newest=h.sandbox.loadPolicy();
  assert.equal(h.pending.policy.length,2);
  policyReply(h.pending.policy[1],"latest_policy");
  await newest;
  policyReply(h.pending.policy[0],"stale_policy");
  await old;
  assert.match(h.get("policyEvents").textContent,/latest_policy/);
  assert.doesNotMatch(h.get("policyEvents").textContent,/stale_policy/);
});

test("stale rejected scenario cannot replace newer valid scenario", async () => {
  const h=harness();
  await h.sandbox.selectLead(0);
  const old=h.sandbox.loadScenario();
  const newest=h.sandbox.loadScenario();
  scenarioReply(h.pending.scenario[1],"current_evidence");
  await newest;
  h.pending.scenario[0].resolve({ok:false});
  await old;
  assert.match(h.get("auditEvents").textContent,/current evidence/);
  assert.doesNotMatch(h.get("auditEvents").textContent,/unavailable/);
});

test("stale rejected policy cannot replace newer valid policy", async () => {
  const h=harness();
  await h.sandbox.selectLead(0);
  const old=h.sandbox.loadPolicy();
  const newest=h.sandbox.loadPolicy();
  assert.equal(h.pending.policy.length,2);
  policyReply(h.pending.policy[1],"latest_valid_policy");
  await newest;
  h.pending.policy[0].resolve({ok:false});
  await old;
  assert.match(h.get("policyEvents").textContent,/latest_valid_policy/);
  assert.doesNotMatch(h.get("policyEvents").textContent,/Policy preview unavailable/);
});

test("A to B to A stale rejected policy does not replace current lead status", async () => {
  const h=harness();
  await h.sandbox.selectLead(0);
  const old=h.sandbox.loadPolicy();
  await h.sandbox.selectLead(1);
  await h.sandbox.selectLead(0);
  assert.match(h.get("policyEvents").textContent,/DEMO-RACE-A selected/);
  h.pending.policy[0].resolve({ok:false});
  await old;
  assert.match(h.get("policyEvents").textContent,/DEMO-RACE-A selected/);
  assert.doesNotMatch(h.get("policyEvents").textContent,/Policy preview unavailable/);
});

test("scenario response is discarded after workflow choice changes", async () => {
  const h=harness();
  await h.sandbox.selectLead(0);
  const old=h.sandbox.loadScenario();
  h.get("scenarioChoice").value="appointment_mock";
  scenarioReply(h.pending.scenario[0],"obsolete_workflow");
  await old;
  assert.doesNotMatch(h.get("auditEvents").textContent,/obsolete workflow/);
});

test("scenario rejection cannot overwrite changed workflow choice", async () => {
  const h=harness();
  await h.sandbox.selectLead(0);
  const old=h.sandbox.loadScenario();
  h.get("scenarioChoice").value="closed_job_mock";
  h.pending.scenario[0].resolve({ok:false});
  await old;
  assert.doesNotMatch(h.get("auditEvents").textContent,/timeline unavailable/);
});

test("policy response is discarded after consent case changes", async () => {
  const h=harness();
  await h.sandbox.selectLead(0);
  const old=h.sandbox.loadPolicy();
  h.get("policyChoice").value="revoked_mock";
  policyReply(h.pending.policy[0],"obsolete_policy");
  await old;
  assert.doesNotMatch(h.get("policyEvents").textContent,/obsolete_policy/);
});

test("policy rejection cannot overwrite changed consent case", async () => {
  const h=harness();
  await h.sandbox.selectLead(0);
  const old=h.sandbox.loadPolicy();
  h.get("policyChoice").value="consent_record_mock";
  h.pending.policy[0].resolve({ok:false});
  await old;
  assert.doesNotMatch(h.get("policyEvents").textContent,/Policy preview unavailable/);
});

test("scenario A -> B -> A change invalidates old in-flight result without a new request", async () => {
  const h=harness();
  h.init();
  await h.sandbox.selectLead(0);
  const old=h.sandbox.loadScenario();
  h.get("scenarioChoice").value="appointment_mock";
  h.get("scenarioChoice").listeners.change();
  h.get("scenarioChoice").value="review";
  h.get("scenarioChoice").listeners.change();
  scenarioReply(h.pending.scenario[0],"obsolete_returned_choice");
  await old;
  assert.match(h.get("auditEvents").textContent,/Scenario changed/);
  assert.doesNotMatch(h.get("auditEvents").textContent,/obsolete returned choice/);
});

test("policy A -> B -> A change invalidates old in-flight failure without a new request", async () => {
  const h=harness();
  h.init();
  await h.sandbox.selectLead(0);
  const old=h.sandbox.loadPolicy();
  h.get("policyChoice").value="revoked_mock";
  h.get("policyChoice").listeners.change();
  h.get("policyChoice").value="unknown";
  h.get("policyChoice").listeners.change();
  h.pending.policy[0].resolve({ok:false});
  await old;
  assert.match(h.get("policyEvents").textContent,/Consent case changed/);
  assert.doesNotMatch(h.get("policyEvents").textContent,/Policy preview unavailable/);
});
