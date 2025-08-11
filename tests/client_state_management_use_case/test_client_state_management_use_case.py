"""Client State Management BDD Test Module - Delegates to step modules only"""
from pytest_bdd import scenarios, given, when, then, parsers
from conftest import BDDPhase

# Import step modules
from . import given_client_is_registered_with_status
from . import given_offline_threshold_is_set
from . import given_client_was_last_seen_ago
from . import given_client_has_status
from . import given_client_is_online
from . import given_clients_with_different_statuses
from . import given_offline_threshold_is_configured
from . import when_client_polls_server
from . import when_system_checks_client_status
from . import when_server_submits_terminate_command
from . import when_server_retrieves_active_clients_list
from . import when_system_performs_status_check
from . import then_client_last_seen_should_be_updated
from . import then_client_status_should_remain
from . import then_client_should_be_marked_as
from . import then_client_status_should_be_updated_to
from . import then_command_should_be_created_with_type
from . import then_command_should_be_queued
from . import then_command_submission_should_be_successful
from . import then_response_should_include
from . import then_response_should_not_include

# Load all scenarios from feature file
scenarios('story.feature')

# Given step wrappers
@given(parsers.parse('client "{client_id}" is registered with status "{status}"'))
def given_client_is_registered_with_status_wrapper(context, client_id, status):
    """Delegate to given_client_is_registered_with_status step module"""
    context.phase = BDDPhase.GIVEN
    context.client_id = client_id
    context.status = status
    given_client_is_registered_with_status.invoke(context)

@given(parsers.parse('offline threshold is set to {seconds:d} second for testing'))
def given_offline_threshold_is_set_wrapper(context, seconds):
    """Delegate to given_offline_threshold_is_set step module"""
    context.phase = BDDPhase.GIVEN
    context.threshold_seconds = seconds
    given_offline_threshold_is_set.invoke(context)

@given(parsers.parse('client "{client_id}" was last seen {seconds:d} seconds ago'))
def given_client_was_last_seen_ago_wrapper(context, client_id, seconds):
    """Delegate to given_client_was_last_seen_ago step module"""
    context.phase = BDDPhase.GIVEN
    context.client_id = client_id
    context.last_seen_seconds_ago = seconds
    given_client_was_last_seen_ago.invoke(context)

@given(parsers.parse('client "{client_id}" has status "{status}"'))
def given_client_has_status_wrapper(context, client_id, status):
    """Delegate to given_client_has_status step module"""
    context.phase = BDDPhase.GIVEN
    context.client_id = client_id
    context.status = status
    given_client_has_status.invoke(context)

@given(parsers.parse('client "{client_id}" is online'))
def given_client_is_online_wrapper(context, client_id):
    """Delegate to given_client_is_online step module"""
    context.phase = BDDPhase.GIVEN
    context.client_id = client_id
    given_client_is_online.invoke(context)

@given('clients with different statuses:')
def given_clients_with_different_statuses_wrapper(context, datatable):
    """Delegate to given_clients_with_different_statuses step module"""
    context.phase = BDDPhase.GIVEN
    context.clients_table = datatable
    given_clients_with_different_statuses.invoke(context)

@given(parsers.parse('offline threshold is configured to {seconds:d} seconds'))
def given_offline_threshold_is_configured_wrapper(context, seconds):
    """Delegate to given_offline_threshold_is_configured step module"""
    context.phase = BDDPhase.GIVEN
    context.threshold_seconds = seconds
    given_offline_threshold_is_configured.invoke(context)

# When step wrappers
@when('client polls server for commands')
def when_client_polls_server_wrapper(context):
    """Delegate to when_client_polls_server step module"""
    context.phase = BDDPhase.WHEN
    when_client_polls_server.invoke(context)

@when('system checks client status')
def when_system_checks_client_status_wrapper(context):
    """Delegate to when_system_checks_client_status step module"""
    context.phase = BDDPhase.WHEN
    when_system_checks_client_status.invoke(context)

@when('server submits terminate command to client')
def when_server_submits_terminate_command_wrapper(context):
    """Delegate to when_server_submits_terminate_command step module"""
    context.phase = BDDPhase.WHEN
    when_server_submits_terminate_command.invoke(context)

@when('server retrieves active clients list')
def when_server_retrieves_active_clients_list_wrapper(context):
    """Delegate to when_server_retrieves_active_clients_list step module"""
    context.phase = BDDPhase.WHEN
    when_server_retrieves_active_clients_list.invoke(context)

@when('system performs status check')
def when_system_performs_status_check_wrapper(context):
    """Delegate to when_system_performs_status_check step module"""
    context.phase = BDDPhase.WHEN
    when_system_performs_status_check.invoke(context)

# Then step wrappers
@then('client last_seen should be updated to current timestamp')
def then_client_last_seen_should_be_updated_wrapper(context):
    """Delegate to then_client_last_seen_should_be_updated step module"""
    context.phase = BDDPhase.THEN
    then_client_last_seen_should_be_updated.invoke(context)

@then(parsers.parse('client status should remain "{status}"'))
def then_client_status_should_remain_wrapper(context, status):
    """Delegate to then_client_status_should_remain step module"""
    context.phase = BDDPhase.THEN
    context.expected_status = status
    then_client_status_should_remain.invoke(context)

@then(parsers.parse('client should be marked as "{status}"'))
def then_client_should_be_marked_as_wrapper(context, status):
    """Delegate to then_client_should_be_marked_as step module"""
    context.phase = BDDPhase.THEN
    context.expected_status = status
    then_client_should_be_marked_as.invoke(context)

@then(parsers.parse('client status should be updated to "{status}"'))
def then_client_status_should_be_updated_to_wrapper(context, status):
    """Delegate to then_client_status_should_be_updated_to step module"""
    context.phase = BDDPhase.THEN
    context.expected_status = status
    then_client_status_should_be_updated_to.invoke(context)

@then(parsers.parse('command should be created with type "{command_type}"'))
def then_command_should_be_created_with_type_wrapper(context, command_type):
    """Delegate to then_command_should_be_created_with_type step module"""
    context.phase = BDDPhase.THEN
    context.expected_command_type = command_type
    then_command_should_be_created_with_type.invoke(context)

@then('command should be queued for client to receive')
def then_command_should_be_queued_wrapper(context):
    """Delegate to then_command_should_be_queued step module"""
    context.phase = BDDPhase.THEN
    then_command_should_be_queued.invoke(context)

@then('command submission should be successful')
def then_command_submission_should_be_successful_wrapper(context):
    """Delegate to then_command_submission_should_be_successful step module"""
    context.phase = BDDPhase.THEN
    then_command_submission_should_be_successful.invoke(context)

@then(parsers.parse('response should include "{client_id}"'))
def then_response_should_include_wrapper(context, client_id):
    """Delegate to then_response_should_include step module"""
    context.phase = BDDPhase.THEN
    context.expected_client_id = client_id
    then_response_should_include.invoke(context)

@then(parsers.parse('response should not include "{client_id}"'))
def then_response_should_not_include_wrapper(context, client_id):
    """Delegate to then_response_should_not_include step module"""
    context.phase = BDDPhase.THEN
    context.excluded_client_id = client_id
    then_response_should_not_include.invoke(context)