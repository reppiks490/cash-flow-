import unittest

from moneyfall.permit_watch import catalog_urls, compare_snapshots, fingerprint_content, host_allowed


class PermitWatchTests(unittest.TestCase):
    def test_catalog_deduplicates_urls_across_market_files(self):
        datasets = [
            {"municipalities": [
                {"name": "A", "official_domains": ["city-a.gov"], "source_urls": ["https://city-a.gov/food", "https://city-a.gov/fire"]},
                {"name": "B", "official_domains": ["city-b.gov", "city-a.gov"], "source_urls": ["https://city-b.gov/vendors", "https://city-a.gov/food"]},
            ]}
        ]
        catalog = catalog_urls(datasets)
        self.assertEqual([entry["url"] for entry in catalog], [
            "https://city-a.gov/food",
            "https://city-a.gov/fire",
            "https://city-b.gov/vendors",
        ])
        self.assertEqual(catalog[0]["markets"], ["A", "B"])

    def test_catalog_excludes_declared_manual_only_sources_without_dropping_research_source(self):
        blocked = "https://city.gov/protected-food-page"
        dataset = {"municipalities": [{
            "name": "Protected City",
            "official_domains": ["city.gov"],
            "source_urls": ["https://city.gov/watchable", blocked],
            "watch_exclusions": [blocked],
        }]}
        catalog = catalog_urls([dataset])
        self.assertEqual([entry["url"] for entry in catalog], ["https://city.gov/watchable"])
        self.assertIn(blocked, dataset["municipalities"][0]["source_urls"])

    def test_watch_exclusion_must_reference_an_official_source_in_same_market(self):
        dataset = {"municipalities": [{
            "name": "Bad City",
            "official_domains": ["city.gov"],
            "source_urls": ["https://city.gov/watchable"],
            "watch_exclusions": ["https://evil.example/not-a-source"],
        }]}
        with self.assertRaises(ValueError):
            catalog_urls([dataset])

    def test_fingerprint_ignores_html_noise_but_not_visible_requirement_changes(self):
        a = b"<html><style>.x{}</style><script>nonce=123</script><body>Permit required   before event</body></html>"
        b = b"<html><script>nonce=999</script><body> Permit required before event </body></html>"
        c = b"<html><body>Permit required 10 days before event</body></html>"
        self.assertEqual(fingerprint_content(a, "text/html"), fingerprint_content(b, "text/html"))
        self.assertNotEqual(fingerprint_content(a, "text/html"), fingerprint_content(c, "text/html"))

    def test_non_html_content_hashes_bytes(self):
        self.assertEqual(fingerprint_content(b"abc", "application/pdf"), fingerprint_content(b"abc", "application/pdf"))
        self.assertNotEqual(fingerprint_content(b"abc", "application/pdf"), fingerprint_content(b"abd", "application/pdf"))

    def test_compare_snapshots_marks_baseline_unchanged_changed_and_errors(self):
        previous = {"https://a.gov/x": {"fingerprint": "aaa"}, "https://b.gov/y": {"fingerprint": "bbb"}}
        current = {
            "https://a.gov/x": {"fingerprint": "aaa", "status_code": 200},
            "https://b.gov/y": {"fingerprint": "ccc", "status_code": 200},
            "https://c.gov/z": {"fingerprint": "ddd", "status_code": 200},
            "https://d.gov/q": {"error": "timeout"},
        }
        result = compare_snapshots(previous, current)
        self.assertEqual(result["https://a.gov/x"]["state"], "unchanged")
        self.assertEqual(result["https://b.gov/y"]["state"], "changed")
        self.assertEqual(result["https://c.gov/z"]["state"], "baseline")
        self.assertEqual(result["https://d.gov/q"]["state"], "error")

    def test_access_block_is_manual_on_first_sighting_but_error_after_prior_fingerprint(self):
        url = "https://protected.gov/food"
        current = {url: {"manual_only": True, "status_code": 403, "markets": ["Protected"]}}
        self.assertEqual(compare_snapshots({}, current)[url]["state"], "manual")
        self.assertEqual(compare_snapshots({url: {"fingerprint": "known-good"}}, current)[url]["state"], "error")

    def test_host_allowlist_accepts_exact_or_subdomain_only(self):
        self.assertTrue(host_allowed("www.city.gov", ["city.gov"]))
        self.assertTrue(host_allowed("city.gov", ["city.gov"]))
        self.assertFalse(host_allowed("city.gov.evil.example", ["city.gov"]))
        self.assertFalse(host_allowed("evilcity.gov", ["city.gov"]))


if __name__ == "__main__":
    unittest.main()
