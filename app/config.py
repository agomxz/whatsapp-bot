import os
from dotenv import load_dotenv
import logging
import sys

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_KEY = os.getenv("TWILIO_KEY")
CHROMA_DIR = "./chroma_db"
CHROMA_DB = "autos"
CHROMA_DB_BLOG = "blog"
REDIS_URL = os.getenv("REDIS_URL")

TO_WHATSAPP = "whatsapp:+5215579123590"
FROM_WHATSAPP = "whatsapp:+14155238886"
TWILIO_ACCOUNT_SID = "AC89a4f161a470135a4c8267f35f85d120"
TWILIO_CONTENT_SID = "HXb5b62575e6e4ff6129ad7c8efe1f983e"


KAVAK_WEBSITE = "https://www.kavak.com/mx/blog/sedes-de-kavak-en-mexico"

logger = logging.getLogger("whatsapp-bot")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)

logger.propagate = False
