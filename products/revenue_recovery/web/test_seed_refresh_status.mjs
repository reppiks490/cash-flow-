/* RRE-03: synthetic seed POST success must not mask failed dashboard refresh. */
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {test} from "node:test";
import {runInNewContext} from "node:vm";

const script = readFileSync(new URL("./app.js", import.meta.url), "utf8");
const tick = () => new Promise(setImmediate);
function harness() {
  const nodes = new Map();
  const pending = [];
  const node = id => {
    if (!nodes.has(id)) nodes.set(id, {
      textContent:"",value:"",disabled:false,children:[],
      append(child){this.children.push(child);},
      replaceChildren(){this.children=[];},addEventListener(){},setAttribute(){}
    });
    return nodes.get(id);
  };
  const sandbox = {
    document:{getElementById:node,addEventListener(){},
      createElement:()=>({textContent:"",children:[],append(child){this.children.push(child);},
        addEventListener(){},setAttribute(){}})},
    fetch:(path,opts)=>{assert.equal(opts.credentials,"omit");let resolve,reject;
      const promise=new Promise((yes,no)=>{resolve=yes;reject=no;});
      pending.push({path,method:opts.method || "GET",resolve,reject});return promise;},
    AbortController,setTimeout:()=>1,clearTimeout:()=>{},location:{hostname:"localhost"}
  };
  runInNewContext(script,sandbox);
  return {sandbox,node,pending};
}
async function waitFor(h,n) {
  for(let i=0;i<30&&h.pending.length<n;i++) await tick();
  assert.ok(h.pending.length>=n,"expected request "+n);
}
const ok = payload => ({ok:true,json:async()=>payload});

test("successful synthetic seed POSTs followed by failed refresh retain offline warning",async()=>{
  const h=harness();
  const task=h.sandbox.seedDemo();
  for(let i=0;i<3;i++){
    await waitFor(h,i+1);
    assert.equal(h.pending[i].method,"POST");
    h.pending[i].resolve(ok({synthetic:true}));
  }
  await waitFor(h,4);
  assert.equal(h.pending[3].path,"/api/demo/leads");
  h.pending[3].reject(new Error("local API disconnected"));
  await task;
  assert.equal(h.node("leadSource").textContent,"Offline fixtures");
  assert.match(h.node("connection").textContent,/Offline fixture mode/);
  assert.equal(h.node("seedDemo").disabled,false);
});

test("successful seed and successful dashboard read show truthful success",async()=>{
  const h=harness();
  const task=h.sandbox.seedDemo();
  for(let i=0;i<3;i++){
    await waitFor(h,i+1);
    h.pending[i].resolve(ok({synthetic:true}));
  }
  await waitFor(h,4);
  h.pending[3].resolve(ok({synthetic:true,leads:[]}));
  await waitFor(h,5);
  h.pending[4].resolve(ok({synthetic:true,counts:{received_demo_leads:3},
    verified:{payment_receipts:0,contractor_recovered_revenue_cents:0,
      rre_subscription_revenue_cents:0,rre_monthly_profit_cents:0}}));
  await task;
  assert.equal(h.node("leadSource").textContent,"Local API");
  assert.match(h.node("connection").textContent,/Three explicitly synthetic examples/);
});
