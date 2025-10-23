import os
import json
from supabase import create_client, Client
from postgrest.exceptions import APIError

class SupabaseManager:
    """
    A portable Supabase client that loads credentials from environment variables
    or falls back to config.json if present.
    """

    def __init__(self):
        # Try environment variables first
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        # Fallback to config.json if environment variables are missing
        if not supabase_url or not supabase_key:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            if os.path.exists(config_path):
                with open(config_path) as f:
                    config = json.load(f)
                    supabase_url = config.get("SUPABASE_URL")
                    supabase_key = config.get("SUPABASE_KEY")

        # If still missing, raise error
        if not supabase_url or not supabase_key:
            raise ValueError(
                "Supabase credentials not found. "
                "Set SUPABASE_URL and SUPABASE_KEY as environment variables "
                "or create a config.json file."
            )

        # Initialize the client
        self.client: Client = create_client(supabase_url, supabase_key)

    # ------------------------
    # CRUD Operations
    # ------------------------

    def get_all(self, table: str):
        try:
            result = self.client.table(table).select("*").execute()
            return result.data
        except APIError as e:
            print("Error fetching data:", e)
            return []

    def insert(self, table: str, data: dict):
        try:
            result = self.client.table(table).insert(data).execute()
            return result.data
        except APIError as e:
            print("Insert error:", e)
            return None

    def update(self, table: str, updates: dict, filters: dict):
        query = self.client.table(table).update(updates)
        for key, value in filters.items():
            query = query.eq(key, value)
        try:
            return query.execute().data
        except APIError as e:
            print("Update error:", e)
            return None

    def delete(self, table: str, filters: dict):
        query = self.client.table(table).delete()
        for key, value in filters.items():
            query = query.eq(key, value)
        try:
            return query.execute().data
        except APIError as e:
            print("Delete error:", e)
            return None

    def filter(self, table: str, filters: dict):
        query = self.client.table(table).select("*")
        for key, value in filters.items():
            query = query.eq(key, value)
        try:
            return query.execute().data
        except APIError as e:
            print("Filter error:", e)
            return []

# ------------------------
# Global instance for easy imports
# ------------------------
db = SupabaseManager()

# Example usage
if __name__ == "__main__":
    print("All players:", db.get_all("players"))
