import os
import bcrypt
import hashlib
from dotenv import load_dotenv


def load_secrets():
    load_dotenv()
    return {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
    }


def hash_text(text: str) -> bytes:
    return bcrypt.hashpw(text.encode(), bcrypt.gensalt())



def verify_text(text: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(text.encode(), hashed)



def sanitize_letter(letter: str) -> str:
    letter = letter.strip().lower()
    if len(letter) !=1 or not letter.isalpha():
        return None
    return letter



def file_checksum(path: str) -> str:
    try: 
        with open(path, "rb") as f:
            data = f.read()
        return hashlib.sha256(data).hexdigest()
    except FileNotFoundError:
        return None
    