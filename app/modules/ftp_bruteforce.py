"""FTP Bruteforce Testing Module for 999SecurityDiagnostics

This module provides FTP security testing capabilities for authorized penetration testing.
Only use for authorized security audits with explicit permission.
"""

import ftplib
import logging
from typing import Tuple, List, Optional
from time import sleep
import random

class FTPBruteForceSimulator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Default wordlist with common username:password pairs
        self.default_wordlist = [
            ('admin', 'admin'),
            ('ftp', 'ftp'),
            ('anonymous', 'anonymous'),
            ('user', 'password'),
            ('test', 'test'),
            ('admin', 'password'),
            ('administrator', 'password123'),
            ('root', 'root')
        ]
    
    def test_credentials(self, target: str, username: str, password: str, port: int = 21) -> Tuple[bool, str]:
        """Test a single set of FTP credentials.
        
        Args:
            target: The target FTP server IP/hostname
            username: FTP username to test
            password: FTP password to test
            port: FTP port (default: 21)
            
        Returns:
            Tuple[bool, str]: (success status, result message)
        """
        try:
            ftp = ftplib.FTP()
            ftp.connect(target, port, timeout=5)
            ftp.login(username, password)
            
            # If login succeeds, properly close the connection
            ftp.quit()
            return True, f"[+] Successful login - {username}:{password}"
            
        except ftplib.error_perm as e:
            return False, f"[-] Failed login attempt - {username}:{password} - Permission denied"
        except Exception as e:
            return False, f"[-] Error testing {username}:{password} - {str(e)}"
    
    def simulate_bruteforce(self, target: str, port: int = 21, custom_wordlist: Optional[List[Tuple[str, str]]] = None,
                          delay: bool = True) -> str:
        """Simulate FTP bruteforce attempt for security testing.
        
        Args:
            target: The target FTP server IP/hostname
            port: FTP port (default: 21)
            custom_wordlist: Optional custom list of (username, password) tuples
            delay: Whether to add random delays between attempts (default: True)
            
        Returns:
            str: Test results summary
        """
        wordlist = custom_wordlist if custom_wordlist else self.default_wordlist
        results = []
        
        self.logger.info(f"Starting FTP security test on {target}:{port}")
        results.append(f"\nFTP Security Test - {target}:{port}")
        results.append("-" * 40)
        
        for username, password in wordlist:
            if delay:
                # Add random delay between attempts to avoid overwhelming the server
                sleep(random.uniform(0.5, 2.0))
            
            success, message = self.test_credentials(target, username, password, port)
            results.append(message)
            
            # If successful login found, stop testing
            if success:
                self.logger.warning(f"Weak FTP credentials found: {username}:{password}")
                results.append("\n[!] WARNING: Weak FTP credentials identified!")
                results.append("[!] Recommendation: Change default/weak passwords")
                break
        
        if not any(msg.startswith("[+]") for msg in results):
            results.append("\n[✓] No weak FTP credentials found")
            
        return "\n".join(results)
