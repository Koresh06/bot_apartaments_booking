from dataclasses import dataclass
from typing import Optional

from environs import Env


@dataclass
class DbConfig:
    # Основная конфигурация
    password: str
    user: str
    database: str
    host: str
    port: int = 5432

    # Конфигурация тестовой базы данных
    test_database: Optional[str] = None

    def construct_sqlalchemy_url(self, driver="asyncpg", host=None, port=None, is_test=False) -> str:
        from sqlalchemy.engine.url import URL

        if not host:
            host = self.host
        if not port:
            port = self.port
        
        # Проверяем, если это тестовая среда
        database = self.test_database if is_test else self.database

        uri = URL.create(
            drivername=f"postgresql+{driver}",
            username=self.user,
            password=self.password,
            host=host,
            port=port,
            database=database,  # Используем либо основную, либо тестовую базу
        )
        return uri.render_as_string(hide_password=False)

    @staticmethod
    def from_env(env: Env, is_test=False):
        host = env.str("DB_HOST")
        password = env.str("POSTGRES_PASSWORD")
        user = env.str("POSTGRES_USER")
        database = env.str("POSTGRES_DB")
        port = env.int("DB_PORT", 5432)
        
        test_database = env.str("TEST_POSTGRES_DB")

        if is_test:
            return DbConfig(
                host=host, 
                password=password, 
                user=user, 
                database=database, 
                port=port,
                test_database=test_database
            )

        return DbConfig(
            host=host, 
            password=password, 
            user=user, 
            database=database, 
            port=port,
            test_database=test_database
        )


@dataclass
class TgBot:
    """
    Creates the TgBot object from environment variables.
    """

    token: str
    admin_ids: list[int]
    use_redis: bool

    @staticmethod
    def from_env(env: Env):
        """
        Creates the TgBot object from environment variables.
        """
        token = env.str("BOT_TOKEN")
        admin_ids = list(map(int, env.list("ADMINS")))
        use_redis = env.bool("USE_REDIS")
        return TgBot(
            token=token,
            admin_ids=admin_ids,
            use_redis=use_redis,
        )


@dataclass
class RedisConfig:
    """
    Redis configuration class.

    Attributes
    ----------
    redis_pass : Optional(str)
        The password used to authenticate with Redis.
    redis_port : Optional(int)
        The port where Redis server is listening.
    redis_host : Optional(str)
        The host where Redis server is located.
    """

    redis_port: Optional[int] = None
    redis_host: Optional[str] = None
    redis_pass: Optional[str] = None

    def dsn(self) -> str:
        """
        Constructs and returns a Redis DSN (Data Source Name) for this database configuration.
        """
        if self.redis_pass:
            return f"redis://:{self.redis_pass}@{self.redis_host}:{self.redis_port}/0"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}/0"

    @staticmethod
    def from_env(env: Env):
        """
        Creates the RedisConfig object from environment variables.
        """
        # redis_pass = env.str("REDIS_PASSWORD")
        redis_port = env.int("REDIS_PORT")
        redis_host = env.str("REDIS_HOST")

        return RedisConfig(
            redis_port=redis_port, 
            redis_host=redis_host
        )


@dataclass
class ApiConfig:
    """ "
    Creates the ApiConfig object from environment variables.
    """

    admin_login: str
    admin_password: str
    secret_key: str
    web_url: str
    host: str = "127.0.0.1"
    port: int = 8000

    @staticmethod
    def from_env(env: Env):
        """
        Creates the ApiConfig object from environment variables.
        """
        admin_login = env.str("ADMIN_LOGIN")
        admin_password = env.str("ADMIN_PASSWORD")
        secret_key = env.str("SECRET_KEY")
        host = env.str("API_HOST")
        port = env.int("API_PORT")
        web_url = env.str("WEB_URL")
        return ApiConfig(
            admin_login=admin_login,
            admin_password=admin_password,
            secret_key=secret_key,
            host=host,
            port=port,
            web_url=web_url,
        )


@dataclass
class Config:
    """
    The main configuration class that integrates all the other configuration classes.

    This class holds the other configuration classes, providing a centralized point of access for all settings.

    Attributes
    ----------
    tg_bot : TgBot
        Holds the settings related to the Telegram Bot.
    db : Optional[DbConfig]
        Holds the settings specific to the database (default is None).
    redis : Optional[RedisConfig]
        Holds the settings specific to Redis (default is None).
    """

    tg_bot: TgBot
    db: Optional[DbConfig] = None
    redis: Optional[RedisConfig] = None
    api: Optional[ApiConfig] = None


def load_config(path: str = None) -> Config:
    """
    This function takes an optional file path as input and returns a Config object.
    :param path: The path of env file from where to load the configuration variables.
    It reads environment variables from a .env file if provided, else from the process environment.
    :return: Config object with attributes set as per environment variables.
    """

    # Create an Env object.
    # The Env object will be used to read environment variables.
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot.from_env(env),
        db=DbConfig.from_env(env),
        redis=RedisConfig.from_env(env),
        api=ApiConfig.from_env(env),
    )


config = load_config(".env")