import os
import pytest
from src.config import Config


@pytest.fixture(autouse=True)
def clean_env():
    """Fixture to save and restore environment variables, ensuring tests don't affect each other."""
    original_env = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(original_env)


def test_config_from_env():
    os.environ['ANTHROPIC_API_KEY'] = 'test-key'
    os.environ['OPENROUTER_API_KEY'] = 'test-openrouter-key'
    os.environ['OLLAMA_API_BASE'] = 'http://localhost:11434'

    config = Config.load_from_env()

    assert config.anthropic_api_key == 'test-key'
    assert config.openrouter_api_key == 'test-openrouter-key'
    assert config.ollama_api_base == 'http://localhost:11434'
    assert config.has_ai_enabled() is True


def test_get_active_provider_with_configured_provider():
    os.environ['AI_REVIEW_PROVIDER'] = 'claude'
    os.environ['ANTHROPIC_API_KEY'] = 'test-key'

    config = Config.load_from_env()
    assert config.get_active_provider() == 'claude'


def test_get_active_provider_auto_detect_claude():
    os.environ['ANTHROPIC_API_KEY'] = 'test-key'

    config = Config.load_from_env()
    assert config.get_active_provider() == 'claude'


def test_get_active_provider_auto_detect_openrouter():
    os.environ['OPENROUTER_API_KEY'] = 'test-key'

    config = Config.load_from_env()
    assert config.get_active_provider() == 'openrouter'


def test_get_active_provider_auto_detect_ollama():
    os.environ['OLLAMA_API_BASE'] = 'http://custom-ollama:11434'
    config = Config.load_from_env()
    assert config.get_active_provider() == 'ollama'


def test_ollama_api_base_default_value():
    config = Config.load_from_env()
    assert config.ollama_api_base == 'http://localhost:11434'


def test_environment_variables_not_set():
    config = Config.load_from_env()
    assert config.anthropic_api_key is None
    assert config.openrouter_api_key is None
    assert config.ai_provider is None
    assert config.has_ai_enabled() is False
    assert config.get_active_provider() is None


def test_invalid_ollama_api_base():
    os.environ['OLLAMA_API_BASE'] = 'invalid-url'
    with pytest.raises(ValueError):
        Config.load_from_env()


def test_valid_ollama_api_base():
    os.environ['OLLAMA_API_BASE'] = 'https://api.ollama.example.com'
    config = Config.load_from_env()
    assert config.ollama_api_base == 'https://api.ollama.example.com'