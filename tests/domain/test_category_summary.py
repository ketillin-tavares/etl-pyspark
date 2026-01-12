import pytest
from pydantic import ValidationError

from src.domain.entities import CategorySummary


class TestCategorySummary:
    """Testes para a entidade CategorySummary."""

    def test_category_summary_valid(self):
        """Testa criação de resumo válido."""
        summary = CategorySummary(
            categoria="electronics",
            preco_medio=150.50,
            avaliacao_media=4.25,
        )

        assert summary.categoria == "electronics"
        assert summary.preco_medio == 150.50
        assert summary.avaliacao_media == 4.25

    def test_category_summary_preco_cannot_be_negative(self):
        """Testa que preço médio negativo gera erro."""
        with pytest.raises(ValidationError):
            CategorySummary(
                categoria="test",
                preco_medio=-10.0,
                avaliacao_media=4.0,
            )

    def test_category_summary_avaliacao_max_5(self):
        """Testa que avaliação máxima é 5."""
        with pytest.raises(ValidationError):
            CategorySummary(
                categoria="test",
                preco_medio=100.0,
                avaliacao_media=5.5,
            )
