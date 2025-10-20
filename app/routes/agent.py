from fastapi import APIRouter, status, HTTPException, Query
from typing import List, Dict, Any
import json
import uuid

# LangChain imports
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Local imports
from app.config import logger
from app.schemas.chat import ChatRequest, ChatResponse, Message
from app.services.redis_chat_service import RedisChatService
from app.services.redis_manager import get_redis, RedisConnectionError
from app.services.langchain_manager import langchain_manager
from app.services.vehicle_service import vehicle_service
from app.utils.loader_data import load_products
from app.schemas.items import VehiclesResponse

from app.utils.utils import is_vehicle_query
from app.constants.propmts import (
    COMPARE_PROMPT,
    DATA_NOT_FOUND,
    SUGGEST_RESPONSE_PROMPT,
)

router = APIRouter()

# Initialize chat service with RedisManager
chat_service = RedisChatService()


@router.get("/", summary="Healthcheck", status_code=status.HTTP_200_OK)
async def home() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "API Running"}


@router.get("/redis/")
async def test_redis() -> Dict[str, Any]:
    """
    Test Redis connection and return basic info.

    This endpoint is useful for debugging and testing the Redis connection.
    It will show the number of keys before and after flushing the database.

    Note: This endpoint is for testing purposes only
    """
    try:
        redis_client = get_redis()

        if not redis_client.ping():
            raise RedisConnectionError("Redis ping failed")

        keys_before = redis_client.dbsize()
        logger.info(f"Keys before flush: {keys_before}")

        redis_client.flushdb()

        keys_after = redis_client.dbsize()
        logger.info(f"Keys after flush: {keys_after}")

        return {
            "status": "success",
            "message": "Redis connection and operations successful",
            "keys_before_flush": keys_before,
            "keys_after_flush": keys_after,
        }

    except RedisConnectionError as e:
        logger.error(f"Redis connection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not connect to Redis: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Redis operation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Redis operation failed: {str(e)}",
        )


@router.get("/generate/{prompt}")
async def generate(prompt: str) -> Dict[str, str]:
    """Simple endpoint to test the LLM model without conversation context"""
    try:

        if not prompt or not prompt.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt cannot be empty. Please provide a valid input.",
            )

        logger.info(f"Generating response for prompt: {prompt}")
        llm = langchain_manager.get_llm()
        response = llm(prompt)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}",
        )


@router.get("/items/")
def get_items(ids: List[int] = Query(default=None)) -> VehiclesResponse:
    """Fetch data from fake database using product IDs"""
    try:
        products = load_products()
        if ids:
            filtered = [p for p in products if p["id"] in ids]
            if not filtered:
                raise HTTPException(status_code=404, detail="Items not found")
            return VehiclesResponse(response=filtered)

        return VehiclesResponse(response=products)

    except Exception as e:
        logger.error(f"Error fetching items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching items: {str(e)}",
        )


@router.post("/compare/")
async def compare_items(ids: List[int]) -> Dict[str, Any]:
    """
    Compare items using LLM with LangChain manager.

    Args:
        ids: List of product IDs to compare (at least 2 required)

    Returns:
        JSON with comparison result

    Raises:
        HTTPException: If less than 2 valid item IDs are provided
    """
    products = load_products()
    selected = [p for p in products if p["id"] in ids]

    if len(selected) < 2:
        raise HTTPException(
            status_code=400, detail="Please provide at least two valid item IDs"
        )

    try:
        # Get LLM instance from LangChain manager
        llm = langchain_manager.get_llm()

        # Create a comparison chain
        prompt = PromptTemplate(
            input_variables=["items"],
            template=(COMPARE_PROMPT),
        )

        chain = LLMChain(llm=llm, prompt=prompt)
        items_text = json.dumps(selected, indent=2, ensure_ascii=False)

        # Generate comparison using the chain
        result = await chain.arun(items=items_text)

        return {
            "comparison": result,
            "compared_items": [{"id": p["id"], "name": p["name"]} for p in selected],
        }

    except Exception as e:
        logger.error(f"Error in compare endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the comparison: {str(e)}",
        )


@router.post("/chat/", response_model=ChatResponse, summary="Chat with the AI")
async def chat(chat_request: ChatRequest):
    """
    Chat endpoint that maintains conversation context using Redis.

    - If conversation_id is not provided, a new conversation will be started.
    - The last 10 messages are kept in the conversation history.
    - Each conversation expires after 7 days of inactivity.
    """
    try:
        # Generate a new conversation ID if not provided
        logger.info(f"Chat request: {chat_request}")
        conversation_id = chat_request.conversation_id or f"conv_{str(uuid.uuid4())}"

        # Get conversation history
        history = await chat_service.get_conversation_history(conversation_id)
        logger.info(f"Conversation history: {history}")

        # Add user message to history
        user_message = Message(role="user", content=chat_request.message)
        await chat_service.save_message(conversation_id, user_message.dict())

        # Check if this is a vehicle-related query
        if is_vehicle_query(chat_request.message):
            logger.info("Vehicle-related query detected, using RAG...")

            # Get relevant vehicle information using RAG
            logger.info("Searching for relevant vehicles...")
            relevant_vehicles = vehicle_service.search_vehicles(
                chat_request.message, k=3
            )

            if relevant_vehicles:
                logger.info(f"Found {len(relevant_vehicles)} relevant vehicles")

                # Format the context from relevant vehicles
                context = "\n\n".join(
                    [
                        f"Vehiculo: {v['name']}\n"
                        f"Precio: ${v['price']:,}\n"
                        f"Año: {v['year']}\n"
                        f"TipoCombustible: {v['fuel_type']}\n"
                        f"TipoTransmision: {v['transmission']}\n"
                        for v in relevant_vehicles
                    ]
                )

                # Get RAG chain and generate response in Spanish
                rag_chain = langchain_manager.get_rag_chain()
                response = rag_chain.predict(
                    context=context,
                    question=f"{chat_request.message} (responde en español)",
                )
                logger.info("Generated RAG response")

            else:
                response = DATA_NOT_FOUND
                logger.info("No relevant vehicles found for the query")

        else:
            # For non-vehicle queries, use llama3 to generate a response in Spanish
            logger.info("Non-vehicle query detected, generating response with llama3")
            prompt = (SUGGEST_RESPONSE_PROMPT + " Responde siempre en español.").format(
                user_query=chat_request.message
            )

            # Get the LLM instance and generate a response
            llm = langchain_manager.get_llm()
            response = llm.invoke(prompt)

        # Save assistant's response to history
        assistant_message = Message(role="assistant", content=response)
        await chat_service.save_message(conversation_id, assistant_message.dict())

        # Get updated history
        updated_history = await chat_service.get_conversation_history(conversation_id)

        return ChatResponse(
            response=response,
            conversation_id=conversation_id,
            message_history=updated_history,
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}",
        )
