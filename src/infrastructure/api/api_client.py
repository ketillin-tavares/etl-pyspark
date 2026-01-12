from typing import Any, Dict, List, Optional

import requests
from loguru import logger
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from src.config.settings import get_settings
from src.domain.entities import Product
from src.domain.exceptions import APIException
from src.domain.interfaces import ProductRepositoryInterface


class FakeStoreAPIClient(ProductRepositoryInterface):
    """
    Cliente para comunicação com a FakeStore API.

    Implementa o repositório de produtos utilizando a API externa
    como fonte de dados, com suporte a retry automático.

    Attributes:
        base_url: URL base da API.
        timeout: Timeout para requisições.
        max_retries: Número máximo de tentativas.
        session: Sessão HTTP reutilizável.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        """
        Inicializa o cliente da API.

        Args:
            base_url: URL base da API (usa config se não fornecido).
            timeout: Timeout em segundos (usa config se não fornecido).
            max_retries: Máximo de retries (usa config se não fornecido).
        """
        settings = get_settings()

        self.base_url = base_url or settings.api.base_url
        self.timeout = timeout or settings.api.timeout
        self.max_retries = max_retries or settings.api.max_retries
        self.session = requests.Session()
        self._token: Optional[str] = None

        logger.info(f"Cliente FakeStore API inicializado: {self.base_url}")

    def _get_retry_decorator(self):
        """
        Retorna o decorator de retry configurado.

        Returns:
            Decorator Tenacity configurado para retry.
        """
        return retry(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type((requests.RequestException, APIException)),
            before_sleep=before_sleep_log(logger, "WARNING"),
            reraise=True,
        )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Executa uma requisição HTTP com retry.

        Args:
            method: Método HTTP (GET, POST, etc).
            endpoint: Endpoint da API.
            data: Dados para envio (opcional).
            headers: Headers adicionais (opcional).

        Returns:
            Dados da resposta JSON.

        Raises:
            APIException: Em caso de erro na requisição.
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = headers or {}

        if self._token:
            request_headers["Authorization"] = f"Bearer {self._token}"

        @self._get_retry_decorator()
        def execute_request() -> Any:
            """Executa a requisição com retry."""
            logger.debug(f"Requisição {method} para {url}")

            response = None
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    headers=request_headers,
                    timeout=self.timeout,
                )

                response.raise_for_status()

                logger.debug(f"Resposta recebida: status {response.status_code}")
                return response.json()

            except requests.exceptions.Timeout as e:
                logger.error(f"Timeout na requisição para {url}: {e}")
                raise APIException(f"Timeout na requisição: {e}")

            except requests.exceptions.HTTPError as e:
                status_code = response.status_code if response is not None else None
                logger.error(f"Erro HTTP {status_code}: {e}")
                raise APIException(f"Erro HTTP: {e}", status_code=status_code)

            except requests.exceptions.RequestException as e:
                logger.error(f"Erro na requisição: {e}")
                raise APIException(f"Erro na requisição: {e}")

        return execute_request()

    def fetch_all(self) -> List[Product]:
        """
        Busca todos os produtos da API.

        Returns:
            Lista de produtos.

        Raises:
            APIException: Em caso de erro na comunicação.
        """
        logger.info("Buscando todos os produtos da API")

        response = self._make_request("GET", "/products")

        products = [Product(**item) for item in response]

        logger.info(f"Total de produtos obtidos: {len(products)}")
        return products

    def close(self) -> None:
        """
        Fecha a sessão HTTP.

        Deve ser chamado ao finalizar o uso do cliente
        para liberar recursos.
        """
        self.session.close()
        logger.debug("Sessão HTTP fechada")
