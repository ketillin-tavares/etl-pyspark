from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001_create_categoria_media"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Cria a tabela categoria_media.

    Campos:
    - id: Identificador único autoincremental
    - categoria: Nome da categoria (único)
    - preco_medio: Média de preços da categoria
    - avaliacao_media: Média de avaliações da categoria
    - created_at: Data de criação do registro
    - updated_at: Data da última atualização
    """
    op.create_table(
        "categoria_media",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("categoria", sa.String(length=255), nullable=False),
        sa.Column("preco_medio", sa.Float(), nullable=False),
        sa.Column("avaliacao_media", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("categoria"),
    )

    op.create_index(
        "ix_categoria_media_categoria",
        "categoria_media",
        ["categoria"],
        unique=True,
    )


def downgrade() -> None:
    """
    Remove a tabela categoria_media.
    """
    op.drop_index("ix_categoria_media_categoria", table_name="categoria_media")
    op.drop_table("categoria_media")
