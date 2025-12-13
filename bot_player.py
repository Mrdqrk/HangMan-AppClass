import random
import string


class BotPlayer:
    # letter frequency (most to least common letters)
    FREQ_ORDER = list("ETAOINSHRDLCUMWFGYPBVKJXQZ")

    def __init__(self, difficulty, all_letters=None):
        self.difficulty = (difficulty or "medium").strip().lower()
        self.guessed = set()
        self.all_letters = list(all_letters) if all_letters is not None else list(string.ascii_uppercase)
        self.all_letters = [c.upper() for c in self.all_letters if c.isalpha()]

        ranked = [c for c in self.FREQ_ORDER if c in self.all_letters]
        for c in self.all_letters:
            if c not in ranked:
                ranked.append(c)
        self.ranked = ranked

    def reset(self):
        self.guessed.clear()

    def should_guess(self) -> bool:
        # when bot will act
        return True

    def make_guess(self):
        remaining = [l for l in self.all_letters if l not in self.guessed]
        if not remaining:
            return None

        available_ranked = [c for c in self.ranked if c in remaining]
        n = len(available_ranked)

        top_end = max(1, int(n * 0.30))            # top 30%
        mid_end = max(top_end + 1, int(n * 0.70))  # up to 70%

        top_band = available_ranked[:top_end]
        mid_band = available_ranked[top_end:mid_end]
        low_band = available_ranked[mid_end:] if mid_end < n else []

        if self.difficulty == "hard":
            r = random.random()
            if r < 0.85 and top_band:
                pool = top_band
            elif r < 0.97 and (mid_band or top_band):
                pool = mid_band if mid_band else top_band
            else:
                pool = low_band if low_band else remaining

        elif self.difficulty == "easy":
            r = random.random()
            if r < 0.15 and top_band:
                pool = top_band
            elif r < 0.50 and (mid_band or top_band):
                pool = mid_band if mid_band else top_band
            else:
                pool = low_band if low_band else remaining

        else:  # medium
            r = random.random()
            if r < 0.55 and top_band:
                pool = top_band
            elif r < 0.90 and (mid_band or top_band):
                pool = mid_band if mid_band else top_band
            else:
                pool = low_band if low_band else remaining

        guess = random.choice(pool)
        self.guessed.add(guess)
        return guess
