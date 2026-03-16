"""
Payload Manager Module for WebScanPro
Can load custom payloads from API or local files
"""
import os
import requests
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PayloadManager:
    """Manages SQL injection payloads from various sources"""
    
    def __init__(self):
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_payloads = [
            "'",  # Basic error-based
            "' OR '1'='1",  # Classic injection
            "1' UNION SELECT null--",  # Union-based
        ]
    
    def get_payloads_from_api(self, target_type: str = "sqli") -> List[str]:
        """
        Get payloads from OpenRouter API
        """
        if not self.openrouter_api_key:
            print("[!] No OpenRouter API key found, using base payloads")
            return self.base_payloads
            
        try:
            print(f"[API] Fetching {target_type} payloads from OpenRouter...")
            
            # Simple prompt to generate payloads
            prompt = f"""Generate 5 effective {target_type} payloads for testing web applications. 
            Return only the payloads, one per line, no explanations."""
            
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse payloads from response
                payloads = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        payloads.append(line)
                
                print(f"[API] Generated {len(payloads)} payloads from OpenRouter")
                return payloads[:10]  # Limit to 10 for performance
            else:
                print(f"[!] API request failed: {response.status_code}")
                return self.base_payloads
                
        except Exception as e:
            print(f"[!] Error fetching payloads from API: {str(e)}")
            return self.base_payloads
    
    def get_all_payloads(self, use_api: bool = True) -> List[str]:
        """
        Get all payloads (base + API-generated)
        """
        if use_api:
            api_payloads = self.get_payloads_from_api()
            # Combine base and API payloads, remove duplicates
            all_payloads = list(set(self.base_payloads + api_payloads))
            print(f"[Payloads] Total payloads: {len(all_payloads)}")
            return all_payloads
        else:
            print(f"[Payloads] Using base payloads: {len(self.base_payloads)}")
            return self.base_payloads
