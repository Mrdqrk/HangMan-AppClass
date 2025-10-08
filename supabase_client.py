# supabase_client.py 
import os
from supabase  import create_client, Client

# Load base info from environment variables for safety
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jaduiuxggmwxftpltvvh.supabase.co/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImphZHVpdXhnZ213eGZ0cGx0dnZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4ODcwODAsImV4cCI6MjA3NTQ2MzA4MH0.eSph4F9e8K6c5lwRpGAYZYZDOdKP-uCUoaFWidaoF-8")

# Initialize the Supabase client once
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
