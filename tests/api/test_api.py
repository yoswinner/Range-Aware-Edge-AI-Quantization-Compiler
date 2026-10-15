"""Tests for the RANGE//LAB API endpoints and serialization."""

import unittest
from fastapi.testclient import TestClient

from src.api.server import BUILTIN_EXAMPLES, app


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "online")
        self.assertEqual(data["app"], "RANGE//LAB")

    def test_examples_endpoint(self):
        resp = self.client.get("/api/examples")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 8)
        # Check first example structure
        ex0 = data[0]
        self.assertIn("id", ex0)
        self.assertIn("name", ex0)
        self.assertIn("source", ex0)

    def test_compile_safe_arithmetic(self):
        payload = {
            "source": "int x = 10; int y = 20; int z = x + y; print z;",
            "widen_after": 3,
            "narrow": False,
        }
        resp = self.client.post("/api/compile", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertIn("tokens", data)
        self.assertIn("ast", data)
        self.assertIn("tac", data)
        self.assertIn("cfg", data)
        self.assertIn("ssa", data)
        self.assertIn("ranges", data)
        self.assertIn("quantization", data)
        self.assertIn("diagnostics", data)
        self.assertIn("summary", data)
        self.assertIn("simulation", data)

        # Verify summary counts
        summary = data["summary"]
        self.assertEqual(summary["total_ssa_values"], 3)
        self.assertEqual(summary["safe_count"], 3)
        self.assertEqual(summary["quantized_count"], 3)
        self.assertEqual(summary["simulation_equivalent"], True)

    def test_compile_overflow_rejection(self):
        payload = {
            "source": "int x = 100; int y = 30; int z = x + y; print z;",
            "widen_after": 3,
            "narrow": False,
        }
        resp = self.client.post("/api/compile", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        summary = data["summary"]
        self.assertEqual(summary["safe_count"], 2)
        self.assertEqual(summary["rejected_count"], 1)

    def test_compile_syntax_error(self):
        payload = {
            "source": "int x = 10 + ;",
            "widen_after": 3,
        }
        resp = self.client.post("/api/compile", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data["success"])
        self.assertIn("error", data)
        self.assertEqual(data["error"]["stage"], "Parser")
        self.assertIsNotNone(data["error"]["line"])

    def test_compile_semantic_error(self):
        payload = {
            "source": "int x = 10; int z = x + undeclared_var; print z;",
            "widen_after": 3,
        }
        resp = self.client.post("/api/compile", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data["success"])
        self.assertIn("error", data)
        self.assertEqual(data["error"]["stage"], "Semantic Analysis")

    def test_compile_empty_source(self):
        payload = {"source": "   "}
        resp = self.client.post("/api/compile", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data["success"])
        self.assertIn("error", data)

    def test_compile_all_builtin_examples(self):
        for ex in BUILTIN_EXAMPLES:
            with self.subTest(example_id=ex["id"]):
                payload = {
                    "source": ex["source"],
                    "widen_after": ex.get("widen_after", 3),
                    "narrow": ex.get("narrow", False),
                }
                resp = self.client.post("/api/compile", json=payload)
                self.assertEqual(resp.status_code, 200)
                data = resp.json()
                self.assertTrue(data["success"], f"Failed to compile {ex['id']}: {data.get('error')}")


if __name__ == "__main__":
    unittest.main()
