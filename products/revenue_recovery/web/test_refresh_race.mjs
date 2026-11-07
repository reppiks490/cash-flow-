/* Synthetic-only async race regressions; no network, dependencies or browser required. */
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {test} from "node:test";
import {runInNewContext} from "node:vm";
// Register additional source-preserved race tests under the existing CI Node entrypoint.
import "./test_refresh_failure_race.mjs";
import "./test_seed_refresh_status.mjs";
import "./test_seed_status_ownership.mjs";

const script = readFileSync(new URL("./app.js", import.meta.url), "utf8");
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => {resolve = yes; reject = no;});
  return {promise, resolve, reject};
};
const response = payload => ({ok:true, json:async()=>payload});
async function untilRequests(h, count) {
  for (let i=0; i<20 && h.pending.length<count; i++) await new Promise(setImmediate);
  assert.ok(h.pending.length>=count, "expected deferred fetch request");
}
const lead = ref => ({synthetic:true,external_ref:ref,source:"website",need:"repair",status:"received"});
const score = count => ({synthetic:true,counts:{received_demo_leads:count},
  verified:{payment_receipts:0,contractor_recovered_revenue_cents:0,
    rre_subscription_revenue_cents:0,rre_monthly_profit_cents:0}});

function harness() {
  const nodes = new Map();
  const pending = [];
  const node = id => {
    if (!nodes.has(id)) nodes.set(id, {
      textContent:"",value:"",children:[],append(child){this.children.push(child);},
      replaceChildren(){this.children=[];},addEventListener(){},setAttribute(){}
    });
    return nodes.get(id);
  };
  const sandbox = {
    document:{getElementById:node,addEventListener(){},
      createElement:()=>({textContent:"",children:[],append(child){this.children.push(child);},
        addEventListener(){},setAttribute(){}})},
    fetch:(path,opts)=>{assert.equal(opts.credentials,"omit");const d=deferred();
      pending.push({path,...d});return d.promise;},
    AbortController,setTimeout:()=>1,clearTimeout:()=>{},location:{hostname:"localhost"}
  };
  runInNewContext(script,sandbox);
  return {sandbox,pending,node};
}

test("older successful lead refresh cannot replace newer response",async()=>{
  const h=harness();
  const older=h.sandbox.refresh(),newer=h.sandbox.refresh();
  assert.equal(h.pending.length,2);
  h.pending[1].resolve(response({synthetic:true,leads:[lead("DEMO-NEW")]}));
  await untilRequests(h, h.pending.length === 2 ? 3 : h.pending.length === 1 ? 2 : 4);
  assert.equal(h.pending[2].path,"/api/demo/scorecard");
  h.pending[2].resolve(response(score(1)));await newer;
  h.pending[0].resolve(response({synthetic:true,leads:[lead("DEMO-OLD")]}));await older;
  assert.equal(h.node("leadRows").children[0].children[0].textContent,"DEMO-NEW");
  assert.match(h.node("connection").textContent,/Connected/);
});

test("older failed refresh cannot overwrite successful newer dashboard",async()=>{
  const h=harness();
  const older=h.sandbox.refresh(),newer=h.sandbox.refresh();
  h.pending[1].resolve(response({synthetic:true,leads:[lead("DEMO-NEW")]}));
  await untilRequests(h, h.pending.length === 2 ? 3 : h.pending.length === 1 ? 2 : 4);
  h.pending[2].resolve(response(score(1)));await newer;
  h.pending[0].reject(new Error("old offline"));await older;
  assert.equal(h.node("leadSource").textContent,"Local API");
  assert.match(h.node("connection").textContent,/Connected/);
});

test("older scorecard cannot overwrite newer refresh scorecard",async()=>{
  const h=harness();
  const older=h.sandbox.refresh();
  h.pending[0].resolve(response({synthetic:true,leads:[lead("DEMO-OLD")]}));
  await untilRequests(h, h.pending.length === 2 ? 3 : h.pending.length === 1 ? 2 : 4);
  assert.equal(h.pending[1].path,"/api/demo/scorecard");
  const newer=h.sandbox.refresh();
  h.pending[2].resolve(response({synthetic:true,leads:[lead("DEMO-NEW")]}));
  await untilRequests(h, h.pending.length === 2 ? 3 : h.pending.length === 1 ? 2 : 4);
  h.pending[3].resolve(response(score(9)));await newer;
  h.pending[1].resolve(response(score(1)));await older;
  assert.match(h.node("scorecardInfo").textContent,/inquiries: 9/);
  assert.match(h.node("connection").textContent,/Connected/);
});

// A compromised or incompatible demo endpoint must not present impossible counts.
test("negative and excessive synthetic scorecard counts fail closed",async()=>{
  for (const invalid of [-1,2001,Number.MAX_SAFE_INTEGER]) {
    const h=harness();
    const pending=h.sandbox.refreshScorecard();
    assert.equal(h.pending.length,1);
    h.pending[0].resolve(response(score(invalid)));
    await pending;
    assert.match(h.node("scorecardInfo").textContent,/disconnected/);
    assert.doesNotMatch(h.node("scorecardInfo").textContent,/inquiries:/);
  }
});
