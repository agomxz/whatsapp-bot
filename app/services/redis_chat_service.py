import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.services.redis_manager import redis_manager, RedisConnectionError
from app.config import logger

class RedisChatService:
    """
    Service for managing chat conversations using Redis as the backend storage.
    Handles message history and conversation state.
    """
    
    def __init__(self, max_history: int = 10, expire_days: int = 7):
        """
        Initialize the Redis chat service.
        
        Args:
            max_history: Maximum number of messages to keep in history
            expire_days: Number of days until conversation expires (default: 7)
        """
        self.redis = redis_manager.client
        self.max_history = max_history
        self.expire_seconds = expire_days * 24 * 60 * 60  # Convert days to seconds
        
    def _get_conversation_key(self, conversation_id: str) -> str:
        """Generate the Redis key for a conversation."""
        return f"chat:{conversation_id}"
    
    async def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """
        Retrieve conversation history from Redis.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            List of message dictionaries, most recent first
            
        Raises:
            RedisConnectionError: If there's an issue connecting to Redis
        """
        try:
            key = self._get_conversation_key(conversation_id)
            # Get all messages in the list (0 to -1)
            messages = self.redis.lrange(key, 0, -1)
            # Parse JSON messages and return most recent first
            return [json.loads(msg) for msg in reversed(messages)]
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding message JSON: {str(e)}")
            return []
        except RedisConnectionError as e:
            logger.error(f"Redis connection error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting conversation history: {str(e)}")
            raise
            return []
    
    async def save_message(self, conversation_id: str, message: Dict) -> None:
        """
        Save a message to the conversation history.
        
        Args:
            conversation_id: Unique identifier for the conversation
            message: Message dictionary to save
            
        Raises:
            RedisConnectionError: If there's an issue connecting to Redis
            ValueError: If the message is invalid
        """
        if not message or 'content' not in message:
            raise ValueError("Invalid message format: 'content' is required")
            
        key = self._get_conversation_key(conversation_id)
        
        try:
            # Add timestamp if not present
            if 'timestamp' not in message:
                message['timestamp'] = datetime.utcnow().isoformat()
            
            # Add role if not present
            if 'role' not in message:
                message['role'] = 'user'
                
            # Add to the list
            pipeline = self.redis.pipeline()
            pipeline.rpush(key, json.dumps(message))
            
            # Trim the list to maintain max history
            pipeline.ltrim(key, -self.max_history, -1)
            
            # Set expiry on the key (only needs to be done once per conversation)
            pipeline.expire(key, self.expire_seconds)
            
            # Execute all commands in a single transaction
            pipeline.execute()
            
        except RedisConnectionError as e:
            logger.error(f"Redis connection error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            raise

# Create a default instance
default_redis_chat_service = RedisChatService()
