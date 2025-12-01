import random

class BotPlayer:
    def __init__(self, difficulty, all_letters):
        self.difficulty = difficulty
        self.all_letters = all_letters
        self.guessed = set()

    def should_guess(self):
        # probability thresholds
        thresholds = {"easy": 0.25, "medium": 0.40, "hard": 0.55}
        return random.random() < thresholds.get(self.difficulty, 0.25)

    def make_guess(self):
        remaining = [l for l in self.all_letters if l not in self.guessed]
        if not remaining:
            return None
        guess = random.choice(remaining)
        self.guessed.add(guess)
        return guess
