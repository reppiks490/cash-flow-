"use strict";
// Synthetic-only frontend contract tests. Run with: node --test input_boundary.test.cjs
const {test} = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "app.js"), "utf8");
const context = {document:{addEventListener(){}}, AbortController, setTimeout, clearTimeout};
vm.createContext(context);
vm.runInContext(source, context, {timeout:1500});
const safeLead = value => vm.runInContext("safeLead(" + JSON.stringify(value) + ")", context);
const safeDraft = value => vm.runInContext("safeDraftMessage(" + JSON.stringify(value) + ")", context);
const valid = {synthetic:true,external_ref:"DEMO-HVAC-001",source:"website",need:"repair",status:"received"};

test("canonical synthetic categorical lead is accepted without added fields", () => {
  const accepted = safeLead(valid);
  assert.equal(accepted.external_ref, valid.external_ref);
  assert.deepEqual(Object.keys(accepted).sort(), Object.keys(valid).sort());
});
test("untrusted synthetic flag cannot authorize customer identifiers or extra fields", () => {
  for (const patch of [
    {external_ref:"real-person@example.com"}, {external_ref:"DEMO-../../secret"},
    {external_ref:"DEMO-"}, {source:"customer@example.com"},
    {need:"Call 555-555-1234"}, {status:"closed"},
    {phone:"555-555-1234"}, {synthetic:false}
  ]) assert.equal(safeLead({...valid,...patch}), null, JSON.stringify(patch));
});
test("reject prototype-polluted, missing, and non-record lead payloads", () => {
  for (const candidate of [null, [], "DEMO-HVAC-001", {}, {...valid,synthetic:"true"},
    {...valid,external_ref:"DEMO-"+"x".repeat(57)}]) {
    assert.equal(safeLead(candidate), null);
  }
});
test("draft preview rejects contact destinations and unbounded content", () => {
  for (const candidate of ["", "Call 555-555-1234", "a@b.com", "https://example.com",
    "www.example.com", "a".repeat(1501), "Hello\u0000world", 123]) {
    assert.equal(safeDraft(candidate), false, JSON.stringify(candidate).slice(0,100));
  }
  assert.equal(safeDraft("UNSENT SYNTHETIC HVAC REVIEW ONLY"), true);
});
