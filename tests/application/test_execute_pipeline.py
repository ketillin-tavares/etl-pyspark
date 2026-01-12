from unittest.mock import MagicMock, patch

import pytest

from src.application.execute_pipeline import ExecutePipelineUseCase
from src.domain.exceptions import APIException, TransactionException


@pytest.fixture(autouse=True)
def mock_settings():
    """Mock das configurações para todos os testes."""
    mock_pipeline_settings = MagicMock()
    mock_pipeline_settings.batch_size = 5
    mock_pipeline_settings.min_price = 100.0
    mock_pipeline_settings.min_rating = 3.5

    mock_settings_obj = MagicMock()
    mock_settings_obj.pipeline = mock_pipeline_settings

    with patch(
        "src.application.load_data.get_settings", return_value=mock_settings_obj
    ):
        with patch(
            "src.application.transform_products.get_settings",
            return_value=mock_settings_obj,
        ):
            yield mock_settings_obj


class TestExecutePipelineUseCase:
    """Testes para ExecutePipelineUseCase."""

    def test_execute_full_pipeline_success(
        self, sample_products, sample_category_summaries
    ):
        """Testa execução completa do pipeline."""
        mock_product_repo = MagicMock()
        mock_product_repo.fetch_all.return_value = sample_products

        mock_category_repo = MagicMock()
        mock_category_repo.save_all_with_transaction.return_value = True

        mock_transformer = MagicMock()
        mock_transformer.filter_products.return_value = sample_products[:3]
        mock_transformer.summarize_by_category.return_value = sample_category_summaries
        mock_transformer.partition_data.return_value = [sample_category_summaries]

        use_case = ExecutePipelineUseCase(
            mock_product_repo,
            mock_category_repo,
            mock_transformer,
        )

        result = use_case.execute()

        assert result.success is True
        assert result.total_products_fetched == 5
        assert result.filtered_products_count == 3
        assert result.categories_count == 3
        assert result.batches_count == 1
        assert result.error_message is None

    def test_execute_pipeline_api_failure(self):
        """Testa falha na extração."""
        mock_product_repo = MagicMock()
        mock_product_repo.fetch_all.side_effect = APIException("API Error")

        mock_category_repo = MagicMock()
        mock_transformer = MagicMock()

        use_case = ExecutePipelineUseCase(
            mock_product_repo,
            mock_category_repo,
            mock_transformer,
        )

        result = use_case.execute()

        assert result.success is False
        assert "API Error" in result.error_message

    def test_execute_pipeline_transaction_failure(
        self, sample_products, sample_category_summaries
    ):
        """Testa falha na persistência."""
        mock_product_repo = MagicMock()
        mock_product_repo.fetch_all.return_value = sample_products

        mock_category_repo = MagicMock()
        mock_category_repo.save_all_with_transaction.side_effect = TransactionException(
            "Transaction failed"
        )

        mock_transformer = MagicMock()
        mock_transformer.filter_products.return_value = sample_products
        mock_transformer.summarize_by_category.return_value = sample_category_summaries
        mock_transformer.partition_data.return_value = [sample_category_summaries]

        use_case = ExecutePipelineUseCase(
            mock_product_repo,
            mock_category_repo,
            mock_transformer,
        )

        result = use_case.execute()

        assert result.success is False
        assert "Transaction failed" in result.error_message
