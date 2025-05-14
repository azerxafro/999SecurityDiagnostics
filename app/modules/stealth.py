import logging
import random
import time
from typing import Dict
from app import socketio

class StealthScanner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.delay_between_requests = 1.0  # Default delay in seconds
        self.proxy_list = []
        self.current_proxy = None
        self.max_retries = 3
        
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
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/122.0.6261.89 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.2365.92"
        ]
        agent = random.choice(agents)
        self.emit_log(f"Using User-Agent: {agent}")
        return agent
        
    def get_request_headers(self) -> Dict[str, str]:
        """Get stealth request headers with enhanced browser simulation"""
        self.emit_log("Generating stealth request headers")
        
        # Generate plausible browser headers
        headers = {
            'User-Agent': self.random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        # Add random ordered platforms for better stealth
        if random.random() < 0.3:  # 30% chance
            headers['Sec-CH-UA-Platform'] = random.choice(['"Windows"', '"macOS"', '"Linux"'])
            
        # Add random mobile indication
        if random.random() < 0.2:  # 20% chance
            headers['Sec-CH-UA-Mobile'] = '?1'
            
        return headers
        
    def apply_scan_delay(self):
        """Apply delay between requests"""
        delay = self.delay_between_requests
        self.emit_log(f"Applying stealth delay: {delay:.2f}s")
        time.sleep(delay)
        
    def rotate_request_pattern(self):
        """Rotate request patterns for stealth"""
        self.emit_log("Rotating request pattern")
        
        # Randomly adjust delays with more variation
        min_delay = random.uniform(0.5, 1.5)
        max_delay = random.uniform(2.0, 4.0)
        self.set_scan_delay(min_delay, max_delay)
        
        # Add IP rotation technique hint
        self.emit_log("Consider using a proxy for IP rotation")
        
        # Add request pattern variance
        if random.random() < 0.3:  # 30% chance to add extra delay
            extra_delay = random.uniform(1.0, 3.0)
            self.emit_log(f"Adding extra cooldown delay: {extra_delay:.2f}s")
            time.sleep(extra_delay)
        
    def get_scan_config(self) -> Dict:
        """Get current stealth configuration"""
        config = {
            'delay': self.delay_between_requests,
            'headers': self.get_request_headers(),
            'current_proxy': self.current_proxy,
            'proxy_count': len(self.proxy_list),
            'max_retries': self.max_retries,
            'pattern': self.get_request_pattern()
        }
        self.emit_log("Retrieved current stealth configuration")
        return config
        
    def validate_proxy(self, proxy: str) -> bool:
        """Validate proxy format and basic connectivity"""
        if not proxy:
            return False
            
        try:
            # Check proxy format
            parts = proxy.split("://")
            if len(parts) == 1:
                protocol = "http"
                host_port = parts[0]
            else:
                protocol = parts[0].lower()
                host_port = parts[1]
                
            if protocol not in ["http", "https", "socks4", "socks5"]:
                self.emit_log(f"Invalid proxy protocol: {protocol}")
                return False
                
            # Validate host:port format
            host, port = host_port.split(":")
            if not (1 <= int(port) <= 65535):
                self.emit_log(f"Invalid port number: {port}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Proxy validation error: {str(e)}")
            return False
            
    def add_proxy(self, proxy: str) -> bool:
        """Add a proxy to the rotation list"""
        if not self.validate_proxy(proxy):
            self.emit_log("Invalid proxy format")
            return False
            
        try:
            # Format proxy with protocol if needed
            if '://' not in proxy:
                proxy = f'http://{proxy}'
                
            # Don't add duplicates
            if proxy in self.proxy_list:
                self.emit_log(f"Proxy already in list: {proxy}")
                return False
                
            self.proxy_list.append(proxy)
            self.emit_log(f"Added proxy: {proxy}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding proxy: {str(e)}")
            return False
            
    def rotate_proxy(self) -> str:
        """Rotate to next proxy in the list with retry mechanism"""
        if not self.proxy_list:
            return None
            
        # Try different proxies up to max_retries times
        for _ in range(self.max_retries):
            self.current_proxy = random.choice(self.proxy_list)
            if self.validate_proxy(self.current_proxy):
                self.emit_log(f"Rotating to proxy: {self.current_proxy}")
                return self.current_proxy
                
            # Remove invalid proxy from list
            self.proxy_list.remove(self.current_proxy)
            self.emit_log(f"Removed invalid proxy: {self.current_proxy}")
            
        self.emit_log("No valid proxies available")
        return None
        
    def get_request_pattern(self) -> Dict[str, any]:
        """Generate randomized request pattern for stealth"""
        pattern = {
            'headers': self.get_request_headers(),
            'proxy': self.current_proxy,
            'delay': self.delay_between_requests,
            'retry_count': random.randint(1, self.max_retries),
            'timeout': random.uniform(5.0, 15.0)
        }
        
        # Random request options (30% chance each)
        if random.random() < 0.3:
            pattern['verify_ssl'] = False
        if random.random() < 0.3:
            pattern['allow_redirects'] = False
        if random.random() < 0.3:
            pattern['stream'] = True
            
        return pattern
        
    def set_stealth_level(self, level: str):
        """Configure stealth settings based on predefined levels"""
        levels = {
            'minimal': {
                'delay_range': (0.5, 1.5),
                'proxy_required': False,
                'max_retries': 2,
                'rotate_frequency': 0.1  # 10% chance to rotate per request
            },
            'moderate': {
                'delay_range': (1.0, 3.0),
                'proxy_required': True,
                'max_retries': 3,
                'rotate_frequency': 0.3  # 30% chance to rotate per request
            },
            'maximum': {
                'delay_range': (2.0, 5.0),
                'proxy_required': True,
                'max_retries': 5,
                'rotate_frequency': 0.5  # 50% chance to rotate per request
            }
        }
        
        if level not in levels:
            self.emit_log(f"Invalid stealth level: {level}. Using 'moderate'")
            level = 'moderate'
            
        config = levels[level]
        self.emit_log(f"Setting stealth level to: {level}")
        
        # Apply configuration
        self.set_scan_delay(*config['delay_range'])
        self.max_retries = config['max_retries']
        
        if config['proxy_required'] and not self.proxy_list:
            self.emit_log("Warning: Proxy required but none configured")
            
        return config
        
    def simulate_browser_fingerprint(self) -> Dict[str, str]:
        """Generate a consistent browser fingerprint for the session"""
        platforms = {
            'windows': {
                'os': 'Windows NT 10.0',
                'platform': 'Win64',
                'webkit': '537.36',
                'chrome': '122.0.0.0'
            },
            'macos': {
                'os': 'Macintosh; Intel Mac OS X 10_15_7',
                'webkit': '605.1.15',
                'safari': '17.2'
            },
            'linux': {
                'os': 'X11; Linux x86_64',
                'webkit': '537.36',
                'chrome': '122.0.0.0'
            }
        }
        
        # Choose platform and stick with it for consistency
        if not hasattr(self, '_platform'):
            self._platform = random.choice(list(platforms.keys()))
        
        platform_info = platforms[self._platform]
        
        fingerprint = {
            'user_agent': self._generate_consistent_ua(platform_info),
            'accept_language': 'en-US,en;q=0.9,es;q=0.8',
            'color_depth': str(random.choice([24, 32])),
            'resolution': random.choice(['1920x1080', '2560x1440', '1366x768']),
            'timezone': str(random.randint(-12, 12)),
            'session_storage': 'true',
            'indexedDB': 'true',
            'cpu_cores': str(random.randint(4, 16)),
            'touch_points': '0' if self._platform != 'mobile' else str(random.randint(1, 5))
        }
        
        return fingerprint