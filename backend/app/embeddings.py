import os
from sentence_transformers import SentenceTransformer
from cryptography.fernet import Fernet
import numpy as np
from .db.dynamo_client import db_client

# Load or generate encryption key
FERNET_KEY = os.getenv('FERNET_KEY')
if not FERNET_KEY:
    FERNET_KEY = Fernet.generate_key().decode()
    # In production, store this securely!
fernet = Fernet(FERNET_KEY.encode())

# Load embedding model
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
model = SentenceTransformer(EMBEDDING_MODEL)

def generate_embedding(text: str) -> np.ndarray:
    embedding = model.encode([text])[0]
    return embedding

def encrypt_embedding(embedding: np.ndarray) -> bytes:
    emb_bytes = embedding.astype(np.float32).tobytes()
    return fernet.encrypt(emb_bytes)

def decrypt_embedding(enc_bytes: bytes) -> np.ndarray:
    dec_bytes = fernet.decrypt(enc_bytes)
    return np.frombuffer(dec_bytes, dtype=np.float32)

def store_habit_embedding(user_id: str, habit_id: str, text: str, table_name: str = 'Habits'):
    embedding = generate_embedding(text)
    enc_embedding = encrypt_embedding(embedding)
    # Update the Habits table item with the new HabitEmbedding attribute
    key = {'UserID': user_id, 'HabitID': habit_id}
    update_expression = 'SET HabitEmbedding = :emb'
    expression_attribute_values = {':emb': enc_embedding.hex()}
    db_client.update_item(table_name, key, update_expression, expression_attribute_values)
    return {'UserID': user_id, 'HabitID': habit_id, 'HabitEmbedding': enc_embedding.hex()}

def get_habit_embedding(user_id: str, habit_id: str, table_name: str = 'Habits'):
    key = {'UserID': user_id, 'HabitID': habit_id}
    item = db_client.get_item(table_name, key)
    if item and 'HabitEmbedding' in item:
        enc_embedding = bytes.fromhex(item['HabitEmbedding'])
        return decrypt_embedding(enc_embedding)
    return None 