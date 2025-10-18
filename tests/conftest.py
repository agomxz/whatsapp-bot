import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_redis():
    with patch("app.db.redis.Redis") as mock_redis:
        yield mock_redis


@pytest.fixture
def mock_llm():
    with patch("app.services.langchain_manager.LLM_MODEL") as mock_llm:
        yield mock_llm


@pytest.fixture
def env_setup(monkeypatch):
    # Set up test environment variables
    monkeypatch.setenv("REDIS_URL", "redis://test-redis:6379")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "test-token")
