from app.services.llm_service import LLMService

def get_llm_service() -> LLMService:
    return LLMService()