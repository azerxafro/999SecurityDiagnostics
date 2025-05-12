import logging
import random
import time
from typing import Dict
from app import socketio

class StealthScanner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.delay_between_requests = 1.0  # Default delay in seconds
        
    def emit_log(self, message):
        """Emit log message to connected clients"""
        try:
            socketio.emit('log_message', {'message': message})
        except Exception as e:
            self.logger.error(f"Error emitting log: {str(e)}")
            
    def set_scan_delay(self, min_delay: float, max_delay: float):
        """Set random delay between requests"""
        self.emit_log(f"Setting scan delay range: {min_delay}-{max_delay}s")
        delay = random.uniform(min_delay, max_delay)
        self.delay_between_requests = delay
        self.emit_log(f"Current delay set to: {delay:.2f}s")
        
    def random_user_agent(self) -> str:
        """Generate random user agent for stealth"""
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0)"
        ]
        agent = random.choice(agents)
        self.emit_log(f"Using User-Agent: {agent}")
        return agent
        
    def get_request_headers(self) -> Dict[str, str]:
        """Get stealth request headers"""
        self.emit_log("Generating stealth request headers")
        headers = {
            'User-Agent': self.random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'close'
        }
        return headers
        
    def apply_scan_delay(self):
        """Apply delay between requests"""
        delay = self.delay_between_requests
        self.emit_log(f"Applying stealth delay: {delay:.2f}s")
        time.sleep(delay)
        
    def rotate_request_pattern(self):
        """Rotate request patterns for stealth"""
        self.emit_log("Rotating request pattern")
        # Randomly adjust delays
        self.set_scan_delay(0.5, 2.0)
        # Could add more stealth techniques here
        
    def get_scan_config(self) -> Dict:
        """Get current stealth configuration"""
        config = {
            'delay': self.delay_between_requests,
            'headers': self.get_request_headers()
        }
        self.emit_log("Retrieved current stealth configuration")
        return config