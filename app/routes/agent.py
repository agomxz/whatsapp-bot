from fastapi import APIRouter, status, HTTPException, Depends, Query
from typing import List, Dict, Optional, Any
import json
import uuid
import logging

# Local imports
from app.config import logger, LLM_MODEL
from app.schemas.chat import ChatRequest, ChatResponse, Message
from app.services.redis_chat_service import RedisChatService
from app.services.redis_manager import get_redis, RedisConnectionError
from app.services.langchain_manager import langchain_manager
from fastapi import Query
from app.utils.loader_data import load_products

router = APIRouter()

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
        # Get Redis client from the manager
        redis_client = get_redis()
        
        # Test connection
        if not redis_client.ping():
            raise RedisConnectionError("Redis ping failed")
        
        # Get and log current keys
        keys_before = redis_client.dbsize()
        logger.info(f"Keys before flush: {keys_before}")
        
        # Flush the database (use with caution in production!)
        redis_client.flushdb()
        
        # Get and log keys after flush
        keys_after = redis_client.dbsize()
        logger.info(f"Keys after flush: {keys_after}")
        
        return {
            "status": "success",
            "message": "Redis connection and operations successful",
            "keys_before_flush": keys_before,
            "keys_after_flush": keys_after,
            "connection_info": {
                "host": redis_client.connection_pool.connection_kwargs.get('host'),
                "port": redis_client.connection_pool.connection_kwargs.get('port'),
                "db": redis_client.connection_pool.connection_kwargs.get('db')
            }
        }
        
    except RedisConnectionError as e:
        logger.error(f"Redis connection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not connect to Redis: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Redis operation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Redis operation failed: {str(e)}"
        )


# Initialize chat service with RedisManager
chat_service = RedisChatService()

@router.post("/chat", response_model=ChatResponse, summary="Chat with the AI")
async def chat(chat_request: ChatRequest):
    """
    Chat endpoint that maintains conversation context using Redis.
    
    - If conversation_id is not provided, a new conversation will be started.
    - The last 10 messages are kept in the conversation history.
    - Each conversation expires after 7 days of inactivity.
    """
    try:
        # Generate a new conversation ID if not provided
        conversation_id = chat_request.conversation_id or f"conv_{str(uuid.uuid4())}"
        
        # Get conversation history
        history = await chat_service.get_conversation_history(conversation_id)
        
        # Add user message to history
        user_message = Message(role="user", content=chat_request.message)
        await chat_service.save_message(conversation_id, user_message.dict())
        
        # Format the conversation history for the model
        formatted_history = "\n".join(
            [f"{msg['role'].capitalize()}: {msg['content']}" for msg in history]
        )
        
        # Get conversation chain from LangChain manager
        conversation_chain = langchain_manager.get_chain("conversation")
        
        # Generate response using the conversation chain
        response = conversation_chain.predict(
            input=chat_request.message,
            chat_history=formatted_history
        )
        
        # Save assistant's response to history
        assistant_message = Message(role="assistant", content=response)
        await chat_service.save_message(conversation_id, assistant_message.dict())
        
        # Get updated history
        updated_history = await chat_service.get_conversation_history(conversation_id)
        
        return ChatResponse(
            response=response,
            conversation_id=conversation_id,
            message_history=updated_history
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@router.get("/generate")
async def generate(prompt: str):
    """Simple endpoint to test the LLM model without conversation context"""
    try:
        llm = langchain_manager.get_llm()
        response = llm(prompt)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}"
        )


@router.get("/items/")
def get_items(ids: List[int] = Query(default=None)):
    products = load_products()
    if ids:
        filtered = [p for p in products if p["id"] in ids]
        if not filtered:
            raise HTTPException(status_code=404, detail="Items not found")
        return filtered
    return products


@router.post("/compare/")
def compare_items(ids: List[int]):
    products = load_products()
    selected = [p for p in products if p["id"] in ids]

    if len(selected) < 2:
        raise HTTPException(
            status_code=400, detail="Please provide at least two valid item IDs"
        )

    llm = Ollama(model="llama3", base_url=OLLAMA_URL)

    # Prompt template for comparison
    prompt = PromptTemplate(
        input_variables=["items"],
        template=(
            "You are a helpful assistant. Compare the following items in detail:\n"
            "{items}\n\n"
            "Explain which product is better overall, and why, considering features, price, and rating."
        ),
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    items_text = json.dumps(selected, indent=2)
    result = chain.run(items=items_text)

    return {"comparison": result}