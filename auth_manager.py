"""
Authentication Manager for Fineract Login
"""
import requests
import base64
import os
from typing import Dict, Tuple
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AuthManager:
    """Handle Fineract authentication and credential management"""
    
    @staticmethod
    def authenticate(server_url: str, tenant_id: str, username: str, password: str) -> Tuple[bool, str, Dict]:
        """
        Authenticate with Fineract server
        
        Args:
            server_url: Base URL of Fineract server (e.g., https://20.40.56.140:8443)
            tenant_id: Tenant identifier
            username: User's username
            password: User's password
            
        Returns:
            Tuple of (success: bool, message: str, user_data: dict)
        """
        try:
            # Construct authentication endpoint
            auth_url = f"{server_url}/fineract-provider/api/v1/authentication"
            
            # Prepare request
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
                'Fineract-Platform-Tenantid': tenant_id
            }
            
            payload = {
                "username": username,
                "password": password
            }
            
            # Make authentication request
            response = requests.post(
                auth_url,
                json=payload,
                headers=headers,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return True, "Authentication successful", user_data
            else:
                error_msg = "Authentication failed"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('defaultUserMessage', error_msg)
                except:
                    pass
                return False, error_msg, {}
                
        except requests.exceptions.ConnectionError:
            return False, f"Cannot connect to server: {server_url}", {}
        except requests.exceptions.Timeout:
            return False, "Connection timeout - server not responding", {}
        except Exception as e:
            return False, f"Error: {str(e)}", {}
    
    @staticmethod
    def generate_auth_token(username: str, password: str) -> str:
        """
        Generate Basic authentication token
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Base64 encoded auth token with 'Basic ' prefix
        """
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    @staticmethod
    def save_credentials(server_url: str, tenant_id: str, username: str, password: str, env_path: str = ".env"):
        """
        Save credentials to .env file
        
        Args:
            server_url: Fineract server URL
            tenant_id: Tenant ID
            username: Username
            password: Password (will be encoded)
            env_path: Path to .env file
        """
        # Generate auth token
        auth_token = AuthManager.generate_auth_token(username, password)
        
        # Construct full base URL for API
        if not server_url.endswith('/api/v1'):
            base_url = f"{server_url}/fineract-provider/api/v1"
        else:
            base_url = server_url
        
        # Read existing .env or create new
        env_lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_lines = f.readlines()
        
        # Update or add credentials
        credentials_map = {
            'FINERACT_BASE_URL': base_url,
            'FINERACT_AUTH_TOKEN': auth_token,
            'FINERACT_TENANT_ID': tenant_id
        }
        
        # Track which keys were updated
        updated_keys = set()
        
        # Update existing lines
        for i, line in enumerate(env_lines):
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key = line.split('=')[0].strip()
                if key in credentials_map:
                    env_lines[i] = f"{key}={credentials_map[key]}\n"
                    updated_keys.add(key)
        
        # Add missing keys
        for key, value in credentials_map.items():
            if key not in updated_keys:
                env_lines.append(f"{key}={value}\n")
        
        # Write back to .env
        with open(env_path, 'w') as f:
            f.writelines(env_lines)
    
    @staticmethod
    def is_authenticated(env_path: str = ".env") -> bool:
        """
        Check if valid credentials exist
        
        Args:
            env_path: Path to .env file
            
        Returns:
            True if credentials exist, False otherwise
        """
        if not os.path.exists(env_path):
            return False
        
        required_keys = ['FINERACT_BASE_URL', 'FINERACT_AUTH_TOKEN', 'FINERACT_TENANT_ID']
        
        with open(env_path, 'r') as f:
            content = f.read()
            
        for key in required_keys:
            # Check if key exists and has a value
            if f"{key}=" not in content:
                return False
            
            # Extract the value after the equals sign
            for line in content.split('\n'):
                if line.strip().startswith(f"{key}="):
                    value = line.split('=', 1)[1].strip()
                    # Check if value is empty or placeholder
                    if not value or value.startswith('your') or value.startswith('https://your'):
                        return False
                    break
        
        return True
    
    @staticmethod
    def clear_credentials(env_path: str = ".env"):
        """
        Clear saved credentials (logout)
        
        Args:
            env_path: Path to .env file
        """
        if not os.path.exists(env_path):
            return
        
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Clear credential values
        for i, line in enumerate(lines):
            if line.strip().startswith('FINERACT_'):
                key = line.split('=')[0]
                lines[i] = f"{key}=\n"
        
        with open(env_path, 'w') as f:
            f.writelines(lines)
