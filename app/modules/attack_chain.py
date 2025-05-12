import logging
from .vulnerability_scanner import VulnerabilityScanner
from .sqli_simulator import SQLiSimulator
from .xss_simulator import XSSSimulator
from typing import List, Dict

class ChainedAttackSimulator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.vuln_scanner = VulnerabilityScanner()
        self.sqli_simulator = SQLiSimulator()
        self.xss_simulator = XSSSimulator()
        
    def run_chain(self, target: str) -> str:
        """Run a chain of security tests"""
        results = [
            f"Running Chained Security Test on {target}",
            "=" * 50,
            "\nPhase 1: Port & Service Discovery",
            "-" * 40
        ]
        
        try:
            # Phase 1: Port Scanning
            scan_results = self.vuln_scanner.scan_target(target)
            results.extend([scan_results, "\n"])
            
            # Only continue if we found web ports
            if "80/tcp" in scan_results or "443/tcp" in scan_results:
                # Phase 2: SQLi Testing
                results.extend([
                    "Phase 2: SQL Injection Testing",
                    "-" * 40
                ])
                sqli_results = self.sqli_simulator.test_endpoint(target)
                results.extend([sqli_results, "\n"])
                
                # Phase 3: XSS Testing
                results.extend([
                    "Phase 3: Cross-Site Scripting Testing",
                    "-" * 40
                ])
                xss_results = self.xss_simulator.test_xss(target)
                results.extend([xss_results, "\n"])
            
            # Educational summary
            results.extend([
                "\nEducational Summary:",
                "=" * 50,
                "1. Port scanning helps identify attack surface",
                "2. Web applications often have multiple vulnerabilities",
                "3. Chained attacks combine multiple techniques",
                "4. Always implement defense in depth",
                "\nReminder: Only test on authorized systems!"
            ])
            
            return "\n".join(results)
            
        except Exception as e:
            self.logger.error(f"Chained attack error: {str(e)}")
            return f"Error during chained attack simulation: {str(e)}"