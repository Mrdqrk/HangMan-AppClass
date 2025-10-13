import json, os
from supabase import create_client, Client

# Load credentials from config.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

SUPABASE_URL = config["SUPABASE_URL"]
SUPABASE_KEY = config["SUPABASE_KEY"]

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

#Function list
class SupabaseDB:
    def __init__(self, client: Client):
        self.client = client

    def push(self, table: str, data: dict):
        # Insert data into a table
        return self.client.table(table).insert(data).execute()

    def pull(self, table: str, filters: dict = None):
        # Select data from a table (with optional filters)
        query = self.client.table(table).select("*")
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        return query.execute().data

    def update(self, table: str, data: dict, filters: dict):
        # Update data in a table where filters match
        query = self.client.table(table).update(data)
        for key, value in filters.items():
            query = query.eq(key, value)
        return query.execute()

    def delete(self, table: str, filters: dict):
        # Delete rows matching filters
        query = self.client.table(table).delete()
        for key, value in filters.items():
            query = query.eq(key, value)
        return query.execute()

db = SupabaseDB(supabase)
