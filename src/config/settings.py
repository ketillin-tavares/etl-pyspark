from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv(".env", override=True)


class APISettings(BaseSettings):
    """Configurações da API FakeStore."""

    base_url: str = Field(
        ...,
        description="URL base da API FakeStore",
        validation_alias="API_BASE_URL",
    )
    timeout: int = Field(
        30, description="Timeout em segundos", validation_alias="API_TIMEOUT"
    )
    max_retries: int = Field(
        3,
        description="Número máximo de retries",
        validation_alias="API_MAX_RETRIES",
    )


class DatabaseSettings(BaseSettings):
    """Configurações do banco de dados PostgreSQL."""

    host: str = Field(..., description="Host do PostgreSQL", validation_alias="DB_HOST")
    port: int = Field(
        5432, description="Porta do PostgreSQL", validation_alias="DB_PORT"
    )
    user: str = Field(
        ..., description="Usuário do PostgreSQL", validation_alias="DB_USER"
    )
    password: str = Field(
        ..., description="Senha do PostgreSQL", validation_alias="DB_PASSWORD"
    )
    database: str = Field(
        ..., description="Nome do banco de dados", validation_alias="DB_NAME"
    )

    @property
    def connection_url(self) -> str:
        """
        Retorna a URL de conexão do banco de dados.

        Returns:
            String de conexão formatada para SQLAlchemy.
        """
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class PipelineSettings(BaseSettings):
    """Configurações do pipeline ETL."""

    batch_size: int = Field(
        5,
        description="Tamanho do batch para particionamento",
        validation_alias="PIPELINE_BATCH_SIZE",
    )
    min_price: float = Field(
        100.0,
        description="Preço mínimo para filtro",
        validation_alias="PIPELINE_MIN_PRICE",
    )
    min_rating: float = Field(
        3.5,
        description="Avaliação mínima para filtro",
        validation_alias="PIPELINE_MIN_RATING",
    )


class Settings(BaseSettings):
    """Configurações principais da aplicação."""

    environment: str = Field(
        ...,
        description="Ambiente de execução",
        validation_alias="ENVIRONMENT",
    )
    api: APISettings = Field(default_factory=APISettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    pipeline: PipelineSettings = Field(default_factory=PipelineSettings)


@lru_cache
def get_settings() -> Settings:
    return Settings()
