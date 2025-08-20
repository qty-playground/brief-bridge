"""Test wrapper for tunnel setup feature - delegates to step modules"""
from pytest_bdd import scenarios, given, when, then, parsers
from conftest import BDDPhase

# Import step modules
from . import given_server_is_running_locally
from . import given_ngrok_is_installed
from . import given_server_is_running
from . import given_administrator_has_custom_domain
from . import given_administrator_has_cloudflare_account
from . import given_tunnel_is_already_setup
from . import given_tunnel_is_running
from . import given_system_configured_with_providers
from . import given_no_tunnel_is_configured
from . import when_administrator_starts_server_with_tunnel
from . import when_administrator_calls_tunnel_setup_api
from . import when_administrator_sets_up_custom_tunnel
from . import when_administrator_sets_up_cloudflare_tunnel
from . import when_administrator_queries_tunnel_status
from . import when_administrator_queries_service_endpoint
from . import when_tunnel_connection_is_interrupted
from . import when_primary_tunnel_service_fails
from . import then_system_should_start_ngrok_tunnel
from . import then_should_display_public_url_pattern
from . import then_api_should_be_accessible
from . import then_system_should_start_tunnel_service
from . import then_response_should_contain
from . import then_system_should_use_provided_url
from . import then_should_not_start_tunnel_service
from . import then_install_urls_should_use_custom_domain
from . import then_system_should_setup_cloudflare_tunnel
from . import then_provide_stable_public_url
from . import then_response_should_show
from . import then_system_should_attempt_reconnection
from . import then_if_reconnection_fails_should
from . import then_system_should_switch_to_next_service
from . import then_update_all_related_urls
from . import then_response_should_contain_service_endpoint_url
from . import then_response_should_show_active_provider_information
from . import then_response_should_indicate_no_active_service_endpoint
from . import then_response_should_show_inactive_status

# Load all scenarios from feature file
scenarios('story.feature')

# Given step wrappers
@given('Brief Bridge server is running locally')
def given_brief_bridge_server_is_running_locally(context, ngrok_cleanup):
    """Delegate to given_server_is_running_locally step module"""
    context.phase = BDDPhase.GIVEN
    given_server_is_running_locally.invoke(context)

@given('ngrok is installed on the system')
def given_ngrok_installed_on_system(context):
    """Delegate to given_ngrok_is_installed step module"""
    context.phase = BDDPhase.GIVEN
    given_ngrok_is_installed.invoke(context)

@given('Brief Bridge server is running')
def given_brief_bridge_server_is_running(context):
    """Delegate to given_server_is_running step module"""
    context.phase = BDDPhase.GIVEN
    given_server_is_running.invoke(context)

@given('administrator has custom domain and SSL certificate')
def given_admin_has_custom_domain_and_ssl(context):
    """Delegate to given_administrator_has_custom_domain step module"""
    context.phase = BDDPhase.GIVEN
    given_administrator_has_custom_domain.invoke(context)

@given('administrator has Cloudflare account')
def given_admin_has_cloudflare_account(context):
    """Delegate to given_administrator_has_cloudflare_account step module"""
    context.phase = BDDPhase.GIVEN
    given_administrator_has_cloudflare_account.invoke(context)

@given('tunnel is already setup and running')
def given_tunnel_already_setup_and_running(context):
    """Delegate to given_tunnel_is_already_setup step module"""
    context.phase = BDDPhase.GIVEN
    given_tunnel_is_already_setup.invoke(context)

@given('tunnel is running')
def given_tunnel_currently_running(context):
    """Delegate to given_tunnel_is_running step module"""
    context.phase = BDDPhase.GIVEN
    given_tunnel_is_running.invoke(context)

@given('system configured with multiple tunnel providers priority:')
def given_system_configured_with_multiple_providers(context, docstring):
    """Delegate to given_system_configured_with_providers step module"""
    context.phase = BDDPhase.GIVEN
    given_system_configured_with_providers.invoke(context, providers_config=docstring)

@given('no tunnel is configured')
def given_no_tunnel_configured(context):
    """Delegate to given_no_tunnel_is_configured step module"""
    context.phase = BDDPhase.GIVEN
    given_no_tunnel_is_configured.invoke(context)

# When step wrappers
@when('administrator starts server with --enable-tunnel parameter')
def when_admin_starts_server_with_tunnel_param(context):
    """Delegate to when_administrator_starts_server_with_tunnel step module"""
    context.phase = BDDPhase.WHEN
    when_administrator_starts_server_with_tunnel.invoke(context)

@when('administrator calls tunnel setup API with:')
def when_admin_calls_tunnel_setup_api(context, docstring):
    """Delegate to when_administrator_calls_tunnel_setup_api step module"""
    context.phase = BDDPhase.WHEN
    when_administrator_calls_tunnel_setup_api.invoke(context, request_body=docstring)

@when('administrator sets up custom tunnel with:')
def when_admin_sets_up_custom_tunnel(context, docstring):
    """Delegate to when_administrator_sets_up_custom_tunnel step module"""
    context.phase = BDDPhase.WHEN
    when_administrator_sets_up_custom_tunnel.invoke(context, request_body=docstring)

@when('administrator sets up Cloudflare tunnel with:')
def when_admin_sets_up_cloudflare_tunnel(context, docstring):
    """Delegate to when_administrator_sets_up_cloudflare_tunnel step module"""
    context.phase = BDDPhase.WHEN
    when_administrator_sets_up_cloudflare_tunnel.invoke(context, request_body=docstring)

@when('administrator queries tunnel status')
def when_admin_queries_tunnel_status(context):
    """Delegate to when_administrator_queries_tunnel_status step module"""
    context.phase = BDDPhase.WHEN
    when_administrator_queries_tunnel_status.invoke(context)

@when('administrator queries service endpoint')
def when_admin_queries_service_endpoint(context):
    """Delegate to when_administrator_queries_service_endpoint step module"""
    context.phase = BDDPhase.WHEN
    when_administrator_queries_service_endpoint.invoke(context)

@when('tunnel connection is interrupted')
def when_tunnel_connection_interrupted(context):
    """Delegate to when_tunnel_connection_is_interrupted step module"""
    context.phase = BDDPhase.WHEN
    when_tunnel_connection_is_interrupted.invoke(context)

@when('primary tunnel service fails')
def when_primary_tunnel_fails(context):
    """Delegate to when_primary_tunnel_service_fails step module"""
    context.phase = BDDPhase.WHEN
    when_primary_tunnel_service_fails.invoke(context)

# Then step wrappers
@then('system should automatically start ngrok tunnel')
def then_system_starts_ngrok_tunnel_automatically(context):
    """Delegate to then_system_should_start_ngrok_tunnel step module"""
    context.phase = BDDPhase.THEN
    then_system_should_start_ngrok_tunnel.invoke(context)

@then(parsers.parse('should display public URL with pattern "{pattern}"'))
def then_displays_public_url_with_pattern(context, pattern):
    """Delegate to then_should_display_public_url_pattern step module"""
    context.phase = BDDPhase.THEN
    then_should_display_public_url_pattern.invoke(context, url_pattern=pattern)

@then('API should be accessible through public URL')
def then_api_accessible_through_public_url(context):
    """Delegate to then_api_should_be_accessible step module"""
    context.phase = BDDPhase.THEN
    then_api_should_be_accessible.invoke(context)

@then('system should start specified tunnel service')
def then_system_starts_specified_tunnel_service(context):
    """Delegate to then_system_should_start_tunnel_service step module"""
    context.phase = BDDPhase.THEN
    then_system_should_start_tunnel_service.invoke(context)

@then('response should contain:')
def then_response_contains(context, docstring):
    """Delegate to then_response_should_contain step module"""
    context.phase = BDDPhase.THEN
    then_response_should_contain.invoke(context, expected_response=docstring)

@then('system should use provided URL')
def then_system_uses_provided_url(context):
    """Delegate to then_system_should_use_provided_url step module"""
    context.phase = BDDPhase.THEN
    then_system_should_use_provided_url.invoke(context)

@then('should not start any tunnel service')
def then_does_not_start_tunnel_service(context):
    """Delegate to then_should_not_start_tunnel_service step module"""
    context.phase = BDDPhase.THEN
    then_should_not_start_tunnel_service.invoke(context)

@then('install URLs should use custom domain')
def then_install_urls_use_custom_domain(context):
    """Delegate to then_install_urls_should_use_custom_domain step module"""
    context.phase = BDDPhase.THEN
    then_install_urls_should_use_custom_domain.invoke(context)

@then('system should setup Cloudflare tunnel')
def then_system_sets_up_cloudflare_tunnel(context):
    """Delegate to then_system_should_setup_cloudflare_tunnel step module"""
    context.phase = BDDPhase.THEN
    then_system_should_setup_cloudflare_tunnel.invoke(context)

@then('provide stable public URL')
def then_provides_stable_public_url(context):
    """Delegate to then_provide_stable_public_url step module"""
    context.phase = BDDPhase.THEN
    then_provide_stable_public_url.invoke(context)

@then('response should show:')
def then_response_shows(context, docstring):
    """Delegate to then_response_should_show step module"""
    context.phase = BDDPhase.THEN
    then_response_should_show.invoke(context, expected_response=docstring)

@then('system should automatically attempt reconnection')
def then_system_attempts_reconnection_automatically(context):
    """Delegate to then_system_should_attempt_reconnection step module"""
    context.phase = BDDPhase.THEN
    then_system_should_attempt_reconnection.invoke(context)

@then('if reconnection fails should:')
def then_if_reconnection_fails(context, docstring):
    """Delegate to then_if_reconnection_fails_should step module"""
    context.phase = BDDPhase.THEN
    then_if_reconnection_fails_should.invoke(context, failure_actions=docstring)

@then('system should automatically switch to next available service')
def then_system_switches_to_next_service_automatically(context):
    """Delegate to then_system_should_switch_to_next_service step module"""
    context.phase = BDDPhase.THEN
    then_system_should_switch_to_next_service.invoke(context)

@then('update all related URLs')
def then_updates_all_related_urls(context):
    """Delegate to then_update_all_related_urls step module"""
    context.phase = BDDPhase.THEN
    then_update_all_related_urls.invoke(context)

@then('response should contain service endpoint URL')
def then_response_contains_service_endpoint_url(context):
    """Delegate to then_response_should_contain_service_endpoint_url step module"""
    context.phase = BDDPhase.THEN
    then_response_should_contain_service_endpoint_url.invoke(context)

@then('response should show active provider information')
def then_response_shows_active_provider_information(context):
    """Delegate to then_response_should_show_active_provider_information step module"""
    context.phase = BDDPhase.THEN
    then_response_should_show_active_provider_information.invoke(context)

@then('response should indicate no active service endpoint')
def then_response_indicates_no_active_service_endpoint(context):
    """Delegate to then_response_should_indicate_no_active_service_endpoint step module"""
    context.phase = BDDPhase.THEN
    then_response_should_indicate_no_active_service_endpoint.invoke(context)

@then('response should show inactive status')
def then_response_shows_inactive_status(context):
    """Delegate to then_response_should_show_inactive_status step module"""
    context.phase = BDDPhase.THEN
    then_response_should_show_inactive_status.invoke(context)