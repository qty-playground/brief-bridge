"""Tests for BDD phase-aware ScenarioContext implementation"""

import pytest
from conftest import ScenarioContext, BDDPhase


class TestBDDPhaseManagement:
    """Test phase-based state management in ScenarioContext"""
    
    def test_given_phase_allows_input_state_setting(self):
        """GIVEN phase should allow setting input state"""
        ctx = ScenarioContext()
        ctx.set_phase(BDDPhase.GIVEN)
        
        # Should be able to set input state
        ctx.client_id = "test-123"
        ctx.request_data = {"key": "value"}
        ctx.expected_status = 200
        
        assert ctx.client_id == "test-123"
        assert ctx.request_data == {"key": "value"}
        assert ctx.expected_status == 200
        
        # Should track input state
        input_state = ctx.get_input_state()
        assert "client_id" in input_state
        assert "request_data" in input_state
        assert "expected_status" in input_state

    def test_when_phase_allows_result_collection_but_prevents_input_modification(self):
        """WHEN phase should allow result collection but prevent input state modification"""
        ctx = ScenarioContext()
        
        # Setup in GIVEN phase
        ctx.set_phase(BDDPhase.GIVEN)
        ctx.client_id = "test-123"
        ctx.request_data = {"key": "value"}
        
        # Switch to WHEN phase
        ctx.set_phase(BDDPhase.WHEN)
        
        # Should be able to collect results
        ctx.response = {"status": 200, "body": "success"}
        ctx.execution_time = 0.5
        ctx.error = None
        
        assert ctx.response == {"status": 200, "body": "success"}
        assert ctx.execution_time == 0.5
        assert ctx.error is None
        
        # Should track results
        results = ctx.get_results()
        assert "response" in results
        assert "execution_time" in results
        assert "error" in results
        
        # Should prevent modification of input state
        with pytest.raises(AttributeError, match="Cannot modify input state 'client_id' in WHEN phase"):
            ctx.client_id = "modified-123"
            
        with pytest.raises(AttributeError, match="Cannot modify input state 'request_data' in WHEN phase"):
            ctx.request_data = {"modified": "data"}

    def test_then_phase_prevents_all_state_modification(self):
        """THEN phase should be read-only"""
        ctx = ScenarioContext()
        
        # Setup in GIVEN phase
        ctx.set_phase(BDDPhase.GIVEN)
        ctx.client_id = "test-123"
        
        # Collect results in WHEN phase
        ctx.set_phase(BDDPhase.WHEN)
        ctx.response = {"status": 200}
        
        # Switch to THEN phase
        ctx.set_phase(BDDPhase.THEN)
        
        # Should be able to read existing state
        assert ctx.client_id == "test-123"
        assert ctx.response == {"status": 200}
        
        # Should prevent any state modification
        with pytest.raises(AttributeError, match="Cannot set attribute 'new_input' in THEN phase"):
            ctx.new_input = "not allowed"
            
        with pytest.raises(AttributeError, match="Cannot set attribute 'verification_result' in THEN phase"):
            ctx.verification_result = True

    def test_phase_transitions_preserve_existing_state(self):
        """State should be preserved across phase transitions"""
        ctx = ScenarioContext()
        
        # GIVEN: Setup input state
        ctx.set_phase(BDDPhase.GIVEN)
        ctx.client_id = "test-123"
        ctx.setup_data = "initial"
        
        # WHEN: Collect results
        ctx.set_phase(BDDPhase.WHEN)
        ctx.response = {"result": "success"}
        ctx.timing = 1.23
        
        # Should still access GIVEN state
        assert ctx.client_id == "test-123"
        assert ctx.setup_data == "initial"
        
        # THEN: Read-only access to all state
        ctx.set_phase(BDDPhase.THEN)
        assert ctx.client_id == "test-123"      # From GIVEN
        assert ctx.setup_data == "initial"      # From GIVEN
        assert ctx.response == {"result": "success"}  # From WHEN
        assert ctx.timing == 1.23               # From WHEN

    def test_state_introspection_methods(self):
        """Test helper methods for state introspection"""
        ctx = ScenarioContext()
        
        # GIVEN phase
        ctx.set_phase(BDDPhase.GIVEN)
        ctx.client_id = "test-123"
        ctx.test_data = {"setup": True}
        
        input_state = ctx.get_input_state()
        assert input_state == {
            "client_id": "test-123",
            "test_data": {"setup": True}
        }
        assert ctx.get_results() == {}  # No results yet
        
        # WHEN phase
        ctx.set_phase(BDDPhase.WHEN)
        ctx.response = {"status": 200}
        ctx.duration = 0.5
        
        # Input state unchanged
        assert ctx.get_input_state() == input_state
        
        # Results collected
        results = ctx.get_results()
        assert results == {
            "response": {"status": 200},
            "duration": 0.5
        }

    def test_clear_state_functionality(self):
        """Test state clearing functionality"""
        ctx = ScenarioContext()
        
        # Add some state
        ctx.set_phase(BDDPhase.GIVEN)
        ctx.client_id = "test-123"
        
        ctx.set_phase(BDDPhase.WHEN)
        ctx.response = {"status": 200}
        
        # Clear state
        ctx.clear_state()
        
        # State should be cleared
        assert ctx.get_input_state() == {}
        assert ctx.get_results() == {}
        
        # Attributes should be removed
        with pytest.raises(AttributeError):
            _ = ctx.client_id
        with pytest.raises(AttributeError):
            _ = ctx.response

    def test_phase_detection(self):
        """Test phase detection functionality"""
        ctx = ScenarioContext()
        
        assert ctx.get_phase() == BDDPhase.GIVEN  # Default
        
        ctx.set_phase(BDDPhase.WHEN)
        assert ctx.get_phase() == BDDPhase.WHEN
        
        ctx.set_phase(BDDPhase.THEN)
        assert ctx.get_phase() == BDDPhase.THEN


class TestBDDContextIntegration:
    """Integration tests for BDD context usage patterns"""
    
    def test_typical_bdd_scenario_flow(self):
        """Test a complete BDD scenario flow"""
        ctx = ScenarioContext()
        
        # === GIVEN phase ===
        ctx.set_phase(BDDPhase.GIVEN)
        ctx.client_id = "integration-test-client"
        ctx.endpoint = "/api/clients"
        ctx.request_payload = {
            "name": "Test Client",
            "type": "integration"
        }
        
        # === WHEN phase ===
        ctx.set_phase(BDDPhase.WHEN)
        
        # Simulate API call and result collection
        ctx.http_response = {
            "status_code": 201,
            "headers": {"content-type": "application/json"},
            "body": {"client_id": "generated-id-456", "status": "created"}
        }
        ctx.execution_duration = 0.234
        ctx.database_queries_count = 2
        
        # === THEN phase ===
        ctx.set_phase(BDDPhase.THEN)
        
        # Assertions can read all state
        assert ctx.client_id == "integration-test-client"  # From GIVEN
        assert ctx.endpoint == "/api/clients"              # From GIVEN
        assert ctx.http_response["status_code"] == 201     # From WHEN
        assert ctx.http_response["body"]["status"] == "created"  # From WHEN
        assert ctx.execution_duration < 1.0               # From WHEN
        
        # Verify state categories
        input_state = ctx.get_input_state()
        assert "client_id" in input_state
        assert "endpoint" in input_state
        assert "request_payload" in input_state
        
        results = ctx.get_results()
        assert "http_response" in results
        assert "execution_duration" in results
        assert "database_queries_count" in results