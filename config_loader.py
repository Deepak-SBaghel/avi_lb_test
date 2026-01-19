"""
Configuration loader module for parsing YAML configuration files.
Handles loading test configurations, API endpoints, and credentials.
"""

import yaml
import os
from typing import Dict, Any, List


class ConfigLoader:
    """Loads and parses YAML configuration files."""
    
    def __init__(self, config_file: str = "test_config.yaml"):
        """
        Initialize ConfigLoader with a configuration file.
        
        Args:
            config_file: Path to the YAML configuration file
        """
        self.config_file = config_file
        self.config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load YAML configuration file."""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        
        try:
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            print(f"[CONFIG_LOADER] Configuration loaded from {self.config_file}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration."""
        return self.config.get('api', {})
    
    def get_credentials(self) -> Dict[str, str]:
        """Get user credentials."""
        return self.config.get('credentials', {})
    
    def get_test_cases(self) -> List[Dict[str, Any]]:
        """Get list of test cases."""
        return self.config.get('test_cases', [])
    
    def get_target_virtual_service(self) -> str:
        """Get target virtual service name."""
        return self.config.get('target_virtual_service', 'backend-vs-t1r_1000-1')
    
    def get_timeout(self) -> int:
        """Get API timeout in seconds."""
        return self.config.get('api', {}).get('timeout', 30)
    
    def get_parallelism_method(self) -> str:
        """Get parallelism execution method (threading, multiprocessing, or asyncio)."""
        return self.config.get('parallelism', {}).get('method', 'threading')
    
    def get_max_workers(self) -> int:
        """Get maximum number of parallel workers."""
        return self.config.get('parallelism', {}).get('max_workers', 4)
