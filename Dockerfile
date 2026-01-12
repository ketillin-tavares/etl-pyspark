FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    JAVA_HOME=/usr/lib/jvm/default-java \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Instalar Java, curl e dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jdk-headless \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Instalar UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Criar diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências primeiro
COPY pyproject.toml uv.lock ./

# Instalar dependências (sem dev)
RUN uv sync --frozen --no-dev --no-install-project

# Copiar código fonte
COPY . .

# Instalar o projeto
RUN uv sync --frozen --no-dev

# Criar usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

USER appuser

# Comando padrão
CMD ["uv", "run", "python", "-m", "src.main"]
