"use strict";

// Synthetic dashboard markup contract. Run: node --test products/revenue_recovery/web/test_markup_contract.js
// Static checks are not a substitute for browser/assistive-technology acceptance.
const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
const js = fs.readFileSync(path.join(__dirname, "app.js"), "utf8");

test("every dashboard DOM lookup resolves to one unique element ID", () => {
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]);
  assert.equal(new Set(ids).size, ids.length, "duplicate element IDs");
  const lookups = [...js.matchAll(/\$\("([A-Za-z][A-Za-z0-9_-]*)"\)/g)].map(match => match[1]);
  assert.ok(lookups.length > 0, "no dashboard lookups found");
  for (const id of lookups) assert.ok(ids.includes(id), "missing dashboard element: " + id);
});

test("interactive synthetic controls have accessible labels and status regions", () => {
  assert.match(html, /<html\s+lang="en"/);
  assert.match(html, /<a\s+class="skip"\s+href="#main">/);
  assert.match(html, /<main\s+id="main"/);
  for (const id of ["draft", "scenarioChoice", "policyChoice"]) {
    assert.ok(html.includes('for="' + id + '"'), "missing label for " + id);
  }
  for (const id of ["connection", "copyStatus", "auditEvents", "policyEvents"]) {
    const tag = [...html.matchAll(/<[^>]+>/g)].map(match => match[0]).find(markup => new RegExp('\\bid="' + id + '"').test(markup));
    assert.ok(tag, "missing status element: " + id);
    assert.match(tag, /\\brole="status"/, "missing status role for " + id);
  }
  assert.match(html, /<caption\s+class="sr-only">/);
});

test("page is explicitly synthetic and loads only same-origin assets", () => {
  assert.match(html, /SYNTHETIC DATA ONLY/);
  assert.match(html, /NOT FOR CUSTOMER DATA/);
  const urls = [...html.matchAll(/(?:src|href)="([^"]+)"/g)].map(match => match[1]);
  assert.ok(urls.length > 0);
  for (const url of urls) {
    assert.ok(url.startsWith("#") || url.startsWith("./"), "unexpected external asset/link: " + url);
  }
  assert.doesNotMatch(html, /<form\b/i, "demo must not submit real customer data");
});
