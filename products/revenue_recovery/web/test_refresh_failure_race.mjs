/* Synthetic-only regression: a failed newer refresh invalidates older scorecard work. */
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {test} from "node:test";
import {runInNewContext} from "node:vm";

const source = readFileSync(new URL("./app.js", import.meta.url), "utf8");
function deferred() {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return {promise, resolve, reject};
}
function harness() {
  const pending = [], nodes = new Map();
  function node(id) {
    if (!nodes.has(id)) nodes.set(id, {
      textContent:"", value:"", children:[], disabled:false,
      append(child){this.children.push(child);},
      replaceChildren(){this.children=[];},
      addEventListener(){},setAttribute(){}
    });
    return nodes.get(id);
  }
  const document = {
    getElementById:node, addEventListener(){},
    createElement:()=>({textContent:"",children:[],
      append(child){this.children.push(child);},addEventListener(){},setAttribute(){}})
  };
  const sandbox = {
    document, AbortController, location:{hostname:"localhost"},
    setTimeout:()=>1,clearTimeout:()=>{},
    fetch:(path,options)=>{
      assert.equal(options.credentials,"omit");
      const request = deferred();
      pending.push({path,...request});
      return request.promise;
    }
  };
  runInNewContext(source,sandbox);
  return {sandbox,pending,node};
}
const lead = {synthetic:true,external_ref:"DEMO-RACE-1",source:"website",need:"repair",status:"received"};
const response = payload => ({ok:true,json:async()=>payload});
const score = {synthetic:true,counts:{received_demo_leads:77},
  verified:{payment_receipts:0,contractor_recovered_revenue_cents:0,
    rre_subscription_revenue_cents:0,rre_monthly_profit_cents:0}};

test("older scorecard cannot overwrite newer offline fallback after failed refresh",async()=>{
  const h=harness();
  const older=h.sandbox.refresh();
  assert.equal(h.pending[0].path,"/api/demo/leads");
  h.pending[0].resolve(response({synthetic:true,leads:[lead]}));
  for(let i=0;i<20 && h.pending.length<2;i++) await new Promise(setImmediate);
  assert.equal(h.pending[1].path,"/api/demo/scorecard");

  const newer=h.sandbox.refresh();
  assert.equal(h.pending[2].path,"/api/demo/leads");
  h.pending[2].reject(new Error("newest refresh offline"));
  await newer;
  assert.equal(h.node("leadSource").textContent,"Offline fixtures");
  assert.match(h.node("scorecardInfo").textContent,/Offline examples only/);

  h.pending[1].resolve(response(score));
  await older;
  assert.equal(h.node("leadSource").textContent,"Offline fixtures");
  assert.match(h.node("scorecardInfo").textContent,/Offline examples only/);
  assert.doesNotMatch(h.node("scorecardInfo").textContent,/inquiries: 77/);
  assert.match(h.node("connection").textContent,/Offline fixture mode/);
});
