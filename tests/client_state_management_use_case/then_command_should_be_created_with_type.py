"""Then command should be created with type - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext, expected_command_type: str) -> None:
    """
    Verify command was created with specified type
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production verification
    assert hasattr(ctx, 'created_command'), "Command should have been created"
    assert ctx.created_command.type == expected_command_type, f"Command type should be {expected_command_type} but was {ctx.created_command.type}"