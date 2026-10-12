"""Explicit scenario heuristics; these are not measured financial EV."""
import math

DIMENSIONS = ('budget', 'deficiency', 'value', 'reachability', 'demonstrability', 'speed')


def fraction(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError('Score dimensions must be finite numbers from 0 to 1')
    return value


def readiness(dimensions):
    missing = [k for k in DIMENSIONS if dimensions.get(k) is None]
    values = [fraction(dimensions[k]) for k in DIMENSIONS if k not in missing]
    return {'score': 0 if missing else 100 * math.prod(values), 'missing': missing}


def opportunity_score(scenario):
    values = [fraction(scenario[k]) for k in (
        'probability', 'margin', 'urgency', 'reachability', 'automation', 'scale', 'defensibility')]
    days = scenario['days']
    capital = scenario['upfront_cents']
    if isinstance(days, bool) or not isinstance(days, (int, float)) or not math.isfinite(days) or days <= 0:
        raise ValueError('Days must be positive and finite')
    if isinstance(capital, bool) or not isinstance(capital, int) or capital < 0:
        raise ValueError('Upfront capital must be nonnegative integer cents')
    # Zero upfront is a feasibility gate, not a zero denominator.
    return 0 if capital else 100 * math.prod(values) * min(1, 7 / days)


def promote(incumbent_score, challenger_score, *, paid_conversions):
    if isinstance(paid_conversions, bool) or not isinstance(paid_conversions, int) or paid_conversions < 0:
        raise ValueError('Paid conversions must be a nonnegative integer')
    for score in (incumbent_score,challenger_score):
        if isinstance(score,bool) or not isinstance(score,(int,float)) or not math.isfinite(score) or score < 0:
            raise ValueError('Opportunity scores must be finite and nonnegative')
    return paid_conversions >= 3 and challenger_score > incumbent_score * 1.15
