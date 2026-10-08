import json
import unittest
import server

class ApiTests(unittest.TestCase):
    def test_health(self):
        status, _, body = server.handle("GET", "/health", {})
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(body)["ok"])

    def test_unknown_route(self):
        self.assertEqual(server.handle("GET", "/missing", {})[0], 404)

    def test_encode_returns_real_svg_qr(self):
        status, _, body = server.handle("POST", "/encode", {"text": "https://example.com"})
        self.assertEqual(status, 200)
        payload = json.loads(body)
        self.assertTrue(payload["svg"].startswith("<?xml"))
        self.assertIn("path", payload["svg"])

    def test_validation(self):
        status, _, body = server.handle("POST", "/encode", {})
        self.assertEqual(status, 400)

if __name__ == "__main__":
    unittest.main()
