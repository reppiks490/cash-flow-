"use strict";
// Static accessibility and safety contract for the synthetic-only dashboard.
// This is not a substitute for browser/screen-reader or mobile testing.
const {test} = require("node:test");
const assert = require("node:assert/strict");
const {readFileSync} = require("node:fs");
const {join} = require("node:path");

const html = readFileSync(join(__dirname, "index.html"), "utf8");

test("responsive document declares language and viewport", () => {
  assert.match(html, /<html\s+lang="en">/i);
  assert.match(html, /<meta\s+name="viewport"\s+content="width=device-width, initial-scale=1">/i);
  assert.match(html, /<main\s+id="main">/i);
});

test("keyboard skip target exists and points to main landmark", () => {
  assert.match(html, /<a\s+class="skip"\s+href="#main">Skip to dashboard<\/a>/i);
  assert.match(html, /<main\s+id="main">/i);
});

test("synthetic pipeline table has caption and explicit column headers", () => {
  assert.match(html, /<table><caption\s+class="sr-only">Synthetic HVAC lead records<\/caption>/i);
  for (const label of ["Reference", "Source", "Request", "Stage", "Action"]) {
    assert.ok(html.includes('<th scope="col">' + label + '</th>'), label);
  }
  assert.match(html, /class="table-scroll"[^>]*tabindex="0"[^>]*role="region"[^>]*aria-label=/i);
});

test("editable draft and scenario controls have associated labels", () => {
  for (const id of ["draft", "scenarioChoice", "policyChoice"]) {
    assert.ok(html.includes('for="' + id + '"'), "missing label for " + id);
    assert.match(html, new RegExp(String.raw`<(?:textarea|select)\s+id="${id}"`));
  }
  assert.match(html, /id="draft"[^>]*aria-describedby="draftWarning"/);
  assert.match(html, /id="copyStatus"[^>]*role="status"/);
});

test("demo clearly disclaims revenue and contains no submit forms or external scripts", () => {
  assert.match(html, /SYNTHETIC DATA ONLY/);
  assert.match(html, /No authenticated payment receipts/);
  assert.match(html, /NOT FOR CUSTOMER DATA/);
  assert.doesNotMatch(html, /<form\b/i);
  // Static guard against remote dependencies in either quote style or attribute order.
  // This is NOT a CSP or browser/network security test.
  const remoteAsset = /<(?:script|link)\b[^>]*\b(?:src|href)\s*=\s*(["'])(?:https?:)?\/\/[^"']*\1/i;
  assert.doesNotMatch(html, remoteAsset);
  assert.doesNotMatch(html, /<base\b/i);
  assert.doesNotMatch(html, /<meta\b[^>]*http-equiv\s*=\s*(["'])refresh\1/i);
  assert.doesNotMatch(html, /<button\b[^>]*type="submit"/i);
});
