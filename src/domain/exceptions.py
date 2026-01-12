class DomainException(Exception):
    """
    Exceção base para erros de domínio.

    Todas as exceções específicas do domínio devem herdar desta classe.
    """

    def __init__(self, message: str):
        """
        Inicializa a exceção com uma mensagem.

        Args:
            message: Mensagem descritiva do erro.
        """
        self.message = message
        super().__init__(self.message)


class APIException(DomainException):
    """
    Exceção para erros relacionados à API externa.

    Attributes:
        status_code: Código HTTP do erro, se disponível.
    """

    def __init__(self, message: str, status_code: int = None):
        """
        Inicializa a exceção de API.

        Args:
            message: Mensagem descritiva do erro.
            status_code: Código HTTP do erro.
        """
        self.status_code = status_code
        super().__init__(message)


class DatabaseException(DomainException):
    """
    Exceção para erros relacionados ao banco de dados.

    Utilizada para encapsular erros de conexão, transação
    e operações no PostgreSQL.
    """

    pass


class TransactionException(DatabaseException):
    """
    Exceção específica para erros de transação.

    Indica que uma transação falhou e foi revertida.
    """

    pass


class ValidationException(DomainException):
    """
    Exceção para erros de validação de dados.

    Utilizada quando os dados não atendem aos critérios esperados.
    """

    pass


class TransformationException(DomainException):
    """
    Exceção para erros durante transformação de dados.

    Utilizada quando ocorrem erros no processamento Spark.
    """

    pass
