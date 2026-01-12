import pytest
from unittest.mock import MagicMock

from src.application.extract_products import ExtractProductsUseCase
from src.domain.exceptions import APIException


class TestExtractProductsUseCase:
    """Testes para ExtractProductsUseCase."""

    def test_execute_success(self, sample_products):
        """Testa extração bem sucedida."""
        mock_repo = MagicMock()
        mock_repo.fetch_all.return_value = sample_products

        use_case = ExtractProductsUseCase(mock_repo)
        result = use_case.execute()

        assert len(result) == 5
        mock_repo.fetch_all.assert_called_once()

    def test_execute_api_error(self):
        """Testa tratamento de erro da API."""
        mock_repo = MagicMock()
        mock_repo.fetch_all.side_effect = APIException("API Error")

        use_case = ExtractProductsUseCase(mock_repo)

        with pytest.raises(APIException):
            use_case.execute()

    def test_execute_empty_result(self):
        """Testa resultado vazio."""
        mock_repo = MagicMock()
        mock_repo.fetch_all.return_value = []

        use_case = ExtractProductsUseCase(mock_repo)
        result = use_case.execute()

        assert len(result) == 0
