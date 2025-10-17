import redis
from typing import Optional
import logging
from app.config import REDIS_HOST, REDIS_PORT, logger


class RedisConnectionError(Exception):
    """Custom exception for Redis connection errors."""

    pass


class RedisManager:
    """
    A singleton class to manage Redis connections.
    Provides a single point of configuration for Redis connections
    and ensures only one connection pool is used throughout the application.
    """

    _instance = None
    _client = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)
            # Initialize the Redis client on first instantiation
            cls._instance._initialize_client()
        return cls._instance

    def _initialize_client(self):
        """Initialize the Redis client with connection pooling."""
        try:
            self._client = redis.Redis(
                host=REDIS_HOST,
                port=int(REDIS_PORT),
                db=0,
                socket_connect_timeout=5,
                socket_timeout=5,
                decode_responses=True,
                retry_on_timeout=True,
                max_connections=20,  # Adjust based on your needs
            )
            # Test the connection
            self._client.ping()
            logger.info("Successfully connected to Redis")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise RedisConnectionError(f"Could not connect to Redis: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error initializing Redis: {str(e)}")
            raise

    @property
    def client(self) -> redis.Redis:
        """Get the Redis client instance."""
        if self._client is None:
            self._initialize_client()
        return self._client

    def get_connection(self) -> redis.Redis:
        """Get a Redis connection from the pool."""
        return self.client

    def test_connection(self) -> bool:
        """Test if the Redis connection is working."""
        try:
            return bool(self.client.ping())
        except Exception as e:
            logger.error(f"Redis connection test failed: {str(e)}")
            return False


# Create a singleton instance
redis_manager = RedisManager()


def get_redis() -> redis.Redis:
    """
    Get a Redis client instance.
    This is the preferred way to get a Redis connection throughout the application.
    """
    return redis_manager.client
