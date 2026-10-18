import json
import unittest
from pathlib import Path

import moneyfall.permit_friction as permit_friction


class PermitFrictionTests(unittest.TestCase):
    def profile(self, **overrides):
        data = {
            'agency_handoffs': 0.8,
            'sequential_dependencies': 0.9,
            'manual_or_offline_steps': 0.6,
            'inspection_dependencies': 0.8,
            'deadline_pressure': 0.7,
            'geographic_restrictions': 0.5,
            'fee_complexity': 0.6,
        }
        data.update(overrides)
        return data

    def test_complete_profile_scores_and_tiers(self):
        result = permit_friction.friction_score(self.profile())
        self.assertEqual(result['missing'], [])
        self.assertGreater(result['score'], 70)
        self.assertIn(result['tier'], {'high', 'severe'})

    def test_unknown_factor_blocks_ranking_instead_of_guessing(self):
        result = permit_friction.friction_score(self.profile(fee_complexity=None))
        self.assertEqual(result['score'], 0)
        self.assertEqual(result['tier'], 'unranked')
        self.assertEqual(result['missing'], ['fee_complexity'])

    def test_invalid_factor_rejected(self):
        for bad in (-0.01, 1.01, float('nan'), float('inf'), True, 'high'):
            with self.assertRaises(ValueError):
                permit_friction.friction_score(self.profile(agency_handoffs=bad))

    def test_offer_ladder_maps_friction_to_research_scope(self):
        self.assertEqual(permit_friction.offer_for_score(39)['action'], 'skip')
        self.assertEqual(permit_friction.offer_for_score(55)['price_cents'], 40000)
        self.assertEqual(permit_friction.offer_for_score(75)['price_cents'], 80000)
        self.assertEqual(permit_friction.offer_for_score(90)['price_cents'], 160000)

    def test_research_pack_requires_official_sources_and_preserves_uncertainty(self):
        municipality = {
            'name': 'Example City',
            'retrieved_at': '2026-10-18',
            'requirements': [
                {'label': 'Health permit', 'status': 'required', 'source_url': 'https://example.gov/health'},
                {'label': 'Fire inspection', 'status': 'may_require', 'source_url': 'https://example.gov/fire'},
                {'label': 'Zoning review', 'status': 'unknown', 'source_url': 'https://example.gov/zoning'},
            ],
        }
        pack = permit_friction.build_readiness_pack(municipality)
        self.assertEqual(pack['required'][0]['label'], 'Health permit')
        self.assertEqual(pack['may_require'][0]['label'], 'Fire inspection')
        self.assertEqual(pack['unknown'][0]['label'], 'Zoning review')
        self.assertIn('not legal advice', pack['disclaimer'].lower())
        bad = dict(municipality)
        bad['requirements'] = [{'label': 'Mystery permit', 'status': 'required', 'source_url': 'https://example.com/blog'}]
        with self.assertRaises(ValueError):
            permit_friction.build_readiness_pack(bad)

    def test_pilot_dataset_is_source_backed_and_contains_multiple_markets(self):
        path = Path('config/permit_friction_chicagoland.json')
        self.assertTrue(path.exists())
        data = json.loads(path.read_text())
        self.assertGreaterEqual(len(data['municipalities']), 6)
        ranked = []
        for market in data['municipalities']:
            self.assertTrue(market['source_urls'])
            self.assertTrue(all(url.startswith('https://') for url in market['source_urls']))
            result = permit_friction.friction_score(market['factors'])
            if not result['missing']:
                ranked.append(result['score'])
        self.assertGreaterEqual(len(ranked), 5)
        self.assertGreater(max(ranked), 70)


if __name__ == '__main__':
    unittest.main()
