from loguru import logger

from src.application.extract_products import ExtractProductsUseCase
from src.application.load_data import LoadDataUseCase
from src.application.transform_products import TransformProductsUseCase
from src.domain.entities import PipelineResult
from src.domain.exceptions import DomainException
from src.domain.interfaces import (
    CategorySummaryRepositoryInterface,
    DataTransformerInterface,
    ProductRepositoryInterface,
)


class ExecutePipelineUseCase:
    """
    Caso de uso principal para execução do pipeline completo.

    Orquestra a extração, transformação e carregamento de dados
    conforme especificado no desafio técnico.
    """

    def __init__(
        self,
        product_repository: ProductRepositoryInterface,
        category_repository: CategorySummaryRepositoryInterface,
        transformer: DataTransformerInterface,
    ) -> None:
        """
        Inicializa o caso de uso.

        Args:
            product_repository: Repositório para buscar produtos.
            category_repository: Repositório para salvar resumos.
            transformer: Transformador de dados.
        """
        self._extract_use_case = ExtractProductsUseCase(product_repository)
        self._transform_use_case = TransformProductsUseCase(transformer)
        self._load_use_case = LoadDataUseCase(category_repository, transformer)

    def execute(self) -> PipelineResult:
        """
        Executa o pipeline completo ETL.

        Etapas:
        1. Extração: Busca produtos da FakeStore API
        2. Transformação: Filtra e sumariza por categoria
        3. Carregamento: Persiste no PostgreSQL

        Returns:
            Resultado da execução do pipeline.
        """

        try:
            logger.info("\n[ETAPA 1/3] EXTRAÇÃO DE DADOS")
            products = self._extract_use_case.execute()

            logger.info("\n[ETAPA 2/3] TRANSFORMAÇÃO DE DADOS")
            filtered_products, summaries = self._transform_use_case.execute(products)

            logger.info("\n[ETAPA 3/3] CARREGAMENTO DE DADOS")
            batches_count = self._load_use_case.execute(summaries)

            result = PipelineResult(
                success=True,
                total_products_fetched=len(products),
                filtered_products_count=len(filtered_products),
                categories_count=len(summaries),
                batches_count=batches_count,
            )

            logger.info("PIPELINE CONCLUÍDO COM SUCESSO")
            logger.info(f"Produtos extraídos: {result.total_products_fetched}")
            logger.info(f"Produtos após filtro: {result.filtered_products_count}")
            logger.info(f"Categorias sumarizadas: {result.categories_count}")
            logger.info(f"Lotes processados: {result.batches_count}")

            return result

        except DomainException as e:
            logger.error(f"Pipeline falhou: {e.message}")
            return PipelineResult(
                success=False,
                error_message=e.message,
            )

        except Exception as e:
            logger.error(f"Erro inesperado no Pipeline: {e}")
            return PipelineResult(
                success=False,
                error_message=str(e),
            )
