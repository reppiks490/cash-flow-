"""Synthetic tenant-scope invariants; this does NOT test real identity or DB RLS."""
import concurrent.futures
import unittest

from backend.tenant_scope import (
    DemoPrincipal, TenantScopeDenied, TenantScopedDemoStore, require_demo_permission,
)


def actor(tenant="DEMO-TENANT-ALPHA", role="operator", name="DEMO-ACTOR-ONE"):
    return DemoPrincipal(tenant_id=tenant, subject_id=name, role=role)


def lead(ref="DEMO-TENANT-SHARED", need="repair"):
    return {"synthetic": True, "external_ref": ref, "source": "website", "need": need}


class TenantScopeTests(unittest.TestCase):
    def setUp(self):
        self.store = TenantScopedDemoStore()
        self.a = actor()
        self.b = actor("DEMO-TENANT-BRAVO")

    def test_tenant_queues_are_isolated_even_when_references_overlap(self):
        self.store.ingest(self.a, self.a.tenant_id, lead(need="repair"))
        self.store.ingest(self.b, self.b.tenant_id, lead(need="maintenance"))
        self.assertEqual(self.store.read(self.a, self.a.tenant_id, "DEMO-TENANT-SHARED")["need"], "repair")
        self.assertEqual(self.store.read(self.b, self.b.tenant_id, "DEMO-TENANT-SHARED")["need"], "maintenance")
        self.assertEqual(len(self.store.list(self.a, self.a.tenant_id)), 1)
        self.assertEqual(len(self.store.list(self.b, self.b.tenant_id)), 1)

    def test_cross_tenant_get_list_ingest_and_review_fail_closed(self):
        self.store.ingest(self.a, self.a.tenant_id, lead())
        for do in (
            lambda: self.store.read(self.b, self.a.tenant_id, "DEMO-TENANT-SHARED"),
            lambda: self.store.list(self.b, self.a.tenant_id),
            lambda: self.store.ingest(self.b, self.a.tenant_id, lead("DEMO-UNAUTH")),
            lambda: self.store.prepare_review(self.b, self.a.tenant_id, "DEMO-TENANT-SHARED"),
        ):
            with self.subTest(do=do), self.assertRaises(TenantScopeDenied):
                do()
        self.assertEqual(len(self.store.list(self.a, self.a.tenant_id)), 1)

    def test_viewer_cannot_write_or_review(self):
        viewer = actor(role="viewer")
        self.store.ingest(self.a, self.a.tenant_id, lead())
        self.assertEqual(len(self.store.list(viewer, viewer.tenant_id)), 1)
        for operation in (
            lambda: self.store.ingest(viewer, viewer.tenant_id, lead("DEMO-NEW")),
            lambda: self.store.prepare_review(viewer, viewer.tenant_id, "DEMO-TENANT-SHARED"),
        ):
            with self.assertRaises(TenantScopeDenied):
                operation()

    def test_reviewer_can_preview_without_booking_or_sending(self):
        reviewer = actor(role="reviewer")
        self.store.ingest(self.a, self.a.tenant_id, lead())
        result = self.store.prepare_review(reviewer, reviewer.tenant_id, "DEMO-TENANT-SHARED")
        self.assertTrue(result["synthetic"])
        self.assertTrue(result["review_required"])
        self.assertFalse(result["identity_verified"])
        self.assertFalse(result["recipient_consent_verified"])
        self.assertFalse(result["transmitted"])
        self.assertFalse(result["actual_appointment_confirmed"])
        self.assertFalse(result["actual_payment_verified"])
        with self.assertRaises(TenantScopeDenied):
            self.store.ingest(reviewer, reviewer.tenant_id, lead("DEMO-NEW"))

    def test_real_world_capabilities_are_never_authorized_even_for_operator(self):
        for action in ("send", "sms", "email", "call", "book", "charge",
                       "refund", "verify_real_payment", "ingest_real_customer",
                       "change_membership", "admin", "unknown", "", True):
            with self.subTest(action=action), self.assertRaises(TenantScopeDenied):
                require_demo_permission(self.a, self.a.tenant_id, action)

    def test_rejects_forged_or_untrusted_fixture_identity(self):
        for patch in (
            {"tenant_id": "TENANT-ALPHA"},
            {"tenant_id": "DEMO-TENANT-foo@example.org"},
            {"subject_id": "someone@example.org"},
            {"subject_id": "DEMO-ACTOR-OTHER@example.org"},
            {"role": "owner"},
            {"role": "admin"},
            {"role": True},
            {"synthetic": False},
            {"synthetic": 1},
        ):
            params = {"tenant_id": "DEMO-TENANT-ALPHA",
                      "subject_id": "DEMO-ACTOR-ONE", "role": "viewer", "synthetic": True}
            params.update(patch)
            with self.subTest(patch=patch), self.assertRaises(TenantScopeDenied):
                DemoPrincipal(**params)
        with self.assertRaises(TenantScopeDenied):
            require_demo_permission({"tenant_id": "DEMO-TENANT-ALPHA"}, self.a.tenant_id, "read")

    def test_invalid_lead_cannot_be_reclassified_as_real_record(self):
        for changes in ({"email": "someone@example.invalid"}, {"synthetic": False},
                        {"external_ref": "5551234567"}, {"need": "call my phone"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.store.ingest(self.a, self.a.tenant_id, {**lead(), **changes})
        self.assertEqual(self.store.list(self.a, self.a.tenant_id), [])

    def test_defensive_copies_prevent_return_value_mutation(self):
        original, first = self.store.ingest(self.a, self.a.tenant_id, lead())
        self.assertTrue(first)
        original["need"] = "heating issue"
        fetched = self.store.read(self.a, self.a.tenant_id, "DEMO-TENANT-SHARED")
        fetched["need"] = "maintenance"
        self.assertEqual(self.store.read(self.a, self.a.tenant_id, "DEMO-TENANT-SHARED")["need"], "repair")

    def test_same_tenant_parallel_idempotent_intake(self):
        payload = lead("DEMO-CONCURRENT-001")
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
            results = list(executor.map(
                lambda _: self.store.ingest(self.a, self.a.tenant_id, payload),
                range(25),
            ))
        self.assertEqual(sum(created for _, created in results), 1)
        self.assertEqual(len(self.store.list(self.a, self.a.tenant_id)), 1)

    def test_unauthenticated_http_demo_api_has_no_tenant_routes(self):
        # Security fixture never added to backend.app route table.
        from backend.app import DemoStore, make_handler
        import http.client
        import threading
        from http.server import ThreadingHTTPServer
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(DemoStore()))
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            for path in ("/api/tenants", "/api/tenant/DEMO-TENANT-ALPHA",
                         "/api/auth", "/api/workspaces", "/api/users"):
                client = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                try:
                    client.request("GET", path)
                    reply = client.getresponse()
                    reply.read()
                    self.assertEqual(reply.status, 404)
                finally:
                    client.close()
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
