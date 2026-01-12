from abc import ABC, abstractmethod
from typing import List

from src.domain.entities import CategorySummary, Product


class ProductRepositoryInterface(ABC):
    """
    Interface para repositório de produtos.

    Define o contrato para operações de acesso a dados
    relacionados a produtos.
    """

    @abstractmethod
    def fetch_all(self) -> List[Product]:
        """
        Busca todos os produtos disponíveis.

        Returns:
            Lista de produtos.

        Raises:
            APIException: Em caso de erro na comunicação com a API.
        """
        pass


class CategorySummaryRepositoryInterface(ABC):
    """
    Interface para repositório de resumo de categorias.

    Define o contrato para operações de persistência
    dos dados sumarizados por categoria.
    """

    @abstractmethod
    def save_all_with_transaction(self, batches: List[List[CategorySummary]]) -> bool:
        """
        Salva todos os lotes dentro de uma única transação.

        Se qualquer lote falhar, toda a operação é revertida.

        Args:
            batches: Lista de lotes de resumos.

        Returns:
            True se salvou todos com sucesso.

        Raises:
            TransactionException: Em caso de falha, reverte tudo.
        """
        pass


class DataTransformerInterface(ABC):
    """
    Interface para transformador de dados.

    Define o contrato para operações de transformação
    utilizando PySpark.
    """

    @abstractmethod
    def filter_products(
        self, products: List[Product], min_price: float, min_rating: float
    ) -> List[Product]:
        """
        Filtra produtos baseado nos critérios especificados.

        Args:
            products: Lista de produtos a filtrar.
            min_price: Preço mínimo.
            min_rating: Avaliação mínima.

        Returns:
            Lista de produtos filtrados.
        """
        pass

    @abstractmethod
    def summarize_by_category(self, products: List[Product]) -> List[CategorySummary]:
        """
        Sumariza os produtos por categoria.

        Args:
            products: Lista de produtos para sumarizar.

        Returns:
            Lista de resumos por categoria.
        """
        pass

    @abstractmethod
    def partition_data(
        self, data: List[CategorySummary], batch_size: int
    ) -> List[List[CategorySummary]]:
        """
        Particiona os dados em lotes menores.

        Args:
            data: Dados a serem particionados.
            batch_size: Tamanho de cada lote.

        Returns:
            Lista de lotes.
        """
        pass
