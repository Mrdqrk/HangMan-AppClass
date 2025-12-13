import os
import random
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class SupabaseClient:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise RuntimeError(
                "Missing Supabase configuration. "
                f"SUPABASE_URL={url}, SUPABASE_KEY_SET={bool(key)}"
            )

        self.client: Client = create_client(url, key)

    # player
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

    # game
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

    # phrase
    def get_random_phrase(self, difficulty="medium"):
        allowed = {"cowboy", "cowboys", "pixar", "social"}

        result = (
            self.client
            .from_("phrases")
            .select("phraseid, phrasetext, category, difficulty")
            .execute()
        )

        rows = result.data or []
        rows = [
            r for r in rows
            if (r.get("difficulty") or "").strip().lower() == difficulty.lower()
            and (r.get("category") or "").strip().lower() in allowed
        ]

        if rows:
            choice = random.choice(rows)
            return choice["phraseid"], choice["phrasetext"], choice.get("category", "")

        return None, None, None

    # guesses
    def record_guess(self, gameid, playerid, letter, correct):
        data = {
            "gameid": gameid,
            "playerid": playerid,
            "guessedletter": letter,
            "correct": correct
        }
        return self.client.from_("guesses").insert(data).execute()

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
            return self.client.rpc("increment_score", {
                "p_gameid": gameid,
                "p_playerid": playerid
            }).execute()
        except Exception:
            return None

    # leaderboard
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
        return result.data


db = SupabaseClient()
