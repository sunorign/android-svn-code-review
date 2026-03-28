import os
import pytest
from src.config import Config, JsonConfigLoader


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


def test_json_config_loader_loads_config():
    """Test that JsonConfigLoader can load config from JSON file."""
    config = JsonConfigLoader.load()
    assert config.ai_provider == 'openrouter'
    assert config.api_timeout == 60
    assert config.openrouter_api_key is not None
    assert len(config.openrouter_api_key) > 0
    assert config.openrouter_model == 'minimax/minimax-m2.5'
    assert config.anthropic_max_tokens == 4096
    assert config.has_ai_enabled() is True


def test_json_config_loader_with_custom_path():
    """Test loading config from a custom path (should fail if file not exists)."""
    with pytest.raises(FileNotFoundError):
        JsonConfigLoader.load('invalid/path/to/config.json')


def test_load_with_fallback():
    """Test load_with_fallback handles missing JSON file."""
    # Should fallback to environment variables if JSON doesn't exist
    os.environ['OPENROUTER_API_KEY'] = 'custom-key'
    os.environ['AI_REVIEW_PROVIDER'] = 'openrouter'

    config = JsonConfigLoader.load_with_fallback('invalid/path/to/config.json')
    assert config.openrouter_api_key == 'custom-key'
    assert config.ai_provider == 'openrouter'
    assert config.has_ai_enabled() is True


def test_openrouter_http_referer_field():
    """Test that openrouter_http_referer field is properly initialized."""
    # Test JSON loading
    config = JsonConfigLoader.load()
    assert isinstance(config.openrouter_http_referer, str)

    # Test environment variable loading
    os.environ['OPENROUTER_HTTP_REFERER'] = 'https://example.com'
    config = Config.load_from_env()
    assert config.openrouter_http_referer == 'https://example.com'


def test_load_from_env_default_provider():
    """Test that default provider is openrouter when no environment variable is set."""
    config = Config.load_from_env()
    assert config.ai_provider == 'openrouter'