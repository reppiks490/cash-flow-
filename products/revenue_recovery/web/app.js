"use strict";

// Local-only synthetic UI. Never send messages or persist contact information.
const FIXTURES = Object.freeze([
  {synthetic:true,external_ref:"DEMO-HVAC-001",source:"website",need:"AC not cooling",status:"received"},
  {synthetic:true,external_ref:"DEMO-HVAC-002",source:"phone",need:"estimate follow-up",status:"received"},
  {synthetic:true,external_ref:"DEMO-HVAC-003",source:"referral",need:"AC maintenance",status:"received"}
]);
// Mirror backend/contracts.py's synthetic-only categorical intake contract.
// A browser payload is untrusted even if it is labeled synthetic.
const DEMO_SOURCES = new Set(["demo", "website", "phone", "referral"]);
const DEMO_NEEDS = new Set(["AC not cooling", "AC maintenance", "repair",
  "maintenance", "estimate follow-up", "heating issue"]);
const DEMO_REF = /^(?:DEMO|QA)[-_][A-Za-z0-9_-]{1,56}$/i;
const DEMO_KEYS = new Set(["synthetic", "external_ref", "source", "need", "status"]);
const $ = id => document.getElementById(id);
let leads = [];
let selectionSequence = 0;
let selectedReference = null;
let scenarioRequestSequence = 0;
let policyRequestSequence = 0;

function safeLead(value) {
  if (!value || typeof value !== "object" || Array.isArray(value) || value.synthetic !== true) return null;
  const keys = Object.keys(value);
  if (keys.length !== DEMO_KEYS.size || keys.some(key => !DEMO_KEYS.has(key))) return null;
  if (typeof value.external_ref !== "string") return null;
  const match = DEMO_REF.exec(value.external_ref);
  if (!match || match[0] !== value.external_ref) return null;
  if (!DEMO_SOURCES.has(value.source) || !DEMO_NEEDS.has(value.need) ||
      value.status !== "received") return null;
  return {synthetic:true,external_ref:value.external_ref,source:value.source,need:value.need,status:value.status};
}

function safeDraftMessage(value) {
  // Finite synthetic template previews must not expose contact details or unbounded text.
  return typeof value === "string" && value.length > 0 && value.length <= 1500 &&
    /^[\x20-\x7e\n]*$/.test(value) &&
    !/https?:\/\/|www\.|@|\b\d{3}[-. ]?\d{3}[-. ]?\d{4}\b/i.test(value);
}

function draftFor(lead) {
  return "Hello,\n\nThanks for reaching out about your HVAC request (" +
    lead.external_ref + "). We can review your service needs and discuss available appointment options. " +
    "Would you like us to prepare a proposed next step?\n\n" +
    "This is an UNSENT synthetic draft. Confirm consent, customer identity and accurate details before any real communication.";
}

async function selectLead(index) {
  const lead = leads[index];
  if (!lead) return;
  selectedReference = lead.external_ref;
  $("auditEvents").textContent = "Lead " + selectedReference + " selected. Choose a mock scenario to inspect.";
  $("policyEvents").textContent = "Lead " + selectedReference + " selected. Choose a synthetic consent case to inspect.";
  const requestNumber = ++selectionSequence;
  $("draft").value = "Preparing local synthetic preview...";
  $("copyStatus").textContent = "Checking read-only preview for " + lead.external_ref + " (no messages sent).";
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 2500);
  try {
    const url = "/api/demo/recovery/" + encodeURIComponent(lead.external_ref);
    const response = await fetch(url, {cache:"no-store",credentials:"omit",signal:controller.signal});
    if (!response.ok) throw new Error("Review preview unavailable");
    const data = await response.json();
    const p = data && data.preview;
    if (data.synthetic !== true || !p || p.synthetic !== true ||
        p.external_ref !== lead.external_ref ||
        !p.qualification || p.qualification.result !== "manual_review_required" ||
        p.qualification.qualified !== false || p.qualification.consent_verified !== false ||
        !p.followup || p.followup.status !== "unsent_unapproved_draft" ||
        p.followup.approved !== false || p.followup.transmitted !== false ||
        !safeDraftMessage(p.followup.message) ||
        !p.crm || p.crm.dry_run !== true || p.crm.transmitted !== false ||
        !p.appointment || p.appointment.confirmed !== false ||
        !p.attribution || p.attribution.verified_recovered_revenue_cents !== 0) {
      throw new Error("Unsafe or incompatible review preview");
    }
    if (requestNumber !== selectionSequence) return;
    $("draft").value = p.followup.message;
    $("copyStatus").textContent = "Read-only local API preview for " + lead.external_ref +
       ". UNSENT; not approved; qualification and consent require human review.";
  } catch (_error) {
    if (requestNumber !== selectionSequence) return;
    $("draft").value = "OFFLINE SYNTHETIC FALLBACK — NOT SERVER GENERATED.\n\n" + draftFor(lead);
    $("copyStatus").textContent = "Offline fixture draft for " + lead.external_ref +
       ". Not sent, approved, or verified.";
  } finally {clearTimeout(timeout);}
}

function render(rows, source) {
  selectionSequence += 1;
  selectedReference = null;
  $("auditEvents").textContent = "Select a lead above to inspect the synthetic evidence path.";
  $("policyEvents").textContent = "No real communication is enabled.";
  $("draft").value = "Select a synthetic lead above.";
  $("copyStatus").textContent = "";
  leads = rows.map(safeLead).filter(Boolean);
  $("leadCount").textContent = String(leads.length);
  $("followCount").textContent = String(leads.length);
  $("leadSource").textContent = source;
  const tbody = $("leadRows");
  tbody.replaceChildren();
  if (!leads.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 5; td.className = "empty"; td.textContent = "No synthetic leads in the current view.";
    tr.append(td); tbody.append(tr);
    return;
  }
  for (const [index, lead] of leads.entries()) {
    const tr = document.createElement("tr");
    for (const value of [lead.external_ref, lead.source, lead.need]) {
      const td = document.createElement("td"); td.textContent = value; tr.append(td);
    }
    const stage = document.createElement("td");
    const span = document.createElement("span"); span.className = "stage"; span.textContent = lead.status;
    stage.append(span); tr.append(stage);
    const action = document.createElement("td");
    const button = document.createElement("button");
    button.type = "button"; button.textContent = "Draft"; button.setAttribute("aria-label","Prepare unsent draft for " + lead.external_ref);
    button.addEventListener("click", () => selectLead(index));
    action.append(button); tr.append(action);
    tbody.append(tr);
  }
}

async function refresh() {
  $("connection").textContent = "Checking local synthetic API...";
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 2500);
  try {
    // Relative same-origin path only. No third-party endpoint, CORS or credential use.
    const response = await fetch("/api/demo/leads", {cache:"no-store",credentials:"omit",signal:controller.signal});
    if (!response.ok) throw new Error("Synthetic API unavailable");
    const payload = await response.json();
    if (payload.synthetic !== true || !Array.isArray(payload.leads) ||
        payload.leads.length > 2000 || payload.leads.some(row => safeLead(row) === null)) {
      throw new Error("Unsafe or incompatible synthetic lead response");
    }
    render(payload.leads, "Local API");
    await refreshScorecard();
    $("connection").textContent = "Connected to local synthetic API. No real customers or payments.";
  } catch (_error) {
    render(FIXTURES, "Offline fixtures");
    $("scorecardInfo").textContent = "Offline examples only. No payment sources connected.";
    $("connection").textContent = "Offline fixture mode. This is a demonstration only; no customer records or payments are connected.";
  } finally {clearTimeout(timeout);}
}

async function refreshScorecard() {
  try {
    const response = await fetch("/api/demo/scorecard", {cache:"no-store",credentials:"omit"});
    if (!response.ok) throw new Error("scorecard unavailable");
    const data = await response.json();
    const v = data && data.verified;
    if (data.synthetic !== true || !data.counts || !v ||
        !Number.isInteger(data.counts.received_demo_leads) ||
        v.payment_receipts !== 0 ||
        v.contractor_recovered_revenue_cents !== 0 ||
        v.rre_subscription_revenue_cents !== 0 ||
        v.rre_monthly_profit_cents !== 0) {
      throw new Error("unexpected or unverified scorecard");
    }
    $("scorecardInfo").textContent =
      "Synthetic process-memory inquiries: " + data.counts.received_demo_leads +
      ". Real customer count: unknown (no billing source connected). No confirmed bookings.";
  } catch (_error) {
    $("scorecardInfo").textContent = "Scorecard disconnected — fixture mode only. No real financial results.";
  }
}

async function loadScenario() {
  if (!selectedReference) {
    $("auditEvents").textContent = "Select a synthetic lead first. No customer data is connected.";
    return;
  }
  const choice = $("scenarioChoice").value;
  if (!["review", "appointment_mock", "closed_job_mock"].includes(choice)) {
    $("auditEvents").textContent = "Unsupported scenario.";
    return;
  }
  const ref = selectedReference;
  const selectionAtStart = selectionSequence;
  const requestAtStart = ++scenarioRequestSequence;
  $("auditEvents").textContent = "Loading read-only synthetic timeline...";
  try {
    const path = "/api/demo/scenarios/" + encodeURIComponent(ref) + "/" + choice;
    const response = await fetch(path, {cache:"no-store",credentials:"omit"});
    if (!response.ok) throw new Error("scenario unavailable");
    const data = await response.json();
    const result = data && data.scenario;
    const metrics = result && result.metrics;
    if (data.synthetic !== true || !result || result.synthetic !== true ||
        result.external_ref !== ref || result.scenario !== choice ||
        !Array.isArray(result.events) || !metrics ||
        metrics.actual_messages_sent !== 0 ||
        metrics.actual_bookings_confirmed !== 0 ||
        metrics.actual_jobs_closed !== 0 ||
        metrics.verified_recovered_revenue_cents !== 0 ||
        metrics.verified_rre_subscription_revenue_cents !== 0 ||
        metrics.verified_payment_receipts !== 0 ||
        result.events.some(e => e.synthetic !== true ||
          e.source_evidence_verified !== false || e.external_side_effect !== false)) {
      throw new Error("invalid unverified evidence payload");
    }
    if (selectedReference !== ref || selectionSequence !== selectionAtStart ||
        requestAtStart !== scenarioRequestSequence) return;
    const entries = result.events.map(e => e.sequence + ". " + e.event_type.replaceAll("_", " ")).join("\n");
    $("auditEvents").textContent = "SYNTHETIC / " + choice.toUpperCase() + "\n" +
      entries + "\n\nActual confirmed appointments: 0. Actual jobs: 0. " +
      "Verified recovered revenue: $0. No payment receipts. No messages sent.\n" +
      "This is a process demonstration, NOT proof of income or customer activity.";
  } catch (_error) {
    if (selectedReference === ref && selectionSequence === selectionAtStart &&
        requestAtStart === scenarioRequestSequence) {
      $("auditEvents").textContent = "Synthetic timeline unavailable. No action was taken.";
    }
  }
}

async function loadPolicy() {
  if (!selectedReference) {
    $("policyEvents").textContent = "Select a synthetic lead first.";
    return;
  }
  const choice = $("policyChoice").value;
  if (!["unknown", "revoked_mock", "consent_record_mock"].includes(choice)) {
    $("policyEvents").textContent = "Unsupported policy scenario.";
    return;
  }
  const ref = selectedReference;
  const selectionAtStart = selectionSequence;
  const requestAtStart = ++policyRequestSequence;
  $("policyEvents").textContent = "Checking read-only synthetic suppression...";
  try {
    const path = "/api/demo/policy/" + encodeURIComponent(ref) + "/" + choice;
    const response = await fetch(path, {cache:"no-store",credentials:"omit"});
    if (!response.ok) throw new Error("Policy unavailable");
    const result = await response.json();
    const policy = result && result.policy;
    if (result.synthetic !== true || !policy || policy.synthetic !== true ||
        policy.external_ref !== ref || policy.mode !== choice ||
        policy.consent_verified !== false || policy.operator_authorized !== false ||
        policy.may_contact_real_person !== false || policy.actual_message_sent !== false ||
        !Array.isArray(policy.reasons) ||
        (choice === "revoked_mock" && (policy.draft !== null || policy.suppressed !== true))) {
      throw new Error("Unsafe synthetic policy response");
    }
    if (selectedReference !== ref || selectionSequence !== selectionAtStart ||
        requestAtStart !== policyRequestSequence) return;
    $("policyEvents").textContent = "SYNTHETIC POLICY: " + choice + "\n" +
      "Real outreach: DISABLED\nActual sends: 0\nHuman identity: UNVERIFIED\n" +
      "Internal draft: " + (policy.draft === null ? "SUPPRESSED" : "UNSENT / REVIEW ONLY") +
      "\nReasons:\n" + policy.reasons.join("\n") +
      "\nNo customer consent or legal authorization is established.";
  } catch (_error) {
    if (selectedReference === ref && selectionSequence === selectionAtStart &&
        requestAtStart === policyRequestSequence) {
      $("policyEvents").textContent = "Policy preview unavailable. No action was taken.";
    }
  }
}

async function seedDemo() {
  // No contact data, no external API, no payment, and no persistent storage.
  if (!["127.0.0.1", "localhost"].includes(location.hostname)) {
    $("connection").textContent = "Synthetic seeding only works on the local loopback demo.";
    return;
  }
  $("seedDemo").disabled = true;
  try {
    for (const lead of FIXTURES) {
      const safe = {synthetic:true,external_ref:lead.external_ref,source:lead.source,need:lead.need};
      const response = await fetch("/api/demo/leads", {
        method:"POST", cache:"no-store", credentials:"omit",
        headers:{"Content-Type":"application/json"}, body:JSON.stringify(safe)
      });
      if (!response.ok) throw new Error("Synthetic seed rejected");
    }
    await refresh();
    $("connection").textContent = "Three explicitly synthetic examples loaded into local process memory only. No live integrations.";
  } catch (_error) {
    $("connection").textContent = "Local synthetic demo seeding unavailable. No customer data sent and no external actions.";
  } finally {
    $("seedDemo").disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  $("seedDemo").addEventListener("click", seedDemo);
  $("runScenario").addEventListener("click", loadScenario);
  $("runPolicy").addEventListener("click", loadPolicy);
  $("refresh").addEventListener("click", refresh);
  $("copyDraft").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText($("draft").value);
      $("copyStatus").textContent = "Copied locally; not sent.";
    } catch (_error) {
      $("copyStatus").textContent = "Clipboard unavailable; select and copy the text manually.";
    }
  });
  refresh();
});
