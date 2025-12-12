# bot_player.py
import random
import string


class BotPlayer:
    # Common English letters in frequency order
    COMMON_LETTERS = list("ETAOINSHRDLU")

    def __init__(self, difficulty, all_letters=None):

        self.difficulty = difficulty
        self.guessed = set()
        self.all_letters = list(all_letters) if all_letters is not None else list(string.ascii_uppercase)

    def reset(self):

        self.guessed.clear()

    def make_guess(self):

        remaining = [l for l in self.all_letters if l not in self.guessed]
        if not remaining:
            return None

        # HARD: always try common letters first
        if self.difficulty == "hard":
            for letter in self.COMMON_LETTERS:
                if letter in remaining:
                    self.guessed.add(letter)
                    return letter
            guess = random.choice(remaining)

        # MEDIUM: 50% smart, 50% random
        elif self.difficulty == "medium":
            if random.random() < 0.5:
                smart_choices = [l for l in self.COMMON_LETTERS if l in remaining]
                if smart_choices:
                    guess = random.choice(smart_choices)
                else:
                    guess = random.choice(remaining)
            else:
                guess = random.choice(remaining)

        # EASY: mostly random, sometimes picks a good letter by accident
        else:  # "easy" or anything else
            if random.random() < 0.2:
                smart_choices = [l for l in self.COMMON_LETTERS if l in remaining]
                if smart_choices:
                    guess = random.choice(smart_choices)
                else:
                    guess = random.choice(remaining)
            else:
                guess = random.choice(remaining)

        self.guessed.add(guess)
        return guess
