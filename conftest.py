"""Root conftest.py for pytest configuration and shared fixtures"""

import pytest
from enum import Enum
from typing import Any, Dict


class BDDPhase(Enum):
    """BDD test phases with different state management permissions"""
    GIVEN = "given"  # Setup phase - can set input state
    WHEN = "when"    # Action phase - can collect results, cannot modify input state  
    THEN = "then"    # Assertion phase - read-only access


class ScenarioContext:
    """
    BDD Test Context with phase-aware state management
    
    Enforces proper separation of concerns across Given-When-Then phases:
    - GIVEN: Can set input state and test data
    - WHEN: Can collect execution results, cannot modify input state
    - THEN: Read-only access for assertions
    
    Example usage:
        # Given phase - setup allowed
        ctx.set_phase(BDDPhase.GIVEN)
        ctx.client_id = "test-123"
        ctx.request_data = {...}
        
        # When phase - result collection allowed
        ctx.set_phase(BDDPhase.WHEN) 
        ctx.response = api_call_result  # ✅ Result collection
        ctx.client_id = "new"          # ❌ Raises error
        
        # Then phase - read-only
        ctx.set_phase(BDDPhase.THEN)
        assert ctx.response.status == 200  # ✅ Read access
        ctx.verification_result = True     # ❌ Raises error
    """
    
    def __init__(self):
        # Internal state - not accessible via normal attribute access
        object.__setattr__(self, '_phase', BDDPhase.GIVEN)
        object.__setattr__(self, '_input_state', {})
        object.__setattr__(self, '_results', {})
        object.__setattr__(self, '_phase_locked', False)
    
    def set_phase(self, phase: BDDPhase) -> None:
        """Set current BDD phase to control state management permissions"""
        object.__setattr__(self, '_phase', phase)
    
    def get_phase(self) -> BDDPhase:
        """Get current BDD phase"""
        return self._phase
    
    def lock_phase(self) -> None:
        """Lock phase to prevent accidental phase changes during test execution"""
        object.__setattr__(self, '_phase_locked', True)
    
    def unlock_phase(self) -> None:
        """Unlock phase for manual control (use with caution)"""
        object.__setattr__(self, '_phase_locked', False)
    
    def __setattr__(self, name: str, value: Any) -> None:
        """Override attribute setting to enforce phase-based permissions"""
        # Allow internal attributes
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return
            
        current_phase = self._phase
        
        if current_phase == BDDPhase.GIVEN:
            # GIVEN: Can set any state (input data, test setup)
            self._input_state[name] = value
            object.__setattr__(self, name, value)
            
        elif current_phase == BDDPhase.WHEN:
            # WHEN: Can collect results, cannot modify input state
            if name in self._input_state:
                raise AttributeError(
                    f"Cannot modify input state '{name}' in WHEN phase. "
                    f"Input state can only be set in GIVEN phase."
                )
            # Allow result collection
            self._results[name] = value
            object.__setattr__(self, name, value)
            
        elif current_phase == BDDPhase.THEN:
            # THEN: Read-only phase
            raise AttributeError(
                f"Cannot set attribute '{name}' in THEN phase. "
                f"THEN phase is read-only for assertions."
            )
    
    def __getattr__(self, name: str) -> Any:
        """Standard attribute access - no restrictions on reading"""
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def get_input_state(self) -> Dict[str, Any]:
        """Get all input state set during GIVEN phase"""
        return self._input_state.copy()
    
    def get_results(self) -> Dict[str, Any]:
        """Get all results collected during WHEN phase"""  
        return self._results.copy()
    
    def clear_state(self) -> None:
        """Clear all state - use with caution, mainly for testing"""
        object.__setattr__(self, '_input_state', {})
        object.__setattr__(self, '_results', {})
        # Clear dynamic attributes
        attrs_to_remove = [attr for attr in dir(self) 
                          if not attr.startswith('_') and not callable(getattr(self, attr))]
        for attr in attrs_to_remove:
            delattr(self, attr)


@pytest.fixture
def context() -> ScenarioContext:
    """Provide fresh ScenarioContext instance for each test scenario"""
    return ScenarioContext()