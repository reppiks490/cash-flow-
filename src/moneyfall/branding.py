"""Customer-facing proof branding with a backward-compatible legacy default."""

LEGACY_PROOF_BRAND = "MONEYFALL"
MAX_PROOF_BRAND_LENGTH = 64


def proof_brand(job):
    """Return a validated one-line proof brand for a render job.

    Historical jobs omit ``brand`` and therefore keep the original MONEYFALL
    output. New or rerendered jobs can explicitly select another customer-facing
    identity, such as ``Vellumflare Studio``.
    """
    raw = job.get("brand", LEGACY_PROOF_BRAND)
    if not isinstance(raw, str):
        raise ValueError("Proof brand must be text")
    brand = raw.strip()
    if not brand or len(brand) > MAX_PROOF_BRAND_LENGTH:
        raise ValueError("Invalid proof brand length")
    if any(char in brand for char in "\r\n\t"):
        raise ValueError("Proof brand must fit one line")
    return brand
