import random
from hangman_agent import hangman_agent
import string
// import mysql.connector
import supabase_client

def get_random_phrase(cursor):
    cursor.execute("SELECT phraseText FROM phrases ORDER BY RAND() LIMIT 1;")
    res = cursor.fetchone()
    if res:
        return res[0]
    else:
        return None

def update_revealed(phrase, guessed_letters):
    return ''.join([
        char if not char.isalpha() or char.lower() in guessed_letters else '_'
        for char in phrase
    ])

def display_progress(phrase, guessed_letters):
    return ' '.join([
        char if not char.isalpha() or char.lower() in guessed_letters else '_'
        for char in phrase
    ])

# def main():
#   # this is just an example. We can place our database table Here
#     word_list = ["hangman", "python", "challenge", "developer", "agent", "TL;DR", "Hello, World", "There's a SNAKE in my boot"]
#    # word = random.choice(word_list)
def main():
    # --- Connect to the DB ---
    conn = mysql.connector.connect(
        host="Hangmanhost",
        user="HangmanTeam",       # CHANGE THIS
        password="DKDonkeyKong",   # CHANGE THIS
        database="hangDb"
    )
    cursor = conn.cursor()

    phrase = get_random_phrase(cursor)
    if not phrase:
        print("No phrases found in the database!")
        return
    # phrase = random.choice(word_list)
    human_guessed = set()
    ai_guessed = set()
    human_attempts = 6
    ai_attempts = 6
    winner = None

    print("Let's play Hangman Duel!")
    print("Both players try to guess the same phrase.")
    print("Word:", display_progress(phrase, set()))

    turn = "Your turn"  # Human starts

    while True:
        # Show progress for both
        print("-" * 30)
        print(f"Current phrase: {display_progress(phrase, human_guessed | ai_guessed)}")
        print(f"Human mistakes left: {human_attempts}")
        print(f"AI mistakes left: {ai_attempts}")
        print(f"Human guessed: {sorted(human_guessed)}")
        print(f"AI guessed: {sorted(ai_guessed)}")
        print("-" * 30)

        # Check win/loss
        current_revealed = update_revealed(phrase, human_guessed | ai_guessed)
        if '_' not in current_revealed:
            winner = turn
            break
        if human_attempts == 0:
            winner = "AI"
            break
        if ai_attempts == 0:
            winner = "Your turn"
            break

        if turn == "Your turn":
            guess = input("Your guess: ").strip()
            #if not (guess.isalpha() and len(guess) == 1):
            if len(guess) != 1 or not guess.isalpha():
                print("Please enter a single alphabetical letter.")
                continue
            guess = guess.lower()
            if guess in human_guessed | ai_guessed:
                print("That letter has already been guessed.")
                continue
            human_guessed.add(guess)
            #if guess in phrase:
            if any(char.lower() == guess for char in phrase if char.isalpha()):
                print("Correct! Go again.")
                continue  # Human gets another turn
            else:
                print("Incorrect!")
                human_attempts -= 1
                turn = "AI"
        else:  # AI's turn
            guess = hangman_agent(human_guessed | ai_guessed, current_revealed, phrase)
            print(f"AI guesses: {guess}")
            ai_guessed.add(guess)
            #if guess in phrase:
            if any(char.lower() == guess for char in phrase if char.isalpha()):
                print("AI correct! AI goes again.")
                continue  # AI gets another turn
            else:
                print("AI incorrect!")
                ai_attempts -= 1
                turn = "Your turn"

    print("=" * 30)
    print(f"Final word: {display_progress(phrase, human_guessed | ai_guessed)}")
    if winner == "Your turn":
        print("Congratulations! You win!")
    elif winner == "AI":
        print("AI wins!")
    else:
        print(f"{winner.capitalize()} guessed the word and wins!")
    print(f"The word was: {phrase}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
