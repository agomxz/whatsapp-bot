import pytest
from fastapi import status


class TestAgentRoutes:
    def test_read_root(self, client):
        """Test the root endpoint returns a welcome message."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()

    @pytest.mark.asyncio
    async def test_chat_endpoint(self, client, mock_llm):
        """Test the chat endpoint with a simple message."""
        # Mock the LLM response
        mock_llm.return_value.invoke.return_value = "Test response from LLM"

        test_message = {"message": "Hello, test!"}
        response = client.post("/chat/", json=test_message)

        assert response.status_code == status.HTTP_200_OK
        assert "response" in response.json()
        assert response.json()["response"] == "Test response from LLM"

    @pytest.mark.asyncio
    async def test_compare_endpoint(self, client, mock_llm):
        """Test the compare endpoint with sample items."""
        # Mock the LLM response
        mock_llm.return_value.invoke.return_value = "Comparison result"

        test_items = [
            {"id": "1", "name": "Item 1", "features": "Feature 1"},
            {"id": "2", "name": "Item 2", "features": "Feature 2"},
        ]
        response = client.post("/compare/", json={"items": test_items})

        assert response.status_code == status.HTTP_200_OK
        assert "comparison" in response.json()
        assert "compared_items" in response.json()
        assert len(response.json()["compared_items"]) == 2
