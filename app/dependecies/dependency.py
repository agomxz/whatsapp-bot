from app.services.llm_service import LLMService
from app.utils.twilio import TwilioService


def get_llm_service() -> LLMService:
    return LLMService()


def get_twilio_service() -> TwilioService:
    return TwilioService()