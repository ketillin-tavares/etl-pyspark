from typing import List, Optional

from loguru import logger

from src.config.settings import get_settings
from src.domain.entities import CategorySummary
from src.domain.exceptions import TransactionException
from src.domain.interfaces import (
    CategorySummaryRepositoryInterface,
    DataTransformerInterface,
)


class LoadDataUseCase:
    """
    Caso de uso para carregamento de dados no banco.

    Responsável por particionar e persistir os dados
    com controle de transação.
    """

    def __init__(
        self,
        repository: CategorySummaryRepositoryInterface,
        transformer: DataTransformerInterface,
    ) -> None:
        """
        Inicializa o caso de uso.

        Args:
            repository: Repositório para persistência.
            transformer: Transformador para particionamento.
        """
        self._repository = repository
        self._transformer = transformer
        self._settings = get_settings()

    def execute(
        self,
        summaries: List[CategorySummary],
        batch_size: Optional[int] = None,
    ) -> int:
        """
        Executa o carregamento de dados.

        Particiona os dados e persiste com controle de transação.
        Se qualquer lote falhar, toda a operação é revertida.

        Args:
            summaries: Resumos a serem salvos.
            batch_size: Tamanho do lote (usa config se não fornecido).

        Returns:
            Número de lotes processados.

        Raises:
            TransactionException: Em caso de falha na persistência.
        """
        size = batch_size or self._settings.pipeline.batch_size

        logger.info(f"Iniciando carregamento: {len(summaries)} registros")
        logger.info(f"Tamanho do lote: {size}")

        try:
            batches = self._transformer.partition_data(summaries, size)

            if not batches:
                logger.warning("Nenhum dado para carregar")
                return 0

            self._repository.save_all_with_transaction(batches)

            logger.info(f"Carregamento concluído: {len(batches)} lotes")
            return len(batches)

        except TransactionException:
            raise
        except Exception as e:
            logger.error(f"Erro inesperado no carregamento: {e}")
            raise TransactionException(f"Erro no carregamento: {e}") from e
