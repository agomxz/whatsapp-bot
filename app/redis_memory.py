from langchain.schema import AIMessage, HumanMessage
import redis
import json
from langchain.memory import ConversationBufferMemory
from app.config import REDIS_HOST, REDIS_PORT
from app.config import logger
import pickle

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def load_memory(user_id: str):   
    """
    Busca si existe el usuario en la memoria del bot
    """ 
    data = r.get(user_id)    
    if data:
        #Si existe lo carga de redis
        return pickle.loads(data)
    
    #Si no lo crea
    return ConversationBufferMemory(memory_key="chat_history", return_messages=True)



def save_memory(user_id: str, memory):
    r.set(user_id, pickle.dumps(memory))
        

# --- Serialización para Redis ---
def serialize_messages(messages):
    serialized = []
    for m in messages:
        if isinstance(m, AIMessage):
            serialized.append({"role": "ai", "content": m.content})
        elif isinstance(m, HumanMessage):
            serialized.append({"role": "user", "content": m.content})
        elif isinstance(m, dict):
            serialized.append(m)
    return serialized




def deserialize_messages(messages):
    deserialized = []
    for m in messages:
        role = m.get("role")
        content = m.get("content")
        if role == "ai":
            deserialized.append(AIMessage(content=content))
        elif role == "user":
            deserialized.append(HumanMessage(content=content))
        else:
            deserialized.append(m)
    return deserialized






def get_chat_memory(user_id):
    data = r.get(f"chat:{user_id}")
    if data:
        messages = json.loads(data)
        return deserialize_messages(messages)
    return []


def save_chat_memory(user_id, messages):
    r.set(f"chat:{user_id}", json.dumps(serialize_messages(messages)), ex=86400)



def get_last_car(user_id):
    data = r.get(f"last_car:{user_id}")
    return json.loads(data) if data else None

def save_last_car(user_id, car_data):
    r.set(f"last_car:{user_id}", json.dumps(car_data), ex=86400)

