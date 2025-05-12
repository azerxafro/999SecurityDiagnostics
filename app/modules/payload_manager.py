import logging
from typing import List, Dict
from app import socketio
import time

class PayloadManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.community_payloads = {
            'sqli': [],
            'xss': [],
            'ssh': [],
            'ftp': []
        }
        self.payload_categories = {
            'sqli': ['error-based', 'union-based', 'blind', 'time-based'],
            'xss': ['reflected', 'stored', 'dom-based'],
            'ssh': ['default-creds', 'wordlist', 'custom'],
            'ftp': ['anonymous', 'default-creds', 'wordlist']
        }
        
    def emit_log(self, message):
        """Emit log message to connected clients"""
        try:
            socketio.emit('log_message', {'message': message})
        except Exception as e:
            self.logger.error(f"Error emitting log: {str(e)}")

    def add_payload(self, payload_type: str, payload: str, category: str = None) -> bool:
        """Add a new community payload with category"""
        if payload_type not in self.community_payloads:
            self.emit_log(f"Invalid payload type: {payload_type}")
            return False
            
        if not self.validate_payload(payload_type, payload, category):
            return False
            
        payload_info = {
            'payload': payload,
            'category': category or 'default',
            'added_time': time.time()
        }
        
        self.community_payloads[payload_type].append(payload_info)
        self.emit_log(f"Added new {payload_type} payload in category {category}: {payload}")
        return True
        
    def get_payloads(self, payload_type: str, category: str = None) -> List[Dict]:
        """Get all payloads of a specific type and optional category"""
        if payload_type not in self.community_payloads:
            self.emit_log(f"Invalid payload type requested: {payload_type}")
            return []
            
        payloads = self.community_payloads[payload_type]
        
        if category:
            payloads = [p for p in payloads if p['category'] == category]
            
        self.emit_log(f"Retrieving {payload_type} payloads" + (f" for category {category}" if category else ""))
        return payloads
        
    def validate_payload(self, payload_type: str, payload: str, category: str = None) -> bool:
        """Validate a payload before using it"""
        self.emit_log(f"Validating {payload_type} payload")
        
        if not payload or not payload.strip():
            self.emit_log("Empty payload rejected")
            return False
            
        # Validate category if provided
        if category and category not in self.payload_categories.get(payload_type, []):
            self.emit_log(f"Invalid category '{category}' for {payload_type}")
            return False
            
        # Enhanced type-specific validation
        if payload_type == 'sqli':
            dangerous_patterns = {"DROP", "DELETE", "TRUNCATE", "--TABLES", "SELECT @@VERSION"}
            payload_upper = payload.upper()
            if any(pattern in payload_upper for pattern in dangerous_patterns):
                self.emit_log("Dangerous SQL payload detected and rejected")
                return False
                
            sql_patterns = ["'", "\"", "OR", "AND", "UNION", "SELECT"]
            if not any(pattern.lower() in payload.lower() for pattern in sql_patterns):
                self.emit_log("Invalid SQLi payload pattern")
                return False
                
        elif payload_type == 'xss':
            dangerous_patterns = ["<script>alert(document.cookie)", "document.location", "eval("]
            if any(pattern.lower() in payload.lower() for pattern in dangerous_patterns):
                self.emit_log("Dangerous XSS payload detected and rejected")
                return False
                
            xss_patterns = ["<script", "onerror", "onload", "javascript:", "<img", "<svg"]
            if not any(pattern.lower() in payload.lower() for pattern in xss_patterns):
                self.emit_log("Invalid XSS payload pattern")
                return False
                
        elif payload_type in ['ssh', 'ftp']:
            # Enhanced password complexity check
            if len(payload) < 8:
                self.emit_log(f"{payload_type.upper()} password too short")
                return False
            
            if not any(c.isupper() for c in payload) or not any(c.islower() for c in payload):
                self.emit_log(f"{payload_type.upper()} password needs both upper and lower case")
                return False
                
            if not any(c.isdigit() for c in payload):
                self.emit_log(f"{payload_type.upper()} password needs at least one number")
                return False
        
        self.emit_log(f"Payload validation successful for {payload_type}")
        return True