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
.
├── main.py # FastAPI entry point
├── requirements.txt # Python dependencies
├── .env.example # Environment variables template
├── README.md # Project documentation
└── app/
├── routes.py # API routes (WhatsApp webhook)
├── services.py # Bot logic and OpenAI integration
└── utils.py # Helpers and tools