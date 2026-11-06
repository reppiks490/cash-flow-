"use strict";
// Run: node products/revenue_recovery/web/dom_contract.test.cjs
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");
const root = __dirname;
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const js = fs.readFileSync(path.join(root, "app.js"), "utf8");
const css = fs.readFileSync(path.join(root, "styles.css"), "utf8");

test("every JS-selected DOM ID exists exactly once", () => {
  const ids = [...js.matchAll(/\$\("([A-Za-z][\w-]*)"\)/g)].map(match => match[1]);
  assert.ok(ids.length > 0, "test must discover selectors");
  for (const id of new Set(ids)) {
    const occurrences = [...html.matchAll(/\bid="([^"]+)"/g)].filter(match => match[1] === id);
    assert.equal(occurrences.length, 1, `Expected one element with id=${id}`);
  }
});

test("critical status and draft controls have accessible labels", () => {
  assert.match(html, /<label\s+for="draft">/);
  assert.match(html, /id="connection"[^>]*role="status"|role="status"[^>]*id="connection"/);
  assert.match(html, /id="copyStatus"[^>]*role="status"|role="status"[^>]*id="copyStatus"/);
  assert.match(html, /<a\s+class="skip"\s+href="#main">/);
});

test("prototype resources are local and contain no inline event handlers", () => {
  assert.match(html, /src="\.\/app\.js"/);
  assert.match(html, /href="\.\/styles\.css"/);
  assert.doesNotMatch(html, /\bon(?:click|submit|load|error)\s*=/i);
  assert.doesNotMatch(html, /(?:src|href)="https?:\/\//i);
});

test("synthetic and unverified revenue warnings remain prominent", () => {
  assert.match(html, /SYNTHETIC DATA ONLY/);
  assert.match(html, /Verified recovered revenue/);
  assert.match(html, /No authenticated payment receipts/);
  assert.match(html, /HUMAN APPROVAL REQUIRED/);
  assert.match(html, /NOT FOR CUSTOMER DATA/);
});

test("narrow lead table is a named keyboard-focusable scroll region", () => {
  assert.match(html, /<div class="table-scroll"[^>]*tabindex="0"[^>]*role="region"[^>]*aria-label="[^"]+"/);
  assert.match(html, /focus the table and use horizontal arrow keys/);
  assert.match(css, /\\.table-scroll:focus-visible/);
  assert.match(css, /\\.table-scroll\\s*\\{[^}]*overscroll-behavior-x:\\s*contain/);
});

test("synthetic timeline and policy output are keyboard-focusable", () => {
  for (const id of ["auditEvents", "policyEvents"]) {
    const tag = [...html.matchAll(/<pre\\s+[^>]*>/g)].map(x => x[0])
      .find(x => x.includes('id="' + id + '"'));
    assert.ok(tag, id + " must be present");
    assert.match(tag, /tabindex="0"/);
    assert.match(tag, /aria-label="[^"]+"/);
  }
  assert.match(css, /\\.audit-events:focus-visible/);
});

test("responsive action buttons preserve 44px target and visible focus", () => {
  assert.match(css, /@media\\s*\\(max-width:\\s*760px\\)/);
  assert.match(css, /\\.top-actions button\\s*\\{\\s*min-height:\\s*44px/);
  assert.match(css, /outline:\\s*2px solid/);
});
