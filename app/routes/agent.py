from fastapi import APIRouter, status, HTTPException, Query
from typing import List, Dict
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

from app.utils.utils import is_vehicle_query
from app.constants.propmts import COMPARE_PROMPT

router = APIRouter()


# Initialize chat service with RedisManager
chat_service = RedisChatService()


@router.get("/", summary="Healthcheck", status_code=status.HTTP_200_OK)
async def home() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "API Running"}


@router.get("/redis/")
async def test_redis():
    """
    Test Redis connection and return basic info.

    This endpoint is useful for debugging and testing the Redis connection.
    It will show the number of keys before and after flushing the database.

    Note: This endpoint is for testing purposes only and should be disabled in production.
    """
    try:
        redis_client = get_redis()

        # Test connection
        if not redis_client.ping():
            raise RedisConnectionError("Redis ping failed")

        keys_before = redis_client.dbsize()
        logger.info(f"Keys before flush: {keys_before}")

        # redis_client.flushdb()

        # keys_after = redis_client.dbsize()
        # logger.info(f"Keys after flush: {keys_after}")

        return {
            "status": "success",
            "message": "Redis connection and operations successful",
            "keys_before_flush": keys_before,
            # "keys_after_flush": keys_after,
            "connection_info": {
                "host": redis_client.connection_pool.connection_kwargs.get("host"),
                "port": redis_client.connection_pool.connection_kwargs.get("port"),
                "db": redis_client.connection_pool.connection_kwargs.get("db"),
            },
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
def get_items(ids: List[int] = Query(default=None)):
    """Fetch data from fake database using product IDs"""
    products = load_products()
    if ids:
        filtered = [p for p in products if p["id"] in ids]
        if not filtered:
            raise HTTPException(status_code=404, detail="Items not found")
        return filtered
    return products


@router.post("/compare/")
async def compare_items(ids: List[int]):
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
        logger.info(f"Conversation ID: {conversation_id}")
        history = await chat_service.get_conversation_history(conversation_id)

        # Add user message to history
        logger.info(f"User message: {chat_request.message}")
        user_message = Message(role="user", content=chat_request.message)
        await chat_service.save_message(conversation_id, user_message.dict())

        # Format the conversation history for the model
        logger.info(f"Conversation history: {history}")
        # formatted_history = "\n".join(
        #     [f"{msg['role'].capitalize()}: {msg['content']}" for msg in history]
        # )

        # Get conversation chain from LangChain manager
        # conversation_chain = langchain_manager.get_chain("conversation")

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
                        f"Vehicle: {v['name']}\n"
                        f"Price: ${v['price']:,}\n"
                        f"Year: {v['year']}\n"
                        # f"Mileage: {v['mileage_km']:,} km\n"
                        f"Fuel Type: {v['fuel_type']}\n"
                        f"Transmission: {v['transmission']}\n"
                        # f"Description: {v['description']}"
                        for v in relevant_vehicles
                    ]
                )

                # Get RAG chain and generate response
                rag_chain = langchain_manager.get_rag_chain()
                response = rag_chain.predict(
                    context=context, question=chat_request.message
                )
                logger.info("Generated RAG response")
            else:
                response = "I couldn't find any vehicles matching your query. Could you provide more details?"
                logger.info("No relevant vehicles found for the query")

        else:
            # For non-vehicle queries, use llama3 to generate a response
            logger.info("Non-vehicle query detected, generating response with llama3")
            prompt = (
                "You are a helpful assistant that specializes in vehicle information. "
                'The user asked: "{user_query}"\n'
                "Politely explain that you can only help with vehicle-related questions and provide "
                "some examples of vehicle questions they could ask instead. Keep it friendly and helpful."
            ).format(user_query=chat_request.message)

            # Get the LLM instance and generate a response
            llm = langchain_manager.get_llm()
            response = llm.invoke(prompt)

            # Ensure we have a response, fallback to default if needed
            if (
                not response or len(response.strip()) < 50
            ):  # Simple check for empty or very short responses
                response = (
                    "I'm sorry, but I'm currently only able to assist with vehicle-related queries. "
                    "Please ask me about vehicles, such as their models, prices, features, or availability.\n\n"
                    "For example, you can ask:\n"
                    "- Show me electric vehicles under $50,000\n"
                    "- What Toyotas do you have available?\n"
                    "- Find me a red car with low mileage"
                )

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
