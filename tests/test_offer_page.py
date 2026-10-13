import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps" / "offer-page" / "index.html"


class _PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.scripts = []
        self.forms = []
        self.labels_for = []
        self.inputs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        element_id = attrs.get("id")
        if element_id:
            self.ids.append(element_id)
        if tag == "a":
            self.links.append(attrs)
        elif tag == "script":
            self.scripts.append(attrs)
        elif tag == "form":
            self.forms.append(attrs)
        elif tag == "label" and attrs.get("for"):
            self.labels_for.append(attrs["for"])
        elif tag in {"input", "textarea", "select"}:
            self.inputs.append(attrs)


class OfferPageContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")
        cls.parser = _PageParser()
        cls.parser.feed(cls.html)
        cls.ids = set(cls.parser.ids)

    def test_vellumflare_identity_scope_and_claim_boundaries(self):
        expected_copy = [
            "Vellumflare Studio",
            "$149",
            "15-second",
            "editable SVG",
            "one consolidated revision",
            "confirmed payment",
            "approved inputs",
        ]
        for phrase in expected_copy:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), self.html.lower())
        self.assertRegex(
            self.html.lower(),
            r"(does not|no)\s+(promise|guarantee).{0,80}(leads|sales|revenue|performance)",
        )
        self.assertIn("custom 3d", self.html.lower())
        self.assertIn("separate", self.html.lower())

    def test_immersive_controls_are_present_and_ids_are_unique(self):
        self.assertEqual(len(self.parser.ids), len(set(self.parser.ids)))
        expected_ids = {
            "atelier-canvas",
            "webgl-fallback",
            "stage-fallback",
            "dialog-fallback",
            "immersive-dialog",
            "immersive-canvas",
            "motion-toggle",
            "material-vellum",
            "material-flare",
            "material-hybrid",
            "fold-toggle",
            "light-toggle",
            "specimen-studio",
            "specimen-home",
            "specimen-wellness",
            "motion-play",
            "motion-progress",
            "brief-form",
            "brief-copy",
            "brief-download",
            "brief-email",
        }
        self.assertSetEqual(expected_ids - self.ids, set())

    def test_accessibility_and_motion_safety_contract(self):
        self.assertTrue(
            any(link.get("href") == "#main-content" for link in self.parser.links),
            "offer page must expose a skip link",
        )
        self.assertIn("prefers-reduced-motion", self.html)
        self.assertIn("aria-live", self.html)
        self.assertIn("focus-visible", self.html)
        self.assertIn("visibilitychange", self.html)
        self.assertRegex(self.html, r"IntersectionObserver")
        self.assertIn("webglcontextlost", self.html)
        self.assertIn("webglcontextrestored", self.html)
        self.assertIn("ArrowLeft", self.html)
        self.assertIn("ArrowRight", self.html)

        controls = {
            attrs.get("id")
            for attrs in self.parser.inputs
            if attrs.get("id")
        }
        for control_id in controls:
            if control_id.startswith("brief-") and control_id not in {
                "brief-copy",
                "brief-download",
                "brief-email",
            }:
                self.assertIn(control_id, self.parser.labels_for)

    def test_renderer_startup_waits_for_renderer_and_motion_state(self):
        initial_pause = self.html.index("setGlobalPause(globalPaused);")
        renderer_init = self.html.index("const heroRenderer")
        motion_state = self.html.index("let motionRaf")
        self.assertGreater(initial_pause, renderer_init)
        self.assertGreater(initial_pause, motion_state)
        self.assertIn("let heroVisible", self.html)
        self.assertIn("let stageVisible", self.html)
        self.assertRegex(
            self.html,
            r"heroRenderer\.setPaused\([^;]*!heroVisible",
        )
        self.assertRegex(
            self.html,
            r"stageRenderer\.setPaused\([^;]*!stageVisible",
        )

    def test_motion_study_is_bounded_to_fifteen_seconds(self):
        self.assertRegex(self.html, r"MOTION_DURATION\s*=\s*15(?:\.0+)?")
        self.assertIn("motion-progress", self.html)
        self.assertRegex(self.html.lower(), r"0\.0\s*/\s*15s|0\s*/\s*15s")
        self.assertIn("requestAnimationFrame", self.html)
        self.assertIn("cancelAnimationFrame", self.html)

    def test_brief_composer_is_local_only_and_has_safe_handoff_actions(self):
        form = next((item for item in self.parser.forms if item.get("id") == "brief-form"), None)
        self.assertIsNotNone(form)
        self.assertFalse(form.get("action"), "brief form must not post to a remote endpoint")
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("XMLHttpRequest", self.html)
        self.assertIn("new Blob", self.html)
        self.assertIn("navigator.clipboard", self.html)
        self.assertIn("encodeURIComponent", self.html)
        self.assertIn("mailto:", self.html)
        self.assertRegex(self.html.lower(), r"nothing is sent automatically|does not send automatically")
        self.assertNotRegex(self.html.lower(), r"payment\s+(is|has been)\s+(configured|connected)")

    def test_page_has_no_external_runtime_or_checkout_dependency(self):
        external_scripts = [script for script in self.parser.scripts if script.get("src")]
        self.assertEqual(external_scripts, [])
        self.assertNotRegex(self.html.lower(), r"stripe\.js|checkout\.stripe|paypal\.com/sdk")
        self.assertNotRegex(self.html.lower(), r"<iframe[^>]+src=[\"']https?://")
        self.assertNotRegex(self.html.lower(), r"https?://[^\"']+\.(glb|gltf|fbx|obj|hdr|ktx2)")


if __name__ == "__main__":
    unittest.main()
