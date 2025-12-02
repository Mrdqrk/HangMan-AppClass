import tkinter as tk
from tkinter import messagebox
from supabase_client import db
from character_loader import load_local_character
from bot_player import BotPlayer
from villain_manager import VillainManager

class HangmanGame(tk.Frame):
    def __init__(self, master, username, characterid=17, difficulty="medium"):
        super().__init__(master)
        self.master = master
        self.username = username
        self.difficulty = difficulty

        # phrase setup (now includes category)
        self.phraseid, phrase, self.category = db.get_random_phrase(difficulty)
        self.word = phrase.upper().strip() if phrase else "PYTHON"
        self.playerid = db.get_or_create_player(username)
        self.bot_playerid = db.get_or_create_player("Bot")  # separate bot player
        self.gameid = db.start_game(self.phraseid, self.playerid)

        self.guessed = set()
        self.wrong_guesses = 0
        self.bot_wrong_guesses = 0
        self.parts_order = ["head", "left_arm", "right_arm", "left_leg", "right_leg"]

        self.drawn_parts = []
        self.bot_drawn_parts = []

        self.canvas = tk.Canvas(self, width=800, height=500, bg="white")
        self.canvas.pack()

        # category display
        self.category_var = tk.StringVar(value=f"Category: {self.category}")
        tk.Label(self, textvariable=self.category_var, font=("Arial", 14), fg="gray").pack()

        # health bars
        self.player_health = tk.IntVar(value=len(self.parts_order))
        self.bot_health = tk.IntVar(value=len(self.parts_order))
        tk.Label(self, text="Player Health").pack()
        tk.Label(self, textvariable=self.player_health, font=("Arial", 14), fg="green").pack()
        tk.Label(self, text="Bot Health").pack()
        tk.Label(self, textvariable=self.bot_health, font=("Arial", 14), fg="red").pack()

        # word display
        self.word_var = tk.StringVar()
        tk.Label(self, textvariable=self.word_var, font=("Arial", 24)).pack()
        self.update_word_display()

        # bot setup
        self.bot = BotPlayer(difficulty, [chr(i) for i in range(65, 91)])
        self.bot_word_var = tk.StringVar()
        tk.Label(self, textvariable=self.bot_word_var, font=("Arial", 24), fg="purple").pack()
        self.update_bot_word_display()

        # score display
        self.score_var = tk.StringVar()
        tk.Label(self, textvariable=self.score_var, font=("Arial", 18), fg="blue").pack()
        self.update_score_display()

        # entry + button
        self.entry = tk.Entry(self)
        self.entry.pack()
        tk.Button(self, text="Guess", command=self.make_guess).pack(pady=5)

        # player torso
        self.images = load_local_character(characterid)
        self.coords = {"head": (120, 100), "torso": (120, 180),
                       "left_arm": (80, 180), "right_arm": (160, 180),
                       "left_leg": (110, 260), "right_leg": (130, 260)}
        if "torso" in self.images:
            img, partid = self.images["torso"]
            scaled = img.subsample(3, 3)
            torso_item = self.canvas.create_image(*self.coords["torso"], image=scaled)
            self.drawn_parts.append((scaled, torso_item))
            db.reveal_part(self.gameid, partid)

        # villain torso
        if not hasattr(master, "villains"):
            master.villains = VillainManager([18, 19, 20])
        self.current_villain = master.villains.next_villain()
        self.villain_images = load_local_character(self.current_villain)
        self.villain_coords = {"head": (680, 100), "torso": (680, 180),
                               "left_arm": (640, 180), "right_arm": (720, 180),
                               "left_leg": (670, 260), "right_leg": (690, 260)}
        if "torso" in self.villain_images:
            img, partid = self.villain_images["torso"]
            scaled = img.subsample(3, 3)
            torso_item = self.canvas.create_image(*self.villain_coords["torso"], image=scaled)
            self.bot_drawn_parts.append((scaled, torso_item))
            db.reveal_part(self.gameid, partid)

    def update_word_display(self):
        # show spaces immediately, underscores for unguessed letters
        display = " ".join([
            letter if (letter in self.guessed or letter == " ") else "_"
            for letter in self.word
        ])
        self.word_var.set(display)

    def update_bot_word_display(self):
        display = " ".join([
            "0" if letter in self.bot.guessed else (" " if letter == " " else "_")
            for letter in self.word
        ])
        self.bot_word_var.set(display)

    def update_score_display(self):
        score = db.get_score(self.gameid, self.playerid)
        self.score_var.set(f"Score: {score}")

    def make_guess(self):
        guess = self.entry.get().upper().strip()
        self.entry.delete(0, tk.END)

        # reject invalid input including spaces
        if not guess or len(guess) != 1 or not guess.isalpha() or guess == " ":
            messagebox.showerror("Error", "Enter a single letter (A-Z). Spaces are not allowed.")
            return

        correct = guess in self.word
        db.record_guess(self.gameid, self.playerid, guess, correct)

        if correct:
            self.guessed.add(guess)
            self.update_word_display()

            # increment score in DB
            db.increment_score(self.gameid, self.playerid)

            # refresh score display
            self.update_score_display()

            if all(letter in self.guessed or letter == " " for letter in self.word):
                db.update("games", {"status": "won"}, {"gameid": self.gameid})
                messagebox.showinfo("Win", f"You guessed the word: {self.word}")
        else:
            self.wrong_guesses += 1
            self.player_health.set(len(self.parts_order) - self.wrong_guesses)

            # reveal next player part (on wrong guess only)
            if self.wrong_guesses <= len(self.parts_order):
                part = self.parts_order[self.wrong_guesses - 1]
                if part in self.images:
                    img, partid = self.images[part]
                    scaled = img.subsample(3, 3)
                    item = self.canvas.create_image(*self.coords[part], image=scaled)
                    self.drawn_parts.append((scaled, item))
                    db.reveal_part(self.gameid, partid)

            if self.wrong_guesses >= len(self.parts_order):
                db.update("games", {"status": "lost"}, {"gameid": self.gameid})
                messagebox.showinfo("Lose", f"You lost! The word was {self.word}")

        # bot turn always runs
        self.bot_turn()

    def bot_turn(self):
        if self.bot.should_guess():
            guess = self.bot.make_guess()
            if guess:
                db.record_guess(self.gameid, self.bot_playerid, guess, guess in self.word)
                self.bot.guessed.add(guess)

                # always refresh bot word display
                self.update_bot_word_display()

                if guess not in self.word:
                    self.bot_wrong_guesses += 1
                    self.bot_health.set(len(self.parts_order) - self.bot_wrong_guesses)

                    # reveal next villain part (on wrong guess only)
                    if self.bot_wrong_guesses <= len(self.parts_order):
                        part = self.parts_order[self.bot_wrong_guesses - 1]
                        if part in self.villain_images:
                            img, partid = self.villain_images[part]
                            scaled = img.subsample(3, 3)
                            item = self.canvas.create_image(*self.villain_coords[part], image=scaled)
                            self.bot_drawn_parts.append((scaled, item))
                            db.reveal_part(self.gameid, partid)
