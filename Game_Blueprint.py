import random
from hangman_agent import hangman_agent

def update_revealed(word, guessed_letters):
    return ''.join([letter if letter in guessed_letters else '_' for letter in word])

def display_progress(word, guessed_letters):
    return ' '.join([letter if letter in guessed_letters else '_' for letter in word])

def main():
  # this is just an example. We can place our database table Here
    word_list = ["hangman", "python", "challenge", "developer", "agent"]
    word = random.choice(word_list)
    human_guessed = set()
    ai_guessed = set()
    human_attempts = 6
    ai_attempts = 6
    winner = None

    print("Let's play Hangman Duel!")
    print("Both players try to guess the same phrase.")
    print("Word:", display_progress(word, set()))

    turn = "human"  # Human starts

    while True:
        # Show progress for both
        print("-" * 30)
        print(f"Current word: {display_progress(word, human_guessed | ai_guessed)}")
        print(f"Human mistakes left: {human_attempts}")
        print(f"AI mistakes left: {ai_attempts}")
        print(f"Human guessed: {sorted(human_guessed)}")
        print(f"AI guessed: {sorted(ai_guessed)}")
        print("-" * 30)

        # Check win/loss
        current_revealed = update_revealed(word, human_guessed | ai_guessed)
        if '_' not in current_revealed:
            winner = turn
            break
        if human_attempts == 0:
            winner = "AI"
            break
        if ai_attempts == 0:
            winner = "human"
            break

        if turn == "human":
            guess = input("Your guess: ").lower()
            if not (guess.isalpha() and len(guess) == 1):
                print("Please enter a single alphabetical letter.")
                continue
            if guess in human_guessed | ai_guessed:
                print("That letter has already been guessed.")
                continue
            human_guessed.add(guess)
            if guess in word:
                print("Correct! Go again.")
                continue  # Human gets another turn
            else:
                print("Incorrect!")
                human_attempts -= 1
                turn = "AI"
        else:  # AI's turn
            guess = hangman_agent(human_guessed | ai_guessed, current_revealed, word)
            print(f"AI guesses: {guess}")
            ai_guessed.add(guess)
            if guess in word:
                print("AI correct! AI goes again.")
                continue  # AI gets another turn
            else:
                print("AI incorrect!")
                ai_attempts -= 1
                turn = "human"

    print("=" * 30)
    print(f"Final word: {display_progress(word, human_guessed | ai_guessed)}")
    if winner == "human":
        print("Congratulations! You win!")
    elif winner == "AI":
        print("AI wins!")
    else:
        print(f"{winner.capitalize()} guessed the word and wins!")
    print(f"The word was: {word}")

if __name__ == "__main__":
    main()
