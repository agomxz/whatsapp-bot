import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_KEY = os.getenv("TWILIO_KEY")
CHROMA_DIR = "./chroma_db"
CHROMA_DB = 'autos'