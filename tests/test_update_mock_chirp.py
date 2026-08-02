import ast
import os
import tempfile
import unittest

from src.wwara_chirp.update_mock_chirp import UpdateMockChirp


class TestUpdateMockChirp(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)

        self.updater = UpdateMockChirp()
        self.updater.CHIRP_COMMON_FILENAME = "test_chirp_common.py"
        self.updater.MOCK_CHIRP_FILENAME = "test_mock_chirp.py"

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.temp_dir.cleanup()

    def test_parse_chirp_common(self):
        with open("test_chirp_common.py", "w", encoding="utf-8") as file:
            file.write(
                "from chirp import errors\n"
                "TONES = (67.0, 69.3)\n"
                "DTCS_CODES = (23, 25)\n"
                "not_a_constant = 'ignored'\n"
            )

        expected = {
            "TONES": (67.0, 69.3),
            "DTCS_CODES": (23, 25),
        }

        result = self.updater.parse_chirp_common()

        self.assertEqual(result, expected)

    def test_parse_mock_chirp(self):
        with open("test_mock_chirp.py", "w", encoding="utf-8") as file:
            file.write(
                "class MockChirp:\n"
                "    TONES = (67.0, 69.3)\n"
                "    DTCS_CODES = (23, 25)\n"
                "    helper = 'ignored'\n"
            )

        expected = {
            "TONES": (67.0, 69.3),
            "DTCS_CODES": (23, 25),
        }

        result = self.updater.parse_mock_chirp()

        self.assertEqual(result, expected)

    def test_compare_constants(self):
        common_constants = {
            "TONES": (67.0, 69.3),
            "DTCS_CODES": (23, 25),
            "MODES": ("FM",),
        }
        mock_constants = {
            "TONES": (67.0,),
            "DTCS_CODES": (23, 25),
            "CHIRP_SOURCES": ["local-only"],
        }

        updated, result = self.updater.compare_constants(
            common_constants,
            mock_constants,
        )

        self.assertTrue(updated)
        self.assertEqual(result["TONES"], (67.0, 69.3))
        self.assertEqual(result["DTCS_CODES"], (23, 25))
        self.assertEqual(result["CHIRP_SOURCES"], ["local-only"])
        self.assertNotIn("MODES", result)

    def test_update_mock_chirp(self):
        with open("test_mock_chirp.py", "w", encoding="utf-8") as file:
            file.write(
                "class MockChirp:\n"
                "    TONES = (67.0,)\n"
                "    DTCS_CODES = (23,)\n"
                "\n"
                "class Other:\n"
                "    TONES = ('leave-alone',)\n"
            )

        mock_constants = {
            "TONES": (67.0, 69.3),
            "DTCS_CODES": (23, 25),
        }

        self.updater.update_mock_chirp(mock_constants)

        with open("test_mock_chirp.py", "r", encoding="utf-8") as file:
            result = file.read()

        self.assertIn("    TONES = (67.0, 69.3)\n", result)
        self.assertIn("    DTCS_CODES = (23, 25)\n", result)
        self.assertIn("    TONES = ('leave-alone',)\n", result)

        parsed = ast.parse(result)
        self.assertIsInstance(parsed, ast.Module)

    def test_commit_and_create_pr(self):
        pass


if __name__ == "__main__":
    unittest.main()
