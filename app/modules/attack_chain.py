import logging
from .vulnerability_scanner import VulnerabilityScanner
from .sqli_simulator import SQLiSimulator
from .xss_simulator import XSSSimulator
from .ssh_bruteforce import SSHBruteForceSimulator
from .ftp_bruteforce import FTPBruteForceSimulator
from .stealth import StealthScanner
from .payload_manager import PayloadManager
from typing import List, Dict, Tuple
from app import socketio
import time
import re

class ChainedAttackSimulator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.vuln_scanner = VulnerabilityScanner()
        self.sqli_simulator = SQLiSimulator()
        self.xss_simulator = XSSSimulator()
        self.ssh_simulator = SSHBruteForceSimulator()
        self.ftp_simulator = FTPBruteForceSimulator()
        self.stealth = StealthScanner()
        self.payload_manager = PayloadManager()
        self.chain_progress = 0
        self.services = {
            'web': [],    # HTTP/HTTPS ports
            'ssh': [],    # SSH ports
            'db': [],     # Database ports
            'ftp': [],    # FTP ports
            'other': []   # Other services
        }
        
    def emit_log(self, message: str, progress: int = None) -> None:
        """Emit log message and progress to connected clients"""
        try:
            socketio.emit('log_message', {'message': message})
            if progress is not None:
                self.chain_progress = progress
                socketio.emit('chain_progress', {'progress': progress})
        except Exception as e:
            self.logger.error(f"Error emitting log: {str(e)}")

    def _parse_services(self, scan_output: str) -> None:
        """Parse discovered services from scan output"""
        # Reset services
        for key in self.services:
            self.services[key] = []
            
        # Find all port/service combinations
        port_matches = re.finditer(r'(\d+)/tcp\s+open\s+(\w+)', scan_output)
        
        for match in port_matches:
            port = int(match.group(1))
            service = match.group(2).lower()
            
            if service in ['http', 'https']:
                self.services['web'].append(port)
            elif service == 'ssh':
                self.services['ssh'].append(port)
            elif service == 'ftp':
                self.services['ftp'].append(port)
            elif service in ['mysql', 'postgresql', 'mongodb']:
                self.services['db'].append(port)
            else:
                self.services['other'].append(port)

    def _test_web_services(self, target: str, stealth_mode: bool = True) -> List[str]:
        """Test discovered web services"""
        results = []
        
        if not self.services['web']:
            return ["No web services discovered to test"]
            
        for port in self.services['web']:
            web_target = f"{target}:{port}" if port not in [80, 443] else target
            
            # SQL Injection Testing
            self.emit_log(f"Testing SQL injection on {web_target}", 40)
            sqli_results = self.sqli_simulator.test_endpoint(web_target)
            results.extend([sqli_results, ""])
            
            if stealth_mode:
                self.stealth.apply_scan_delay()
            
            # XSS Testing
            self.emit_log(f"Testing XSS on {web_target}", 60)
            xss_results = self.xss_simulator.test_xss(web_target)
            results.extend([xss_results, ""])
            
            if stealth_mode:
                self.stealth.apply_scan_delay()
                
        return results

    def _test_ssh_services(self, target: str, stealth_mode: bool = True) -> List[str]:
        """Test discovered SSH services"""
        results = []
        
        if not self.services['ssh']:
            return ["No SSH services discovered to test"]
            
        usernames = ['admin', 'root', 'user']
        for port in self.services['ssh']:
            ssh_target = f"{target}:{port}" if port != 22 else target
            
            for username in usernames:
                self.emit_log(f"Testing SSH auth on {ssh_target} with username: {username}", 70)
                ssh_results = self.ssh_simulator.simulate_bruteforce(ssh_target, username)
                results.extend([ssh_results, ""])
                
                if stealth_mode:
                    self.stealth.apply_scan_delay()
                    
        return results

    def _test_ftp_services(self, target: str, stealth_mode: bool = True) -> List[str]:
        """Test discovered FTP services"""
        results = []
        
        if not self.services['ftp']:
            return ["No FTP services discovered to test"]
            
        for port in self.services['ftp']:
            ftp_target = target
            self.emit_log(f"Testing FTP auth on {ftp_target}:{port}", 80)
            ftp_results = self.ftp_simulator.simulate_bruteforce(ftp_target, port=port)
            results.extend([ftp_results, ""])
            
            if stealth_mode:
                self.stealth.apply_scan_delay()
                    
        return results

    def run_chain(self, target: str, stealth_mode: bool = True) -> str:
        """Run a complete chain of security tests"""
        self.emit_log("Initializing chained security test", 0)
        results = []
        
        try:
            # Phase 1: Initial Scan
            self.emit_log(f"\nPhase 1: Service Discovery on {target}", 10)
            results.extend([
                f"Chained Security Test on {target}",
                "=" * 50,
                "\nPhase 1: Service Discovery",
                "-" * 40
            ])
            
            if stealth_mode:
                self.stealth.set_scan_delay(1.0, 3.0)
                self.emit_log("Stealth mode enabled - Using random delays")
            
            # Run initial scan
            scan_results = self.vuln_scanner.scan_target(target)
            self._parse_services(scan_results)
            results.extend([scan_results, ""])
            
            # Phase 2: Web Testing
            self.emit_log("\nPhase 2: Web Vulnerability Testing", 30)
            results.extend([
                "\nPhase 2: Web Vulnerability Testing",
                "-" * 40
            ])
            web_results = self._test_web_services(target, stealth_mode)
            results.extend(web_results)
            
            # Phase 3: SSH Testing
            self.emit_log("\nPhase 3: SSH Security Testing", 50)
            results.extend([
                "\nPhase 3: SSH Security Testing",
                "-" * 40
            ])
            ssh_results = self._test_ssh_services(target, stealth_mode)
            results.extend(ssh_results)

            # Phase 4: FTP Testing
            self.emit_log("\nPhase 4: FTP Security Testing", 70)
            results.extend([
                "\nPhase 4: FTP Security Testing",
                "-" * 40
            ])
            ftp_results = self._test_ftp_services(target, stealth_mode)
            results.extend(ftp_results)
            
            # Phase 5: Service Summary
            self.emit_log("\nPhase 5: Security Analysis", 90)
            results.extend([
                "\nSecurity Analysis",
                "=" * 50,
                f"Web Services: {len(self.services['web'])} ports",
                f"SSH Services: {len(self.services['ssh'])} ports",
                f"FTP Services: {len(self.services['ftp'])} ports",
                f"Database Services: {len(self.services['db'])} ports",
                f"Other Services: {len(self.services['other'])} ports",
                "\nRecommendations:",
                "1. Minimize exposed services",
                "2. Implement strong access controls",
                "3. Keep all services updated",
                "4. Monitor for suspicious activity",
                "5. Use WAF for web services",
                "6. Enable fail2ban for SSH and FTP",
                "\nReminder: Only test authorized systems!"
            ])
            
            self.emit_log("Chained security test completed", 100)
            socketio.emit('scan_complete', {'message': 'Chained security test completed'})
            return "\n".join(results)
            
        except Exception as e:
            error_msg = f"Error in security test chain: {str(e)}"
            self.logger.error(error_msg)
            self.emit_log(error_msg)
            return error_msg

from flask import Blueprint, render_template, request
from app.modules.vulnerability_scanner import VulnerabilityScanner
from app.modules.sqli_simulator import SQLiSimulator
from app.modules.ssh_bruteforce import SSHBruteForceSimulator
from app.modules.ftp_bruteforce import FTPBruteForceSimulator
from app.modules.xss_simulator import XSSSimulator
from app.modules.attack_chain import ChainedAttackSimulator

main_bp = Blueprint('main', __name__)

@main_bp.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@main_bp.route("/scan", methods=["POST"])
def scan():
    scan_type = request.form.get("scan_type")
    target = request.form.get("target")
    ssh_user = request.form.get("ssh_user")
    ssh_pass = request.form.get("ssh_pass")
    custom_payload = request.form.get("custom_payload")
    
    results = "No results available."
    
    try:
        if scan_type == "vuln_scan":
            scanner = VulnerabilityScanner()
            results = scanner.scan_target(target)
        elif scan_type == "sqli":
            scanner = SQLiSimulator()
            results = scanner.test_endpoint(target)
        elif scan_type == "ssh_brute":
            if not ssh_user:  # Require username for SSH testing
                results = "Error: SSH username required"
            else:
                scanner = SSHBruteForceSimulator()
                custom_pass_list = [ssh_pass] if ssh_pass else None
                results = scanner.simulate_bruteforce(target, ssh_user, custom_pass_list)
        elif scan_type == "ftp_brute":
            scanner = FTPBruteForceSimulator()
            results = scanner.simulate_bruteforce(target)
        elif scan_type == "xss":
            scanner = XSSSimulator()
            results = scanner.test_xss(target)
        elif scan_type == "attack_chain":
            scanner = ChainedAttackSimulator()
            results = scanner.run_chain(target)
        elif scan_type == "community":
            if not custom_payload:
                results = "Error: Custom payload required"
            elif scan_type == "sqli":
                scanner = SQLiSimulator()
                results = scanner.test_endpoint(target, custom_payload)
            elif scan_type == "xss":
                scanner = XSSSimulator()
                # Add custom payload to XSS test
                scanner.payloads.append(custom_payload)
                results = scanner.test_xss(target)
                
    except Exception as e:
        results = f"Error during scan: {str(e)}"
    
    return render_template("results.html", scan_type=scan_type, target=target, results=results)