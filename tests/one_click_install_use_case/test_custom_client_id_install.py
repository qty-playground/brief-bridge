"""Test install with custom client ID scenario"""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from conftest import ScenarioContext

# Load scenarios from feature file
scenarios('story.feature')

# Import step modules
from . import given_server_is_running_and_accessible_via_public_url
from . import when_user_executes_install_command_with_specified_client_id
from . import then_client_should_register_with_id
from . import then_client_should_start_polling_for_commands

# BDD Step Implementations using Command Pattern

@given("server is running and accessible via public URL")
def step_given_server_is_running_and_accessible_via_public_url(context: ScenarioContext):
    """Given server is running and accessible via public URL"""
    given_server_is_running_and_accessible_via_public_url.invoke(context)

@when('user executes install command with specified client ID:')
def step_when_user_executes_install_command_with_specified_client_id(context: ScenarioContext, docstring):
    """When user executes install command with specified client ID"""
    when_user_executes_install_command_with_specified_client_id.invoke(context, docstring)

@then(parsers.parse('client should register with ID "{client_id}"'))
def step_then_client_should_register_with_id(context: ScenarioContext, client_id: str):
    """Then client should register with specified ID"""
    then_client_should_register_with_id.invoke(context, client_id)

@then("client should start polling for commands")
def step_then_client_should_start_polling_for_commands(context: ScenarioContext):
    """Then client should start polling for commands"""
    then_client_should_start_polling_for_commands.invoke(context)