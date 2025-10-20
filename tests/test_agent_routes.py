from fastapi import status
from fastapi.testclient import TestClient
from app.main import app
from pydantic import ValidationError
from app.schemas.items import Vehicle


client = TestClient(app)


def test_healthcheck():
    response = client.get("/agent/")
    assert response.status_code == 200
    assert response.json() == {"status": "API Running"}


def test_get_items_returns_valid_list():
    response = client.get("/agent/items/")
    assert response.status_code == 200, "Expected 200 OK response"
    data = response.json()

    assert isinstance(data, dict), "Response should be a dictionary"

    items = data["response"]

    for i, item in enumerate(items, start=1):
        try:
            vehicle = Vehicle(**item)
        except ValidationError as e:
            raise AssertionError(f"Vehicle {i} failed schema validation: {e}")

        assert 0 <= vehicle.rating <= 5, f"Vehicle {i} has invalid rating"
        assert (
            vehicle.year >= 1886
        ), f"Vehicle {i} has invalid year (before cars existed)"
        assert vehicle.price > 0, f"Vehicle {i} price negative"


def test_llm_response():
    """Test the LLM generation endpoint with various inputs."""
    test_prompt = "Hola"
    response = client.get(
        f"/agent/generate/{test_prompt}",
    )

    # Check response status and structure
    assert (
        response.status_code == status.HTTP_200_OK
    ), f"Expected status 200 but got {response.status_code}: {response.text}"
    response_data = response.json()

    # Check response structure
    assert "response" in response_data, "Response should contain 'response' field"
    assert isinstance(
        response_data["response"], str
    ), f"Response should be a string, got {type(response_data['response'])}"
    assert len(response_data["response"].strip()) > 0, "Response should not be empty"

    # Test with an empty prompt (should still work but might return a default response)
    response = client.get(
        "/agent/generate",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
