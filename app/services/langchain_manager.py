"""LangChain manager for managing LLM instances and chains."""

from typing import Dict, Any
from langchain_community.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from app.config import (
    OLLAMA_URL,
    LLM_TEMPERATURE,
    LLM_TOP_P,
    LLM_CONTEXT_WINDOW,
)

# RAG prompt template
RAG_PROMPT_TEMPLATE = """You are a helpful vehicle assistant. Use the following context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}
Helpful Answer:"""


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
        # Always use 'llama3' model regardless of config
        self.llm = Ollama(
            model="llama3",  # Explicitly set to llama3
            base_url=OLLAMA_URL,
            temperature=LLM_TEMPERATURE,
            top_p=LLM_TOP_P,
            num_ctx=LLM_CONTEXT_WINDOW,
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

                memory = kwargs.pop("memory", None) or ConversationBufferWindowMemory(
                    k=10, memory_key="history", return_messages=True
                )

                self.chains[chain_type] = ConversationChain(
                    llm=self.llm, memory=memory, **kwargs
                )
            elif chain_type == "rag":

                prompt = PromptTemplate(
                    template=RAG_PROMPT_TEMPLATE,
                    input_variables=["context", "question"],
                )

                self.chains[chain_type] = LLMChain(
                    llm=self.llm, prompt=prompt, **kwargs
                )
            else:
                raise ValueError(f"Unsupported chain type: {chain_type}")
        return self.chains[chain_type]

    def get_rag_chain(self, **kwargs) -> Any:
        """Get or create a RAG chain.

        Returns:
            LLMChain: Configured RAG chain
        """
        return self.get_chain("rag", **kwargs)


# Create a singleton instance
langchain_manager = LangChainManager()
