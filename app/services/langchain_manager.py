"""LangChain manager for managing LLM instances and chains."""
from typing import Optional, Dict, Any
from langchain_community.llms import Ollama
from app.config import LLM_MODEL, OLLAMA_URL, LLM_TEMPERATURE, LLM_TOP_P, LLM_CONTEXT_WINDOW


class LangChainManager:
    """Singleton manager for LangChain components.
    
    This manager provides centralized access to LLM instances and chains,
    ensuring efficient resource usage and consistent configuration.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LangChainManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize LangChain components."""
        self.llm = Ollama(
            model=LLM_MODEL,
            base_url=OLLAMA_URL,
            temperature=LLM_TEMPERATURE,
            top_p=LLM_TOP_P,
            num_ctx=LLM_CONTEXT_WINDOW
        )
        self.chains: Dict[str, Any] = {}

    def get_llm(self) -> Ollama:
        """Get the LLM instance.
        
        Returns:
            Ollama: The configured LLM instance
        """
        return self.llm

    def get_chain(self, chain_type: str, **kwargs) -> Any:
        """Get or create a chain of the specified type.
        
        Args:
            chain_type: Type of chain to get/create
            **kwargs: Additional arguments for chain creation
            
        Returns:
            The requested chain instance
            
        Raises:
            ValueError: If the chain type is not supported
        """
        if chain_type not in self.chains:
            if chain_type == "conversation":
                from langchain.chains import ConversationChain
                from langchain.memory import ConversationBufferWindowMemory
                
                memory = kwargs.pop('memory', None) or ConversationBufferWindowMemory(
                    k=10,
                    memory_key="chat_history",
                    return_messages=True
                )
                
                self.chains[chain_type] = ConversationChain(
                    llm=self.llm,
                    memory=memory,
                    **kwargs
                )
            else:
                raise ValueError(f"Unsupported chain type: {chain_type}")
        return self.chains[chain_type]


# Create a singleton instance
langchain_manager = LangChainManager()
