import sys
import unittest
from unittest.mock import patch
import src.large_test_data_generator as pkg
sys.modules.setdefault("large_test_data_generator", pkg)
from src.large_test_data_generator import cli

class TestCLI(unittest.TestCase):
    def test_verbose_enables_debug_logging(self):
        test_args = ["generate-test-data", "-v", "--parameters", "input/customer_master_parameters.json"]
        with patch.object(sys, "argv", test_args):
            with patch("src.large_test_data_generator.cli.generate_data"):
                with self.assertLogs(cli.logger, level="DEBUG") as cm:
                    cli.main()
        self.assertTrue(any("Verbose logging enabled" in m for m in cm.output))

if __name__ == "__main__":
    unittest.main()
