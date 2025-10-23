from supabase_client import db

# Get all players
players = db.get_all("players")
print("=== All players ===")
print(players)

# Insert a new player
new_player = db.insert("players", {"playername": "David", "comp": True})
print("=== Added David ===")
print(new_player)

# Filter players where comp=True
competitive_players = db.filter("players", {"comp": True})
print("=== Competitive players ===")
print(competitive_players)

# Update David to comp=False
updated = db.update("players", {"comp": False}, {"playername": "David"})
print("=== Updated David ===")
print(updated)

# Delete David
deleted = db.delete("players", {"playername": "David"})
print("=== Deleted David ===")
print(deleted)
