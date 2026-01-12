import pytest
from unittest.mock import MagicMock, patch

from sqlalchemy.exc import SQLAlchemyError

from src.domain.exceptions import TransactionException
from src.infrastructure.database.repository import PostgreSQLRepository
from src.infrastructure.database.connection import Database


class TestPostgreSQLRepository:
    """Testes para PostgreSQLRepository."""

    @pytest.fixture
    def mock_database(self):
        """Fixture para Database mockado."""
        db = MagicMock(spec=Database)
        db.session_factory = MagicMock()
        return db

    @pytest.fixture
    def mock_session(self):
        """Fixture para sessão mockada."""
        session = MagicMock()
        session.commit = MagicMock()
        session.rollback = MagicMock()
        session.close = MagicMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def repository(self, mock_database, mock_session):
        """
        Fixture para repositório com dependências mockadas.

        Args:
            mock_database: Database mockado.
            mock_session: Sessão mockada.

        Returns:
            Instância do repositório.
        """
        mock_database.session_factory.return_value = mock_session

        with patch(
            "src.infrastructure.database.repository.get_database",
            return_value=mock_database,
        ):
            repo = PostgreSQLRepository(database=mock_database)
            yield repo

    def test_save_all_with_transaction_success(
        self, repository, mock_session, sample_category_summaries
    ):
        """Testa salvamento com transação única."""
        batches = [
            sample_category_summaries[:2],
            sample_category_summaries[2:],
        ]

        result = repository.save_all_with_transaction(batches)

        assert result is True
        mock_session.commit.assert_called_once()
        mock_session.rollback.assert_not_called()

    def test_save_all_with_transaction_rollback_on_error(
        self, repository, mock_session, sample_category_summaries
    ):
        """Testa rollback em caso de erro."""
        mock_session.add.side_effect = SQLAlchemyError("DB Error")

        batches = [sample_category_summaries]

        with pytest.raises(TransactionException):
            repository.save_all_with_transaction(batches)

        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()

    def test_save_all_with_transaction_empty_batches(self, repository):
        """Testa transação com batches vazios."""
        result = repository.save_all_with_transaction([])

        assert result is True

    def test_close(self, repository, mock_database):
        """Testa fechamento da conexão."""
        repository.close()

        mock_database.close.assert_called_once()
