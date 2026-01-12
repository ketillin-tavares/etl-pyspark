from itertools import batched
from typing import List, Optional

from loguru import logger
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

from src.config.settings import get_settings
from src.domain.entities import CategorySummary, Product
from src.domain.exceptions import TransformationException
from src.domain.interfaces import DataTransformerInterface


class SparkTransformer(DataTransformerInterface):
    """
    Transformador de dados utilizando PySpark.

    Implementa as operações de ETL especificadas no desafio,
    incluindo filtros, agregações e particionamento.

    Attributes:
        spark: Sessão Spark.
        settings: Configurações do pipeline.
    """

    # Schema do produto para criação do DataFrame
    PRODUCT_SCHEMA = StructType(
        [
            StructField("id", IntegerType(), False),
            StructField("title", StringType(), False),
            StructField("price", DoubleType(), False),
            StructField("description", StringType(), True),
            StructField("category", StringType(), False),
            StructField("image", StringType(), True),
            StructField("rating_rate", DoubleType(), False),
            StructField("rating_count", IntegerType(), False),
        ]
    )

    def __init__(self, spark: Optional[SparkSession] = None):
        """
        Inicializa o transformador.

        Args:
            spark: Sessão Spark existente (cria uma nova se não fornecida).
        """
        self.settings = get_settings()

        if spark:
            self.spark = spark
        else:
            self.spark = self._create_spark_session()

        logger.info("SparkTransformer inicializado")

    def _create_spark_session(self) -> SparkSession:
        """
        Cria uma nova sessão Spark.

        Returns:
            Sessão Spark configurada.
        """
        logger.info("Criando sessão Spark")

        spark = (
            SparkSession.builder.appName("FKE-Pipeline")
            .master("local[*]")
            .config("spark.driver.memory", "2g")
            .config("spark.sql.shuffle.partitions", "4")
            .config("spark.ui.enabled", "false")
            .getOrCreate()
        )

        spark.sparkContext.setLogLevel("WARN")

        logger.info("Sessão Spark criada com sucesso")
        return spark

    def _products_to_dataframe(self, products: List[Product]) -> DataFrame:
        """
        Converte lista de produtos para DataFrame Spark.

        Args:
            products: Lista de produtos.

        Returns:
            DataFrame Spark com os produtos.

        Raises:
            TransformationException: Em caso de erro na conversão.
        """
        if not products:
            logger.warning("Lista de produtos vazia")
            return self.spark.createDataFrame([], self.PRODUCT_SCHEMA)

        try:
            data = [
                (
                    product.id,
                    product.title,
                    float(product.price),
                    product.description,
                    product.category,
                    product.image,
                    float(product.rating.rate),
                    product.rating.count,
                )
                for product in products
            ]

            df = self.spark.createDataFrame(data, self.PRODUCT_SCHEMA)
            logger.debug(f"DataFrame criado com {df.count()} registros")

            return df

        except Exception as e:
            logger.error(f"Erro ao converter produtos para DataFrame: {e}")
            raise TransformationException(f"Erro na conversão: {e}")

    def _dataframe_to_products(self, df: DataFrame) -> List[Product]:
        """
        Converte DataFrame Spark para lista de produtos.

        Args:
            df: DataFrame com dados de produtos.

        Returns:
            Lista de produtos.
        """
        rows = df.collect()

        products = [
            Product(
                id=row.id,
                title=row.title,
                price=row.price,
                description=row.description or "",
                category=row.category,
                image=row.image or "",
                rating={"rate": row.rating_rate, "count": row.rating_count},
            )
            for row in rows
        ]

        return products

    def filter_products(
        self,
        products: List[Product],
        min_price: float,
        min_rating: float,
    ) -> List[Product]:
        """
        Filtra produtos baseado nos critérios especificados.

        Aplica os filtros:
        - Preço >= min_price
        - Avaliação >= min_rating

        Também realiza limpeza de dados removendo nulos e inconsistências.

        Args:
            products: Lista de produtos a filtrar.
            min_price: Preço mínimo (default do desafio: 100.0).
            min_rating: Avaliação mínima (default do desafio: 3.5).

        Returns:
            Lista de produtos filtrados.
        """
        logger.info(
            f"Filtrando produtos: preço >= {min_price}, avaliação >= {min_rating}"
        )

        df = self._products_to_dataframe(products)
        initial_count = df.count()

        # Limpeza: remover nulos
        df_cleaned = df.na.drop(subset=["id", "price", "category", "rating_rate"])

        # Limpeza: remover outliers (preços negativos ou zerados)
        df_cleaned = df_cleaned.filter(functions.col("price") > 0)

        # Limpeza: remover avaliações inválidas
        df_cleaned = df_cleaned.filter(
            (functions.col("rating_rate") >= 0) & (functions.col("rating_rate") <= 5)
        )

        cleaned_count = df_cleaned.count()
        logger.info(f"Após limpeza: {cleaned_count}/{initial_count} produtos")

        # Aplicar filtros do desafio
        df_filtered = df_cleaned.filter(
            (functions.col("price") >= min_price)
            & (functions.col("rating_rate") >= min_rating)
        )

        filtered_count = df_filtered.count()
        logger.info(f"Após filtros: {filtered_count}/{cleaned_count} produtos")

        return self._dataframe_to_products(df_filtered)

    def summarize_by_category(self, products: List[Product]) -> List[CategorySummary]:
        """
        Sumariza os produtos por categoria.

        Cria um DataFrame com:
        - categoria: nome distinto da categoria
        - preco_medio: média do campo price
        - avaliacao_media: média das avaliações

        Args:
            products: Lista de produtos para sumarizar.

        Returns:
            Lista de resumos por categoria.
        """
        logger.info("Sumarizando produtos por categoria")

        if not products:
            logger.warning("Nenhum produto para sumarizar")
            return []

        df = self._products_to_dataframe(products)

        # Agrupar por categoria e calcular médias
        df_summary = (
            df.groupBy("category")
            .agg(
                functions.round(functions.avg("price"), 2).alias("preco_medio"),
                functions.round(functions.avg("rating_rate"), 2).alias(
                    "avaliacao_media"
                ),
            )
            .withColumnRenamed("category", "categoria")
            .orderBy("categoria")
        )

        # Converter para lista de CategorySummary
        rows = df_summary.collect()

        summaries = [
            CategorySummary(
                categoria=row.categoria,
                preco_medio=row.preco_medio,
                avaliacao_media=row.avaliacao_media,
            )
            for row in rows
        ]

        logger.info(f"Gerados {len(summaries)} resumos de categoria")

        for summary in summaries:
            logger.debug(
                f"  {summary.categoria}: preço={summary.preco_medio}, "
                f"avaliação={summary.avaliacao_media}"
            )

        return summaries

    def partition_data(
        self,
        data: List[CategorySummary],
        batch_size: int,
    ) -> List[List[CategorySummary]]:
        """
        Particiona os dados em lotes menores.

        Divide os dados em lotes do tamanho especificado
        para facilitar o processamento e inserção no banco.

        Args:
            data: Dados a serem particionados.
            batch_size: Tamanho de cada lote (default do desafio: 5).

        Returns:
            Lista de lotes.
        """
        if not data:
            logger.warning("Nenhum dado para particionar")
            return []

        batches = list(batched(data, batch_size))

        logger.info(
            f"Dados particionados em {len(batches)} lotes de até {batch_size} registros"
        )

        return batches

    def stop(self) -> None:
        """
        Encerra a sessão Spark.

        Deve ser chamado ao finalizar o uso do transformador
        para liberar recursos.
        """
        if self.spark:
            self.spark.stop()
            logger.info("Sessão Spark encerrada")
