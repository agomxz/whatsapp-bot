# 🚗 WhatsApp Car Sales Bot

This project is a **WhatsApp chatbot** built with **FastAPI** and **OpenAI models** to help automate the sales process of car-related products.  
The bot connects to the **WhatsApp Cloud API (Meta)**, receives customer messages, and responds intelligently using **LangChain** with OpenAI.

---

## ✨ Features
- ✅ Integration with **WhatsApp Cloud API**  
- ✅ Powered by **OpenAI models** for natural conversations  
- ✅ Built with **FastAPI** for scalability  
- ✅ `.env` configuration support (via `python-dotenv`)  
- ✅ Easily extendable to support multiple products and categories  

---

## 📂 Project Structure
whatsapp-bot/
│── app/
│ ├── init.py
│ ├── main.py # FastAPI entrypoint
│ ├── config.py # App configuration & environment variables
│ ├── db.py # Database connection setup
│ ├── routes/ # API route definitions
│ │ └── init.py
│ ├── schemas/ # Pydantic schemas (request/response validation)
│ │ └── init.py
│ ├── services/ # Business logic and integrations
│ │ └── init.py
│ ├── utils/ # Utility/helper functions
│ └── init.py
│
├── .env # Environment variables (Twilio SID, tokens, etc.)
├── requirements.txt # Python dependencies
└── README.md # Project documentation


## Tools
- OpeanAI Account
- Twilio Account
- Ngrok Account
- Railway


## How to run local
´´´
app.main:app --reload --port 8000


´´´
### Use ngrok to expose webhook

ngrok http http://localhost:8000

