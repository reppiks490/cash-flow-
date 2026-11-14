"use strict";

// Static accessibility contract for the synthetic-only dashboard.
// These checks do not replace browser, screen-reader, or keyboard acceptance.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
const css = fs.readFileSync(path.join(__dirname, "styles.css"), "utf8");

test("document declares language, viewport, and synthetic demo identity", () => {
  assert.match(html, /<html\s+lang="en">/i);
  assert.match(html, /<meta\s+name="viewport"\s+content="width=device-width, initial-scale=1">/i);
  assert.match(html, /<title>[^<]*Synthetic Demo<\/title>/i);
  assert.match(html, /SYNTHETIC DATA ONLY/);
});

test("skip link targets the unique main landmark and focus is visible", () => {
  assert.match(html, /<a\s+class="skip"\s+href="#main">Skip to dashboard<\/a>/);
  assert.equal((html.match(/<main\s+id="main">/g) || []).length, 1);
  assert.match(css, /\.skip:focus\s*\{[^}]*top:\s*10px/);
});

test("navigation and lead table have accessible names and headers", () => {
  assert.match(html, /<nav\s+aria-label="Sections">/);
  assert.match(html, /<div\s+class="table-scroll"[^>]*tabindex="0"[^>]*role="region"[^>]*aria-label="[^"]+"/);
  assert.match(html, /<table><caption\s+class="sr-only">Synthetic HVAC lead records<\/caption>/);
  assert.equal((html.match(/<th\s+scope="col">/g) || []).length, 5);
  assert.match(css, /\.table-scroll:focus-visible/);
});

test("draft and simulator inputs have explicit labels and status feedback", () => {
  for (const id of ["draft", "scenarioChoice", "policyChoice"]) {
    assert.match(html, new RegExp('<label\\s+for="' + id + '">'));
    assert.match(html, new RegExp('<(?:textarea|select)\\s+id="' + id + '"'));
  }
  for (const id of ["connection", "copyStatus", "auditEvents", "policyEvents"]) {
    assert.match(html, new RegExp('<[^>]*(?=[^>]*\\bid="' + id + '")(?=[^>]*\\brole="status")[^>]*>'));
  }
});

test("synthetic actions are buttons, not navigation to outbound endpoints", () => {
  for (const id of ["seedDemo", "refresh", "copyDraft", "runScenario", "runPolicy"]) {
    assert.match(html, new RegExp('<button(?=[^>]*\\btype="button")(?=[^>]*\\bid="' + id + '")[^>]*>'));
  }
  assert.doesNotMatch(html, /<form\b/i);
  assert.doesNotMatch(html, /<script[^>]+src="https?:\/\//i);
});
