from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Base declarativa para todos os modelos ORM.

    Todos os modelos devem herdar desta classe.
    """

    pass


class CategoriaMedia(Base):
    """
    Modelo ORM para a tabela categoria_media.

    Attributes:
        id: Identificador único do registro.
        categoria: Nome da categoria (único).
        preco_medio: Preço médio dos produtos da categoria.
        avaliacao_media: Avaliação média dos produtos da categoria.
        created_at: Data de criação do registro.
        updated_at: Data da última atualização.
    """

    __tablename__ = "categoria_media"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    categoria: Mapped[str] = mapped_column(nullable=False, unique=True)
    preco_medio: Mapped[float] = mapped_column(nullable=False)
    avaliacao_media: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Representação textual do modelo."""
        return (
            f"CategoriaMedia(id={self.id}, categoria='{self.categoria}', "
            f"preco_medio={self.preco_medio}, avaliacao_media={self.avaliacao_media})"
        )
