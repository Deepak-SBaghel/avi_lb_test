"""
Main entry point for the Python Test Automation Framework.
Handles test orchestration with parallel execution support.
"""

import sys
import argparse
import threading
import multiprocessing
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Dict, Any
from config_loader import ConfigLoader
from api_client import APIClient
from test_orchestrator import TestOrchestrator


class TestFramework:
    """Main test automation framework."""
    
    def __init__(self, config_file: str = "test_config.yaml"):
        """
        Initialize the test framework.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_loader = ConfigLoader(config_file)
        self.api_client = None
        self.test_results = []
    
    def setup(self) -> bool:
        """
        Set up the test framework (register and login).
        
        Returns:
            True if setup successful, False otherwise
        """
        print("\n" + "="*70)
        print("TEST FRAMEWORK SETUP")
        print("="*70)
        
        try:
            api_config = self.config_loader.get_api_config()
            credentials = self.config_loader.get_credentials()
            
            base_url = api_config.get('base_url')
            timeout = self.config_loader.get_timeout()
            
            if not base_url or not credentials.get('username') or not credentials.get('password'):
                print("[SETUP] ERROR: Missing API configuration or credentials")
                return False
            
            # Initialize API client
            self.api_client = APIClient(base_url, timeout)
            
            # Register user
            print(f"\n[SETUP] Registering user: {credentials['username']}")
            if not self.api_client.register(credentials['username'], credentials['password']):
                print("[SETUP] WARNING: Registration failed or user already exists")
            
            # Login
            print(f"[SETUP] Logging in user: {credentials['username']}")
            if not self.api_client.login(credentials['username'], credentials['password']):
                print("[SETUP] ERROR: Login failed")
                return False
            
            print("[SETUP] ✓ Framework setup completed successfully")
            return True
            
        except Exception as e:
            print(f"[SETUP] Error during setup: {e}")
            return False
    
    def run_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single test case.
        
        Args:
            test_case: Test case configuration
            
        Returns:
            Test results
        """
        test_name = test_case.get('name', 'unknown')
        print(f"\n[TEST_FRAMEWORK] Running test case: {test_name}")
        
        try:
            orchestrator = TestOrchestrator(
                self.api_client,
                test_case.get('target_virtual_service', self.config_loader.get_target_virtual_service())
            )
            
            result = orchestrator.run_full_workflow()
            
            return {
                'test_name': test_name,
                'status': 'completed',
                'results': result
            }
            
        except Exception as e:
            print(f"[TEST_FRAMEWORK] Error running test case '{test_name}': {e}")
            return {
                'test_name': test_name,
                'status': 'failed',
                'error': str(e)
            }
    
    def run_tests_sequentially(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run test cases sequentially.
        
        Args:
            test_cases: List of test cases
            
        Returns:
            List of test results
        """
        print(f"\n[TEST_FRAMEWORK] Running {len(test_cases)} test case(s) sequentially")
        results = []
        
        for test_case in test_cases:
            result = self.run_test_case(test_case)
            results.append(result)
        
        return results
    
    def run_tests_in_parallel_threading(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run test cases in parallel using threading.
        
        Args:
            test_cases: List of test cases
            
        Returns:
            List of test results
        """
        max_workers = self.config_loader.get_max_workers()
        print(f"\n[TEST_FRAMEWORK] Running {len(test_cases)} test case(s) in parallel (threading, {max_workers} workers)")
        
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.run_test_case, tc) for tc in test_cases]
            for future in futures:
                results.append(future.result())
        
        return results
    
    def run_tests_in_parallel_multiprocessing(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run test cases in parallel using multiprocessing.
        
        Args:
            test_cases: List of test cases
            
        Returns:
            List of test results
        """
        max_workers = self.config_loader.get_max_workers()
        print(f"\n[TEST_FRAMEWORK] Running {len(test_cases)} test case(s) in parallel (multiprocessing, {max_workers} workers)")
        
        results = []
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.run_test_case, tc) for tc in test_cases]
            for future in futures:
                results.append(future.result())
        
        return results
    
    def run_tests_async(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run test cases asynchronously using asyncio.
        
        Args:
            test_cases: List of test cases
            
        Returns:
            List of test results
        """
        print(f"\n[TEST_FRAMEWORK] Running {len(test_cases)} test case(s) asynchronously (asyncio)")
        
        async def run_async():
            tasks = [asyncio.to_thread(self.run_test_case, tc) for tc in test_cases]
            return await asyncio.gather(*tasks)
        
        results = asyncio.run(run_async())
        return results
    
    def run_tests(self, parallelism_method: str = None) -> List[Dict[str, Any]]:
        """
        Run all test cases with specified parallelism method.
        
        Args:
            parallelism_method: Method to use ('sequential', 'threading', 'multiprocessing', 'asyncio')
            
        Returns:
            List of test results
        """
        test_cases = self.config_loader.get_test_cases()
        
        if not test_cases:
            print("[TEST_FRAMEWORK] ERROR: No test cases found in configuration")
            return []
        
        if parallelism_method is None:
            parallelism_method = self.config_loader.get_parallelism_method()
        
        if parallelism_method == 'sequential':
            self.test_results = self.run_tests_sequentially(test_cases)
        elif parallelism_method == 'threading':
            self.test_results = self.run_tests_in_parallel_threading(test_cases)
        elif parallelism_method == 'multiprocessing':
            self.test_results = self.run_tests_in_parallel_multiprocessing(test_cases)
        elif parallelism_method == 'asyncio':
            self.test_results = self.run_tests_async(test_cases)
        else:
            print(f"[TEST_FRAMEWORK] ERROR: Unknown parallelism method: {parallelism_method}")
            return []
        
        return self.test_results
    
    def print_final_summary(self) -> None:
        """Print final test execution summary."""
        print("\n" + "*"*70)
        print("FINAL TEST EXECUTION SUMMARY")
        print("*"*70)
        
        for result in self.test_results:
            test_name = result.get('test_name', 'unknown')
            status = result.get('status', 'unknown')
            print(f"\nTest Case: {test_name}")
            print(f"Status: {status}")
            
            if status == 'completed':
                workflow_results = result.get('results', {})
                for stage, stage_result in workflow_results.items():
                    stage_status = stage_result.get('status', 'unknown') if stage_result else 'not-executed'
                    print(f"  - {stage}: {stage_status}")
            elif status == 'failed':
                error = result.get('error', 'unknown error')
                print(f"  Error: {error}")
        
        print("\n" + "*"*70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='VMware Avi Load Balancer Test Automation Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py                          # Run with default configuration
  python main.py --config custom.yaml     # Use custom configuration file
  python main.py --parallel threading     # Run with threading
  python main.py --parallel multiprocessing # Run with multiprocessing
  python main.py --parallel asyncio       # Run asynchronously
        '''
    )
    
    parser.add_argument('--config', default='test_config.yaml',
                        help='Path to configuration file (default: test_config.yaml)')
    parser.add_argument('--parallel', choices=['sequential', 'threading', 'multiprocessing', 'asyncio'],
                        help='Parallelism method (overrides config setting)')
    
    args = parser.parse_args()
    
    try:
        # Initialize framework
        framework = TestFramework(args.config)
        
        # Setup (register and login)
        if not framework.setup():
            print("[MAIN] Setup failed. Exiting.")
            sys.exit(1)
        
        # Run tests
        framework.run_tests(args.parallel)
        
        # Print summary
        framework.print_final_summary()
        
        print("\n[MAIN] Test automation framework execution completed.")
        
    except KeyboardInterrupt:
        print("\n[MAIN] Test execution interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"[MAIN] Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
