/* Synthetic-only seed/refresh ordering regression; no network or dependencies. */
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {test} from "node:test";
import {runInNewContext} from "node:vm";

const script = readFileSync(new URL("./app.js", import.meta.url), "utf8");
function deferred() {
  let resolve, reject;
  const promise = new Promise((yes, no) => {resolve = yes; reject = no;});
  return {promise, resolve, reject};
}
const ok = payload => ({ok:true,json:async()=>payload});
const lead = {synthetic:true,external_ref:"DEMO-HVAC-001",source:"website",need:"repair",status:"received"};
const scorecard = {synthetic:true,counts:{received_demo_leads:1},verified:{
  payment_receipts:0,contractor_recovered_revenue_cents:0,
  rre_subscription_revenue_cents:0,rre_monthly_profit_cents:0}};
async function waitFor(h,n) {
  for(let i=0;i<30 && h.requests.length<n;i++) await new Promise(setImmediate);
  assert.ok(h.requests.length>=n,"expected request "+n);
}
function harness() {
  const nodes=new Map(), requests=[];
  const node=id=>{
    if(!nodes.has(id)) nodes.set(id,{textContent:"",value:"",disabled:false,children:[],
      replaceChildren(){this.children=[];},append(child){this.children.push(child);},
      addEventListener(){},setAttribute(){}});
    return nodes.get(id);
  };
  const sandbox={document:{getElementById:node,addEventListener(){},
    createElement:()=>({children:[],append(child){this.children.push(child);},
      addEventListener(){},setAttribute(){}})},
    fetch:(path,options)=>{assert.equal(options.credentials,"omit");
      const d=deferred();requests.push({path,...d});return d.promise;},
    location:{hostname:"localhost"},AbortController,setTimeout:()=>1,clearTimeout:()=>{}};
  runInNewContext(script,sandbox);
  return {sandbox,node,requests};
}
for (const newerRefreshSucceeds of [true,false]) {
  test("late failed seed cannot overwrite newer "+(newerRefreshSucceeds?"online":"offline")+" refresh",async()=>{
    const h=harness();
    const seed=h.sandbox.seedDemo();
    assert.equal(h.requests[0].path,"/api/demo/leads");
    const refresh=h.sandbox.refresh();
    assert.equal(h.requests[1].path,"/api/demo/leads");
    if(newerRefreshSucceeds) {
      h.requests[1].resolve(ok({synthetic:true,leads:[lead]}));
      await waitFor(h,3);
      assert.equal(h.requests[2].path,"/api/demo/scorecard");
      h.requests[2].resolve(ok(scorecard));
    } else {
      h.requests[1].reject(new Error("offline"));
    }
    await refresh;
    const status=h.node("connection").textContent;
    assert.match(status,newerRefreshSucceeds?/Connected/:/Offline fixture/);
    h.requests[0].reject(new Error("seed POST failed"));
    await seed;
    assert.equal(h.node("connection").textContent,status);
    assert.equal(h.node("seedDemo").disabled,false);
  });
}
