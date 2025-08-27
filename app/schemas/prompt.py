from pydantic import BaseModel


# Modelo de datos para request
class PromptRequest(BaseModel):
    prompt: str


class QueryRequest(BaseModel):
    question: str
