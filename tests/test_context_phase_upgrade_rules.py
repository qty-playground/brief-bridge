"""Test ScenarioContext phase upgrade rules and property syntax"""

import pytest
from conftest import ScenarioContext, BDDPhase


class TestPhaseUpgradeRules:
    """Test BDD phase transition rules: GIVEN → WHEN → THEN only"""
    
    def test_property_syntax_works(self):
        """Test that phase can be accessed as property"""
        ctx = ScenarioContext()
        
        # Initial phase should be GIVEN
        assert ctx.phase == BDDPhase.GIVEN
        
        # Test property setter
        ctx.phase = BDDPhase.WHEN
        assert ctx.phase == BDDPhase.WHEN
        
        ctx.phase = BDDPhase.THEN
        assert ctx.phase == BDDPhase.THEN
    
    def test_valid_phase_upgrades(self):
        """Test all valid phase transitions"""
        ctx = ScenarioContext()
        
        # GIVEN → WHEN (normal flow)
        ctx.phase = BDDPhase.GIVEN
        ctx.phase = BDDPhase.WHEN  # Should work
        assert ctx.phase == BDDPhase.WHEN
        
        # WHEN → THEN (normal flow)
        ctx.phase = BDDPhase.THEN  # Should work
        assert ctx.phase == BDDPhase.THEN
    
    def test_valid_phase_skips(self):
        """Test valid phase skips (GIVEN → THEN directly)"""
        ctx = ScenarioContext()
        
        # GIVEN → THEN (skip WHEN if no action needed)
        ctx.phase = BDDPhase.GIVEN
        ctx.phase = BDDPhase.THEN  # Should work
        assert ctx.phase == BDDPhase.THEN
    
    def test_same_phase_assignment_allowed(self):
        """Test that setting same phase is allowed"""
        ctx = ScenarioContext()
        
        # Stay in GIVEN
        ctx.phase = BDDPhase.GIVEN
        ctx.phase = BDDPhase.GIVEN  # Should work
        assert ctx.phase == BDDPhase.GIVEN
        
        # Stay in WHEN
        ctx.phase = BDDPhase.WHEN
        ctx.phase = BDDPhase.WHEN  # Should work
        assert ctx.phase == BDDPhase.WHEN
        
        # Stay in THEN
        ctx.phase = BDDPhase.THEN
        ctx.phase = BDDPhase.THEN  # Should work
        assert ctx.phase == BDDPhase.THEN
    
    def test_invalid_downgrade_when_to_given(self):
        """Test WHEN → GIVEN is forbidden"""
        ctx = ScenarioContext()
        ctx.phase = BDDPhase.WHEN
        
        with pytest.raises(ValueError) as exc_info:
            ctx.phase = BDDPhase.GIVEN
        
        error_msg = str(exc_info.value)
        assert "Invalid phase transition: when → given" in error_msg
        assert "BDD phases can only progress forward" in error_msg
        assert "Cannot downgrade from when back to given" in error_msg
    
    def test_invalid_downgrade_then_to_when(self):
        """Test THEN → WHEN is forbidden"""
        ctx = ScenarioContext()
        ctx.phase = BDDPhase.WHEN
        ctx.phase = BDDPhase.THEN
        
        with pytest.raises(ValueError) as exc_info:
            ctx.phase = BDDPhase.WHEN
        
        error_msg = str(exc_info.value)
        assert "Invalid phase transition: then → when" in error_msg
        assert "BDD phases can only progress forward" in error_msg
        assert "Cannot downgrade from then back to when" in error_msg
    
    def test_invalid_downgrade_then_to_given(self):
        """Test THEN → GIVEN is forbidden"""
        ctx = ScenarioContext()
        ctx.phase = BDDPhase.THEN
        
        with pytest.raises(ValueError) as exc_info:
            ctx.phase = BDDPhase.GIVEN
        
        error_msg = str(exc_info.value)
        assert "Invalid phase transition: then → given" in error_msg
        assert "BDD phases can only progress forward" in error_msg
        assert "Cannot downgrade from then back to given" in error_msg
    
    def test_deprecated_methods_still_work(self):
        """Test that old set_phase/get_phase methods still work"""
        ctx = ScenarioContext()
        
        # Test deprecated set_phase
        ctx.set_phase(BDDPhase.WHEN)
        assert ctx.get_phase() == BDDPhase.WHEN
        assert ctx.phase == BDDPhase.WHEN
        
        # Test deprecated get_phase  
        ctx.phase = BDDPhase.THEN
        assert ctx.get_phase() == BDDPhase.THEN
    
    def test_phase_upgrade_with_state_management(self):
        """Test phase upgrades work with state management"""
        ctx = ScenarioContext()
        
        # GIVEN: Set input state
        ctx.phase = BDDPhase.GIVEN
        ctx.client_id = "test-123"
        ctx.api_endpoint = "/api/clients"
        
        # WHEN: Collect results, cannot modify input
        ctx.phase = BDDPhase.WHEN
        ctx.response_data = {"status": "success"}
        
        with pytest.raises(AttributeError):
            ctx.client_id = "modified"  # Should fail
        
        # THEN: Read-only
        ctx.phase = BDDPhase.THEN
        assert ctx.client_id == "test-123"
        assert ctx.response_data["status"] == "success"
        
        with pytest.raises(AttributeError):
            ctx.validation_result = True  # Should fail
    
    def test_phase_downgrade_preserves_state(self):
        """Test that failed downgrade attempts don't corrupt state"""
        ctx = ScenarioContext()
        ctx.phase = BDDPhase.GIVEN
        ctx.test_data = "important"
        ctx.phase = BDDPhase.WHEN
        ctx.result = "success"
        ctx.phase = BDDPhase.THEN
        
        # Try to downgrade - should fail but preserve state
        original_phase = ctx.phase
        with pytest.raises(ValueError):
            ctx.phase = BDDPhase.GIVEN
        
        # State should be preserved
        assert ctx.phase == original_phase
        assert ctx.test_data == "important"
        assert ctx.result == "success"


class TestPhaseUpgradeIntegration:
    """Integration tests for phase upgrade rules in realistic scenarios"""
    
    def test_typical_bdd_flow_with_properties(self):
        """Test typical BDD flow using property syntax"""
        ctx = ScenarioContext()
        
        # === GIVEN Phase ===
        ctx.phase = BDDPhase.GIVEN
        ctx.client_id = "client-001"
        ctx.expected_status = "ONLINE"
        ctx.api_url = "http://test-api.com"
        
        # === WHEN Phase ===  
        ctx.phase = BDDPhase.WHEN
        # Simulate API call results
        ctx.api_response = {
            "client_id": "client-001",
            "status": "ONLINE",
            "last_seen": "2024-01-01T00:00:00Z"
        }
        ctx.response_time = 0.123
        
        # === THEN Phase ===
        ctx.phase = BDDPhase.THEN
        assert ctx.api_response["client_id"] == ctx.client_id
        assert ctx.api_response["status"] == ctx.expected_status
        assert ctx.response_time < 1.0
        
        # Verify all state is accessible
        input_state = ctx.get_input_state()
        results = ctx.get_results()
        
        assert "client_id" in input_state
        assert "api_response" in results
        assert "response_time" in results
    
    def test_skip_when_phase_scenario(self):
        """Test scenario that skips WHEN phase (GIVEN → THEN)"""
        ctx = ScenarioContext()
        
        # Setup in GIVEN
        ctx.phase = BDDPhase.GIVEN
        ctx.configuration_value = "test-config"
        ctx.expected_result = True
        
        # Skip directly to THEN for configuration validation
        ctx.phase = BDDPhase.THEN
        assert ctx.configuration_value == "test-config"
        assert ctx.expected_result is True
        
        # Verify state tracking
        input_state = ctx.get_input_state()
        results = ctx.get_results()
        assert len(input_state) == 2
        assert len(results) == 0  # No WHEN phase results