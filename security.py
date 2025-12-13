import os
import bcrypt
import hashlib
from dotenv import load_dotenv


def load_secrets():
    load_dotenv("secret.env")
    return {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
    }


def create_user(username, password):
    from supabase_client import db
    hashed = hash_text(password)
    db.client.from_("players").insert({
        "playername": username,
        "password_hash": hashed.decode()
    }).execute()


def authenticate(username, password):
    from supabase_client import db
    result = db.client.from_("players").select("*").eq("playername", username).execute()

    if not result.data:
        return False

    row = result.data[0]

    if "password_hash" not in row or not row["password_hash"]:
        return False

    stored_hash = row["password_hash"].encode()
    return verify_text(password, stored_hash)


def hash_text(text: str) -> bytes:
    return bcrypt.hashpw(text.encode(), bcrypt.gensalt())


def verify_text(text: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(text.encode(), hashed)


def sanitize_letter(letter: str) -> str:
    letter = letter.strip().lower()
    if len(letter) != 1 or not letter.isalpha():
        return None
    return letter


def file_checksum(path: str) -> str:
    try:
        with open(path, "rb") as f:
            data = f.read()
        return hashlib.sha256(data).hexdigest()
    except FileNotFoundError:
        return None
