from typing import Optional

from pydantic import BaseModel, Field


class Rating(BaseModel):
    """
    Modelo que representa a avaliação de um produto.

    Attributes:
        rate: Nota média do produto (0 a 5).
        count: Número de avaliações recebidas.
    """

    rate: float = Field(ge=0, le=5, description="Nota média do produto")
    count: int = Field(ge=0, description="Número de avaliações")


class Product(BaseModel):
    """
    Modelo que representa um produto da FakeStore API.

    Attributes:
        id: Identificador único do produto.
        title: Título/nome do produto.
        price: Preço do produto.
        description: Descrição detalhada.
        category: Categoria do produto.
        image: URL da imagem do produto.
        rating: Objeto com dados de avaliação.
    """

    id: int = Field(description="ID único do produto")
    title: str = Field(description="Título do produto")
    price: float = Field(ge=0, description="Preço do produto")
    description: str = Field(description="Descrição do produto")
    category: str = Field(description="Categoria do produto")
    image: str = Field(description="URL da imagem")
    rating: Rating = Field(description="Dados de avaliação")

    def meets_criteria(self, min_price: float, min_rating: float) -> bool:
        """
        Verifica se o produto atende aos critérios de filtro.

        Args:
            min_price: Preço mínimo exigido.
            min_rating: Avaliação mínima exigida.

        Returns:
            True se o produto atende aos critérios, False caso contrário.
        """
        return self.price >= min_price and self.rating.rate >= min_rating


class CategorySummary(BaseModel):
    """
    Modelo que representa o resumo estatístico de uma categoria.

    Contém os dados agregados por categoria conforme especificado
    no desafio técnico.

    Attributes:
        categoria: Nome da categoria.
        preco_medio: Média dos preços dos produtos da categoria.
        avaliacao_media: Média das avaliações da categoria.
    """

    categoria: str = Field(description="Nome da categoria")
    preco_medio: float = Field(ge=0, description="Média de preços")
    avaliacao_media: float = Field(ge=0, le=5, description="Média de avaliações")


class PipelineResult(BaseModel):
    """
    Resultado da execução do pipeline.

    Attributes:
        success: Indica se o pipeline foi executado com sucesso.
        total_products_fetched: Total de produtos obtidos da API.
        filtered_products_count: Quantidade após filtros.
        categories_count: Número de categorias sumarizadas.
        batches_count: Número de lotes processados.
        error_message: Mensagem de erro, se houver.
    """

    success: bool = Field(description="Indica se o pipeline foi executado com sucesso")
    total_products_fetched: int = Field(
        default=0, ge=0, description="Total de produtos obtidos da API"
    )
    filtered_products_count: int = Field(
        default=0, ge=0, description="Quantidade após filtros"
    )
    categories_count: int = Field(
        default=0, ge=0, description="Número de categorias sumarizadas"
    )
    batches_count: int = Field(
        default=0, ge=0, description="Número de lotes processados"
    )
    error_message: Optional[str] = Field(
        default=None, description="Mensagem de erro, se existir"
    )
