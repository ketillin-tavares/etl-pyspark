import pytest
from pydantic import ValidationError

from src.domain.entities import PipelineResult


class TestPipelineResult:
    """Testes para a entidade PipelineResult."""

    def test_pipeline_result_success(self):
        """Testa criação de resultado de sucesso."""
        result = PipelineResult(
            success=True,
            total_products_fetched=20,
            filtered_products_count=10,
            categories_count=4,
            batches_count=2,
        )

        assert result.success is True
        assert result.total_products_fetched == 20
        assert result.filtered_products_count == 10
        assert result.categories_count == 4
        assert result.batches_count == 2
        assert result.error_message is None

    def test_pipeline_result_failure(self):
        """Testa criação de resultado de falha."""
        result = PipelineResult(
            success=False,
            error_message="Pipeline error occurred",
        )

        assert result.success is False
        assert result.total_products_fetched == 0
        assert result.filtered_products_count == 0
        assert result.categories_count == 0
        assert result.batches_count == 0
        assert result.error_message == "Pipeline error occurred"

    def test_pipeline_result_default_values(self):
        """Testa valores padrão do resultado."""
        result = PipelineResult(success=True)

        assert result.success is True
        assert result.total_products_fetched == 0
        assert result.filtered_products_count == 0
        assert result.categories_count == 0
        assert result.batches_count == 0
        assert result.error_message is None

    def test_pipeline_result_negative_products_fetched(self):
        """Testa que total_products_fetched não pode ser negativo."""
        with pytest.raises(ValidationError):
            PipelineResult(
                success=True,
                total_products_fetched=-1,
            )

    def test_pipeline_result_negative_filtered_count(self):
        """Testa que filtered_products_count não pode ser negativo."""
        with pytest.raises(ValidationError):
            PipelineResult(
                success=True,
                filtered_products_count=-1,
            )

    def test_pipeline_result_negative_categories_count(self):
        """Testa que categories_count não pode ser negativo."""
        with pytest.raises(ValidationError):
            PipelineResult(
                success=True,
                categories_count=-1,
            )

    def test_pipeline_result_negative_batches_count(self):
        """Testa que batches_count não pode ser negativo."""
        with pytest.raises(ValidationError):
            PipelineResult(
                success=True,
                batches_count=-1,
            )
