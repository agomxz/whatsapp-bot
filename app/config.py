import os
from dotenv import load_dotenv
import logging
import sys
from typing import Optional, Any

load_dotenv()


class MissingEnvironmentVariableError(Exception):
    """Raised when a required environment variable is missing."""

    def __init__(self, var_name: str):
        self.var_name = var_name
        self.message = f"Required environment variable '{var_name}' is not set."
        super().__init__(self.message)


def get_required_env(var_name: str, default: Any = None) -> str:
    """Get an environment variable or raise an error if not found.

    Args:
        var_name: Name of the environment variable
        default: Default value to return if variable is not found (raises error if None)

    Returns:
        The value of the environment variable or the default value

    Raises:
        MissingEnvironmentVariableError: If the environment variable is not set and no default is provided
    """
    value = os.getenv(var_name, default)
    if value is None:
        raise MissingEnvironmentVariableError(var_name)
    return value


# Required variables
CHROMA_DIR = get_required_env("CHROMA_DIR", "./chroma")
CHROMA_DB = get_required_env("CHROMA_DB", "data")

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))
LLM_CONTEXT_WINDOW = int(os.getenv("LLM_CONTEXT_WINDOW", "2048"))
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
REDIS_HOST = get_required_env("REDIS_HOST", "localhost")
REDIS_PORT = get_required_env("REDIS_PORT", "6380")

# Optional variables with defaults
OLLAMA_URL = get_required_env("OLLAMA_URL", "http://localhost:11434")

logger = logging.getLogger("IA Agent")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)

logger.propagate = False
