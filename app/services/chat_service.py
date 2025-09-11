from langchain.prompts import ChatPromptTemplate
from app.constants.propmts import (
    WELCOME_PROMPT,
    RECOMMENDATION_PROMPT,
    FINANCING_PROMPT,
    FINANCING_ERROR_PROMPT,
    VEHICLE_SUGGESTION_PROMPT,
    SUMMARY_FRIENDLY_PROMPT,
    SPELLCHECK_PROMPT,
    CLOSE_CHAT_PROMPT,
)
from app.redis_memory import RedisMemoryManager
from app.services.rag import show_car_by_question, show_random_vehicle
from app.services.rag_blog import ask_company_info
from app.utils.utils import calculate_financing
from langchain.agents import Tool
from app.config import logger
import re


class ChatService:
    """
    Service class for handling WhatsApp bot chat operations and interactions.
    """
    
    def __init__(self, redis_memory_manager: RedisMemoryManager):
        """Initialize the ChatService with a Redis memory manager.
        
        Args:
            redis_memory_manager: RedisMemoryManager instance for data persistence
        """
        self.redis_memory_manager = redis_memory_manager
    
    def handle_user_input(self, llm, user_text: str) -> str:
        """Corrects user input using a spellcheck LLM chain and returns it in lowercase.
        
        Args:
            llm: Language model instance
            user_text: Raw user input text
            
        Returns:
            Corrected and lowercased user input
        """
        spellcheck_chain = ChatPromptTemplate.from_template(SPELLCHECK_PROMPT)
        corrected_input = spellcheck_chain | llm
        user_input = corrected_input.invoke({})
        logger.info(user_input.content)
        return user_input.content.lower()
    
    def handle_welcome(self, llm):
        """Returns a welcome message using the welcome prompt and LLM.
        
        Args:
            llm: Language model instance
            
        Returns:
            Welcome message response
        """
        prompt = ChatPromptTemplate.from_messages([("system", WELCOME_PROMPT)])
        chain = prompt | llm
        return chain.invoke({})
    
    def handle_random_vehicle(self, user_id: str, vectorstore):
        """Retrieves a random vehicle from the vectorstore, saves it for the user in Redis,
        and returns the vehicle information.
        
        Args:
            user_id: Unique identifier for the user
            vectorstore: Vector database containing vehicle information
            
        Returns:
            Random vehicle information response
        """
        response = show_random_vehicle(vectorstore, query="Busca en la base de datos de vehículos y devuelve opciones aleatorias ", k=5)
        self.redis_memory_manager.save_last_car(user_id, response.content)
        return response
    
    def handle_vehicle_suggestion(self, user_input: str, chat_history: list, llm):
        """Suggests vehicles based on user input and recent chat history using the LLM.
        Only the last 3 chat messages are considered in the prompt context.
        
        Args:
            user_input: User's input text
            chat_history: List of previous chat messages
            llm: Language model instance
            
        Returns:
            Vehicle suggestion response
        """
        prompt = ChatPromptTemplate.from_messages([("system", VEHICLE_SUGGESTION_PROMPT)])
        chain = prompt | llm
        return chain.invoke({"chat_history": chat_history[-3:], "input": user_input})
    
    def handle_financing(self, user_id: str, user_input: str, llm):
        """Provides financing options for the last selected car.
        If a car is available, formats the financing prompt with price and budget.
        Returns an error prompt if no car is found or an exception occurs.
        
        Args:
            user_id: Unique identifier for the user
            user_input: User's budget input
            llm: Language model instance
            
        Returns:
            Financing information response
        """
        try:
            last_car = self.redis_memory_manager.get_last_car(user_id)
            price = last_car.get("car", False) if last_car else False

            if isinstance(price, str):
                chain = (
                    ChatPromptTemplate.from_template(
                        FINANCING_PROMPT.format(price=price, budget=user_input)
                    )
                    | llm
                )
                return chain.invoke({})
            else:
                chain = ChatPromptTemplate.from_template(FINANCING_ERROR_PROMPT) | llm
                return chain.invoke({})
        except Exception as e:
            logger.error("Unexpected error: %s", e)
            logger.error("Error getting financing")
            chain = ChatPromptTemplate.from_template(FINANCING_ERROR_PROMPT) | llm
            return chain.invoke({})
    
    def tool_financing(self, user_id: str, down_payment: str) -> Tool:
        """Creates a financing tool that extracts the price from the last car
        and uses it with the down payment for financing calculations.
        
        Args:
            user_id: Unique identifier for the user
            down_payment: Down payment amount as string
            
        Returns:
            LangChain Tool for financing calculations
        """
        try:
            last_car = self.redis_memory_manager.get_last_car(user_id)
            if last_car and last_car.get("car"):
                car_data = last_car.get("car")
                
                # Extract price from car data string using regex
                price_match = re.search(r'precio[:\s]*\$?([0-9,]+)', car_data, re.IGNORECASE)
                
                if price_match:
                    price = price_match.group(1).replace(',', '')  # Remove commas
                    
                    # Create the financing tool with extracted price and down payment
                    financing_tool = Tool(
                        name="CarFinancing",
                        func=lambda x: calculate_financing(float(price), float(down_payment)),
                        description=(
                            f"Calcula planes de financiamiento de un auto. "
                            f"Precio del auto: ${price}, Enganche: ${down_payment}. "
                            f"Usa tasa fija de 10% anual y plazos de 3 a 6 años."
                        )
                    )
                    return financing_tool
                else:
                    # Fallback: return tool that requires manual input
                    financing_tool = Tool(
                        name="CarFinancing",
                        func=lambda x: calculate_financing(*map(float, x.split(","))),
                        description=(
                            f"Calcula planes de financiamiento de un auto. "
                            f"No se pudo extraer precio. Enganche: ${down_payment}. "
                            f"El input debe ser 'precio,enganche'. "
                            f"Usa tasa fija de 10% anual y plazos de 3 a 6 años."
                        )
                    )
                    return financing_tool
            else:
                # No car data available, return standard tool
                financing_tool = Tool(
                    name="CarFinancing",
                    func=lambda x: calculate_financing(*map(float, x.split(","))),
                    description=(
                        f"Calcula planes de financiamiento de un auto. "
                        f"No hay vehículo seleccionado. Enganche: ${down_payment}. "
                        f"El input debe ser 'precio,enganche'. "
                        f"Usa tasa fija de 10% anual y plazos de 3 a 6 años."
                    )
                )
                return financing_tool
                
        except Exception as e:
            logger.error("Error creating financing tool: %s", e)
            # Return fallback tool
            financing_tool = Tool(
                name="CarFinancing",
                func=lambda x: calculate_financing(*map(float, x.split(","))),
                description=(
                    f"Calcula planes de financiamiento de un auto. "
                    f"Error al obtener datos. Enganche: ${down_payment}. "
                    f"El input debe ser 'precio,enganche'. "
                    f"Usa tasa fija de 10% anual y plazos de 3 a 6 años."
                )
            )
            return financing_tool
    
    def handle_company_info(self, user_input: str, llm, vectorstore_blog):
        """Answers user questions about a company by querying the blog vectorstore
        and summarizing the response in a friendly format.
        
        Args:
            user_input: User's question about the company
            llm: Language model instance
            vectorstore_blog: Vector database containing blog/company information
            
        Returns:
            Company information response
        """
        result = ask_company_info(vectorstore_blog, user_input)
        response = result["answer"]
        chain = (
            ChatPromptTemplate.from_template(SUMMARY_FRIENDLY_PROMPT.format(text=response))
            | llm
        )
        return chain.invoke({})
    
    def handle_vehicle_question(self, user_input: str, user_id: str, vectorstore):
        """Responds to user queries about specific vehicles by searching the vectorstore.
        Saves the resulting car information to Redis for later reference.
        
        Args:
            user_input: User's vehicle-related question
            user_id: Unique identifier for the user
            vectorstore: Vector database containing vehicle information
            
        Returns:
            Vehicle information response
        """
        response = show_car_by_question(vectorstore=vectorstore, query=user_input)
        self.redis_memory_manager.save_last_car(user_id, response.content)
        return response
    
    def handle_recommendation(self, user_input: str, chat_history: list, llm):
        """Provides vehicle recommendations based on user input using a recommendation prompt.
        
        Args:
            user_input: User's input for recommendations
            chat_history: List of previous chat messages
            llm: Language model instance
            
        Returns:
            Vehicle recommendation response
        """
        prompt = ChatPromptTemplate.from_messages([("system", RECOMMENDATION_PROMPT)])
        chain = prompt | llm
        response = chain.invoke({})
        return response
    
    def handle_close_chat(self, user_id: str, llm):
        """Response with a closing message.
        
        Args:
            user_id: Unique identifier for the user
            llm: Language model instance
            
        Returns:
            Chat closing response
        """
        prompt = ChatPromptTemplate.from_messages([("system", CLOSE_CHAT_PROMPT)])
        chain = prompt | llm
        response = chain.invoke({})
        return response


# Backward compatibility functions - create default instance
from app.redis_memory import redis_memory
default_chat_service = ChatService(redis_memory)

def handle_user_input(llm, user_text: str):
    return default_chat_service.handle_user_input(llm, user_text)

def handle_welcome(llm):
    return default_chat_service.handle_welcome(llm)

def handle_random_vehicle(user_id, vectorstore):
    return default_chat_service.handle_random_vehicle(user_id, vectorstore)

def handle_vehicle_suggestion(user_input, chat_history, llm):
    return default_chat_service.handle_vehicle_suggestion(user_input, chat_history, llm)

def handle_financing(user_id: str, user_input: str, llm):
    return default_chat_service.handle_financing(user_id, user_input, llm)

def tool_financing(user_id: str, down_payment: str):
    return default_chat_service.tool_financing(user_id, down_payment)

def handle_company_info(user_input, llm, vectorstore_blog):
    return default_chat_service.handle_company_info(user_input, llm, vectorstore_blog)

def handle_vehicle_question(user_input, user_id, vectorstore):
    return default_chat_service.handle_vehicle_question(user_input, user_id, vectorstore)

def handle_recommendation(user_input, chat_history, llm):
    return default_chat_service.handle_recommendation(user_input, chat_history, llm)

def handle_close_chat(user_id, llm):
    return default_chat_service.handle_close_chat(user_id, llm)
