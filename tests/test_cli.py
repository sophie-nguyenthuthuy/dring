import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).parent.parent
JWT = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
    "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
)


def run_cli(*args, stdin=None):
    return subprocess.run(
        [sys.executable, "-m", "dring", *args],
        capture_output=True, text=True, input=stdin, cwd=ROOT,
    )


class TestCLI(unittest.TestCase):
    def test_json_output(self):
        r = run_cli("--json", JWT)
        self.assertEqual(r.returncode, 0, r.stderr)
        cands = json.loads(r.stdout)
        self.assertEqual(cands[0]["type"], "jwt")
        self.assertEqual(cands[0]["details"]["alg"], "HS256")

    def test_stdin(self):
        r = run_cli(stdin="*/5 * * * *")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("every 5", r.stdout)

    def test_no_match_exits_1(self):
        r = run_cli("zzz zzz")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no idea", r.stdout)

    def test_list(self):
        r = run_cli("--list")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertGreaterEqual(len(r.stdout.strip().splitlines()), 14)


if __name__ == "__main__":
    unittest.main()
