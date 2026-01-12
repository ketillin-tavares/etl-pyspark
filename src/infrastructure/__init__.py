"""
Módulo de infraestrutura.

Contém as implementações concretas das interfaces do domínio.
"""

from src.infrastructure.api.api_client import FakeStoreAPIClient
from src.infrastructure.database.connection import Database, get_database
from src.infrastructure.database.models import Base, CategoriaMedia
from src.infrastructure.database.repository import PostgreSQLRepository
from src.infrastructure.pyspark.spark_transformer import SparkTransformer

__all__ = [
    "FakeStoreAPIClient",
    "Database",
    "get_database",
    "Base",
    "CategoriaMedia",
    "PostgreSQLRepository",
    "SparkTransformer",
]
