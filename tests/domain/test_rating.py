import pytest
from pydantic import ValidationError

from src.domain.entities import Rating


class TestRating:
    """Testes para a entidade Rating."""

    def test_rating_valid(self):
        """Testa criação de rating válido."""
        rating = Rating(rate=4.5, count=100)

        assert rating.rate == 4.5
        assert rating.count == 100

    def test_rating_min_values(self):
        """Testa valores mínimos permitidos."""
        rating = Rating(rate=0, count=0)

        assert rating.rate == 0
        assert rating.count == 0

    def test_rating_max_value(self):
        """Testa valor máximo permitido para rate."""
        rating = Rating(rate=5.0, count=1000)

        assert rating.rate == 5.0

    def test_rating_invalid_rate_above_max(self):
        """Testa que rate acima de 5 gera erro."""
        with pytest.raises(ValidationError):
            Rating(rate=5.1, count=10)

    def test_rating_invalid_rate_below_min(self):
        """Testa que rate negativo gera erro."""
        with pytest.raises(ValidationError):
            Rating(rate=-0.1, count=10)

    def test_rating_invalid_count_negative(self):
        """Testa que count negativo gera erro."""
        with pytest.raises(ValidationError):
            Rating(rate=4.0, count=-1)
