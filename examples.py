
# main.py
from supabase_client import db


#{db.push,pull,delete,&update}


# Pull all players 
print("=== All players ===")
players = db.pull("players")
print(players)

# Push a new player 
print("\n=== Adding David ===")
push_response = db.push("players", {"playername": "David", "comp": True})
print(push_response)  # Should show insert response

# Pull filtered data 
print("\n=== Pull players where comp=True ===")
competitive_players = db.pull("players", {"comp": True})
print(competitive_players)  # Should include David

# Update a row 
print("\n=== Updating David to comp=False ===")
update_response = db.update("players", {"comp": False}, {"playername": "David"})
print(update_response)  # Should show update response

# Delete the test row 
print("\n=== Deleting David ===")
delete_response = db.delete("players", {"playername": "David"})
print(delete_response)  # Should show delete response

# Final pull to confirm deletion 
print("\n=== All players after deletion ===")
final_players = db.pull("players")
print(final_players)

