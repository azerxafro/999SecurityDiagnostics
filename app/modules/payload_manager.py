import logging
from typing import List, Dict
from app import socketio

class PayloadManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.community_payloads = {
            'sqli': [],
            'xss': [],
            'ssh': [],
            'ftp': []
        }
        
    def emit_log(self, message):
        """Emit log message to connected clients"""
        try:
            socketio.emit('log_message', {'message': message})
        except Exception as e:
            self.logger.error(f"Error emitting log: {str(e)}")

    def add_payload(self, payload_type: str, payload: str) -> bool:
        """Add a new community payload"""
        if payload_type not in self.community_payloads:
            self.emit_log(f"Invalid payload type: {payload_type}")
            return False
            
        if payload in self.community_payloads[payload_type]:
            self.emit_log(f"Payload already exists in {payload_type} category")
            return False
            
        self.community_payloads[payload_type].append(payload)
        self.emit_log(f"Added new {payload_type} payload: {payload}")
        return True
        
    def get_payloads(self, payload_type: str) -> List[str]:
        """Get all payloads of a specific type"""
        if payload_type not in self.community_payloads:
            self.emit_log(f"Invalid payload type requested: {payload_type}")
            return []
            
        self.emit_log(f"Retrieving {payload_type} payloads")
        return self.community_payloads[payload_type]
        
    def validate_payload(self, payload_type: str, payload: str) -> bool:
        """Validate a payload before using it"""
        self.emit_log(f"Validating {payload_type} payload")
        
        # Basic validation rules
        if not payload or len(payload.strip()) == 0:
            self.emit_log("Empty payload rejected")
            return False
            
        # Type-specific validation
        if payload_type == 'sqli':
            # Check for basic SQL injection patterns
            sql_patterns = ["'", "\"", "OR", "AND", "UNION", "SELECT"]
            if not any(pattern.lower() in payload.lower() for pattern in sql_patterns):
                self.emit_log("Invalid SQLi payload pattern")
                return False
        elif payload_type == 'xss':
            # Check for basic XSS patterns
            xss_patterns = ["<script", "onerror", "onload", "javascript:", "<img"]
            if not any(pattern.lower() in payload.lower() for pattern in xss_patterns):
                self.emit_log("Invalid XSS payload pattern")
                return False
        elif payload_type in ['ssh', 'ftp']:
            # Check password complexity for SSH and FTP
            if len(payload) < 8:
                self.emit_log(f"{payload_type.upper()} password too short")
                return False
                
        self.emit_log(f"Payload validation successful for {payload_type}")
        return True