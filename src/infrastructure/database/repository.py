from typing import List, Optional

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from src.domain.entities import CategorySummary
from src.domain.exceptions import TransactionException
from src.domain.interfaces import CategorySummaryRepositoryInterface
from src.infrastructure.database.connection import Database, get_database
from src.infrastructure.database.models import CategoriaMedia


class PostgreSQLRepository(CategorySummaryRepositoryInterface):
    """
    Repositório para operações no PostgreSQL.

    Implementa a persistência dos resumos de categoria
    com suporte completo a transações.

    Attributes:
        database: Instância do gerenciador de banco de dados.
    """

    def __init__(self, database: Optional[Database] = None) -> None:
        """
        Inicializa o repositório.

        Args:
            database: Instância do Database (usa singleton se não fornecido).
        """
        self.database = database or get_database()
        logger.info("Repositório PostgreSQL inicializado")

    def save_all_with_transaction(self, batches: List[List[CategorySummary]]) -> bool:
        """
        Salva todos os lotes em uma única transação.

        Se qualquer lote falhar, toda a operação é revertida.
        Isso garante a consistência dos dados conforme especificado.

        Args:
            batches: Lista de lotes.

        Returns:
            True se todos foram salvos com sucesso.

        Raises:
            TransactionException: Em caso de falha, reverte tudo.
        """
        if not batches:
            logger.warning("Nenhum lote para salvar")
            return True

        total_records = sum(len(batch) for batch in batches)
        logger.info(
            f"Iniciando transação para {len(batches)} lotes ({total_records} registros)"
        )

        session = self.database.session_factory()

        try:
            for batch_index, batch in enumerate(batches):
                logger.debug(f"Processando lote {batch_index + 1}/{len(batches)}")

                for summary in batch:
                    model = CategoriaMedia(
                        categoria=summary.categoria,
                        preco_medio=summary.preco_medio,
                        avaliacao_media=summary.avaliacao_media,
                    )
                    session.add(model)

            session.commit()
            logger.info(f"Transação concluída: {total_records} registros salvos")
            return True

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Erro na transação, rollback executado: {e}")
            raise TransactionException(
                f"Falha na transação. Todos os dados foram revertidos: {e}"
            ) from e

        finally:
            session.close()

    def close(self) -> None:
        """
        Fecha a conexão com o banco.

        Deve ser chamado ao finalizar o uso do repositório.
        """
        self.database.close()
        logger.debug("Repositório fechado")
