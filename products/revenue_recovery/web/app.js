"use strict";

// Local-only synthetic UI. Never send messages or persist contact information.
const FIXTURES = Object.freeze([
  {synthetic:true,external_ref:"DEMO-HVAC-001",source:"website",need:"AC not cooling",status:"received"},
  {synthetic:true,external_ref:"DEMO-HVAC-002",source:"phone",need:"estimate follow-up",status:"received"},
  {synthetic:true,external_ref:"DEMO-HVAC-003",source:"referral",need:"AC maintenance",status:"received"}
]);
const $ = id => document.getElementById(id);
let leads = [];
let selectionSequence = 0;

function safeLead(value) {
  if (!value || typeof value !== "object" || value.synthetic !== true) return null;
  for (const field of ["external_ref","source","need","status"]) {
    if (typeof value[field] !== "string" || value[field].length > 240) return null;
  }
  return {synthetic:true,external_ref:value.external_ref,source:value.source,need:value.need,status:value.status};
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
        typeof p.followup.message !== "string" ||
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
    if (payload.synthetic !== true || !Array.isArray(payload.leads)) throw new Error("Unexpected response");
    render(payload.leads, "Local API");
    $("connection").textContent = "Connected to local synthetic API. No real customers or payments.";
  } catch (_error) {
    render(FIXTURES, "Offline fixtures");
    $("connection").textContent = "Offline fixture mode. This is a demonstration only; no customer records or payments are connected.";
  } finally {clearTimeout(timeout);}
}

document.addEventListener("DOMContentLoaded", () => {
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
