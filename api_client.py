"""
API Client module for interacting with the mock Avi Load Balancer API.
Handles authentication, API calls, and response parsing.
"""

import requests
import json
from typing import Dict, Any, Optional, List
from requests.auth import HTTPBasicAuth


class APIClient:
    """Client for interacting with the mock Avi Load Balancer API."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize API Client.
        
        Args:
            base_url: Base URL of the API (e.g., https://semantic-brandea-banao-dc049ed0.koyeb.app/)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.token = None
        self.session = requests.Session()
    
    def register(self, username: str, password: str) -> bool:
        """
        Register a new user on the mock API.
        
        Args:
            username: Username for registration
            password: Password for registration
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            url = f"{self.base_url}/register"
            payload = {
                "username": username,
                "password": password
            }
            response = self.session.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                print(f"[API_CLIENT] User '{username}' registered successfully")
                return True
            elif response.status_code == 409:
                print(f"[API_CLIENT] User '{username}' already exists")
                return True  # Consider existing user as acceptable
            else:
                print(f"[API_CLIENT] Registration failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"[API_CLIENT] Registration error: {e}")
            return False
    
    def login(self, username: str, password: str) -> bool:
        """
        Login to the mock API and obtain a session token.
        
        Args:
            username: Username for login
            password: Password for login
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            url = f"{self.base_url}/login"
            auth = HTTPBasicAuth(username, password)
            response = self.session.post(url, auth=auth, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                print(f"[API_CLIENT] Login successful. Token: {self.token[:20]}...")
                return True
            else:
                print(f"[API_CLIENT] Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"[API_CLIENT] Login error: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers with bearer token."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def get_tenants(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch all tenants from the API.
        
        Returns:
            List of tenants or None if request fails
        """
        try:
            url = f"{self.base_url}/api/tenant"
            response = self.session.get(url, headers=self._get_headers(), timeout=self.timeout)
            
            if response.status_code == 200:
                tenants = response.json()
                print(f"[API_CLIENT] Fetched {len(tenants) if isinstance(tenants, list) else 1} tenant(s)")
                return tenants if isinstance(tenants, list) else [tenants]
            else:
                print(f"[API_CLIENT] Failed to fetch tenants: {response.status_code}")
                return None
        except Exception as e:
            print(f"[API_CLIENT] Error fetching tenants: {e}")
            return None
    
    def get_virtual_services(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch all virtual services from the API.
        
        Returns:
            List of virtual services or None if request fails
        """
        try:
            url = f"{self.base_url}/api/virtualservice"
            response = self.session.get(url, headers=self._get_headers(), timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                # Handle paginated response
                if isinstance(data, dict) and 'results' in data:
                    services = data.get('results', [])
                else:
                    services = data if isinstance(data, list) else [data]
                print(f"[API_CLIENT] Fetched {len(services)} virtual service(s)")
                return services
            else:
                print(f"[API_CLIENT] Failed to fetch virtual services: {response.status_code}")
                return None
        except Exception as e:
            print(f"[API_CLIENT] Error fetching virtual services: {e}")
            return None
    
    def get_service_engines(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch all service engines from the API.
        
        Returns:
            List of service engines or None if request fails
        """
        try:
            url = f"{self.base_url}/api/serviceengine"
            response = self.session.get(url, headers=self._get_headers(), timeout=self.timeout)
            
            if response.status_code == 200:
                engines = response.json()
                engines_list = engines if isinstance(engines, list) else [engines]
                print(f"[API_CLIENT] Fetched {len(engines_list)} service engine(s)")
                return engines_list
            else:
                print(f"[API_CLIENT] Failed to fetch service engines: {response.status_code}")
                return None
        except Exception as e:
            print(f"[API_CLIENT] Error fetching service engines: {e}")
            return None
    
    def get_virtual_service_by_uuid(self, uuid: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a virtual service by UUID.
        
        Args:
            uuid: UUID of the virtual service
            
        Returns:
            Virtual service data or None if not found
        """
        try:
            url = f"{self.base_url}/api/virtualservice/{uuid}"
            response = self.session.get(url, headers=self._get_headers(), timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[API_CLIENT] Failed to fetch virtual service {uuid}: {response.status_code}")
                return None
        except Exception as e:
            print(f"[API_CLIENT] Error fetching virtual service {uuid}: {e}")
            return None
    
    def get_virtual_service_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a virtual service by name (searches in list).
        
        Args:
            name: Name of the virtual service
            
        Returns:
            Virtual service data or None if not found
        """
        try:
            services = self.get_virtual_services()
            if services:
                for service in services:
                    if service.get('name') == name:
                        print(f"[API_CLIENT] Found virtual service '{name}'")
                        return service
            print(f"[API_CLIENT] Virtual service '{name}' not found")
            return None
        except Exception as e:
            print(f"[API_CLIENT] Error searching for virtual service '{name}': {e}")
            return None
    
    def update_virtual_service(self, uuid: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a virtual service using PUT request.
        
        Args:
            uuid: UUID of the virtual service
            payload: Update payload (e.g., {"enabled": false})
            
        Returns:
            Updated virtual service data or None if request fails
        """
        try:
            url = f"{self.base_url}/api/virtualservice/{uuid}"
            response = self.session.put(url, json=payload, headers=self._get_headers(), timeout=self.timeout)
            
            if response.status_code == 200:
                print(f"[API_CLIENT] Virtual service {uuid} updated successfully")
                return response.json()
            else:
                print(f"[API_CLIENT] Failed to update virtual service {uuid}: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"[API_CLIENT] Error updating virtual service {uuid}: {e}")
            return None
