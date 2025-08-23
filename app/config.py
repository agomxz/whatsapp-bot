import os
from dotenv import load_dotenv
import logging
import sys

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_KEY = os.getenv("TWILIO_KEY")
CHROMA_DIR = "./chroma_db"
CHROMA_DB = 'autos'




logger = logging.getLogger("whatsapp-bot")

logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)

logger.propagate = False