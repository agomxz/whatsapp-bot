from langchain_openai import ChatOpenAI
from app.config import OPENAI_API_KEY


class LLMService:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.api_key = OPENAI_API_KEY

    def get_llm(self) -> ChatOpenAI:
        return ChatOpenAI(model=self.model, api_key=self.api_key, temperature=0.7)

    def invoke(self, prompt: str):
        return self.get_llm().invoke(prompt)
