# 🚗 WhatsApp Car Sales Bot

This project is a **WhatsApp Chatbot** built with **FastAPI** and **OpenAI models** to help automate the sales process of car-related products.  
The bot connects to the **Twilio Sandbox**, receives customer messages, and responds intelligently using **LangChain**.
---

## ✨ Features
- ✅ Integration with **Twilio Sandbox**  
- ✅ Powered by **OpenAI models** for natural conversations  
- ✅ Built with **FastAPI** for scalability  
- ✅ `.env` configuration support (via `python-dotenv`)  
- ✅ Easily extendable to support multiple products and categories  

---

## 📂 Project Structure
whatsapp-bot/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI entrypoint
│   ├── config.py        # App configuration & environment variables
│   ├── db.py            # Database connection setup
│   ├── routes/          # API route definitions
│   │   ├── __init__.py
│   ├── schemas/         # Pydantic schemas (request/response validation)
│   │   ├── __init__.py
│   ├── services/        # Business logic and integrations
│   │   ├── __init__.py
│   └── utils/           # Utility/helper functions
│       ├── __init__.py
├── .env                 # Environment variables (Twilio SID, tokens, etc.)
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation



## 🛠️ Tools
- OpeanAI Account
- Twilio Account
- Ngrok Account (To expose API)
- Railway

---

# How to run local
```
python3 -m venv venv
```

```
pip install -r requirements.txt
```

```
app.main:app --reload --port 8000
```

### Use ngrok to expose webhook
**Note: Use Ngrok token**
```
ngrok http http://localhost:8000
```


### Run with Dockerfile

```
docker build -t botimg .
```

```
docker run --name botcontainer --env-file .env -p 8000:8000 botimg
```


### Run Redis

```
docker run -d --name redis_container -p 6379:6379 redis_img 
```


### How to run it with Docker-compose

```
docker compose build
```

```
docker compose up
```


#### Example env file
```
OPENAI_API_KEY=SOMETHING
TWILIO_TOKEN=SOMETHING
```