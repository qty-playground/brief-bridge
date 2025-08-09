"""Submit Command Use Case - BDD Step Wrapper File"""
from pytest_bdd import scenarios, given, when, then, parsers
from conftest import BDDPhase

# Import step modules
from . import given_client_is_registered_in_system
from . import given_client_is_registered_and_online
from . import given_client_is_registered_but_offline
from . import given_client_will_execute_commands_successfully
from . import given_client_will_execute_commands_successfully_with_delay
from . import given_no_client_exists_with_id
from . import given_no_preconditions
from . import when_submit_command_with_data as when_submit_command_module
from . import when_submit_commands_to_both_clients
from . import then_command_submission_should_be_successful
from . import then_command_submission_should_fail
from . import then_command_submission_should_fail_after_timeout
from . import then_both_commands_should_execute_independently
from . import then_first_command_response_should_contain
from . import then_second_command_response_should_contain
from . import then_client_should_have_only_their_command_in_repository
from . import then_submission_response_should_contain
from . import then_command_should_be_saved_in_repository
from . import then_no_command_should_be_saved_in_repository

# Load all scenarios from feature file
scenarios('story.feature')

# Step wrappers - delegate to individual step modules
@given(parsers.parse('client "{client_id}" is registered in system'))
def given_client_is_registered_in_system_step(context, client_id):
    """Delegate to given_client_is_registered_in_system step module"""
    # Set GIVEN phase and pass parameters directly to invoke()
    context.phase = BDDPhase.GIVEN
    given_client_is_registered_in_system.invoke(context, client_id=client_id)

@given(parsers.parse('no client exists with id "{client_id}"'))
def given_no_client_exists_with_id_step(context, client_id):
    """Delegate to given_no_client_exists_with_id step module"""
    # Set GIVEN phase and pass parameters directly to invoke()
    context.phase = BDDPhase.GIVEN
    given_no_client_exists_with_id.invoke(context, client_id=client_id)

@given('no preconditions')
def given_no_preconditions_step(context):
    """Delegate to given_no_preconditions step module"""
    # Set GIVEN phase
    context.phase = BDDPhase.GIVEN
    given_no_preconditions.invoke(context)

@when('I submit command with:')
def when_submit_command_with_data(context, docstring):
    """Delegate to when_submit_command_with_data step module"""
    # Set WHEN phase and pass docstring directly to invoke()
    context.phase = BDDPhase.WHEN
    when_submit_command_module.invoke(context, command_data=docstring)

@then('command submission should be successful')
def then_command_submission_was_successful(context):
    """Delegate to then_command_submission_should_be_successful step module"""
    # Set THEN phase
    context.phase = BDDPhase.THEN
    then_command_submission_should_be_successful.invoke(context)

@then('command submission should fail')
def then_command_submission_has_failed(context):
    """Delegate to then_command_submission_should_fail step module"""
    # Set THEN phase
    context.phase = BDDPhase.THEN
    then_command_submission_should_fail.invoke(context)

@then('submission response should contain:')
def then_submission_response_contains_expected_data(context, docstring):
    """Delegate to then_submission_response_should_contain step module"""
    # Set THEN phase and pass docstring directly to invoke()
    context.phase = BDDPhase.THEN
    then_submission_response_should_contain.invoke(context, expected_response_body=docstring)

@then('command should be saved in repository with:')
def then_command_was_saved_in_repository_with_data(context, docstring):
    """Delegate to then_command_should_be_saved_in_repository step module"""
    # Set THEN phase and pass docstring directly to invoke()
    context.phase = BDDPhase.THEN
    then_command_should_be_saved_in_repository.invoke(context, expected_command_data=docstring)

@then('no command should be saved in repository')
def then_no_command_was_saved_in_repository(context):
    """Delegate to then_no_command_should_be_saved_in_repository step module"""
    # Set THEN phase
    context.phase = BDDPhase.THEN
    then_no_command_should_be_saved_in_repository.invoke(context)

@given(parsers.parse('client "{client_id}" is registered and online'))
def given_client_is_registered_and_online_step(context, client_id):
    """Delegate to given_client_is_registered_and_online step module"""
    # Set GIVEN phase and pass parameters directly to invoke()
    context.phase = BDDPhase.GIVEN
    given_client_is_registered_and_online.invoke(context, client_id=client_id)

@given('client will execute commands successfully')
def given_client_will_execute_commands_successfully_step(context):
    """Delegate to given_client_will_execute_commands_successfully step module"""
    # Set GIVEN phase
    context.phase = BDDPhase.GIVEN
    given_client_will_execute_commands_successfully.invoke(context)

@given(parsers.parse('client "{client_id}" is registered but offline'))
def given_client_is_registered_but_offline_step(context, client_id):
    """Delegate to given_client_is_registered_but_offline step module"""
    # Set GIVEN phase and pass parameters directly to invoke()
    context.phase = BDDPhase.GIVEN
    given_client_is_registered_but_offline.invoke(context, client_id=client_id)

@then('command submission should fail after timeout')
def then_command_submission_should_fail_after_timeout_step(context):
    """Delegate to then_command_submission_should_fail_after_timeout step module"""
    # Set THEN phase
    context.phase = BDDPhase.THEN
    then_command_submission_should_fail_after_timeout.invoke(context)

@given(parsers.parse('client "{client_id}" will execute commands successfully with delay {delay_seconds}'))
def given_client_will_execute_commands_successfully_with_delay_step(context, client_id, delay_seconds):
    """Delegate to given_client_will_execute_commands_successfully_with_delay step module"""
    # Set GIVEN phase and pass parameters directly to invoke()
    context.phase = BDDPhase.GIVEN
    given_client_will_execute_commands_successfully_with_delay.invoke(context, client_id=client_id, delay_seconds=delay_seconds)

@when('I submit commands to both clients:')
def when_submit_commands_to_both_clients_step(context, docstring):
    """Delegate to when_submit_commands_to_both_clients step module"""
    # Set WHEN phase and pass docstring directly to invoke()
    context.phase = BDDPhase.WHEN
    when_submit_commands_to_both_clients.invoke(context, commands_data=docstring)

@then('both commands should execute independently')
def then_both_commands_should_execute_independently_step(context):
    """Delegate to then_both_commands_should_execute_independently step module"""
    # Set THEN phase
    context.phase = BDDPhase.THEN
    then_both_commands_should_execute_independently.invoke(context)

@then('first command response should contain:')
def then_first_command_response_should_contain_step(context, docstring):
    """Delegate to then_first_command_response_should_contain step module"""
    # Set THEN phase and pass docstring directly to invoke()
    context.phase = BDDPhase.THEN
    then_first_command_response_should_contain.invoke(context, expected_response_body=docstring)

@then('second command response should contain:')
def then_second_command_response_should_contain_step(context, docstring):
    """Delegate to then_second_command_response_should_contain step module"""
    # Set THEN phase and pass docstring directly to invoke()
    context.phase = BDDPhase.THEN
    then_second_command_response_should_contain.invoke(context, expected_response_body=docstring)

@then(parsers.parse('client "{client_id}" should have only their command in repository'))
def then_client_should_have_only_their_command_in_repository_step(context, client_id):
    """Delegate to then_client_should_have_only_their_command_in_repository step module"""
    # Set THEN phase and pass parameters directly to invoke()
    context.phase = BDDPhase.THEN
    then_client_should_have_only_their_command_in_repository.invoke(context, client_id=client_id)