"""Test wrapper for one-click install feature - delegates to step modules"""
from pytest_bdd import scenarios, given, when, then, parsers
from conftest import BDDPhase

# Import step modules
from . import given_server_is_accessible_via_public_url
from . import given_server_url_is_not_accessible
from . import given_client_is_already_running
from . import when_user_executes_powershell_install
from . import when_user_executes_bash_install
from . import when_user_executes_install_with_client_id
from . import when_user_executes_install_with_parameters
from . import when_user_executes_install_with_background
from . import when_user_executes_install_command
from . import when_user_executes_install_again
from . import then_client_script_should_be_downloaded
from . import then_client_should_auto_register
from . import then_client_should_start_polling
from . import then_user_should_see_success_message
from . import then_client_should_register_with_id
from . import then_client_should_run_with_parameters
from . import then_client_should_run_in_background
from . import then_user_can_continue_using_terminal
from . import then_client_process_should_continue_polling
from . import then_connection_error_should_be_displayed
from . import then_installation_should_abort
from . import then_no_client_process_should_run
from . import then_should_detect_existing_client
from . import then_should_ask_user_to_choose

# Load all scenarios from feature file
scenarios('story.feature')

# Given step wrappers
@given('server is running and accessible via public URL')
def given_server_running_and_accessible(context):
    """Delegate to given_server_is_accessible_via_public_url step module"""
    context.phase = BDDPhase.GIVEN
    given_server_is_accessible_via_public_url.invoke(context)

@given('server URL is not accessible')
def given_server_url_not_accessible(context):
    """Delegate to given_server_url_is_not_accessible step module"""
    context.phase = BDDPhase.GIVEN
    given_server_url_is_not_accessible.invoke(context)

@given('client is already running')
def given_client_already_running(context):
    """Delegate to given_client_is_already_running step module"""
    context.phase = BDDPhase.GIVEN
    given_client_is_already_running.invoke(context)

# When step wrappers
@when('user executes PowerShell install command:')
def when_user_runs_powershell_install(context, docstring):
    """Delegate to when_user_executes_powershell_install step module"""
    context.phase = BDDPhase.WHEN
    when_user_executes_powershell_install.invoke(context, install_command=docstring)

@when('user executes Bash install command:')
def when_user_runs_bash_install(context, docstring):
    """Delegate to when_user_executes_bash_install step module"""
    context.phase = BDDPhase.WHEN
    when_user_executes_bash_install.invoke(context, install_command=docstring)

@when('user executes install command with specified client ID:')
def when_user_runs_install_with_client_id(context, docstring):
    """Delegate to when_user_executes_install_with_client_id step module"""
    context.phase = BDDPhase.WHEN
    when_user_executes_install_with_client_id.invoke(context, install_command=docstring)

@when('user executes install command with multiple parameters:')
def when_user_runs_install_with_parameters(context, docstring):
    """Delegate to when_user_executes_install_with_parameters step module"""
    context.phase = BDDPhase.WHEN
    when_user_executes_install_with_parameters.invoke(context, install_command=docstring)

@when('user executes install command with background flag:')
def when_user_runs_install_with_background(context, docstring):
    """Delegate to when_user_executes_install_with_background step module"""
    context.phase = BDDPhase.WHEN
    when_user_executes_install_with_background.invoke(context, install_command=docstring)

@when('user executes install command')
def when_user_runs_install_command(context):
    """Delegate to when_user_executes_install_command step module"""
    context.phase = BDDPhase.WHEN
    when_user_executes_install_command.invoke(context)

@when('user executes install command again')
def when_user_runs_install_again(context):
    """Delegate to when_user_executes_install_again step module"""
    context.phase = BDDPhase.WHEN
    when_user_executes_install_again.invoke(context)

# Then step wrappers
@then('client script should be downloaded')
def then_client_script_downloaded(context):
    """Delegate to then_client_script_should_be_downloaded step module"""
    context.phase = BDDPhase.THEN
    then_client_script_should_be_downloaded.invoke(context)

@then('client should automatically register with server')
def then_client_auto_registers(context):
    """Delegate to then_client_should_auto_register step module"""
    context.phase = BDDPhase.THEN
    then_client_should_auto_register.invoke(context)

@then('client should start polling for commands')
def then_client_starts_polling(context):
    """Delegate to then_client_should_start_polling step module"""
    context.phase = BDDPhase.THEN
    then_client_should_start_polling.invoke(context)

@then('user should see success message')
def then_user_sees_success_message(context):
    """Delegate to then_user_should_see_success_message step module"""
    context.phase = BDDPhase.THEN
    then_user_should_see_success_message.invoke(context)

@then(parsers.parse('client should register with ID "{client_id}"'))
def then_client_registers_with_id(context, client_id):
    """Delegate to then_client_should_register_with_id step module"""
    context.phase = BDDPhase.THEN
    then_client_should_register_with_id.invoke(context, expected_id=client_id)

@then('client should run with specified parameters:')
def then_client_runs_with_parameters(context, docstring):
    """Delegate to then_client_should_run_with_parameters step module"""
    context.phase = BDDPhase.THEN
    then_client_should_run_with_parameters.invoke(context, expected_params=docstring)

@then('client should run in background')
def then_client_runs_in_background(context):
    """Delegate to then_client_should_run_in_background step module"""
    context.phase = BDDPhase.THEN
    then_client_should_run_in_background.invoke(context)

@then('user should be able to continue using terminal')
def then_user_continues_using_terminal(context):
    """Delegate to then_user_can_continue_using_terminal step module"""
    context.phase = BDDPhase.THEN
    then_user_can_continue_using_terminal.invoke(context)

@then('client process should continue polling for commands')
def then_client_process_continues_polling(context):
    """Delegate to then_client_process_should_continue_polling step module"""
    context.phase = BDDPhase.THEN
    then_client_process_should_continue_polling.invoke(context)

@then('connection error message should be displayed')
def then_connection_error_displayed(context):
    """Delegate to then_connection_error_should_be_displayed step module"""
    context.phase = BDDPhase.THEN
    then_connection_error_should_be_displayed.invoke(context)

@then('installation should abort')
def then_installation_aborts(context):
    """Delegate to then_installation_should_abort step module"""
    context.phase = BDDPhase.THEN
    then_installation_should_abort.invoke(context)

@then('no client process should be running')
def then_no_client_process_running(context):
    """Delegate to then_no_client_process_should_run step module"""
    context.phase = BDDPhase.THEN
    then_no_client_process_should_run.invoke(context)

@then('should detect existing client')
def then_detects_existing_client(context):
    """Delegate to then_should_detect_existing_client step module"""
    context.phase = BDDPhase.THEN
    then_should_detect_existing_client.invoke(context)

@then('should ask user to choose:')
def then_asks_user_to_choose(context, docstring):
    """Delegate to then_should_ask_user_to_choose step module"""
    context.phase = BDDPhase.THEN
    then_should_ask_user_to_choose.invoke(context, choices=docstring)