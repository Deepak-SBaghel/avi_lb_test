"""
Test Orchestrator module for managing test execution with 4-stage workflow.
Handles Pre-Fetcher, Pre-Validation, Task/Trigger, and Post-Validation stages.
"""

import json
from typing import Dict, Any, Optional, List
from api_client import APIClient
from mocks import MockSSH, MockRDP


class TestOrchestrator:
    """Orchestrates test execution with 4-stage workflow."""
    
    def __init__(self, api_client: APIClient, target_vs_name: str):
        """
        Initialize Test Orchestrator.
        
        Args:
            api_client: APIClient instance for API interactions
            target_vs_name: Name of the target virtual service
        """
        self.api_client = api_client
        self.target_vs_name = target_vs_name
        self.test_results = {
            'pre_fetcher': None,
            'pre_validation': None,
            'task_trigger': None,
            'post_validation': None
        }
    
    def stage_1_pre_fetcher(self) -> Dict[str, Any]:
        """
        Stage 1: Pre-Fetcher
        Fetch all tenants, virtual services, and service engines.
        
        Returns:
            Dictionary with fetched data
        """
        print("\n" + "="*70)
        print("STAGE 1: PRE-FETCHER")
        print("="*70)
        print("Fetching tenants, virtual services, and service engines...")
        
        try:
            tenants = self.api_client.get_tenants()
            virtual_services = self.api_client.get_virtual_services()
            service_engines = self.api_client.get_service_engines()
            
            result = {
                'status': 'success',
                'tenants_count': len(tenants) if tenants else 0,
                'virtual_services_count': len(virtual_services) if virtual_services else 0,
                'service_engines_count': len(service_engines) if service_engines else 0,
                'tenants': tenants,
                'virtual_services': virtual_services,
                'service_engines': service_engines
            }
            
            print(f"\n[PRE-FETCHER] Results:")
            print(f"  - Tenants: {result['tenants_count']}")
            print(f"  - Virtual Services: {result['virtual_services_count']}")
            print(f"  - Service Engines: {result['service_engines_count']}")
            
            if virtual_services:
                print(f"\n[PRE-FETCHER] Virtual Services List:")
                for vs in virtual_services:
                    print(f"  - {vs.get('name')} (UUID: {vs.get('uuid', 'N/A')}, Enabled: {vs.get('enabled')})")
            
            self.test_results['pre_fetcher'] = result
            return result
            
        except Exception as e:
            print(f"[PRE-FETCHER] Error: {e}")
            result = {'status': 'failed', 'error': str(e)}
            self.test_results['pre_fetcher'] = result
            return result
    
    def stage_2_pre_validation(self, virtual_services: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Stage 2: Pre-Validation
        Identify and validate the target Virtual Service.
        
        Args:
            virtual_services: List of virtual services (if already fetched)
            
        Returns:
            Dictionary with validation result
        """
        print("\n" + "="*70)
        print("STAGE 2: PRE-VALIDATION")
        print("="*70)
        print(f"Searching for target virtual service: '{self.target_vs_name}'")
        
        try:
            # Fetch virtual service by name
            target_vs = self.api_client.get_virtual_service_by_name(self.target_vs_name)
            
            if not target_vs:
                print(f"[PRE-VALIDATION] ERROR: Virtual service '{self.target_vs_name}' not found!")
                result = {
                    'status': 'failed',
                    'error': f"Virtual service '{self.target_vs_name}' not found"
                }
                self.test_results['pre_validation'] = result
                return result
            
            # Check if enabled
            is_enabled = target_vs.get('enabled', False)
            uuid = target_vs.get('uuid')
            
            print(f"\n[PRE-VALIDATION] Target Virtual Service Found:")
            print(f"  - Name: {target_vs.get('name')}")
            print(f"  - UUID: {uuid}")
            print(f"  - Enabled: {is_enabled}")
            print(f"  - Full Data: {json.dumps(target_vs, indent=2)}")
            
            if not is_enabled:
                print(f"[PRE-VALIDATION] ERROR: Virtual service is not enabled!")
                result = {
                    'status': 'failed',
                    'error': 'Virtual service is not enabled',
                    'virtual_service': target_vs
                }
                self.test_results['pre_validation'] = result
                return result
            
            print(f"[PRE-VALIDATION] ✓ Validation passed - Virtual service is enabled")
            result = {
                'status': 'success',
                'virtual_service': target_vs,
                'uuid': uuid,
                'enabled': is_enabled
            }
            self.test_results['pre_validation'] = result
            return result
            
        except Exception as e:
            print(f"[PRE-VALIDATION] Error: {e}")
            result = {'status': 'failed', 'error': str(e)}
            self.test_results['pre_validation'] = result
            return result
    
    def stage_3_task_trigger(self, uuid: str) -> Dict[str, Any]:
        """
        Stage 3: Task/Trigger
        Convert the Virtual Service endpoint to PUT request and disable it.
        
        Args:
            uuid: UUID of the virtual service to disable
            
        Returns:
            Dictionary with update result
        """
        print("\n" + "="*70)
        print("STAGE 3: TASK/TRIGGER")
        print("="*70)
        print(f"Disabling virtual service (UUID: {uuid})")
        print(f"Sending PUT request with payload: {{'enabled': false}}")
        
        try:
            payload = {'enabled': False}
            response = self.api_client.update_virtual_service(uuid, payload)
            
            if response is None:
                result = {
                    'status': 'failed',
                    'error': 'Failed to update virtual service'
                }
                self.test_results['task_trigger'] = result
                return result
            
            is_enabled = response.get('enabled', True)
            print(f"\n[TASK/TRIGGER] Update Response:")
            print(f"  - Enabled: {is_enabled}")
            print(f"  - Full Response: {json.dumps(response, indent=2)}")
            
            if is_enabled:
                print(f"[TASK/TRIGGER] ERROR: Virtual service is still enabled!")
                result = {
                    'status': 'failed',
                    'error': 'Virtual service was not disabled',
                    'response': response
                }
                self.test_results['task_trigger'] = result
                return result
            
            print(f"[TASK/TRIGGER] ✓ Virtual service disabled successfully")
            result = {
                'status': 'success',
                'response': response,
                'enabled': is_enabled
            }
            self.test_results['task_trigger'] = result
            return result
            
        except Exception as e:
            print(f"[TASK/TRIGGER] Error: {e}")
            result = {'status': 'failed', 'error': str(e)}
            self.test_results['task_trigger'] = result
            return result
    
    def stage_4_post_validation(self, uuid: str) -> Dict[str, Any]:
        """
        Stage 4: Post-Validation
        Verify that the Virtual Service is now disabled.
        
        Args:
            uuid: UUID of the virtual service to verify
            
        Returns:
            Dictionary with validation result
        """
        print("\n" + "="*70)
        print("STAGE 4: POST-VALIDATION")
        print("="*70)
        print(f"Verifying virtual service is disabled (UUID: {uuid})")
        print(f"Sending GET request to check enabled status")
        
        try:
            response = self.api_client.get_virtual_service_by_uuid(uuid)
            
            if response is None:
                result = {
                    'status': 'failed',
                    'error': 'Failed to fetch virtual service'
                }
                self.test_results['post_validation'] = result
                return result
            
            is_enabled = response.get('enabled', True)
            print(f"\n[POST-VALIDATION] Virtual Service Status:")
            print(f"  - Enabled: {is_enabled}")
            print(f"  - Full Data: {json.dumps(response, indent=2)}")
            
            if is_enabled:
                print(f"[POST-VALIDATION] ERROR: Virtual service is still enabled!")
                result = {
                    'status': 'failed',
                    'error': 'Virtual service is still enabled',
                    'response': response
                }
                self.test_results['post_validation'] = result
                return result
            
            print(f"[POST-VALIDATION] ✓ Verification passed - Virtual service is disabled")
            result = {
                'status': 'success',
                'response': response,
                'enabled': is_enabled
            }
            self.test_results['post_validation'] = result
            return result
            
        except Exception as e:
            print(f"[POST-VALIDATION] Error: {e}")
            result = {'status': 'failed', 'error': str(e)}
            self.test_results['post_validation'] = result
            return result
    
    def run_full_workflow(self) -> Dict[str, Any]:
        """
        Run the complete 4-stage test workflow.
        
        Returns:
            Dictionary with all test results
        """
        print("\n" + "#"*70)
        print("STARTING FULL TEST WORKFLOW")
        print("#"*70)
        
        # Stage 1: Pre-Fetcher
        self.stage_1_pre_fetcher()
        
        # Stage 2: Pre-Validation
        pre_validation = self.stage_2_pre_validation()
        if pre_validation['status'] != 'success':
            print("\n[WORKFLOW] Pre-validation failed. Stopping workflow.")
            return self.test_results
        
        uuid = pre_validation.get('uuid')
        
        # Stage 3: Task/Trigger
        self.stage_3_task_trigger(uuid)
        
        # Stage 4: Post-Validation
        self.stage_4_post_validation(uuid)
        
        # Summary
        self._print_summary()
        
        return self.test_results
    
    def _print_summary(self) -> None:
        """Print test execution summary."""
        print("\n" + "#"*70)
        print("TEST EXECUTION SUMMARY")
        print("#"*70)
        
        for stage, result in self.test_results.items():
            status = result.get('status', 'unknown') if result else 'not-executed'
            status_symbol = "✓" if status == "success" else "✗" if status == "failed" else "○"
            print(f"{status_symbol} {stage.upper()}: {status.upper()}")
        
        # Overall result
        all_success = all(
            r and r.get('status') == 'success' 
            for r in self.test_results.values() 
            if r is not None
        )
        
        overall_status = "PASSED" if all_success else "FAILED"
        print(f"\nOVERALL TEST RESULT: {overall_status}")
        print("#"*70)
