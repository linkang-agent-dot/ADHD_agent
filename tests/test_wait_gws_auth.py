import importlib.util
import pathlib
import sys
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "wait_gws_auth.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("wait_gws_auth", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ClassifyProbeResultTests(unittest.TestCase):
    def test_success_is_ready(self):
        self.assertEqual(
            MODULE.classify_probe_result(0, '{"spreadsheetId":"sheet"}', "")[0],
            "ready",
        )

    def test_expired_token_keeps_waiting(self):
        result = MODULE.classify_probe_result(
            1,
            '{"error":{"code":401,"message":"invalid_grant"}}',
            "",
        )
        self.assertEqual(result[0], "waiting")

    def test_unexpected_failure_stops(self):
        result = MODULE.classify_probe_result(
            1,
            '{"error":{"code":403,"message":"forbidden"}}',
            "",
        )
        self.assertEqual(result[0], "error")


if __name__ == "__main__":
    unittest.main()
