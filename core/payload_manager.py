"""
Payload Manager for WebScanPro

This module manages and provides various payloads for security testing.
"""
import os
import json
from typing import Dict, List, Optional
from pathlib import Path

class PayloadManager:
    """Manages and provides payloads for security testing."""
    
    def __init__(self, payloads_dir: str = None):
        """
        Initialize the PayloadManager.
        
        Args:
            payloads_dir: Directory containing payload files
        """
        self.payloads_dir = payloads_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'utils', 
            'payloads'
        )
        self.payloads: Dict[str, List[str]] = {}
        self._load_payloads()
    
    def _load_payloads(self) -> None:
        """Load all payloads from the payloads directory."""
        try:
            payload_files = [
                f for f in os.listdir(self.payloads_dir) 
                if f.endswith('.txt') and os.path.isfile(os.path.join(self.payloads_dir, f))
            ]
            
            for payload_file in payload_files:
                payload_name = os.path.splitext(payload_file)[0]
                self.payloads[payload_name] = self._load_payload_file(payload_name)
                
        except Exception as e:
            print(f"Error loading payloads: {str(e)}")
            # Initialize with empty payloads if loading fails
            self.payloads = {
                'sql': [],
                'xss': [],
                'auth': []
            }
    
    def _load_payload_file(self, payload_name: str) -> List[str]:
        """
        Load payloads from a specific file.
        
        Args:
            payload_name: Name of the payload file (without extension)
            
        Returns:
            List of payloads
        """
        file_path = os.path.join(self.payloads_dir, f"{payload_name}.txt")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception as e:
            print(f"Error loading payload file {file_path}: {str(e)}")
            return []
    
    def get_payloads(self, payload_type: str) -> List[str]:
        """
        Get payloads of a specific type.
        
        Args:
            payload_type: Type of payloads to retrieve (e.g., 'sql', 'xss', 'auth')
            
        Returns:
            List of payloads
        """
        return self.payloads.get(payload_type.lower(), [])
    
    def add_payload(self, payload_type: str, payload: str) -> bool:
        """
        Add a new payload to the specified type.
        
        Args:
            payload_type: Type of payload
            payload: The payload to add
            
        Returns:
            True if successful, False otherwise
        """
        payload = payload.strip()
        if not payload:
            return False
            
        payload_type = payload_type.lower()
        if payload_type not in self.payloads:
            self.payloads[payload_type] = []
            
        if payload not in self.payloads[payload_type]:
            self.payloads[payload_type].append(payload)
            return self._save_payloads(payload_type)
            
        return True
    
    def _save_payloads(self, payload_type: str) -> bool:
        """
        Save payloads of a specific type to file.
        
        Args:
            payload_type: Type of payloads to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(self.payloads_dir, exist_ok=True)
            file_path = os.path.join(self.payloads_dir, f"{payload_type}.txt")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                for payload in self.payloads.get(payload_type, []):
                    f.write(f"{payload}\n")
            return True
        except Exception as e:
            print(f"Error saving payloads: {str(e)}")
            return False
    
    def get_all_payloads(self) -> Dict[str, List[str]]:
        """
        Get all payloads organized by type.
        
        Returns:
            Dictionary mapping payload types to lists of payloads
        """
        return self.payloads