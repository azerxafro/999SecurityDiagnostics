import unittest
from app.modules.ftp_bruteforce import FTPBruteForceSimulator

class TestFTPBruteForce(unittest.TestCase):
    def setUp(self):
        self.ftp_simulator = FTPBruteForceSimulator()
        
    def test_test_credentials(self):
        # Test with invalid credentials (should return False)
        success, message = self.ftp_simulator.test_credentials(
            "example.com",
            "invalid_user",
            "invalid_pass"
        )
        self.assertFalse(success)
        self.assertIn("Failed", message)
        
    def test_simulate_bruteforce(self):
        # Test bruteforce simulation (should return results string)
        results = self.ftp_simulator.simulate_bruteforce("example.com")
        self.assertIsInstance(results, str)
        self.assertIn("FTP Security Test", results)
        
    def test_default_wordlist(self):
        # Test default wordlist exists
        self.assertTrue(len(self.ftp_simulator.default_wordlist) > 0)
        # Test wordlist entries are tuples of (username, password)
        self.assertTrue(all(isinstance(x, tuple) for x in self.ftp_simulator.default_wordlist))
        
if __name__ == '__main__':
    unittest.main()
