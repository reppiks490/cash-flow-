'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const css = fs.readFileSync(path.join(__dirname, 'styles.css'), 'utf8');
const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');

test('narrow mobile breakpoint keeps metric cards in one column', () => {
  const narrow = css.match(/@media\s*\(max-width:\s*420px\)\s*\{([\s\S]*?)\n\}/);
  assert.ok(narrow, '420px narrow-screen rule must exist');
  assert.match(narrow[1], /\.metrics\s*\{\s*grid-template-columns:\s*minmax\(0,\s*1fr\)/);
  assert.match(narrow[1], /\.top-actions button\s*\{[^}]*width:\s*100%/);
  assert.match(narrow[1], /\.outcome strong\s*\{[^}]*overflow-wrap:\s*anywhere/);
});

test('narrow mobile styles target actual dashboard elements', () => {
  assert.match(html, /class="metrics"/);
  assert.match(html, /class="top-actions"/);
  assert.match(html, /class="outcome"/);
  assert.match(html, /name="viewport"\s+content="width=device-width, initial-scale=1"/);
});

test('narrow mobile actions retain minimum touch target and prevent cramped badges', () => {
  const narrow = css.match(/@media\s*\(max-width:\s*420px\)\s*\{([\s\S]*?)\n\}/);
  assert.ok(narrow, '420px narrow-screen rule must exist');
  assert.match(narrow[1], /\.top-actions\s*\{[^}]*align-items:\s*stretch/);
  assert.match(narrow[1], /\.top-actions button\s*\{[^}]*min-height:\s*44px/);
  assert.match(narrow[1], /\.badge\s*\{[^}]*max-width:\s*100%/);
  assert.match(narrow[1], /\.outcome\s*\{[^}]*flex-wrap:\s*wrap/);
});
