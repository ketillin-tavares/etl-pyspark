from contextlib import contextmanager
from typing import Generator, Optional

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from src.config.settings import get_settings
from src.domain.exceptions import DatabaseException


class Database:
    """
    Gerenciador de conexão com o banco de dados.

    Implementa o padrão Singleton para garantir uma única
    instância de engine por aplicação.

    Attributes:
        engine: Engine do SQLAlchemy.
        session_factory: Factory para criação de sessões.
    """

    _instance: Optional["Database"] = None

    def __new__(cls, connection_url: Optional[str] = None) -> "Database":
        """
        Cria ou retorna a instância singleton.

        Args:
            connection_url: URL de conexão opcional.

        Returns:
            Instância única do Database.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, connection_url: Optional[str] = None) -> None:
        """
        Inicializa a conexão com o banco.

        Args:
            connection_url: URL de conexão (usa config se não fornecido).
        """
        if self._initialized:
            return

        settings = get_settings()
        url = connection_url or settings.database.connection_url

        self.engine: Engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=settings.environment == "development",
        )

        self.session_factory = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

        self._initialized = True
        logger.info(f"Conexão com banco inicializada: {settings.database.host}")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Gerenciador de contexto para sessões.

        Fornece uma sessão com commit/rollback automático.

        Yields:
            Sessão do SQLAlchemy.

        Raises:
            DatabaseException: Em caso de erro na sessão.
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
            logger.debug("Sessão commitada com sucesso")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Erro na sessão, rollback executado: {e}")
            raise DatabaseException(f"Erro no banco de dados: {e}") from e
        finally:
            session.close()

    def close(self) -> None:
        """
        Fecha a conexão com o banco.

        Libera os recursos da engine e reseta o singleton.
        """
        if hasattr(self, "engine"):
            self.engine.dispose()
            logger.debug("Conexão com banco fechada")

        Database._instance = None
        self._initialized = False


def get_database(connection_url: Optional[str] = None) -> Database:
    """
    Obtém a instância do banco de dados.

    Args:
        connection_url: URL de conexão opcional.

    Returns:
        Instância do Database.
    """
    return Database(connection_url)
