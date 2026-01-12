from typing import List, Optional

from loguru import logger

from src.config.settings import get_settings
from src.domain.entities import CategorySummary, Product
from src.domain.exceptions import TransformationException
from src.domain.interfaces import DataTransformerInterface


class TransformProductsUseCase:
    """
    Caso de uso para transformação de produtos.

    Responsável por filtrar e sumarizar produtos por categoria.
    """

    def __init__(self, transformer: DataTransformerInterface) -> None:
        """
        Inicializa o caso de uso.

        Args:
            transformer: Transformador de dados.
        """
        self._transformer = transformer
        self._settings = get_settings()

    def execute(
        self,
        products: List[Product],
        min_price: Optional[float] = None,
        min_rating: Optional[float] = None,
    ) -> tuple[List[Product], List[CategorySummary]]:
        """
        Executa a transformação de produtos.

        Aplica filtros e gera sumarização por categoria.

        Args:
            products: Lista de produtos a processar.
            min_price: Preço mínimo (usa config se não fornecido).
            min_rating: Avaliação mínima (usa config se não fornecido).

        Returns:
            Tupla com produtos filtrados e resumos por categoria.

        Raises:
            TransformationException: Em caso de erro no processamento.
        """
        price = min_price or self._settings.pipeline.min_price
        rating = min_rating or self._settings.pipeline.min_rating

        logger.info(f"Iniciando transformação: {len(products)} produtos")
        logger.info(f"Critérios: preço >= {price}, avaliação >= {rating}")

        try:
            filtered_products = self._transformer.filter_products(
                products, price, rating
            )

            summaries = self._transformer.summarize_by_category(filtered_products)

            logger.info(
                f"Transformação concluída: {len(filtered_products)} produtos, "
                f"{len(summaries)} categorias"
            )

            return filtered_products, summaries

        except TransformationException:
            raise
        except Exception as e:
            logger.error(f"Erro inesperado na transformação: {e}")
            raise TransformationException(f"Erro na transformação: {e}") from e
