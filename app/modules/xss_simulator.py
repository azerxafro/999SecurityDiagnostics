import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict
from urllib.parse import urljoin

class XSSSimulator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "'\"><script>alert('XSS')</script>"
        ]
        
    def find_inputs(self, html_content: str) -> List[Dict]:
        """Find potential XSS injection points"""
        inputs = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check forms and their inputs
        for form in soup.find_all('form'):
            for input_field in form.find_all(['input', 'textarea']):
                inputs.append({
                    'type': 'form',
                    'method': form.get('method', 'get').lower(),
                    'action': form.get('action', ''),
                    'input_name': input_field.get('name', ''),
                    'input_type': input_field.get('type', 'text')
                })
                
        return inputs
        
    def test_xss(self, target_url: str) -> str:
        """Test for XSS vulnerabilities"""
        results = [
            f"Testing XSS Vulnerabilities on {target_url}",
            "=" * 50,
            "\nEducational Notes:",
            "- XSS allows attackers to inject malicious scripts",
            "- Always sanitize user input",
            "- Use Content Security Policy (CSP)",
            "- Encode special characters in output\n"
        ]
        
        if not target_url.startswith(('http://', 'https://')):
            target_url = f'http://{target_url}'
            
        try:
            # Get initial page
            response = requests.get(target_url, timeout=5)
            inputs = self.find_inputs(response.text)
            
            if not inputs:
                results.append("No input fields found to test")
                return "\n".join(results)
                
            results.append(f"Found {len(inputs)} potential injection points")
            
            for input_data in inputs:
                results.extend([
                    f"\nTesting {input_data['input_type']} input: {input_data['input_name']}",
                    "-" * 40
                ])
                
                for payload in self.payloads:
                    if input_data['method'] == 'get':
                        test_url = f"{target_url}?{input_data['input_name']}={payload}"
                        try:
                            test_response = requests.get(test_url, timeout=5)
                            if payload.lower() in test_response.text.lower():
                                results.append(f"! Potential XSS Found with: {payload}")
                                results.append("Payload was reflected in response")
                        except requests.exceptions.RequestException as e:
                            results.append(f"Error testing GET payload: {str(e)}")
                            
                    elif input_data['method'] == 'post':
                        try:
                            test_response = requests.post(
                                urljoin(target_url, input_data['action']),
                                data={input_data['input_name']: payload},
                                timeout=5
                            )
                            if payload.lower() in test_response.text.lower():
                                results.append(f"! Potential XSS Found with: {payload}")
                                results.append("Payload was reflected in response")
                        except requests.exceptions.RequestException as e:
                            results.append(f"Error testing POST payload: {str(e)}")
                            
            results.append("\nReminder: Only test on authorized systems!")
            return "\n".join(results)
            
        except Exception as e:
            self.logger.error(f"XSS testing error: {str(e)}")
            return f"Error during XSS testing: {str(e)}"