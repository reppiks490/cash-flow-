"use strict";
// Static contract only. Real browser/assistive-technology acceptance is separate.
const {test} = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const root = __dirname;
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const css = fs.readFileSync(path.join(root, "styles.css"), "utf8");

test("keyboard users can focus the horizontally scrolling lead table", () => {
  assert.match(html, /class="table-scroll"[^>]*tabindex="0"[^>]*role="region"[^>]*aria-label="Synthetic HVAC lead table;/);
  assert.match(html, /focus the table and use horizontal arrow keys/);
  assert.match(css, /\.table-scroll:focus-visible/);
  assert.match(css, /\.table-scroll\s*\{[^}]*overscroll-behavior-x:\s*contain/);
  assert.match(css, /\.table-scroll\{overflow-x:auto\}/);
});

test("timeline and consent policy remain independently keyboard scrollable", () => {
  for (const id of ["auditEvents", "policyEvents"]) {
    const tag = [...html.matchAll(/<pre\s+[^>]*>/g)].map(match => match[0])
      .find(tag => tag.includes('id="' + id + '"'));
    assert.ok(tag, id + " must have a pre element");
    assert.match(tag, /tabindex="0"/);
    assert.match(tag, /aria-label="[^"]+"/);
    assert.match(tag, /role="status"/);
  }
  assert.match(css, /\.audit-events:focus-visible/);
  assert.match(css, /\.audit-events\s*\{[^}]*overflow:\s*auto/);
});

test("small displays retain navigation, keyboard focus and minimum action targets", () => {
  assert.match(html, /<meta name="viewport" content="width=device-width, initial-scale=1">/);
  assert.match(html, /<a class="skip" href="#main">Skip to dashboard<\/a>/);
  assert.match(html, /<main id="main">/);
  assert.match(css, /@media\(max-width:760px\)/);
  assert.match(css, /\.top-actions button\s*\{\s*min-height:\s*44px/);
  assert.match(css, /\.skip:focus\{top:10px\}/);
});

test("disclosures do not overstate live operations", () => {
  for (const phrase of ["SYNTHETIC DATA ONLY", "No authenticated payment receipts",
                        "No production connections", "NOT FOR CUSTOMER DATA",
                        "HUMAN APPROVAL REQUIRED"]) {
    assert.ok(html.includes(phrase), phrase + " disclosure must remain visible");
  }
});
