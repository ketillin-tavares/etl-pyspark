from typing import List

from loguru import logger

from src.domain.entities import Product
from src.domain.exceptions import APIException
from src.domain.interfaces import ProductRepositoryInterface


class ExtractProductsUseCase:
    """
    Caso de uso para extração de produtos da API.

    Responsável por buscar todos os produtos da FakeStore API.
    """

    def __init__(self, product_repository: ProductRepositoryInterface) -> None:
        """
        Inicializa o caso de uso.

        Args:
            product_repository: Repositório de produtos.
        """
        self._repository = product_repository

    def execute(self) -> List[Product]:
        """
        Executa a extração de produtos.

        Returns:
            Lista de produtos obtidos.

        Raises:
            APIException: Em caso de erro na extração.
        """
        logger.info("Iniciando extração de produtos")

        try:
            products = self._repository.fetch_all()
            logger.info(f"Extração concluída: {len(products)} produtos")
            return products

        except APIException:
            raise
        except Exception as e:
            logger.error(f"Erro inesperado na extração: {e}")
            raise APIException(f"Erro na extração: {e}") from e
