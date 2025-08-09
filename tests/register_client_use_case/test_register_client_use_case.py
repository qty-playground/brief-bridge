"""Step wrapper file for Register Client Use Case - delegates to individual step modules"""
from pytest_bdd import scenarios, given, when, then, parsers
from conftest import BDDPhase

# Import step modules
from . import given_client_exists_in_repository
from . import given_no_client_exists
from . import given_no_preconditions
from . import when_execute_client_registration
from . import then_registration_should_be_successful
from . import then_registration_should_fail
from . import then_registration_response_should_contain
from . import then_client_should_be_saved_in_repository
from . import then_repository_should_contain_updated_client
from . import then_no_client_should_be_saved_in_repository

# Load all scenarios from feature file
scenarios('story.feature')

# GIVEN Step Wrappers - delegate to individual step modules
@given(parsers.parse('no client exists with id "{client_id}"'))
def given_no_client_exists_with_id(context, client_id):
    """Delegate to given_no_client_exists step module"""
    # Set GIVEN phase and input state before delegating
    context.phase = BDDPhase.GIVEN
    context.client_id = client_id
    given_no_client_exists.invoke(context)


@given(parsers.parse('client "{client_id}" exists in repository with:'))
def given_client_exists_in_repository_with_data(context, client_id, docstring):
    """Delegate to given_client_exists_in_repository step module"""
    # Set GIVEN phase and input state before delegating
    context.phase = BDDPhase.GIVEN
    context.client_id = client_id
    context.client_data = docstring
    given_client_exists_in_repository.invoke(context)


@given('no preconditions')
def given_no_preconditions_needed(context):
    """Delegate to given_no_preconditions step module"""
    # Set GIVEN phase before delegating
    context.phase = BDDPhase.GIVEN
    given_no_preconditions.invoke(context)


# WHEN Step Wrappers - delegate to individual step modules
@when('I execute client registration with:')
def when_execute_client_registration_with_data(context, docstring):
    """Delegate to when_execute_client_registration step module"""
    # Set WHEN phase and execution data before delegating
    context.phase = BDDPhase.WHEN
    context.request_body = docstring
    when_execute_client_registration.invoke(context)


# THEN Step Wrappers - delegate to individual step modules
@then('registration should be successful')
def then_registration_was_successful(context):
    """Delegate to then_registration_should_be_successful step module"""
    # Set THEN phase before delegating
    context.phase = BDDPhase.THEN
    then_registration_should_be_successful.invoke(context)


@then('registration should fail')
def then_registration_has_failed(context):
    """Delegate to then_registration_should_fail step module"""
    # Set THEN phase before delegating
    context.phase = BDDPhase.THEN
    then_registration_should_fail.invoke(context)


@then('registration response should contain:')
def then_registration_response_contains_expected_data(context, docstring):
    """Delegate to then_registration_response_should_contain step module"""
    # Set THEN phase and verification data before delegating
    context.phase = BDDPhase.THEN
    context.expected_response_body = docstring
    then_registration_response_should_contain.invoke(context)


@then('client should be saved in repository with:')
def then_client_was_saved_in_repository_with_data(context, docstring):
    """Delegate to then_client_should_be_saved_in_repository step module"""
    # Set THEN phase and verification data before delegating
    context.phase = BDDPhase.THEN
    context.expected_client_data = docstring
    then_client_should_be_saved_in_repository.invoke(context)


@then('repository should contain updated client with:')
def then_repository_contains_updated_client_with_data(context, docstring):
    """Delegate to then_repository_should_contain_updated_client step module"""
    # Set THEN phase and verification data before delegating
    context.phase = BDDPhase.THEN
    context.expected_client_data = docstring
    then_repository_should_contain_updated_client.invoke(context)


@then('no client should be saved in repository')
def then_no_client_was_saved_in_repository(context):
    """Delegate to then_no_client_should_be_saved_in_repository step module"""
    # Set THEN phase before delegating
    context.phase = BDDPhase.THEN
    then_no_client_should_be_saved_in_repository.invoke(context)