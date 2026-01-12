import pytest
from unittest.mock import MagicMock, patch

from src.domain.entities import CategorySummary, Product, Rating


@pytest.fixture
def sample_rating() -> Rating:
    """
    Fixture que retorna uma avaliação de exemplo.

    Returns:
        Objeto Rating com dados de teste.
    """
    return Rating(rate=4.5, count=100)


@pytest.fixture
def sample_product(sample_rating: Rating) -> Product:
    """
    Fixture que retorna um produto de exemplo.

    Args:
        sample_rating: Fixture de avaliação.

    Returns:
        Objeto Product com dados de teste.
    """
    return Product(
        id=1,
        title="Test Product",
        price=150.0,
        description="A test product description",
        category="electronics",
        image="https://example.com/image.jpg",
        rating=sample_rating,
    )


@pytest.fixture
def sample_products() -> list[Product]:
    """
    Fixture que retorna uma lista de produtos de exemplo.

    Returns:
        Lista de produtos para testes.
    """
    return [
        Product(
            id=1,
            title="Expensive Electronics",
            price=200.0,
            description="High-end electronic device",
            category="electronics",
            image="https://example.com/1.jpg",
            rating=Rating(rate=4.5, count=100),
        ),
        Product(
            id=2,
            title="Cheap Electronics",
            price=50.0,
            description="Budget electronic device",
            category="electronics",
            image="https://example.com/2.jpg",
            rating=Rating(rate=4.0, count=50),
        ),
        Product(
            id=3,
            title="Premium Clothing",
            price=150.0,
            description="High quality clothing",
            category="clothing",
            image="https://example.com/3.jpg",
            rating=Rating(rate=4.8, count=200),
        ),
        Product(
            id=4,
            title="Low Rated Jewelry",
            price=500.0,
            description="Expensive jewelry",
            category="jewelery",
            image="https://example.com/4.jpg",
            rating=Rating(rate=2.5, count=10),
        ),
        Product(
            id=5,
            title="Quality Jewelry",
            price=300.0,
            description="Quality jewelry item",
            category="jewelery",
            image="https://example.com/5.jpg",
            rating=Rating(rate=4.0, count=75),
        ),
    ]


@pytest.fixture
def sample_category_summaries() -> list[CategorySummary]:
    """
    Fixture que retorna resumos de categoria de exemplo.

    Returns:
        Lista de resumos de categoria para testes.
    """
    return [
        CategorySummary(
            categoria="electronics",
            preco_medio=125.0,
            avaliacao_media=4.25,
        ),
        CategorySummary(
            categoria="clothing",
            preco_medio=150.0,
            avaliacao_media=4.8,
        ),
        CategorySummary(
            categoria="jewelery",
            preco_medio=400.0,
            avaliacao_media=3.25,
        ),
    ]


@pytest.fixture
def mock_settings():
    """
    Fixture que retorna settings mockados.

    Returns:
        Mock das configurações.
    """
    mock = MagicMock()
    mock.environment = "development"
    mock.api.base_url = "https://fakestoreapi.com"
    mock.api.timeout = 30
    mock.api.max_retries = 3
    mock.database.connection_url = "postgresql://test:test@localhost:5432/test"
    mock.database.host = "localhost"
    mock.database.port = 5432
    mock.database.user = "test"
    mock.database.password = "test"
    mock.database.db = "test"
    mock.pipeline.batch_size = 5
    mock.pipeline.min_price = 100.0
    mock.pipeline.min_rating = 3.5
    return mock


@pytest.fixture
def mock_api_response() -> list[dict]:
    """
    Fixture que retorna uma resposta mockada da API.

    Returns:
        Lista de dicionários simulando a resposta da API.
    """
    return [
        {
            "id": 1,
            "title": "Test Product 1",
            "price": 150.0,
            "description": "Description 1",
            "category": "electronics",
            "image": "https://example.com/1.jpg",
            "rating": {"rate": 4.5, "count": 100},
        },
        {
            "id": 2,
            "title": "Test Product 2",
            "price": 75.0,
            "description": "Description 2",
            "category": "clothing",
            "image": "https://example.com/2.jpg",
            "rating": {"rate": 3.0, "count": 50},
        },
    ]
