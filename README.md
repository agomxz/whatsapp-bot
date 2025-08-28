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
- ✅ Get a suggestion vehicle 
- ✅ Ask for vehicle using natural lenguage
- ✅ Ask for finacing using a budget
- ✅ Ask for company information


---

## 📂 Project Structure

```mermaid
flowchart TD
    whatsapp_bot[whatsapp-bot/]
    app[app/]
    init_app[__init__.py]
    main[main.py<br>FastAPI entrypoint]
    config[config.py<br>App configuration & environment variables]
    db[db.py<br>Database connection setup]
    routes[routes/]
    routes_init[__init__.py]
    schemas[schemas/]
    schemas_init[__init__.py]
    services[services/]
    services_init[__init__.py]
    utils[utils/]
    utils_init[__init__.py]
    env[.env<br>Environment variables (Twilio SID, tokens, etc.)]
    requirements[requirements.txt<br>Python dependencies]
    readme[README.md<br>Project documentation]

    whatsapp_bot --> app
    app --> init_app
    app --> main
    app --> config
    app --> db
    app --> routes
    routes --> routes_init
    app --> schemas
    schemas --> schemas_init
    app --> services
    services --> services_init
    app --> utils
    utils --> utils_init
    whatsapp_bot --> env
    whatsapp_bot --> requirements
    whatsapp_bot --> readme
```



## 🛠️ Tools
- OpeanAI Account
- Twilio Account
- Ngrok Account (To expose API)

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

### Run with Dockerfile
```
docker build -t bot_img .
```

```
docker run --name botcontainer --env-file .env -p 8000:8000 botimg
```


### Use ngrok to expose webhook
**Note: Use Ngrok token**
```
ngrok http http://localhost:8000
```

----
### How to run it with Docker-compose

```
docker compose build
```

```
docker compose up
```


#### Example env file
```
OPENAI_API_KEY=xxxxxxxxxxx
TWILIO_TOKEN=xxxxxxxxxxxxx
REDIS_URL=xxxxxxxxxxxxxx
TO_WHATSAPP=XXXXXXXX
FROM_WHATSAPP=XXXXXXXX
CHROMA_DIR =XXXXXXXX
CHROMA_DB=XXXXXXXX
CHROMA_DB_BLOG=XXXXXXXX
```