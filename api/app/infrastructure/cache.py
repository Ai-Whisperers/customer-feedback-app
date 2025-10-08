"""
Centralized Redis cache client.
Provides singleton pattern with connection pooling and retry logic.
"""

from typing import Optional, Any
import redis
from redis.retry import Retry
from redis.backoff import ExponentialBackoff
import structlog

from app.config import settings

logger = structlog.get_logger()


class CacheClient:
    """
    Singleton Redis client with connection pooling and retry logic.

    Benefits:
    - Single connection pool across application
    - Built-in exponential backoff retry
    - Centralized error handling
    - Easy to mock for testing
    - Simple to swap backend (Redis → Valkey)
    """

    _instance: Optional[redis.Redis] = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        """
        Get or create Redis client instance.

        Returns:
            Redis client with connection pooling and retry logic
        """
        if cls._instance is None:
            try:
                cls._instance = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry=Retry(ExponentialBackoff(), 3),
                    health_check_interval=30
                )
                logger.info(
                    "Redis client initialized",
                    url_prefix=settings.REDIS_URL.split('@')[-1] if '@' in settings.REDIS_URL else settings.REDIS_URL[:20]
                )
            except Exception as e:
                logger.error("Failed to initialize Redis client", error=str(e))
                raise

        return cls._instance

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Get value from Redis with error handling.

        Args:
            key: Redis key
            default: Default value if key not found or error occurs

        Returns:
            Value from Redis or default
        """
        try:
            value = cls.get_client().get(key)
            return value if value is not None else default
        except redis.RedisError as e:
            logger.warning("Redis GET failed", key=key, error=str(e))
            return default

    @classmethod
    def set(
        cls,
        key: str,
        value: Any,
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """
        Set value in Redis with error handling.

        Args:
            key: Redis key
            value: Value to store
            ex: Expire time in seconds
            px: Expire time in milliseconds
            nx: Only set if key does not exist
            xx: Only set if key exists

        Returns:
            True if successful, False otherwise
        """
        try:
            result = cls.get_client().set(key, value, ex=ex, px=px, nx=nx, xx=xx)
            return bool(result)
        except redis.RedisError as e:
            logger.error("Redis SET failed", key=key, error=str(e))
            return False

    @classmethod
    def delete(cls, *keys: str) -> int:
        """
        Delete one or more keys from Redis.

        Args:
            keys: Keys to delete

        Returns:
            Number of keys deleted
        """
        try:
            return cls.get_client().delete(*keys)
        except redis.RedisError as e:
            logger.error("Redis DELETE failed", keys=keys, error=str(e))
            return 0

    @classmethod
    def exists(cls, *keys: str) -> int:
        """
        Check if keys exist in Redis.

        Args:
            keys: Keys to check

        Returns:
            Number of keys that exist
        """
        try:
            return cls.get_client().exists(*keys)
        except redis.RedisError as e:
            logger.warning("Redis EXISTS failed", keys=keys, error=str(e))
            return 0

    @classmethod
    def ping(cls) -> bool:
        """
        Ping Redis to check connection.

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            return cls.get_client().ping()
        except redis.RedisError as e:
            logger.error("Redis PING failed", error=str(e))
            return False

    @classmethod
    def reset(cls) -> None:
        """
        Reset singleton instance.
        Useful for testing and connection reset.
        """
        if cls._instance:
            try:
                cls._instance.close()
            except Exception as e:
                logger.warning("Error closing Redis connection", error=str(e))
            finally:
                cls._instance = None
                logger.info("Redis client reset")
