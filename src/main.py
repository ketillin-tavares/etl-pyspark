import sys

from loguru import logger

from src.application.execute_pipeline import ExecutePipelineUseCase
from src.config.settings import get_settings
from src.infrastructure.api.api_client import FakeStoreAPIClient
from src.infrastructure.database.repository import PostgreSQLRepository
from src.infrastructure.pyspark.spark_transformer import SparkTransformer


def main() -> int:
    """
    Função principal do pipeline.

    Configura os componentes e executa o pipeline ETL completo.

    Returns:
        Código de saída (0 para sucesso, 1 para erro).
    """
    api_client = None
    repository = None
    transformer = None

    try:
        api_client = FakeStoreAPIClient()
        repository = PostgreSQLRepository()
        transformer = SparkTransformer()

        use_case = ExecutePipelineUseCase(
            product_repository=api_client,
            category_repository=repository,
            transformer=transformer,
        )

        result = use_case.execute()

        if result.success:
            logger.info("Pipeline executado com sucesso!")
            return 0
        else:
            logger.error(f"Pipeline falhou: {result.error_message}")
            return 1

    except Exception as e:
        logger.exception(f"Erro no pipeline: {e}")
        return 1

    finally:
        if api_client:
            api_client.close()
        if repository:
            repository.close()
        if transformer:
            transformer.stop()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
