"""
Mock module for SSH and RDP components.
Provides stubbed methods for SSH and RDP operations.
"""


class MockSSH:
    """Mock SSH component for testing."""
    
    @staticmethod
    def connect(host: str, port: int = 22, username: str = None, password: str = None) -> bool:
        """
        Mock SSH connection.
        
        Args:
            host: Host to connect to
            port: SSH port (default 22)
            username: Username for authentication
            password: Password for authentication
            
        Returns:
            True (mock success)
        """
        print(f"[MOCK_SSH] Connecting to host {host}:{port} with username '{username}'")
        print(f"[MOCK_SSH] Mock connection established")
        return True
    
    @staticmethod
    def execute_command(command: str) -> str:
        """
        Mock SSH command execution.
        
        Args:
            command: Command to execute
            
        Returns:
            Mock output
        """
        print(f"[MOCK_SSH] Executing command: {command}")
        mock_output = f"Mock output for command: {command}"
        print(f"[MOCK_SSH] Command executed successfully")
        return mock_output
    
    @staticmethod
    def disconnect() -> bool:
        """
        Mock SSH disconnection.
        
        Returns:
            True (mock success)
        """
        print(f"[MOCK_SSH] Disconnecting from host")
        return True


class MockRDP:
    """Mock RDP component for testing."""
    
    @staticmethod
    def connect(host: str, port: int = 3389, username: str = None, password: str = None) -> bool:
        """
        Mock RDP connection.
        
        Args:
            host: Host to connect to
            port: RDP port (default 3389)
            username: Username for authentication
            password: Password for authentication
            
        Returns:
            True (mock success)
        """
        print(f"[MOCK_RDP] Validating remote connection to {host}:{port}")
        print(f"[MOCK_RDP] Authenticating user '{username}'")
        print(f"[MOCK_RDP] Remote connection established")
        return True
    
    @staticmethod
    def execute_remote_action(action: str, parameters: dict = None) -> bool:
        """
        Mock RDP remote action execution.
        
        Args:
            action: Action to perform
            parameters: Action parameters
            
        Returns:
            True (mock success)
        """
        print(f"[MOCK_RDP] Executing remote action: {action}")
        if parameters:
            print(f"[MOCK_RDP] Action parameters: {parameters}")
        print(f"[MOCK_RDP] Remote action completed successfully")
        return True
    
    @staticmethod
    def disconnect() -> bool:
        """
        Mock RDP disconnection.
        
        Returns:
            True (mock success)
        """
        print(f"[MOCK_RDP] Closing remote connection")
        return True
