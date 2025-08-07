import pytest
from pytest_bdd import scenarios

# Import all step definitions
from . import given_steps
from . import when_steps
from . import then_steps

# Load all scenarios from feature file
scenarios('story.feature')
