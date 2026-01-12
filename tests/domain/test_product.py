import pytest
from pydantic import ValidationError

from src.domain.entities import Product


class TestProduct:
    """Testes para a entidade Product."""

    def test_product_valid(self, sample_rating):
        """Testa criação de produto válido."""
        product = Product(
            id=1,
            title="Test Product",
            price=99.99,
            description="A description",
            category="electronics",
            image="https://example.com/img.jpg",
            rating=sample_rating,
        )

        assert product.id == 1
        assert product.title == "Test Product"
        assert product.price == 99.99
        assert product.category == "electronics"

    def test_product_price_cannot_be_negative(self, sample_rating):
        """Testa que preço negativo gera erro."""
        with pytest.raises(ValidationError):
            Product(
                id=1,
                title="Test",
                price=-10.0,
                description="Desc",
                category="cat",
                image="img.jpg",
                rating=sample_rating,
            )

    def test_product_meets_criteria_true(self, sample_product):
        """Testa critério quando produto atende."""
        assert sample_product.meets_criteria(min_price=100.0, min_rating=3.5)

    def test_product_meets_criteria_false_price(self, sample_product):
        """Testa critério quando preço não atende."""
        assert not sample_product.meets_criteria(min_price=200.0, min_rating=3.5)

    def test_product_meets_criteria_false_rating(self, sample_product):
        """Testa critério quando avaliação não atende."""
        assert not sample_product.meets_criteria(min_price=100.0, min_rating=5.0)

    def test_product_with_rating_dict(self):
        """Testa criação de produto com rating como dicionário."""
        product = Product(
            id=1,
            title="Test",
            price=100.0,
            description="Desc",
            category="cat",
            image="img.jpg",
            rating={"rate": 4.0, "count": 50},
        )

        assert product.rating.rate == 4.0
        assert product.rating.count == 50
