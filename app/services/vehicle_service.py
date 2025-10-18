"""Service for handling vehicle data and retrieval."""

import json
from typing import List, Dict, Any
from pathlib import Path
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
import logging
from app.config import OLLAMA_URL

logger = logging.getLogger(__name__)


class VehicleService:
    def __init__(self, data_path: str):
        """Initialize the vehicle service with data path.

        Args:
            data_path: Path to the vehicles data JSON file
        """
        self.data_path = data_path
        self.vehicles = self._load_vehicles()
        self.vector_store = self._create_vector_store()

    def _load_vehicles(self) -> List[Dict[str, Any]]:
        """Load vehicles from the JSON file."""
        try:
            with open(self.data_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading vehicles data: {e}")
            return []

    def _create_vector_store(self):
        """Create a vector store from the vehicles data."""
        if not self.vehicles:
            return None

        # Convert vehicles to Document objects
        documents = []
        for vehicle in self.vehicles:
            # Create a text representation of the vehicle for embedding
            text = (
                f"Vehicle: {vehicle['name']}\n"
                f"Brand: {vehicle['brand']}\n"
                f"Model: {vehicle['model']}\n"
                f"Year: {vehicle['year']}\n"
                f"Price: ${vehicle['price']}\n"
                f"Fuel Type: {vehicle['fuel_type']}\n"
                # f"Mileage: {vehicle['mileage_km']} km\n"
                f"Transmission: {vehicle['transmission']}\n"
                # f"Description: {vehicle['description']}"
            )

            # Store metadata for filtering
            metadata = {
                "id": vehicle["id"],
                "brand": vehicle["brand"],
                "model": vehicle["model"],
                "year": vehicle["year"],
                "price": vehicle["price"],
                "fuel_type": vehicle["fuel_type"],
                "transmission": vehicle["transmission"],
            }

            documents.append(Document(page_content=text, metadata=metadata))

        # Create and return FAISS vector store using Ollama embeddings with llama3 model
        return FAISS.from_documents(
            documents=documents,
            embedding=OllamaEmbeddings(
                base_url=OLLAMA_URL, model="llama3"  # Explicitly use llama3 model
            ),
        )

    def search_vehicles(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search for vehicles using semantic similarity.

        Args:
            query: The search query
            k: Number of results to return

        Returns:
            List of matching vehicles with scores
        """
        if not self.vector_store:
            return []

        # Perform similarity search
        docs_and_scores = self.vector_store.similarity_search_with_score(query, k=k)

        # Format results
        results = []
        for doc, score in docs_and_scores:
            vehicle = {
                "id": doc.metadata["id"],
                "name": f"{doc.metadata['brand']} {doc.metadata['model']} {doc.metadata['year']}",
                "brand": doc.metadata["brand"],
                "model": doc.metadata["model"],
                "year": doc.metadata["year"],
                "price": doc.metadata["price"],
                "fuel_type": doc.metadata["fuel_type"],
                "transmission": doc.metadata["transmission"],
                "score": float(1 - score),  # Convert to similarity score (1 - distance)
                "content": doc.page_content,
            }
            results.append(vehicle)

        return results


# Create a singleton instance
vehicle_service = VehicleService(
    data_path=str(Path(__file__).parent.parent / "data" / "vehicles_data.json")
)
