from app.services.llm_service import LLMService
from app.utils.twilio import TwilioService
from app.redis_memory import RedisMemoryManager
from app.services.chat_service import ChatService


def get_llm_service() -> LLMService:
    return LLMService()


def get_twilio_service() -> TwilioService:
    return TwilioService()


def get_redis_memory_manager() -> RedisMemoryManager:
    return RedisMemoryManager()


def get_chat_service() -> ChatService:
    return ChatService(get_redis_memory_manager())
