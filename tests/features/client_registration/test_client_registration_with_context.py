"""
Test to verify ScenarioContext can be used in sub-directory tests
This demonstrates that the root conftest.py ScenarioContext is accessible
"""

import pytest
from conftest import ScenarioContext, BDDPhase


class TestClientRegistrationWithContext:
    """Test client registration using phase-aware ScenarioContext in sub-directory"""
    
    def test_client_registration_flow_with_phase_context(self):
        """Test complete client registration flow using ScenarioContext phases"""
        ctx = ScenarioContext()
        
        # === GIVEN: Setup test scenario ===
        ctx.set_phase(BDDPhase.GIVEN)
        ctx.client_id = "sub-test-client-456"
        ctx.client_name = "Sub Directory Test Client"
        ctx.expected_response_status = 201
        
        # === WHEN: Execute registration ===  
        ctx.set_phase(BDDPhase.WHEN)
        
        # Simulate client registration execution
        registration_result = {
            "client_id": ctx.client_id,
            "name": ctx.client_name,
            "status": "registered",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        # Collect results
        ctx.registration_response = registration_result
        ctx.actual_status_code = 201
        ctx.registered_client_id = registration_result["client_id"]
        
        # === THEN: Verify registration success ===
        ctx.set_phase(BDDPhase.THEN)
        
        # Assertions using both input state and results
        assert ctx.actual_status_code == ctx.expected_response_status
        assert ctx.registered_client_id == ctx.client_id
        assert ctx.registration_response["name"] == ctx.client_name
        assert ctx.registration_response["status"] == "registered"
    
    def test_context_fixture_availability(self, context: ScenarioContext):
        """Test that the context fixture from root conftest.py is available"""
        # This tests that the fixture is properly inherited
        assert isinstance(context, ScenarioContext)
        assert context.get_phase() == BDDPhase.GIVEN  # Default phase
        
        # Test basic functionality
        context.test_attribute = "sub-directory-test"
        assert context.test_attribute == "sub-directory-test"
        
        # Test phase transitions
        context.set_phase(BDDPhase.WHEN)
        context.result_data = "when-phase-data"
        assert context.result_data == "when-phase-data"
        
        context.set_phase(BDDPhase.THEN)
        assert context.test_attribute == "sub-directory-test"  # Still accessible
        assert context.result_data == "when-phase-data"       # Still accessible
    
    def test_phase_enforcement_in_subdirectory(self):
        """Test that phase enforcement works correctly in sub-directories"""
        ctx = ScenarioContext()
        
        # GIVEN phase
        ctx.set_phase(BDDPhase.GIVEN)
        ctx.input_data = "subdirectory-input"
        
        # WHEN phase - should prevent input modification
        ctx.set_phase(BDDPhase.WHEN)
        ctx.output_data = "subdirectory-output"
        
        with pytest.raises(AttributeError, match="Cannot modify input state 'input_data' in WHEN phase"):
            ctx.input_data = "modified"
        
        # THEN phase - should prevent all modifications
        ctx.set_phase(BDDPhase.THEN)
        
        with pytest.raises(AttributeError, match="Cannot set attribute 'new_data' in THEN phase"):
            ctx.new_data = "not-allowed"
        
        # But reading should work
        assert ctx.input_data == "subdirectory-input"
        assert ctx.output_data == "subdirectory-output"