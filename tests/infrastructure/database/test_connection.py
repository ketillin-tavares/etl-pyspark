from unittest.mock import MagicMock, patch

from src.infrastructure.database.connection import Database


class TestDatabaseConnection:
    """Testes para a classe Database."""

    def test_singleton_pattern(self):
        """Testa que Database implementa singleton."""
        with patch("src.infrastructure.database.connection.create_engine"):
            with patch(
                "src.infrastructure.database.connection.get_settings"
            ) as mock_settings:
                mock_settings.return_value.database.connection_url = "postgresql://test"
                mock_settings.return_value.environment = "test"

                # Resetar singleton para teste
                Database._instance = None

                db1 = Database()
                db2 = Database()

                assert db1 is db2

                # Cleanup
                Database._instance = None

    def test_get_session_context_manager(self):
        """Testa o context manager de sessão."""
        with patch("src.infrastructure.database.connection.create_engine"):
            with patch(
                "src.infrastructure.database.connection.get_settings"
            ) as mock_settings:
                mock_settings.return_value.database.connection_url = "postgresql://test"
                mock_settings.return_value.environment = "test"

                # Resetar singleton
                Database._instance = None

                db = Database()

                mock_session = MagicMock()
                db.session_factory = MagicMock(return_value=mock_session)

                with db.get_session() as session:
                    assert session is mock_session

                mock_session.commit.assert_called_once()
                mock_session.close.assert_called_once()

                # Cleanup
                Database._instance = None
