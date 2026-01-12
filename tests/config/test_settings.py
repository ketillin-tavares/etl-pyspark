import pytest
from pydantic import ValidationError

from src.config.settings import (
    APISettings,
    DatabaseSettings,
    PipelineSettings,
    Settings,
    get_settings,
)


class TestAPISettings:
    def test_api_settings_with_env_vars(self, monkeypatch):
        """Testa criação de APISettings com variáveis de ambiente."""
        monkeypatch.setenv("API_BASE_URL", "https://api.example.com")
        monkeypatch.setenv("API_TIMEOUT", "60")
        monkeypatch.setenv("API_MAX_RETRIES", "5")

        settings = APISettings()

        assert settings.base_url == "https://api.example.com"
        assert settings.timeout == 60
        assert settings.max_retries == 5

    def test_api_settings_default_values(self, monkeypatch):
        """Testa valores padrão de APISettings."""
        monkeypatch.setenv("API_BASE_URL", "https://api.example.com")

        settings = APISettings()

        assert settings.timeout == 30
        assert settings.max_retries == 3

    def test_api_settings_missing_required(self, monkeypatch):
        """Testa que base_url é obrigatório."""
        monkeypatch.delenv("API_BASE_URL", raising=False)

        with pytest.raises(ValidationError):
            APISettings()


class TestDatabaseSettings:
    """Testes para DatabaseSettings."""

    def test_database_settings_with_env_vars(self, monkeypatch):
        """Testa criação de DatabaseSettings com variáveis de ambiente."""
        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_PORT", "5432")
        monkeypatch.setenv("DB_USER", "testuser")
        monkeypatch.setenv("DB_PASSWORD", "testpass")
        monkeypatch.setenv("DB_NAME", "testdb")

        settings = DatabaseSettings()

        assert settings.host == "localhost"
        assert settings.port == 5432
        assert settings.user == "testuser"
        assert settings.password == "testpass"
        assert settings.database == "testdb"

    def test_connection_url_property(self, monkeypatch):
        """Testa a propriedade connection_url."""
        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_PORT", "5432")
        monkeypatch.setenv("DB_USER", "user")
        monkeypatch.setenv("DB_PASSWORD", "pass")
        monkeypatch.setenv("DB_NAME", "mydb")

        settings = DatabaseSettings()

        assert settings.connection_url == "postgresql://user:pass@localhost:5432/mydb"

    def test_database_settings_default_port(self, monkeypatch):
        """Testa valor padrão da porta."""
        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_USER", "user")
        monkeypatch.setenv("DB_PASSWORD", "pass")
        monkeypatch.setenv("DB_NAME", "mydb")

        settings = DatabaseSettings()

        assert settings.port == 5432

    def test_database_settings_missing_required(self, monkeypatch):
        """Testa que campos obrigatórios geram erro."""
        monkeypatch.delenv("DB_HOST", raising=False)
        monkeypatch.delenv("DB_USER", raising=False)
        monkeypatch.delenv("DB_PASSWORD", raising=False)
        monkeypatch.delenv("DB_NAME", raising=False)

        with pytest.raises(ValidationError):
            DatabaseSettings()


class TestPipelineSettings:
    """Testes para PipelineSettings."""

    def test_pipeline_settings_with_env_vars(self, monkeypatch):
        """Testa criação de PipelineSettings com variáveis de ambiente."""
        monkeypatch.setenv("PIPELINE_BATCH_SIZE", "10")
        monkeypatch.setenv("PIPELINE_MIN_PRICE", "150.0")
        monkeypatch.setenv("PIPELINE_MIN_RATING", "4.0")

        settings = PipelineSettings()

        assert settings.batch_size == 10
        assert settings.min_price == 150.0
        assert settings.min_rating == 4.0

    def test_pipeline_settings_default_values(self):
        """Testa valores padrão de PipelineSettings."""
        settings = PipelineSettings()

        assert settings.batch_size == 5
        assert settings.min_price == 100.0
        assert settings.min_rating == 3.5


class TestSettings:
    """Testes para Settings principal."""

    def test_settings_with_env_vars(self, monkeypatch):
        """Testa criação de Settings com variáveis de ambiente."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("API_BASE_URL", "https://api.example.com")
        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_USER", "user")
        monkeypatch.setenv("DB_PASSWORD", "pass")
        monkeypatch.setenv("DB_NAME", "testdb")

        settings = Settings()

        assert settings.environment == "production"
        assert settings.api.base_url == "https://api.example.com"
        assert settings.database.host == "localhost"

    def test_settings_missing_environment(self, monkeypatch):
        """Testa que environment é obrigatório."""
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        monkeypatch.setenv("API_BASE_URL", "https://api.example.com")
        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_USER", "user")
        monkeypatch.setenv("DB_PASSWORD", "pass")
        monkeypatch.setenv("DB_NAME", "testdb")

        with pytest.raises(ValidationError):
            Settings()


class TestGetSettings:
    """Testes para a função get_settings."""

    def test_get_settings_returns_settings(self, monkeypatch):
        """Testa que get_settings retorna instância de Settings."""
        monkeypatch.setenv("ENVIRONMENT", "test")
        monkeypatch.setenv("API_BASE_URL", "https://api.test.com")
        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_USER", "user")
        monkeypatch.setenv("DB_PASSWORD", "pass")
        monkeypatch.setenv("DB_NAME", "testdb")

        # Limpar cache do lru_cache
        get_settings.cache_clear()

        settings = get_settings()

        assert isinstance(settings, Settings)
        assert settings.environment == "test"

    def test_get_settings_is_cached(self, monkeypatch):
        """Testa que get_settings usa cache."""
        monkeypatch.setenv("ENVIRONMENT", "test")
        monkeypatch.setenv("API_BASE_URL", "https://api.test.com")
        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_USER", "user")
        monkeypatch.setenv("DB_PASSWORD", "pass")
        monkeypatch.setenv("DB_NAME", "testdb")

        # Limpar cache
        get_settings.cache_clear()

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2
