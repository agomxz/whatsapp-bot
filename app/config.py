import os
from dotenv import load_dotenv
import logging
import sys

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_KEY = os.getenv("TWILIO_KEY")
CHROMA_DIR = os.getenv("CHROMA_DIR")
CHROMA_DB = os.getenv("CHROMA_DB")
CHROMA_DB_BLOG = os.getenv("CHROMA_DB_BLOG")
REDIS_URL = os.getenv("REDIS_URL")
TO_WHATSAPP = os.getenv("TO_WHATSAPP")
FROM_WHATSAPP = os.getenv("FROM_WHATSAPP")


KAVAK_WEBSITE = "https://www.kavak.com/mx/blog/sedes-de-kavak-en-mexico"

logger = logging.getLogger("whatsapp-bot")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)

logger.propagate = False
