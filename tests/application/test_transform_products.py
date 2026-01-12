import pytest
from unittest.mock import MagicMock, patch

from src.application.transform_products import TransformProductsUseCase
from src.domain.entities import CategorySummary
from src.domain.exceptions import TransformationException


class TestTransformProductsUseCase:
    """Testes para TransformProductsUseCase."""

    def test_execute_success(self, sample_products, mock_settings):
        """Testa transformação bem sucedida."""
        mock_transformer = MagicMock()
        mock_transformer.filter_products.return_value = sample_products[:3]
        mock_transformer.summarize_by_category.return_value = [
            CategorySummary(categoria="test", preco_medio=100.0, avaliacao_media=4.0)
        ]

        with patch("src.application.transform_products.get_settings") as mock:
            mock.return_value = mock_settings
            use_case = TransformProductsUseCase(mock_transformer)
            filtered, summaries = use_case.execute(sample_products)

        assert len(filtered) == 3
        assert len(summaries) == 1
        mock_transformer.filter_products.assert_called_once()
        mock_transformer.summarize_by_category.assert_called_once()

    def test_execute_with_custom_criteria(self, sample_products, mock_settings):
        """Testa transformação com critérios customizados."""
        mock_transformer = MagicMock()
        mock_transformer.filter_products.return_value = []
        mock_transformer.summarize_by_category.return_value = []

        with patch("src.application.transform_products.get_settings") as mock:
            mock.return_value = mock_settings
            use_case = TransformProductsUseCase(mock_transformer)
            use_case.execute(sample_products, min_price=200.0, min_rating=4.5)

        mock_transformer.filter_products.assert_called_once_with(
            sample_products, 200.0, 4.5
        )

    def test_execute_transformation_error(self, sample_products, mock_settings):
        """Testa tratamento de erro de transformação."""
        mock_transformer = MagicMock()
        mock_transformer.filter_products.side_effect = TransformationException("Error")

        with patch("src.application.transform_products.get_settings") as mock:
            mock.return_value = mock_settings
            use_case = TransformProductsUseCase(mock_transformer)

            with pytest.raises(TransformationException):
                use_case.execute(sample_products)
