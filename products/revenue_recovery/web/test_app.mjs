/* Dependency-free, synthetic-only UI behavior tests using Node's built-in VM.
 * This is not a Chromium visual acceptance test and never performs network I/O.
 */
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {test} from "node:test";
import {runInNewContext} from "node:vm";

const script = readFileSync(new URL("./app.js", import.meta.url), "utf8");
const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");

function harness({unsafePreview = false, brokenScenario = false,
                  previewMessage = "SYNTHETIC UNSENT DRAFT: review first",
                  badEventType = false, badPolicyReason = false,
                  forgedSuppression = false} = {}) {
  const nodes = new Map();
  const requests = [];
  const lead = {
    synthetic: true, external_ref: "DEMO-NODE-01",
    source: "website", need: "AC not cooling", status: "received"
  };
  let domReady = null;
  function element(id) {
    if (!nodes.has(id)) {
      nodes.set(id, {
        textContent: "", value: id === "scenarioChoice" ? "review" : "",
        disabled: false, children: [], listeners: {}, attributes: {},
        addEventListener(event, handler) {this.listeners[event] = handler;},
        setAttribute(key, value) {this.attributes[key] = value;},
        replaceChildren() {this.children = [];},
        append(child) {this.children.push(child);}
      });
    }
    return nodes.get(id);
  }
  const document = {
    getElementById: element,
    createElement: () => ({
      textContent: "", className: "", children: [], listeners: {},
      append(child) {this.children.push(child);},
      addEventListener(event, handler) {this.listeners[event] = handler;},
      setAttribute() {},
    }),
    addEventListener(event, handler) {
      if (event === "DOMContentLoaded") domReady = handler;
    }
  };
  const ok = payload => ({ok:true, json: async () => payload});
  const fetch = async (path, opts = {}) => {
    requests.push({path, method: opts.method ?? "GET", credentials: opts.credentials});
    if (path === "/api/demo/leads") {
      if (opts.method === "POST") {
        const item = JSON.parse(opts.body);
        assert.equal(item.synthetic, true);
        assert.equal(typeof item.external_ref, "string");
        assert.equal(item.external_ref.startsWith("DEMO-"), true);
        assert.equal(Object.keys(item).length, 4);
        return ok({created: true, lead:item});
      }
      return ok({synthetic:true, leads:[lead]});
    }
    if (path === "/api/demo/scorecard") {
      return ok({
        synthetic:true,
        counts:{received_demo_leads:1},
        verified:{
          payment_receipts:0, contractor_recovered_revenue_cents:0,
          rre_subscription_revenue_cents:0, rre_monthly_profit_cents:0
        }
      });
    }
    if (path === "/api/demo/recovery/DEMO-NODE-01") {
      return ok({synthetic:true, preview:{
        synthetic:true, external_ref:lead.external_ref,
        qualification:{result:"manual_review_required", qualified:false, consent_verified:false},
        followup:{status:"unsent_unapproved_draft", approved:unsafePreview,
          transmitted:false, message:previewMessage},
        crm:{dry_run:true, transmitted:false},
        appointment:{confirmed:false},
        attribution:{verified_recovered_revenue_cents:0}
      }});
    }
    if (path.startsWith("/api/demo/policy/DEMO-NODE-01/")) {
      const mode = path.split("/").at(-1);
      const suppressed = mode === "revoked_mock";
      return ok({synthetic:true, policy:{
        synthetic:true, external_ref:lead.external_ref, mode,
        suppressed:forgedSuppression ? true : suppressed, consent_verified:false, operator_authorized:false,
        may_contact_real_person:false, actual_message_sent:false,
        reasons:[badPolicyReason ? "Call Jane at 555-0100" :
          (suppressed ? "synthetic_opt_out_revocation" : "consent_evidence_unverified")],
        draft:suppressed ? null : "UNSENT INTERNAL MOCK ONLY"
      }});
    }
    if (path.startsWith("/api/demo/scenarios/DEMO-NODE-01/")) {
      return ok({synthetic:true, scenario:{
        synthetic:true, external_ref:lead.external_ref,
        scenario:"closed_job_mock",
        events:[{synthetic:true, sequence:1,
          event_type:badEventType ? "Call Jane at 555-0100" : "inquiry_observed_synthetic",
          source_evidence_verified:false, external_side_effect:brokenScenario}],
        metrics:{
          actual_messages_sent:0, actual_bookings_confirmed:0,
          actual_jobs_closed:0, verified_recovered_revenue_cents:0,
          verified_rre_subscription_revenue_cents:0, verified_payment_receipts:0
        }
      }});
    }
    throw new Error("Unexpected external or send endpoint " + path);
  };
  const sandbox = {
    document, fetch, location:{hostname:"localhost"},
    navigator:{clipboard:{writeText:async()=>{}}},
    AbortController,
    setTimeout: () => 1,
    clearTimeout: () => {}
  };
  runInNewContext(script, sandbox, {timeout:1000});
  return {sandbox, nodes, requests, start: () => domReady()};
}

test("browser exposes clearly synthetic, safe UI controls", () => {
  assert.match(html, /SYNTHETIC DATA ONLY/);
  assert.match(html, /Recovery process simulator/);
  assert.match(html, /Mock job close \(unverified\)/);
  assert.match(html, /No authenticated payment receipts/);
  assert.ok(!script.includes("innerHTML"));
  assert.ok(!script.includes("localStorage"));
});

test("dashboard refresh consumes zero-claim scorecard", async () => {
  const h = harness();
  await h.sandbox.refresh();
  assert.equal(h.nodes.get("leadCount").textContent, "1");
  assert.match(h.nodes.get("scorecardInfo").textContent, /Real customer count: unknown/);
  assert.ok(h.requests.every(x => x.credentials === "omit"));
});

test("draft selection consumes safe same-origin preview, not a send endpoint", async () => {
  const h = harness();
  await h.sandbox.refresh();
  await h.sandbox.selectLead(0);
  assert.match(h.nodes.get("draft").value, /SYNTHETIC UNSENT DRAFT/);
  assert.match(h.nodes.get("copyStatus").textContent, /human review/);
  assert.ok(h.requests.some(x => x.path.includes("/api/demo/recovery/")));
  assert.ok(h.requests.every(x => !x.path.includes("/api/send")));
});

test("forged approved preview is rejected to offline synthetic fallback", async () => {
  const h = harness({unsafePreview:true});
  await h.sandbox.refresh();
  await h.sandbox.selectLead(0);
  assert.match(h.nodes.get("draft").value, /OFFLINE SYNTHETIC FALLBACK/);
  assert.match(h.nodes.get("copyStatus").textContent, /Not sent, approved, or verified/);
});

test("scenario view labels mock stages and refuses a corrupt evidence event", async () => {
  const safe = harness();
  await safe.sandbox.refresh();
  await safe.sandbox.selectLead(0);
  safe.sandbox.document.getElementById("scenarioChoice").value = "closed_job_mock";
  await safe.sandbox.loadScenario();
  assert.match(safe.nodes.get("auditEvents").textContent, /SYNTHETIC/);
  assert.match(safe.nodes.get("auditEvents").textContent, /Verified recovered revenue: \$0/);
  const broken = harness({brokenScenario:true});
  await broken.sandbox.refresh();
  await broken.sandbox.selectLead(0);
  broken.sandbox.document.getElementById("scenarioChoice").value = "closed_job_mock";
  await broken.sandbox.loadScenario();
  assert.match(broken.nodes.get("auditEvents").textContent, /timeline unavailable/);
});

test("opt-out simulation suppresses drafts even when mock consent is offered", async () => {
  const h = harness();
  await h.sandbox.refresh();
  await h.sandbox.selectLead(0);
  h.sandbox.document.getElementById("policyChoice").value = "revoked_mock";
  await h.sandbox.loadPolicy();
  assert.match(h.nodes.get("policyEvents").textContent, /Internal draft: SUPPRESSED/);
  assert.match(h.nodes.get("policyEvents").textContent, /Real outreach: DISABLED/);
  h.sandbox.document.getElementById("policyChoice").value = "consent_record_mock";
  await h.sandbox.loadPolicy();
  assert.match(h.nodes.get("policyEvents").textContent, /UNSENT \/ REVIEW ONLY/);
  assert.ok(h.requests.every(x => !x.path.includes("/api/send")));
});

test("seed action posts only three local synthetic categorical leads", async () => {
  const h = harness();
  await h.sandbox.seedDemo();
  const posts = h.requests.filter(x => x.method === "POST");
  assert.equal(posts.length, 3);
  assert.ok(posts.every(x => x.path === "/api/demo/leads" && x.credentials === "omit"));
  assert.match(h.nodes.get("connection").textContent, /explicitly synthetic examples/);
});

for (const message of ["Contact customer@example.com", "See https://example.com", "Call 555-123-4567", "A".repeat(1501), "Unsafe\u0000control"]) {
  test("reject unsafe or unbounded preview draft: " + JSON.stringify(message).slice(0,60), async () => {
    const h = harness({previewMessage:message});
    await h.sandbox.refresh();
    await h.sandbox.selectLead(0);
    assert.match(h.nodes.get("draft").value, /OFFLINE SYNTHETIC FALLBACK/);
    assert.doesNotMatch(h.nodes.get("draft").value, /customer@example.com|https:\/\/example.com|555-123-4567|Unsafe/);
  });
}

test("untrusted scenario event type is rejected instead of displayed", async () => {
  const h = harness({badEventType:true});
  await h.sandbox.refresh();
  await h.sandbox.selectLead(0);
  h.sandbox.document.getElementById("scenarioChoice").value = "closed_job_mock";
  await h.sandbox.loadScenario();
  assert.match(h.nodes.get("auditEvents").textContent, /timeline unavailable/);
  assert.doesNotMatch(h.nodes.get("auditEvents").textContent, /Call Jane/);
});

test("untrusted policy reason is rejected instead of displayed", async () => {
  const h = harness({badPolicyReason:true});
  await h.sandbox.refresh();
  await h.sandbox.selectLead(0);
  h.sandbox.document.getElementById("policyChoice").value = "unknown";
  await h.sandbox.loadPolicy();
  assert.match(h.nodes.get("policyEvents").textContent, /Policy preview unavailable/);
  assert.doesNotMatch(h.nodes.get("policyEvents").textContent, /Call Jane/);
});

test("mock unknown consent cannot claim suppressed while retaining a draft", async () => {
  const h = harness({forgedSuppression:true});
  await h.sandbox.refresh();
  await h.sandbox.selectLead(0);
  h.sandbox.document.getElementById("policyChoice").value = "unknown";
  await h.sandbox.loadPolicy();
  assert.match(h.nodes.get("policyEvents").textContent, /Policy preview unavailable/);
  assert.doesNotMatch(h.nodes.get("policyEvents").textContent, /UNSENT \/ REVIEW ONLY/);
});
