import os
import random
from supabase import create_client, Client
from dotenv import load_dotenv


load_dotenv()


class SupabaseClient:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        # Debug prints 
        print("DEBUG SUPABASE_URL:", repr(url))
        print("DEBUG SUPABASE_KEY set?:", bool(key))

        if not url or not key:
            raise RuntimeError(
                "Missing Supabase configuration. "
                f"SUPABASE_URL={url}, SUPABASE_KEY_SET={bool(key)}"
            )

        # Supabase client
        self.client: Client = create_client(url, key)

    # Player
    def get_or_create_player(self, username):
        result = (
            self.client
            .from_("players")
            .select("playerid")
            .eq("playername", username)
            .execute()
        )
        if result.data and len(result.data) > 0:
            return result.data[0]["playerid"]

        insert = (
            self.client
            .from_("players")
            .insert({"playername": username})
            .execute()
        )
        return insert.data[0]["playerid"]

    # Game
    def start_game(self, phraseid, playerid):
        game = (
            self.client
            .from_("games")
            .insert({"phraseid": phraseid})
            .execute()
        )
        gameid = game.data[0]["gameid"]

        self.client.from_("gameplayers").insert({
            "gameid": gameid,
            "playerid": playerid,
            "score": 0
        }).execute()

        return gameid

    def update(self, table, values, match):
        return self.client.from_(table).update(values).match(match).execute()

    # Phrase
    def get_random_phrase(self, difficulty="medium"):
        result = (
            self.client
            .from_("phrases")
            .select("phraseid, phrasetext, category")
            .eq("difficulty", difficulty)
            .execute()
        )
        if result.data and len(result.data) > 0:
            choice = random.choice(result.data)
            return choice["phraseid"], choice["phrasetext"], choice.get("category", "")
        return None, None, None

    # Guess
    def record_guess(self, gameid, playerid, letter, correct):
        data = {
            "gameid": gameid,
            "playerid": playerid,
            "guessedletter": letter,
            "correct": correct
        }
        result = self.client.from_("guesses").insert(data).execute()
        print(f"[DEBUG] record_guess: {data}, Result={result}")
        return result

    def get_score(self, gameid, playerid):
        result = (
            self.client
            .from_("gameplayers")
            .select("score")
            .eq("gameid", gameid)
            .eq("playerid", playerid)
            .execute()
        )
        if result.data and len(result.data) > 0:
            return result.data[0]["score"]
        return 0

    def increment_score(self, gameid, playerid):
        try:
            result = self.client.rpc("increment_score", {
                "p_gameid": gameid,
                "p_playerid": playerid
            }).execute()
            print(f"[DEBUG] increment_score: gameid={gameid}, playerid={playerid}, Result={result}")
            return result
        except Exception as e:
            print(f"[ERROR] increment_score failed: {e}")
            return None

    # Body
    def reveal_part(self, gameid, partid):
        return (
            self.client
            .from_("revealed_parts")
            .insert({"gameid": gameid, "partid": partid, "revealed": True})
            .execute()
        )

    # Leader
    def get_leaderboard(self, difficulty):
        result = (
            self.client
            .from_("leaderboard")
            .select("*")
            .eq("difficulty", difficulty)
            .order("total_score", desc=True)
            .limit(10)
            .execute()
        )
        print(f"[DEBUG] get_leaderboard: Difficulty={difficulty}, Result={result.data}")
        return result.data


# Singleton instance
db = SupabaseClient()
