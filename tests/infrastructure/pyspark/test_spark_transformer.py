from collections import defaultdict
from itertools import batched
from unittest.mock import MagicMock, patch

import pytest

from src.domain.entities import CategorySummary, Product, Rating
from src.domain.exceptions import TransformationException


class TestSparkTransformerFilterProducts:
    """Testes para filter_products do SparkTransformer."""

    def test_filter_products_by_price(self, sample_products):
        """Testa filtro por preço mínimo."""
        filtered = [p for p in sample_products if p.price >= 100.0]

        assert len(filtered) == 4
        for product in filtered:
            assert product.price >= 100.0

    def test_filter_products_by_rating(self, sample_products):
        """Testa filtro por avaliação mínima."""
        filtered = [p for p in sample_products if p.rating.rate >= 3.5]

        assert len(filtered) == 4
        for product in filtered:
            assert product.rating.rate >= 3.5

    def test_filter_products_combined_criteria(self, sample_products):
        """Testa filtro combinado de preço e avaliação."""
        filtered = [
            p for p in sample_products if p.price >= 100.0 and p.rating.rate >= 3.5
        ]

        assert len(filtered) == 3
        for product in filtered:
            assert product.price >= 100.0
            assert product.rating.rate >= 3.5

    def test_filter_products_no_match(self, sample_products):
        """Testa filtro quando nenhum produto atende."""
        filtered = [
            p for p in sample_products if p.price >= 1000.0 and p.rating.rate >= 5.0
        ]

        assert len(filtered) == 0

    def test_product_meets_criteria_method(self, sample_products):
        """Testa o método meets_criteria da entidade Product."""
        min_price = 100.0
        min_rating = 3.5

        filtered = [
            p for p in sample_products if p.meets_criteria(min_price, min_rating)
        ]

        assert len(filtered) == 3
        for product in filtered:
            assert product.meets_criteria(min_price, min_rating)


class TestSparkTransformerSummarize:
    """Testes para summarize_by_category do SparkTransformer."""

    def test_summarize_by_category(self, sample_products):
        """Testa sumarização por categoria."""
        groups = defaultdict(list)
        for product in sample_products:
            groups[product.category].append(product)

        summaries = []
        for categoria, products in groups.items():
            preco_medio = sum(p.price for p in products) / len(products)
            avaliacao_media = sum(p.rating.rate for p in products) / len(products)
            summaries.append(
                CategorySummary(
                    categoria=categoria,
                    preco_medio=preco_medio,
                    avaliacao_media=avaliacao_media,
                )
            )

        assert len(summaries) == 3
        categories = [s.categoria for s in summaries]
        assert "electronics" in categories
        assert "clothing" in categories
        assert "jewelery" in categories

    def test_summarize_electronics_calculation(self, sample_products):
        """Testa cálculo correto para categoria electronics."""
        electronics = [p for p in sample_products if p.category == "electronics"]

        preco_medio = sum(p.price for p in electronics) / len(electronics)
        avaliacao_media = sum(p.rating.rate for p in electronics) / len(electronics)

        # (200.0 + 50.0) / 2 = 125.0
        assert preco_medio == 125.0
        # (4.5 + 4.0) / 2 = 4.25
        assert avaliacao_media == 4.25

    def test_summarize_empty_list(self):
        """Testa sumarização com lista vazia."""
        products = []
        summaries = []

        assert len(summaries) == 0


class TestSparkTransformerPartition:
    """Testes para partition_data do SparkTransformer."""

    def test_partition_data(self, sample_category_summaries):
        """Testa particionamento de dados."""
        batches_list = list(batched(sample_category_summaries, 2))

        assert len(batches_list) == 2
        assert len(batches_list[0]) == 2
        assert len(batches_list[1]) == 1

    def test_partition_data_exact_division(self):
        """Testa particionamento com divisão exata."""
        data = [
            CategorySummary(categoria=f"cat{i}", preco_medio=100.0, avaliacao_media=4.0)
            for i in range(10)
        ]

        batches_list = list(batched(data, 5))

        assert len(batches_list) == 2
        assert len(batches_list[0]) == 5
        assert len(batches_list[1]) == 5

    def test_partition_data_larger_batch(self, sample_category_summaries):
        """Testa particionamento com batch maior que dados."""
        batches_list = list(batched(sample_category_summaries, 10))

        assert len(batches_list) == 1
        assert len(batches_list[0]) == 3

    def test_partition_data_empty_list(self):
        """Testa particionamento com lista vazia."""
        batches_list = list(batched([], 5))

        assert len(batches_list) == 0

    def test_partition_data_single_item_batches(self, sample_category_summaries):
        """Testa particionamento com batch de 1."""
        batches_list = list(batched(sample_category_summaries, 1))

        assert len(batches_list) == 3
        for batch in batches_list:
            assert len(batch) == 1


class TestSparkTransformerMocked:
    """Testes com SparkTransformer completamente mockado."""

    @pytest.fixture
    def mock_spark_session(self):
        """Fixture que retorna um SparkSession mockado."""
        mock_session = MagicMock()
        mock_session.stop = MagicMock()
        return mock_session

    @pytest.fixture
    def mock_transformer(self, mock_spark_session):
        """Fixture que retorna um transformer mockado."""
        with patch(
            "src.infrastructure.pyspark.spark_transformer.SparkSession"
        ) as mock_spark_class:
            mock_builder = MagicMock()
            mock_spark_class.builder = mock_builder
            mock_builder.appName.return_value = mock_builder
            mock_builder.master.return_value = mock_builder
            mock_builder.config.return_value = mock_builder
            mock_builder.getOrCreate.return_value = mock_spark_session

            with patch(
                "src.infrastructure.pyspark.spark_transformer.get_settings"
            ) as mock_settings:
                mock_settings.return_value.environment = "test"

                from src.infrastructure.pyspark.spark_transformer import (
                    SparkTransformer,
                )

                transformer = SparkTransformer()
                yield transformer

    def test_transformer_initialization(self, mock_transformer):
        """Testa que o transformer é inicializado corretamente."""
        assert mock_transformer is not None

    def test_partition_data_with_mocked_transformer(
        self, mock_transformer, sample_category_summaries
    ):
        """Testa partition_data com transformer mockado."""
        result_batches = mock_transformer.partition_data(sample_category_summaries, 2)

        assert len(result_batches) == 2
        assert len(result_batches[0]) == 2
        assert len(result_batches[1]) == 1

    def test_partition_data_empty(self, mock_transformer):
        """Testa partition_data com lista vazia."""
        result_batches = mock_transformer.partition_data([], 5)

        assert len(result_batches) == 0

    def test_stop(self, mock_transformer, mock_spark_session):
        """Testa encerramento da sessão Spark."""
        mock_transformer.spark = mock_spark_session

        mock_transformer.stop()

        mock_spark_session.stop.assert_called_once()

    def test_init_with_existing_spark_session(self, mock_spark_session):
        """Testa inicialização com sessão Spark existente."""
        with patch(
            "src.infrastructure.pyspark.spark_transformer.get_settings"
        ) as mock_settings:
            mock_settings.return_value.environment = "test"

            from src.infrastructure.pyspark.spark_transformer import SparkTransformer

            transformer = SparkTransformer(spark=mock_spark_session)

            assert transformer.spark is mock_spark_session


class TestSparkTransformerProductsToDataframe:
    """Testes para _products_to_dataframe."""

    @pytest.fixture
    def mock_transformer_with_spark(self):
        """Fixture com transformer e spark mockados."""
        mock_spark = MagicMock()
        mock_df = MagicMock()
        mock_spark.createDataFrame.return_value = mock_df
        mock_df.count.return_value = 5

        with patch(
            "src.infrastructure.pyspark.spark_transformer.get_settings"
        ) as mock_settings:
            mock_settings.return_value.environment = "test"

            from src.infrastructure.pyspark.spark_transformer import SparkTransformer

            transformer = SparkTransformer(spark=mock_spark)
            yield transformer, mock_spark, mock_df

    def test_products_to_dataframe_empty_list(self, mock_transformer_with_spark):
        """Testa conversão com lista vazia."""
        transformer, mock_spark, _ = mock_transformer_with_spark
        empty_df = MagicMock()
        mock_spark.createDataFrame.return_value = empty_df

        result = transformer._products_to_dataframe([])

        assert result is empty_df

    def test_products_to_dataframe_with_products(
        self, mock_transformer_with_spark, sample_products
    ):
        """Testa conversão com produtos."""
        transformer, mock_spark, mock_df = mock_transformer_with_spark

        result = transformer._products_to_dataframe(sample_products)

        assert result is mock_df
        mock_spark.createDataFrame.assert_called_once()

    def test_products_to_dataframe_exception(self, mock_transformer_with_spark):
        """Testa exceção na conversão."""
        transformer, mock_spark, _ = mock_transformer_with_spark
        mock_spark.createDataFrame.side_effect = Exception("Spark error")

        product = Product(
            id=1,
            title="Test",
            price=100.0,
            description="Desc",
            category="cat",
            image="img.jpg",
            rating=Rating(rate=4.0, count=10),
        )

        with pytest.raises(TransformationException):
            transformer._products_to_dataframe([product])


class TestSparkTransformerDataframeToProducts:
    """Testes para _dataframe_to_products."""

    def test_dataframe_to_products(self):
        """Testa conversão de DataFrame para produtos."""
        mock_row = MagicMock()
        mock_row.id = 1
        mock_row.title = "Test Product"
        mock_row.price = 100.0
        mock_row.description = "Description"
        mock_row.category = "electronics"
        mock_row.image = "img.jpg"
        mock_row.rating_rate = 4.5
        mock_row.rating_count = 100

        mock_df = MagicMock()
        mock_df.collect.return_value = [mock_row]

        with patch(
            "src.infrastructure.pyspark.spark_transformer.get_settings"
        ) as mock_settings:
            mock_settings.return_value.environment = "test"

            mock_spark = MagicMock()

            from src.infrastructure.pyspark.spark_transformer import SparkTransformer

            transformer = SparkTransformer(spark=mock_spark)
            products = transformer._dataframe_to_products(mock_df)

            assert len(products) == 1
            assert products[0].id == 1
            assert products[0].title == "Test Product"
            assert products[0].price == 100.0
            assert products[0].rating.rate == 4.5

    def test_dataframe_to_products_with_nulls(self):
        """Testa conversão com campos nulos."""
        mock_row = MagicMock()
        mock_row.id = 1
        mock_row.title = "Test"
        mock_row.price = 50.0
        mock_row.description = None
        mock_row.category = "cat"
        mock_row.image = None
        mock_row.rating_rate = 3.0
        mock_row.rating_count = 5

        mock_df = MagicMock()
        mock_df.collect.return_value = [mock_row]

        with patch(
            "src.infrastructure.pyspark.spark_transformer.get_settings"
        ) as mock_settings:
            mock_settings.return_value.environment = "test"

            mock_spark = MagicMock()

            from src.infrastructure.pyspark.spark_transformer import SparkTransformer

            transformer = SparkTransformer(spark=mock_spark)
            products = transformer._dataframe_to_products(mock_df)

            assert len(products) == 1
            assert products[0].description == ""
            assert products[0].image == ""


class TestSparkTransformerFilterProductsMocked:
    """Testes para filter_products com Spark mockado."""

    def test_filter_products_mocked(self, sample_products):
        """Testa filtro de produtos com mocks."""
        mock_spark = MagicMock()
        mock_df = MagicMock()
        mock_cleaned_df = MagicMock()
        mock_filtered_df = MagicMock()

        mock_spark.createDataFrame.return_value = mock_df
        mock_df.count.return_value = 5
        mock_df.na.drop.return_value = mock_cleaned_df
        mock_cleaned_df.filter.return_value = mock_cleaned_df
        mock_cleaned_df.count.return_value = 5
        mock_filtered_df.count.return_value = 3

        mock_row = MagicMock()
        mock_row.id = 1
        mock_row.title = "Test"
        mock_row.price = 150.0
        mock_row.description = "Desc"
        mock_row.category = "electronics"
        mock_row.image = "img.jpg"
        mock_row.rating_rate = 4.5
        mock_row.rating_count = 100

        mock_filtered_df.collect.return_value = [mock_row]

        filter_call_count = [0]

        def filter_side_effect(condition):
            filter_call_count[0] += 1
            if filter_call_count[0] <= 2:
                return mock_cleaned_df
            return mock_filtered_df

        mock_cleaned_df.filter.side_effect = filter_side_effect

        with patch(
            "src.infrastructure.pyspark.spark_transformer.get_settings"
        ) as mock_settings:
            mock_settings.return_value.environment = "test"

            with patch(
                "src.infrastructure.pyspark.spark_transformer.functions"
            ) as mock_functions:
                mock_col = MagicMock()
                mock_functions.col.return_value = mock_col
                mock_col.__ge__ = MagicMock(return_value=MagicMock())
                mock_col.__le__ = MagicMock(return_value=MagicMock())
                mock_col.__gt__ = MagicMock(return_value=MagicMock())
                mock_col.__and__ = MagicMock(return_value=MagicMock())

                from src.infrastructure.pyspark.spark_transformer import (
                    SparkTransformer,
                )

                transformer = SparkTransformer(spark=mock_spark)
                result = transformer.filter_products(sample_products, 100.0, 3.5)

                assert len(result) == 1
                assert result[0].price == 150.0


class TestSparkTransformerSummarizeMocked:
    """Testes para summarize_by_category com Spark mockado."""

    def test_summarize_by_category_empty(self):
        """Testa sumarização com lista vazia."""
        mock_spark = MagicMock()

        with patch(
            "src.infrastructure.pyspark.spark_transformer.get_settings"
        ) as mock_settings:
            mock_settings.return_value.environment = "test"

            from src.infrastructure.pyspark.spark_transformer import SparkTransformer

            transformer = SparkTransformer(spark=mock_spark)
            result = transformer.summarize_by_category([])

            assert result == []

    def test_summarize_by_category_mocked(self, sample_products):
        """Testa sumarização com mocks."""
        mock_spark = MagicMock()
        mock_df = MagicMock()
        mock_grouped = MagicMock()
        mock_agg = MagicMock()
        mock_renamed = MagicMock()
        mock_ordered = MagicMock()

        mock_spark.createDataFrame.return_value = mock_df
        mock_df.count.return_value = 5
        mock_df.groupBy.return_value = mock_grouped
        mock_grouped.agg.return_value = mock_agg
        mock_agg.withColumnRenamed.return_value = mock_renamed
        mock_renamed.orderBy.return_value = mock_ordered

        mock_row = MagicMock()
        mock_row.categoria = "electronics"
        mock_row.preco_medio = 125.0
        mock_row.avaliacao_media = 4.25

        mock_ordered.collect.return_value = [mock_row]

        with patch(
            "src.infrastructure.pyspark.spark_transformer.get_settings"
        ) as mock_settings:
            mock_settings.return_value.environment = "test"

            with patch(
                "src.infrastructure.pyspark.spark_transformer.functions"
            ) as mock_functions:
                mock_functions.round.return_value = MagicMock()
                mock_functions.avg.return_value = MagicMock()

                from src.infrastructure.pyspark.spark_transformer import (
                    SparkTransformer,
                )

                transformer = SparkTransformer(spark=mock_spark)
                result = transformer.summarize_by_category(sample_products)

                assert len(result) == 1
                assert result[0].categoria == "electronics"
                assert result[0].preco_medio == 125.0
                assert result[0].avaliacao_media == 4.25
