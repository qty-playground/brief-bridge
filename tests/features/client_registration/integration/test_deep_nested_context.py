"""
Test to verify ScenarioContext works in deeply nested test directories
"""

from conftest import ScenarioContext, BDDPhase


def test_deeply_nested_context_access():
    """Test that ScenarioContext is accessible even in deeply nested directories"""
    ctx = ScenarioContext()
    
    # Should work exactly the same as in root tests
    ctx.set_phase(BDDPhase.GIVEN)
    ctx.deep_nested_input = "deep-nested-test"
    
    ctx.set_phase(BDDPhase.WHEN)  
    ctx.deep_nested_result = "execution-result"
    
    ctx.set_phase(BDDPhase.THEN)
    assert ctx.deep_nested_input == "deep-nested-test"
    assert ctx.deep_nested_result == "execution-result"


def test_context_fixture_in_deep_directory(context: ScenarioContext):
    """Test that fixture is available in deeply nested directory"""
    assert isinstance(context, ScenarioContext)
    
    # Test basic functionality to ensure it's the same ScenarioContext class
    context.set_phase(BDDPhase.GIVEN)
    context.fixture_test = "deep-fixture-test"
    assert context.fixture_test == "deep-fixture-test"