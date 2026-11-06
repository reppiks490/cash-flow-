"use strict";
// Run: node products/revenue_recovery/web/dom_contract.test.cjs
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");
const root = __dirname;
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const js = fs.readFileSync(path.join(root, "app.js"), "utf8");

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
