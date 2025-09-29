import string

def hangman_agent(guessed_letters, revealed_phrase, word):
    alphabet = set(string.ascii_lowercase)
    remaining = list(alphabet - set(guessed_letters))
    if remaining:
        return random.choice(remaining)
    else:
        return None
