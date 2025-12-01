from supabase_client import db

class VillainManager:
    def __init__(self, villain_ids):
        self.villain_ids = villain_ids
        self.index = 0

    def next_villain(self):
        vid = self.villain_ids[self.index]
        self.index = (self.index + 1) % len(self.villain_ids)
        return vid

    def get_villain_info(self, villain_id):
        data = (
            db.client
            .from_("characters")
            .select("name, description")
            .eq("characterid", villain_id)
            .execute()
            .data
        )
        if data and len(data) > 0:
            return data[0]["name"], data[0]["description"]
        return "Unknown Villain", "No description available."
