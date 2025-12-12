import tkinter as tk
from tkinter import messagebox, simpledialog
import random


from supabase_client import db
from character_loader import load_two_random_characters
from bot_player import BotPlayer

# larger number ⇒ smaller images
SCALE = 5


class HangmanGame(tk.Frame):
    def __init__(self, master, username, difficulty="medium", characterid=17):
        super().__init__(master)
        self.master = master
        self.username = username
        self.difficulty = difficulty
        self.game_over = False


        self.category = "General"
        phrase = None
        self.phraseid = None

        # Try a few times until we get a non-music phrase
        for _ in range(10):
            try:
                result = db.get_random_phrase(difficulty)
            except Exception as e:
                print("[ERROR] get_random_phrase failed, using fallback word:", e)
                phrase = "PYTHON"
                break

            temp_category = "General"
            temp_phrase = None
            temp_phraseid = None

            if isinstance(result, tuple):
                if len(result) >= 3:
                    temp_phraseid, temp_phrase, temp_category = (
                        result[0],
                        result[1],
                        result[2],
                    )
                elif len(result) == 2:
                    temp_phraseid, temp_phrase = result[0], result[1]
                else:
                    temp_phraseid = result[0]
            else:
                temp_phraseid = result

            # skip music category entirely
            if temp_category and str(temp_category).lower() == "music":
                continue

            self.phraseid = temp_phraseid
            phrase = temp_phrase
            self.category = temp_category or "General"
            break

        if phrase is None:
            phrase = "PYTHON"

        self.word = (phrase or "PYTHON").upper().strip()

        self.playerid = db.get_or_create_player(username)
        self.bot_playerid = db.get_or_create_player("Bot")
        self.gameid = db.start_game(self.phraseid, self.playerid)

        # Guess tracking
        self.guessed = set()
        self.wrong_guesses = 0
        self.bot_wrong_guesses = 0

        # Streak tracking
        self.player_correct_streak = 0
        self.player_incorrect_streak = 0
        self.bot_correct_streak = 0
        self.bot_incorrect_streak = 0

        # Order of parts as they are added (we start with NO body)
        self.parts_order = ["torso", "head", "left_arm", "right_arm", "left_leg", "right_leg"]
        self.max_parts = len(self.parts_order)

        # to keep references to images and canvas items
        self.drawn_parts = []       # list of (image, item_id) for player
        self.bot_drawn_parts = []   # list of (image, item_id) for bot
        self.player_items = []      # just the canvas item ids (player)
        self.bot_items = []         # canvas item ids (bot)

        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side="top", fill="both", expand=True)

        self.bottom_frame = tk.Frame(self, bg="#f5f5f5")
        self.bottom_frame.pack(side="bottom", fill="x")

        self.canvas = tk.Canvas(self.top_frame, width=800, height=360, bg="white")
        self.canvas.pack(pady=10)

        # Category
        self.category_var = tk.StringVar(value=f"Category: {self.category}")
        tk.Label(
            self.bottom_frame,
            textvariable=self.category_var,
            font=("Arial", 18),
            fg="gray",
            bg="#f5f5f5",
        ).pack(pady=(5, 0))

        # Health
        tk.Label(self.bottom_frame, text="Player Health", font=("Arial", 12), bg="#f5f5f5").pack()
        self.player_health = tk.IntVar(value=self.max_parts)
        tk.Label(
            self.bottom_frame,
            textvariable=self.player_health,
            font=("Arial", 16),
            fg="green",
            bg="#f5f5f5",
        ).pack()

        tk.Label(self.bottom_frame, text="Bot Health", font=("Arial", 12), bg="#f5f5f5").pack()
        self.bot_health = tk.IntVar(value=self.max_parts)
        tk.Label(
            self.bottom_frame,
            textvariable=self.bot_health,
            font=("Arial", 16),
            fg="red",
            bg="#f5f5f5",
        ).pack()

        # Word (player view)
        self.word_var = tk.StringVar()
        tk.Label(
            self.bottom_frame,
            textvariable=self.word_var,
            font=("Arial", 24),
            pady=5,
            bg="#f5f5f5",
        ).pack()
        self.update_word_display()

        # Bot display (0 = bot guessed this letter)
        self.bot = BotPlayer(difficulty, [chr(i) for i in range(65, 91)])
        self.bot_word_var = tk.StringVar()
        tk.Label(
            self.bottom_frame,
            textvariable=self.bot_word_var,
            font=("Arial", 20),
            fg="purple",
            bg="#f5f5f5",
        ).pack()
        self.update_bot_word_display()

        # Score
        self.score_var = tk.StringVar()
        tk.Label(
            self.bottom_frame,
            textvariable=self.score_var,
            font=("Arial", 18),
            fg="blue",
            pady=5,
            bg="#f5f5f5",
        ).pack()
        self.update_score_display()

        # Input row
        input_row = tk.Frame(self.bottom_frame, bg="#f5f5f5")
        input_row.pack(pady=(5, 10))

        tk.Label(input_row, text="Letter:", font=("Arial", 14), bg="#f5f5f5").grid(row=0, column=0, padx=5)

        self.entry = tk.Entry(input_row, font=("Arial", 16), width=4, justify="center")
        self.entry.grid(row=0, column=1, padx=5)

        guess_btn = tk.Button(input_row, text="Guess Letter", font=("Arial", 12), command=self.make_guess)
        guess_btn.grid(row=0, column=2, padx=5)

        phrase_btn = tk.Button(input_row, text="Guess Phrase", font=("Arial", 12), command=self.guess_phrase)
        phrase_btn.grid(row=0, column=3, padx=5)

        # Press Enter to guess the letter
        self.entry.bind("<Return>", lambda event: self.make_guess())


        # Player character coordinates (left side)
        self.coords = {
            "torso":     (150, 190),
            "head":      (150, 120),
            "left_arm":  (130, 190),
            "right_arm": (170, 190),
            "left_leg":  (142, 250),
            "right_leg": (158, 250),
        }

        # Villain character coordinates (right side)
        self.villain_coords = {
            "torso":     (650, 190),
            "head":      (650, 120),
            "left_arm":  (630, 190),
            "right_arm": (670, 190),
            "left_leg":  (642, 250),
            "right_leg": (658, 250),
        }


        self.images = {}
        self.villain_images = {}
        self.player_characterid = ""
        self.villain_characterid = ""

        try:
            (self.player_characterid, self.images), (
                self.villain_characterid,
                self.villain_images,
            ) = load_two_random_characters(self.category)
            print(
                f"[INFO] Using characters for '{self.category}': "
                f"player={self.player_characterid}, villain={self.villain_characterid}"
            )
        except Exception as e:
            print("[WARN] Character loading failed:", e)

        # NOTE: we start with NO body and build on wrong guesses only.


    def update_word_display(self):
        display = " ".join(
            [letter if (letter in self.guessed or letter == " ") else "_" for letter in self.word]
        )
        self.word_var.set(display)

    def update_bot_word_display(self):
        display = " ".join(
            ["0" if letter in self.bot.guessed else (" " if letter == " " else "_") for letter in self.word]
        )
        self.bot_word_var.set(display)

    def update_score_display(self):
        score = db.get_score(self.gameid, self.playerid)
        self.score_var.set(f"Score: {score}")


    def _redraw_player_body(self):
        """Clear player parts and redraw from self.wrong_guesses."""
        for item in self.player_items:
            self.canvas.delete(item)
        self.player_items.clear()
        self.drawn_parts.clear()

        for i in range(min(self.wrong_guesses, self.max_parts)):
            part_name = self.parts_order[i]
            if part_name in self.images:
                img, _ = self.images[part_name]
                scaled = img.subsample(SCALE, SCALE)
                x, y = self.coords[part_name]
                item = self.canvas.create_image(x, y, image=scaled)
                self.drawn_parts.append((scaled, item))
                self.player_items.append(item)

    def _redraw_bot_body(self):
        """Clear bot parts and redraw from self.bot_wrong_guesses."""
        for item in self.bot_items:
            self.canvas.delete(item)
        self.bot_items.clear()
        self.bot_drawn_parts.clear()

        for i in range(min(self.bot_wrong_guesses, self.max_parts)):
            part_name = self.parts_order[i]
            if part_name in self.villain_images:
                img, _ = self.villain_images[part_name]
                scaled = img.subsample(SCALE, SCALE)
                x, y = self.villain_coords[part_name]
                item = self.canvas.create_image(x, y, image=scaled)
                self.bot_drawn_parts.append((scaled, item))
                self.bot_items.append(item)

    def _remove_last_part(self, for_player: bool):
        """Used for streak bonus 'Take' option."""
        if for_player:
            if self.wrong_guesses > 0:
                self.wrong_guesses -= 1
                self.player_health.set(self.max_parts - self.wrong_guesses)
                self._redraw_player_body()
        else:
            if self.bot_wrong_guesses > 0:
                self.bot_wrong_guesses -= 1
                self.bot_health.set(self.max_parts - self.bot_wrong_guesses)
                self._redraw_bot_body()

    def _add_forced_limb(self, for_player: bool):
        """Penalty limb (3-wrong-in-a-row or wrong phrase guess)."""
        if for_player:
            if self.wrong_guesses >= self.max_parts:
                return
            self.wrong_guesses += 1
            self.player_health.set(self.max_parts - self.wrong_guesses)
            self._redraw_player_body()
        else:
            if self.bot_wrong_guesses >= self.max_parts:
                return
            self.bot_wrong_guesses += 1
            self.bot_health.set(self.max_parts - self.bot_wrong_guesses)
            self._redraw_bot_body()


    def _go_back_to_menu(self):
        # After game over, send player back to difficulty selector
        try:
            self.master.show_difficulty(self.username)
        except Exception as e:
            print("[WARN] Could not go back to menu:", e)

    def _check_player_win(self) -> bool:
        if all(letter in self.guessed or letter == " " for letter in self.word):
            db.update("games", {"status": "won"}, {"gameid": self.gameid})
            self.game_over = True
            messagebox.showinfo("Win", f"🎉 Congrats! You guessed the word:\n\n{self.word}")
            self._go_back_to_menu()
            return True
        return False

    def _player_loses(self):
        if not self.game_over:
            db.update("games", {"status": "lost"}, {"gameid": self.gameid})
            self.game_over = True
            messagebox.showinfo("Lose", f"You lost! The word was: {self.word}")
            self._go_back_to_menu()

    def _bot_loses(self):
        if not self.game_over:
            db.update("games", {"status": "won"}, {"gameid": self.gameid})
            self.game_over = True
            messagebox.showinfo("Win", f"You defeated the villain! The word was: {self.word}")
            self._go_back_to_menu()


    def make_guess(self):
        if self.game_over:
            return

        guess = self.entry.get().upper().strip()
        self.entry.delete(0, tk.END)

        if not guess or len(guess) != 1 or not guess.isalpha():
            messagebox.showerror("Error", "Enter a single letter (A-Z).")
            return

        if guess in self.guessed:
            messagebox.showinfo("Info", f"You already guessed '{guess}'.")
            return

        correct = guess in self.word
        db.record_guess(self.gameid, self.playerid, guess, correct)

        if correct:
            self._handle_player_correct(guess)
        else:
            self._handle_player_wrong(extra_penalty=False)

    def guess_phrase(self):
        """Player guesses the whole phrase."""
        if self.game_over:
            return

        guess = simpledialog.askstring("Guess Phrase", "Enter the full phrase:", parent=self)
        if guess is None:
            return  # cancel

        normalized = guess.upper().strip()
        correct = (normalized == self.word)

        # DB column guessedletter is CHAR(1), so send only one char
        placeholder = normalized[0] if normalized else "?"
        try:
            db.record_guess(self.gameid, self.playerid, placeholder, correct)
        except Exception as e:
            print("[WARN] record_guess failed for phrase guess:", e)

        if correct:
            messagebox.showinfo("Correct!", "You nailed the whole phrase!")

            self.guessed.update({c for c in self.word if c != " "})
            self.update_word_display()
            try:
                db.increment_score(self.gameid, self.playerid)
            except Exception as e:
                print("[WARN] increment_score failed after phrase guess:", e)
            self.update_score_display()

            db.update("games", {"status": "won"}, {"gameid": self.gameid})
            self.game_over = True
            messagebox.showinfo("Win", f"🎉 Congrats! You guessed the phrase:\n\n{self.word}")
            self._go_back_to_menu()
        else:
            self._handle_player_wrong(extra_penalty=True)

    def _handle_player_correct(self, letter: str):
        # small congrats every time you get a letter
        messagebox.showinfo("Correct!", f"Nice! '{letter}' is in the phrase.")

        self.player_correct_streak += 1
        self.player_incorrect_streak = 0

        self.guessed.add(letter)
        self.update_word_display()

        db.increment_score(self.gameid, self.playerid)
        self.update_score_display()

        if self.player_correct_streak >= 2:
            self._apply_streak_bonus_for_player()
            self.player_correct_streak = 0

        self._check_player_win()

    def _handle_player_wrong(self, extra_penalty: bool):
        self.player_correct_streak = 0
        self.player_incorrect_streak += 1

        self.wrong_guesses += 1
        self.player_health.set(self.max_parts - self.wrong_guesses)
        self._redraw_player_body()

        if extra_penalty:
            self._add_forced_limb(True)

        if self.player_incorrect_streak >= 3:
            self._add_forced_limb(True)
            self.player_incorrect_streak = 0

        if self.wrong_guesses >= self.max_parts:
            self._player_loses()
            return

        # bot only moves after the player has 2 wrong in a row
        if not self.game_over and self.player_incorrect_streak >= 2:
            self.player_incorrect_streak = 0
            self.bot_turn()

    def _apply_streak_bonus_for_player(self):
        """Two correct in a row ⇒ player chooses Take/Add bonus."""
        if self.wrong_guesses <= 0 and self.bot_wrong_guesses >= self.max_parts:
            return

        choice = {"value": None}
        win = tk.Toplevel(self)
        win.title("Streak Bonus")
        win.grab_set()  # modal

        tk.Label(
            win,
            text="Two correct guesses in a row!\nChoose your bonus:",
            font=("Arial", 12),
            pady=10,
        ).pack(padx=10)

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=10)

        def choose_take():
            choice["value"] = "take"
            win.destroy()

        def choose_add():
            choice["value"] = "add"
            win.destroy()

        tk.Button(btn_frame, text="Take (remove your limb)", command=choose_take).grid(
            row=0, column=0, padx=5
        )
        tk.Button(btn_frame, text="Add (add limb to bot)", command=choose_add).grid(
            row=0, column=1, padx=5
        )

        self.master.wait_window(win)

        if choice["value"] == "take":
            self._remove_last_part(for_player=True)
        elif choice["value"] == "add":
            self._add_forced_limb(for_player=False)

    # Bot
    def bot_turn(self):
        if self.game_over:
            return

        if not self.bot.should_guess():
            return

        guess = self.bot.make_guess()
        if not guess:
            return

        correct = guess in self.word
        db.record_guess(self.gameid, self.bot_playerid, guess, correct)
        self.update_bot_word_display()

        if correct:
            self._handle_bot_correct()
        else:
            self._handle_bot_wrong()

    def _handle_bot_correct(self):
        self.bot_correct_streak += 1
        self.bot_incorrect_streak = 0

        if self.bot_correct_streak >= 2:
            if random.random() < 0.5:
                self._remove_last_part(for_player=False)
            else:
                self._add_forced_limb(for_player=True)
            self.bot_correct_streak = 0

    def _handle_bot_wrong(self):
        self.bot_correct_streak = 0
        self.bot_incorrect_streak += 1

        self.bot_wrong_guesses += 1
        self.bot_health.set(self.max_parts - self.bot_wrong_guesses)
        self._redraw_bot_body()

        if self.bot_incorrect_streak >= 3:
            self._add_forced_limb(False)
            self.bot_incorrect_streak = 0

        if self.bot_wrong_guesses >= self.max_parts:
            self._bot_loses()
