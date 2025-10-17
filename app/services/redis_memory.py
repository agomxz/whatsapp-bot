from langchain.schema import AIMessage, HumanMessage
import redis
import json
from langchain.memory import ConversationBufferMemory
from app.config import REDIS_URL
from app.config import logger
import pickle


class RedisMemoryManager:
    """
    Redis-based memory manager for WhatsApp bot conversations and data storage
    """

    def __init__(self, redis_url: str = REDIS_URL):
        """Initialize the Redis memory manager.

        Args:
            redis_url: Redis connection URL
        """
        self.redis_client = redis.from_url(redis_url)

    def serialize_messages(self, messages: list) -> list:
        """Serialize LangChain messages to JSON-compatible format.

        Args:
            messages: List of LangChain message objects

        Returns:
            List of serialized message dictionaries
        """
        serialized = []
        for m in messages:
            if isinstance(m, AIMessage):
                serialized.append({"role": "ai", "content": m.content})
            elif isinstance(m, HumanMessage):
                serialized.append({"role": "user", "content": m.content})
            elif isinstance(m, dict):
                serialized.append(m)
        return serialized

    def deserialize_messages(self, messages: list) -> list:
        """Deserialize JSON messages to LangChain message objects.

        Args:
            messages: List of serialized message dictionaries

        Returns:
            List of LangChain message objects
        """
        deserialized = []
        for m in messages:
            role = m.get("role")
            content = m.get("content")
            if role == "ai":
                deserialized.append(AIMessage(content=content))
            elif role == "user":
                deserialized.append(HumanMessage(content=content))
            else:
                deserialized.append(m)
        return deserialized

    def get_chat_memory(self, user_id: str) -> list:
        """Get chat history for a user.

        Args:
            user_id: Unique identifier for the user

        Returns:
            List of deserialized message objects
        """
        data = self.redis_client.get(f"chat:{user_id}")
        if data:
            messages = json.loads(data)
            return self.deserialize_messages(messages)
        return []

    def save_chat_memory(self, user_id: str, messages: list) -> None:
        """Save chat history for a user.

        Args:
            user_id: Unique identifier for the user
            messages: List of message objects to save
        """
        self.redis_client.set(
            f"chat:{user_id}", json.dumps(self.serialize_messages(messages))
        )

    def get_last_car(self, user_id: str) -> dict | None:
        """Get the last car data for a user.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Dictionary with car data or None if not found
        """
        data = self.redis_client.get(f"last_car:{user_id}")

        if data:
            logger.info(data.decode("utf-8"))
            return {"car": data.decode("utf-8")}

        return None

    def save_last_car(self, user_id: str, car_data: str) -> None:
        """Save the last car data for a user.

        Args:
            user_id: Unique identifier for the user
            car_data: Car data to save
        """
        self.redis_client.set(f"last_car:{user_id}", car_data)

    def clean_user_chat(self, user_id: str) -> None:
        """Clean the chat history for a user.

        Args:
            user_id: Unique identifier for the user
        """
        logger.info("Cleaning chat history for user: %s", user_id)
        self.redis_client.delete(f"chat:{user_id}")
        self.redis_client.delete(f"last_car:{user_id}")


# Create a default instance for backward compatibility
redis_memory = RedisMemoryManager()

# Backward compatibility functions


def serialize_messages(messages):
    return redis_memory.serialize_messages(messages)


def deserialize_messages(messages):
    return redis_memory.deserialize_messages(messages)


def get_chat_memory(user_id: str):
    return redis_memory.get_chat_memory(user_id)


def save_chat_memory(user_id: str, messages):
    return redis_memory.save_chat_memory(user_id, messages)


def get_last_car(user_id: str):
    return redis_memory.get_last_car(user_id)


def save_last_car(user_id, car_data):
    return redis_memory.save_last_car(user_id, car_data)
