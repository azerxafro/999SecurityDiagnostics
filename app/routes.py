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
            ftp_user = request.form.get("ftp_user")
            ftp_pass = request.form.get("ftp_pass")
            ftp_port = request.form.get("ftp_port", "21")
            
            try:
                port = int(ftp_port)
            except ValueError:
                port = 21
                
            if ftp_user and ftp_pass:
                # Test specific credentials
                success, message = scanner.test_credentials(target, ftp_user, ftp_pass, port)
                results = f"FTP Security Test - {target}:{port}\n" + "=" * 50 + "\n" + message
            else:
                # Run default bruteforce simulation
                results = scanner.simulate_bruteforce(target, port=port)
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
