"use strict";

// Synthetic dashboard markup contract. Run: node --test products/revenue_recovery/web/markup_contract.test.cjs
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
    const tag = [...html.matchAll(/<[^>]+>/g)].map(match => match[0]).find(markup => markup.includes('id="' + id + '"'));
    assert.ok(tag, "missing status element: " + id);
    assert.match(tag, /\brole="status"/, "missing status role for " + id);
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


test("navigation targets exist and dashboard buttons cannot submit forms", () => {
  const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]));
  const anchors = [...html.matchAll(/<a\b[^>]*\bhref="#([^"]+)"[^>]*>/g)];
  assert.ok(anchors.length >= 4, "missing dashboard navigation links");
  for (const [, target] of anchors) assert.ok(ids.has(target), "missing navigation target: " + target);
  const buttons = [...html.matchAll(/<button\b[^>]*>/g)].map(match => match[0]);
  assert.ok(buttons.length >= 5, "missing dashboard actions");
  for (const button of buttons) assert.match(button, /\btype="button"/, "button must not submit: " + button);
  assert.doesNotMatch(html, /\son[a-z]+\s*=/i, "inline event handlers are not allowed");
});

test("dashboard script avoids executable HTML sinks and browser persistence", () => {
  // Source-level tripwire, not a runtime security guarantee.
  assert.doesNotMatch(js, /\.innerHTML\s*=|\.outerHTML\s*=|insertAdjacentHTML\s*\(/,
    "dashboard must use textContent and DOM nodes for untrusted values");
  assert.doesNotMatch(js, /\beval\s*\(|\bnew\s+Function\s*\(/,
    "dynamic code evaluation is not permitted");
  assert.doesNotMatch(js, /\b(?:localStorage|sessionStorage|indexedDB)\b/,
    "synthetic lead or draft data must not persist in browser storage");
  assert.doesNotMatch(js, /\b(?:WebSocket|EventSource|sendBeacon)\s*\(/,
    "dashboard must not introduce background outbound channels");
});

test("synthetic dashboard fetches remain read-only and omit browser credentials", () => {
  // Defense-in-depth source tripwire; server authorization must independently enforce read-only access.
  const calls = [...js.matchAll(/\\bfetch\\s*\\(([^;]+?)\\)\\s*;/gs)].map(match => match[1]);
  assert.ok(calls.length >= 5, "expected dashboard API reads");
  for (const call of calls) {
    assert.match(call, /credentials\\s*:\\s*["']omit["']/, "API fetch must omit credentials");
    assert.doesNotMatch(call, /\\bmethod\\s*:\\s*["'](?:POST|PUT|PATCH|DELETE)["']/i,
      "synthetic dashboard must not mutate server data");
  }
  assert.doesNotMatch(js, /\\b(?:XMLHttpRequest|navigator\\.sendBeacon)\\b/,
    "unexpected alternate network transport");
});
