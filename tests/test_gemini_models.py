import pytest
from unittest.mock import patch, MagicMock
from engage.app.gemini_models import get_gemini_model, generation_config, safety_settings
from google.genai import types

@pytest.fixture
def mock_gemini_class():
    """Fixture to mock the Gemini class."""
    with patch('engage.app.gemini_models.Gemini') as mock:
        yield mock

@pytest.fixture
def mock_google_auth_default():
    """Fixture to mock google.auth.default."""
    with patch('engage.app.gemini_models.google.auth.default') as mock:
        mock.return_value = (MagicMock(), "mock-project-id")
        yield mock

def test_get_gemini_model_with_api_key(mock_gemini_class, mock_google_auth_default):
    """
    Test that get_gemini_model correctly initializes Gemini with an API key.
    """
    config = {
        "gemini_api_key": "test_api_key",
        "model": {"model_name": "gemini-pro"},
    }

    model = get_gemini_model(config)

    mock_gemini_class.assert_called_once_with(
        id="gemini-pro",
        vertexai=False,
        api_key="test_api_key",
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    assert model == mock_gemini_class.return_value
    mock_google_auth_default.assert_not_called()

def test_get_gemini_model_with_vertex_ai_default_location(mock_gemini_class, mock_google_auth_default):
    """
    Test that get_gemini_model correctly initializes Gemini with Vertex AI
    using default location.
    """
    config = {
        "gemini_api_key": None, # or omit this key
        "model": {"model_name": "gemini-1.0-pro"},
    }

    model = get_gemini_model(config)

    mock_google_auth_default.assert_called_once()
    mock_gemini_class.assert_called_once_with(
        id="gemini-1.0-pro",
        vertexai=True,
        project_id="mock-project-id",
        location="us-central1",
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    assert model == mock_gemini_class.return_value

def test_get_gemini_model_with_vertex_ai_custom_location(mock_gemini_class, mock_google_auth_default):
    """
    Test that get_gemini_model correctly initializes Gemini with Vertex AI
    using a custom location.
    """
    config = {
        "gemini_api_key": "", # or omit this key
        "model": {"model_name": "gemini-1.5-pro"},
        "location": "europe-west1",
    }

    model = get_gemini_model(config)

    mock_google_auth_default.assert_called_once()
    mock_gemini_class.assert_called_once_with(
        id="gemini-1.5-pro",
        vertexai=True,
        project_id="mock-project-id",
        location="europe-west1",
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    assert model == mock_gemini_class.return_value

def test_get_gemini_model_config_without_api_key_field(mock_gemini_class, mock_google_auth_default):
    """
    Test that get_gemini_model defaults to Vertex AI if 'gemini_api_key' field is missing.
    """
    config = {
        "model": {"model_name": "gemini-pro-vision"},
    }

    model = get_gemini_model(config)

    mock_google_auth_default.assert_called_once()
    mock_gemini_class.assert_called_once_with(
        id="gemini-pro-vision",
        vertexai=True,
        project_id="mock-project-id",
        location="us-central1",
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    assert model == mock_gemini_class.return_value
