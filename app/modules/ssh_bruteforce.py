import paramiko
import socket
import logging
from typing import List, Tuple
from app import socketio
import time

class SSHBruteForceSimulator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Educational sample of weak passwords
        self.sample_passwords = [
            "password", "123456", "admin",
            "root", "qwerty", "letmein"
        ]
        
    def emit_log(self, message):
        """Emit log message to connected clients"""
        try:
            socketio.emit('log_message', {'message': message})
        except Exception as e:
            self.logger.error(f"Error emitting log: {str(e)}")
        
    def test_ssh_auth(self, hostname: str, username: str, password: str) -> Tuple[bool, str]:
        """Test a single SSH authentication attempt"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            self.emit_log(f"Attempting login with username: {username}")
            client.connect(
                hostname=hostname,
                username=username,
                password=password,
                timeout=3,
                banner_timeout=3,
                auth_timeout=3
            )
            return True, "Authentication successful"
        except paramiko.AuthenticationException:
            return False, "Authentication failed"
        except (socket.timeout, paramiko.SSHException) as e:
            return False, f"Connection error: {str(e)}"
        finally:
            client.close()
            
    def simulate_bruteforce(self, target: str, username: str, custom_passwords: List[str] = None) -> str:
        """Simulate SSH brute force attempts for educational purposes"""
        self.emit_log(f"Starting SSH security test on {target}")
        
        results = [
            f"SSH Security Test for {target}",
            "=" * 50,
            f"Testing username: {username}",
            "-" * 50,
            "\nEducational Notes:",
            "- Strong passwords should be long and complex",
            "- Use SSH keys instead of passwords when possible",
            "- Implement fail2ban or similar tools",
            "- Monitor auth.log for suspicious attempts\n"
        ]
        
        # Use either custom passwords or sample set
        passwords = custom_passwords if custom_passwords else self.sample_passwords
        
        try:
            for password in passwords[:5]:  # Limit attempts for demonstration
                self.emit_log(f"Testing password: {password}")
                success, message = self.test_ssh_auth(target, username, password)
                
                results.extend([
                    f"Testing password: {password}",
                    f"Result: {message}"
                ])
                
                if success:
                    msg = "\n! Warning: Weak password detected!"
                    self.emit_log(msg)
                    results.extend([
                        msg,
                        "Recommendation: Change password immediately"
                    ])
                    break
                
                # Add delay between attempts
                time.sleep(1)
                    
            self.emit_log("SSH testing completed")
            socketio.emit('scan_complete', {'message': 'SSH Security testing completed'})
            results.append("\nReminder: Only test on authorized systems!")
            return "\n".join(results)
            
        except Exception as e:
            self.logger.error(f"SSH testing error: {str(e)}")
            error_msg = f"Error during SSH testing: {str(e)}"
            self.emit_log(error_msg)
            return error_msg