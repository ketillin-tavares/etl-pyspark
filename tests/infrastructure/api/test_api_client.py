import pytest
import responses
from unittest.mock import patch

from src.domain.entities import Product
from src.domain.exceptions import APIException
from src.infrastructure.api.api_client import FakeStoreAPIClient


class TestFakeStoreAPIClient:
    """Testes para o cliente FakeStoreAPIClient."""

    @pytest.fixture
    def api_client(self, mock_settings):
        """
        Fixture que retorna um cliente da API mockado.

        Args:
            mock_settings: Settings mockados.

        Returns:
            Instância do cliente.
        """
        with patch("src.infrastructure.api.api_client.get_settings") as mock:
            mock.return_value = mock_settings
            client = FakeStoreAPIClient(
                base_url="https://fakestoreapi.com",
                timeout=30,
                max_retries=3,
            )
            yield client
            client.close()

    @responses.activate
    def test_fetch_all_success(self, api_client, mock_api_response):
        """Testa busca de todos os produtos com sucesso."""
        responses.add(
            responses.GET,
            "https://fakestoreapi.com/products",
            json=mock_api_response,
            status=200,
        )

        products = api_client.fetch_all()

        assert len(products) == 2
        assert isinstance(products[0], Product)
        assert products[0].id == 1
        assert products[0].title == "Test Product 1"
        assert products[0].price == 150.0

    @responses.activate
    def test_fetch_all_empty_response(self, api_client):
        """Testa busca quando API retorna lista vazia."""
        responses.add(
            responses.GET,
            "https://fakestoreapi.com/products",
            json=[],
            status=200,
        )

        products = api_client.fetch_all()

        assert len(products) == 0

    @responses.activate
    def test_fetch_all_http_error(self, api_client):
        """Testa tratamento de erro HTTP."""
        responses.add(
            responses.GET,
            "https://fakestoreapi.com/products",
            json={"error": "Server error"},
            status=500,
        )

        with pytest.raises(APIException) as exc_info:
            api_client.fetch_all()

        assert exc_info.value.status_code == 500

    @responses.activate
    def test_fetch_all_not_found(self, api_client):
        """Testa tratamento de erro 404."""
        responses.add(
            responses.GET,
            "https://fakestoreapi.com/products",
            json={"error": "Not found"},
            status=404,
        )

        with pytest.raises(APIException) as exc_info:
            api_client.fetch_all()

        assert exc_info.value.status_code == 404

    def test_client_initialization(self, mock_settings):
        """Testa inicialização do cliente."""
        with patch("src.infrastructure.api.api_client.get_settings") as mock:
            mock.return_value = mock_settings
            client = FakeStoreAPIClient()

            assert client.base_url == "https://fakestoreapi.com"
            assert client.timeout == 30
            assert client.max_retries == 3

            client.close()
