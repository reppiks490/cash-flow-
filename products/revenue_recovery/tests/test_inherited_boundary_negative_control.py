"""SEC-TEST-02: real inherited-field fixture and deliberately defective negative control.

Runs in existing product unittest discovery; Node built-ins only, no network or data.
"""
import pathlib
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "web" / "app.js"

SCRIPT = r"""
"use strict";
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const source = fs.readFileSync(process.argv[1], "utf8");
const original = 'return {synthetic:true,external_ref:value.external_ref,source:value.source,need:value.need,status:value.status};';
const mode = process.argv[2];
const actualSource = mode === "mutant" ? source.replace(original, 'return Object.assign({}, value, {phone:value.phone,operator_authorized:value.operator_authorized});') : source;
if (mode === "mutant" && (actualSource === source || !source.includes(original))) {
  throw Error("MUTATION_SETUP_FAILED: expected safeLead return not found");
}
const inherited = Object.create({phone:"555-555-1234", operator_authorized:true});
Object.assign(inherited, {
  synthetic:true, external_ref:"DEMO-HVAC-001",
  source:"website", need:"repair", status:"received"
});
assert.equal(Object.hasOwn(inherited, "phone"), false);
assert.equal(inherited.phone, "555-555-1234");
const context = {document:{addEventListener(){}}, AbortController, setTimeout, clearTimeout, injected:inherited};
vm.createContext(context);
vm.runInContext(actualSource, context, {timeout:1500});
const accepted = vm.runInContext("safeLead(injected)", context, {timeout:1500});
assert.ok(accepted, "valid synthetic lead rejected");
assert.equal(accepted.external_ref, "DEMO-HVAC-001");
assert.deepEqual(Object.keys(accepted).sort(),
  ["synthetic","external_ref","source","need","status"].sort());
assert.equal(Object.hasOwn(accepted, "phone"), false, "inherited phone copied");
assert.equal(Object.hasOwn(accepted, "operator_authorized"), false,
  "inherited authorization copied");
console.log("INHERITED_BOUNDARY_PASS");
"""

@unittest.skipUnless(shutil.which("node"), "Node runtime unavailable; CI must provide Node")
class InheritedBoundary(unittest.TestCase):
    def run_case(self, mode):
        return subprocess.run(
            ["node", "-e", SCRIPT, str(APP), mode],
            capture_output=True, text=True, timeout=10, check=False,
        )

    def test_inherited_fields_reach_actual_vm_boundary_and_are_stripped(self):
        result = self.run_case("original")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("INHERITED_BOUNDARY_PASS", result.stdout)

    def test_deliberately_unsafe_normalizer_is_detected(self):
        result = self.run_case("mutant")
        self.assertNotEqual(result.returncode, 0, "negative control escaped detection")
        self.assertNotIn("MUTATION_SETUP_FAILED", result.stderr)
        self.assertRegex(result.stderr, "inherited phone copied|inherited authorization copied|Expected values to be strictly deep-equal")


if __name__ == "__main__":
    unittest.main()
