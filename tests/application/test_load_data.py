import pytest
from unittest.mock import MagicMock, patch

from src.application.load_data import LoadDataUseCase
from src.domain.exceptions import TransactionException


class TestLoadDataUseCase:
    """Testes para LoadDataUseCase."""

    def test_execute_success(self, sample_category_summaries, mock_settings):
        """Testa carregamento bem sucedido."""
        mock_repo = MagicMock()
        mock_repo.save_all_with_transaction.return_value = True

        mock_transformer = MagicMock()
        mock_transformer.partition_data.return_value = [
            sample_category_summaries[:2],
            sample_category_summaries[2:],
        ]

        with patch("src.application.load_data.get_settings") as mock:
            mock.return_value = mock_settings
            use_case = LoadDataUseCase(mock_repo, mock_transformer)
            batches = use_case.execute(sample_category_summaries)

        assert batches == 2
        mock_repo.save_all_with_transaction.assert_called_once()

    def test_execute_empty_data(self, mock_settings):
        """Testa carregamento com dados vazios."""
        mock_repo = MagicMock()
        mock_transformer = MagicMock()
        mock_transformer.partition_data.return_value = []

        with patch("src.application.load_data.get_settings") as mock:
            mock.return_value = mock_settings
            use_case = LoadDataUseCase(mock_repo, mock_transformer)
            batches = use_case.execute([])

        assert batches == 0
        mock_repo.save_all_with_transaction.assert_not_called()

    def test_execute_transaction_error(self, sample_category_summaries, mock_settings):
        """Testa rollback em caso de erro."""
        mock_repo = MagicMock()
        mock_repo.save_all_with_transaction.side_effect = TransactionException("Error")

        mock_transformer = MagicMock()
        mock_transformer.partition_data.return_value = [sample_category_summaries]

        with patch("src.application.load_data.get_settings") as mock:
            mock.return_value = mock_settings
            use_case = LoadDataUseCase(mock_repo, mock_transformer)

            with pytest.raises(TransactionException):
                use_case.execute(sample_category_summaries)
