"""Internal proof briefs, not fabricated completed audits or auto-send copy."""
import html


def brief(signal, hypothesis):
    clean = lambda value: html.escape(str(value)).replace('\n', ' ')
    return f'''# Revenue Opportunity Strike — {clean(signal['company'])}

Internal draft; hypothesis: {clean(hypothesis)}; signal: {clean(signal['id'])}.

## Observed selection reason

Public hiring for {clean(signal['title'])}.
Source: {clean(signal['url'])}
Hiring suggests a need; it does not establish buying intent or marketing spend.

## Unverified — complete before outreach

- Verify the company identity, role availability and relevance today.
- Cite a specific visible content/conversion deficiency and competitor evidence.
- Identify an appropriate public business contact; check suppression and consent.
- Build a custom proof using assets with commercial-use rights.
- Verify delivery capability and an active payment route.

## Offer experiment

$149 introductory fixed-fee experiment, subject to scope confirmation:
one evidence-backed opportunity brief, three hooks/CTA concepts, and one
production-ready content concept. No promised leads, revenue or performance.
48-hour delivery starts only after scope and client assets are accepted.
Potential recurring rail: content repurposing/competitor monitoring.

## Measurement

Link this signal to the offer, asset, outreach receipt, reply, payment receipt,
fulfillment and actual costs. Never count a draft or invoice as collected cash.
'''
