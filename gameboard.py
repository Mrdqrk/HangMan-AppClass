import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import random
import os
import json

from supabase_client import db
from character_loader import load_two_random_characters
from bot_player import BotPlayer


class HangmanGame(tk.Frame):
    def __init__(self, master, username, difficulty="medium", characterid=17):
        super().__init__(master, bg="#b7956b")
        self.master = master
        self.username = username
        self.difficulty = (difficulty or "medium").lower()
        self.game_over = False

        # turn
        self.turn = "player"
        self.player_miss_streak = 0
        self.bot_miss_streak = 0
        self._bot_after_id = None

        # phrase
        self.category = "General"
        phrase = None
        self.phraseid = None

        for _ in range(10):
            try:
                result = db.get_random_phrase(self.difficulty)
            except Exception:
                phrase = "PYTHON"
                break

            temp_category = "General"
            temp_phrase = None
            temp_phraseid = None

            if isinstance(result, tuple):
                if len(result) >= 3:
                    temp_phraseid, temp_phrase, temp_category = result[0], result[1], result[2]
                elif len(result) == 2:
                    temp_phraseid, temp_phrase = result[0], result[1]
                else:
                    temp_phraseid = result[0]
            else:
                temp_phraseid = result

            if temp_category and str(temp_category).strip().lower() == "music":
                continue

            self.phraseid = temp_phraseid
            phrase = temp_phrase
            self.category = temp_category or "General"
            break

        if phrase is None:
            phrase = "PYTHON"

        self.word = (phrase or "PYTHON").upper().strip()

        # db
        self.playerid = db.get_or_create_player(username)
        self.bot_playerid = db.get_or_create_player("Bot")
        self.gameid = db.start_game(self.phraseid, self.playerid)

        # state
        self.guessed = set()
        self.wrong_guesses = 0
        self.bot_wrong_guesses = 0
        self.player_correct_streak = 0

        self.parts_order = ["torso", "head", "left_arm", "right_arm", "left_leg", "right_leg"]
        self.max_parts = len(self.parts_order)

        self.drawn_parts = []
        self.bot_drawn_parts = []
        self.player_items = []
        self.bot_items = []

        # ui
        self.top_frame = tk.Frame(self, bg="#b7956b", highlightthickness=0, bd=0)
        self.top_frame.pack(side="top", fill="both", expand=True)

        self.bottom_frame = tk.Frame(self, bg="#b7956b", highlightthickness=0, bd=0)
        self.bottom_frame.pack(side="bottom", fill="x")

        # canvas bg
        self.play_bg_path = os.path.join("images", "bgPlay.jpg")
        self.play_bg_img = None
        self.play_bg_item = None

        self.canvas = tk.Canvas(
            self.top_frame,
            width=800,
            height=360,
            highlightthickness=0,
            bd=0,
            bg="#b7956b"
        )
        self.canvas.pack(pady=10)
        self._load_and_draw_play_background()

        # turn banner
        self.turn_var = tk.StringVar(value="")
        self.turn_label = tk.Label(
            self.top_frame,
            textvariable=self.turn_var,
            font=("Castellar", 28, "bold"),
            bg="#b7956b",
            fg="#b95f1f"
        )
        self.turn_label.pack(pady=(5, 0))

        self.category_var = tk.StringVar(value=f"Category: {self.category}")
        tk.Label(
            self.bottom_frame,
            textvariable=self.category_var,
            font=("Castellar", 18),
            fg="black",
            bg="#b7956b",
        ).pack(pady=(5, 0))

        tk.Label(self.bottom_frame, text="Player Health", font=("Castellar", 12), bg="#b7956b").pack()
        self.player_health = tk.IntVar(value=self.max_parts)
        tk.Label(
            self.bottom_frame,
            textvariable=self.player_health,
            font=("Castellar", 16),
            fg="green",
            bg="#b7956b"
        ).pack()

        tk.Label(self.bottom_frame, text="Bot Health", font=("Castellar", 12), bg="#b7956b").pack()
        self.bot_health = tk.IntVar(value=self.max_parts)
        tk.Label(
            self.bottom_frame,
            textvariable=self.bot_health,
            font=("Castellar", 16),
            fg="red",
            bg="#b7956b"
        ).pack()

        self.word_var = tk.StringVar()
        tk.Label(
            self.bottom_frame,
            textvariable=self.word_var,
            font=("Castellar", 24),
            pady=5,
            bg="#b7956b"
        ).pack()
        self.update_word_display()

        self.bot = BotPlayer(self.difficulty, [chr(i) for i in range(65, 91)])
        self.bot_word_var = tk.StringVar()
        tk.Label(
            self.bottom_frame,
            textvariable=self.bot_word_var,
            font=("Castellar", 20),
            fg="purple",
            bg="#b7956b"
        ).pack()
        self.update_bot_word_display()

        self.score_var = tk.StringVar()
        tk.Label(
            self.bottom_frame,
            textvariable=self.score_var,
            font=("Castellar", 18),
            fg="blue",
            pady=5,
            bg="#b7956b"
        ).pack()
        self.update_score_display()

        input_row = tk.Frame(self.bottom_frame, bg="#b7956b")
        input_row.pack(pady=(5, 10))

        tk.Label(input_row, text="Letter:", font=("Castellar", 14), bg="#b7956b").grid(row=0, column=0, padx=5)

        self.entry = tk.Entry(input_row, font=("Castellar", 16), width=4, justify="center")
        self.entry.grid(row=0, column=1, padx=5)

        self.guess_btn = tk.Button(input_row, text="Guess Letter", font=("Castellar", 12), command=self.make_guess)
        self.guess_btn.grid(row=0, column=2, padx=5)

        self.phrase_btn = tk.Button(input_row, text="Guess Phrase", font=("Castellar", 12), command=self.guess_phrase)
        self.phrase_btn.grid(row=0, column=3, padx=5)

        self.entry.bind("<Return>", lambda event: self.make_guess())

        # anchors
        self.player_anchor = (150, 205)
        self.bot_anchor = (650, 205)

        self.base_offsets = {
            "torso": (0, 0),
            "head": (0, -85),
            "left_arm": (-55, -10),
            "right_arm": (55, -10),
            "left_leg": (-22, 85),
            "right_leg": (22, 85),
        }

        self.tweak_path = os.path.join(os.path.dirname(__file__), "character_offsets.json")
        self.char_tweaks = self._load_tweaks()
        self._scale_cache = {"player": {}, "bot": {}}

        # characters
        self.images = {}
        self.villain_images = {}
        self.player_characterid = ""
        self.villain_characterid = ""

        try:
            (self.player_characterid, self.images), (self.villain_characterid, self.villain_images) = load_two_random_characters(self.category)
        except Exception:
            pass

        if self.play_bg_item is not None:
            self.canvas.tag_lower(self.play_bg_item)

        # audio
        try:
            self.master.audio.stop_sfx()
            self.master.audio.play_duel_loop()
        except Exception:
            pass

        self._set_turn("player")

    # bg in canvas
    def _load_and_draw_play_background(self):
        try:
            if not os.path.exists(self.play_bg_path):
                self.canvas.configure(bg="#b7956b")
                return

            w = int(self.canvas.cget("width"))
            h = int(self.canvas.cget("height"))

            im = Image.open(self.play_bg_path).convert("RGB")
            im = im.resize((w, h), Image.LANCZOS)
            self.play_bg_img = ImageTk.PhotoImage(im)

            self.canvas.delete("bg")
            self.play_bg_item = self.canvas.create_image(0, 0, image=self.play_bg_img, anchor="nw", tags=("bg",))
            self.canvas.tag_lower(self.play_bg_item)
        except Exception:
            self.canvas.configure(bg="#b7956b")

    # tweaks
    def _normalize_key(self, k: str) -> str:
        return (k or "").strip().lower()

    def _resolve_existing_char_key(self, cname: str) -> str:
        cname = (cname or "unknown").strip()
        want = self._normalize_key(cname)
        for existing in self.char_tweaks.keys():
            if self._normalize_key(existing) == want:
                return existing
        return cname

    def _load_tweaks(self):
        if os.path.exists(self.tweak_path):
            try:
                with open(self.tweak_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, dict) else {}
            except Exception:
                return {}
        return {}

    def _get_char_name(self, who: str) -> str:
        return self.player_characterid or "unknown" if who == "player" else self.villain_characterid or "unknown"

    def _part_xy(self, who: str, part: str):
        ax, ay = self.player_anchor if who == "player" else self.bot_anchor
        bx, by = self.base_offsets.get(part, (0, 0))

        cname = self._get_char_name(who)
        key = self._resolve_existing_char_key(cname)
        tweak_map = self.char_tweaks.get(key, {})
        tweak = tweak_map.get(part, [0, 0])
        tx, ty = int(tweak[0]), int(tweak[1])

        return ax + bx + tx, ay + by + ty

    def _get_scaled_part(self, who: str, path: str):
        cname = self._get_char_name(who)
        key = self._resolve_existing_char_key(cname)

        if key not in self._scale_cache[who]:
            if who == "player":
                torso_path = self.images.get("torso", (None, None))[1]
            else:
                torso_path = self.villain_images.get("torso", (None, None))[1]

            ref_path = torso_path or path
            ref_im = Image.open(ref_path).convert("RGBA")
            ref_w, _ = ref_im.size

            target_width = int(self.char_tweaks.get(key, {}).get("_scale", 120))
            factor = (target_width / float(ref_w)) if ref_w else 1.0
            self._scale_cache[who][key] = factor

        factor = self._scale_cache[who][key]

        im = Image.open(path).convert("RGBA")
        w, h = im.size
        new_w = max(1, int(w * factor))
        new_h = max(1, int(h * factor))

        im = im.resize((new_w, new_h), Image.LANCZOS)
        return ImageTk.PhotoImage(im)

    # text
    def update_word_display(self):
        display = " ".join([letter if (letter in self.guessed or letter == " ") else "_" for letter in self.word])
        self.word_var.set(display)

    def update_bot_word_display(self):
        pieces = []
        for ch in self.word:
            if ch == " ":
                pieces.append(" ")
            elif ch in self.bot.guessed:
                pieces.append("X")
            else:
                pieces.append("_")
        self.bot_word_var.set(" ".join(pieces))

    def update_score_display(self):
        score = db.get_score(self.gameid, self.playerid)
        self.score_var.set(f"Score: {score}")

    # cancel bot loop
    def _cancel_bot_after(self):
        if self._bot_after_id is not None:
            try:
                self.after_cancel(self._bot_after_id)
            except Exception:
                pass
            self._bot_after_id = None

    # turns
    def _set_turn(self, who: str):
        if self.game_over:
            return

        if who != "bot":
            self._cancel_bot_after()

        self.turn = who
        if who == "bot":
            self.turn_var.set("BOT'S TURN")
            self.entry.config(state="disabled")
            self.guess_btn.config(state="disabled")
            self.phrase_btn.config(state="disabled")
            self._cancel_bot_after()
            self._bot_after_id = self.after(450, self.bot_turn)
        else:
            self.turn_var.set("YOUR TURN")
            self.entry.config(state="normal")
            self.guess_btn.config(state="normal")
            self.phrase_btn.config(state="normal")
            self.entry.focus_set()

    # draw
    def _redraw_player_body(self):
        for item in self.player_items:
            self.canvas.delete(item)
        self.player_items.clear()
        self.drawn_parts.clear()

        if self.play_bg_item is not None:
            self.canvas.tag_lower(self.play_bg_item)

        for i in range(min(self.wrong_guesses, self.max_parts)):
            part_name = self.parts_order[i]
            if part_name in self.images:
                _, path = self.images[part_name]
                scaled = self._get_scaled_part("player", path)
                x, y = self._part_xy("player", part_name)
                item = self.canvas.create_image(x, y, image=scaled, anchor="center")
                self.drawn_parts.append((scaled, item))
                self.player_items.append(item)

    def _redraw_bot_body(self):
        for item in self.bot_items:
            self.canvas.delete(item)
        self.bot_items.clear()
        self.bot_drawn_parts.clear()

        if self.play_bg_item is not None:
            self.canvas.tag_lower(self.play_bg_item)

        for i in range(min(self.bot_wrong_guesses, self.max_parts)):
            part_name = self.parts_order[i]
            if part_name in self.villain_images:
                _, path = self.villain_images[part_name]
                scaled = self._get_scaled_part("bot", path)
                x, y = self._part_xy("bot", part_name)
                item = self.canvas.create_image(x, y, image=scaled, anchor="center")
                self.bot_drawn_parts.append((scaled, item))
                self.bot_items.append(item)

    # limbs
    def _remove_last_part(self, for_player: bool):
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

    # menu
    def _go_back_to_menu(self):
        self._cancel_bot_after()
        try:
            self.master.audio.stop_sfx()
            self.master.audio.play_duel_loop()
        except Exception:
            pass

        try:
            self.master.show_difficulty(self.username)
        except Exception:
            pass

    # end checks
    def _check_player_win(self) -> bool:
        if all(letter in self.guessed or letter == " " for letter in self.word):
            try:
                self.master.audio.play_win()
            except Exception:
                pass

            db.update("games", {"status": "won"}, {"gameid": self.gameid})
            self.game_over = True
            self._cancel_bot_after()
            messagebox.showinfo("Yeehaw!", f"You won the duel.\n\nThe word was:\n\n{self.word}")
            self._go_back_to_menu()
            return True
        return False

    def _player_loses(self):
        if self.game_over:
            return

        try:
            self.master.audio.play_lost()
        except Exception:
            pass

        db.update("games", {"status": "lost"}, {"gameid": self.gameid})

        self.game_over = True
        self._cancel_bot_after()
        messagebox.showinfo("Dust settled...", f"You got outdueled.\n\nThe word was:\n\n{self.word}")
        self._go_back_to_menu()

    def _bot_loses(self):
        if self.game_over:
            return

        try:
            self.master.audio.play_win()
        except Exception:
            pass

        db.update("games", {"status": "won"}, {"gameid": self.gameid})
        self.game_over = True
        self._cancel_bot_after()
        messagebox.showinfo("Yeehaw!", f"You win this duel.\n\nThe word was:\n\n{self.word}")
        self._go_back_to_menu()

    # input
    def make_guess(self):
        if self.game_over or self.turn != "player":
            return

        guess = self.entry.get().upper().strip()
        self.entry.delete(0, tk.END)

        if not guess or len(guess) != 1 or not guess.isalpha():
            messagebox.showerror("Hold up, partner", "Give me one letter A-Z.")
            return

        if guess in self.guessed:
            messagebox.showinfo("Easy now", f"You already fired at '{guess}'.")
            return

        correct = guess in self.word
        db.record_guess(self.gameid, self.playerid, guess, correct)

        if correct:
            self._handle_player_correct(guess)
        else:
            self._handle_player_wrong(extra_penalty=False)

    def guess_phrase(self):
        if self.game_over or self.turn != "player":
            return

        guess = simpledialog.askstring("Call your shot", "Enter the full phrase:", parent=self)
        if guess is None:
            return

        normalized = guess.upper().strip()
        correct = (normalized == self.word)

        placeholder = normalized[0] if normalized else "?"
        try:
            db.record_guess(self.gameid, self.playerid, placeholder, correct)
        except Exception:
            pass

        if correct:
            try:
                self.master.audio.play_win()
            except Exception:
                pass

            self.guessed.update({c for c in self.word if c != " "})
            self.update_word_display()

            try:
                db.increment_score(self.gameid, self.playerid)
            except Exception:
                pass

            self.update_score_display()
            db.update("games", {"status": "won"}, {"gameid": self.gameid})
            self.game_over = True
            self._cancel_bot_after()
            messagebox.showinfo("Yeehaw!", f"You called it right.\n\nThe phrase was:\n\n{self.word}")
            self._go_back_to_menu()
        else:
            self._handle_player_wrong(extra_penalty=True)

    def _handle_player_correct(self, letter: str):
        try:
            self.master.audio.play_good()
        except Exception:
            pass

        messagebox.showinfo("Good shootin'", f"'{letter}' is in there.")
        self.player_correct_streak += 1
        self.player_miss_streak = 0

        self.guessed.add(letter)
        self.update_word_display()

        db.increment_score(self.gameid, self.playerid)
        self.update_score_display()

        if self.player_correct_streak == 2:
            self._apply_streak_bonus_for_player()
            self.player_correct_streak = 0

        self._check_player_win()

    def _handle_player_wrong(self, extra_penalty: bool):
        self.player_correct_streak = 0
        self.player_miss_streak += 1

        self.wrong_guesses += 1
        self.player_health.set(self.max_parts - self.wrong_guesses)
        self._redraw_player_body()

        if extra_penalty:
            self._add_forced_limb(for_player=True)

        if self.wrong_guesses >= self.max_parts:
            self._player_loses()
            return

        if not self.game_over and self.player_miss_streak >= 2:
            self.player_miss_streak = 0
            self._set_turn("bot")

    def _apply_streak_bonus_for_player(self):
        choice = {"value": None}
        win = tk.Toplevel(self)
        win.title("Streak Bonus")
        win.grab_set()
        win.configure(bg="#b7956b")

        tk.Label(
            win,
            text="Two clean hits in a row.\nPick your bonus:",
            font=("Castellar", 12),
            pady=10,
            bg="#b7956b"
        ).pack(padx=10)

        btn_frame = tk.Frame(win, bg="#b7956b")
        btn_frame.pack(pady=10)

        def choose_take():
            choice["value"] = "take"
            win.destroy()

        def choose_add():
            choice["value"] = "add"
            win.destroy()

        tk.Button(btn_frame, text="Take (remove your limb)", font=("Castellar", 10), command=choose_take).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Add (add limb to bot)", font=("Castellar", 10), command=choose_add).grid(row=0, column=1, padx=5)

        self.master.wait_window(win)

        if choice["value"] == "take":
            self._remove_last_part(for_player=True)
        elif choice["value"] == "add":
            self._add_forced_limb(for_player=False)

    # bot
    def bot_turn(self):
        if self.game_over or self.turn != "bot":
            return

        if self._bot_should_guess_phrase():
            try:
                self.master.audio.play_lost()
            except Exception:
                pass

            db.update("games", {"status": "lost"}, {"gameid": self.gameid})
            self.game_over = True
            self._cancel_bot_after()
            messagebox.showinfo("Outgunned", f"The bot called the whole phrase.\n\nIt was:\n\n{self.word}")
            self._go_back_to_menu()
            return

        guess = self._bot_choose_letter()
        if not guess:
            self._set_turn("player")
            return

        correct = guess in self.word
        db.record_guess(self.gameid, self.bot_playerid, guess, correct)

        if correct:
            self.bot_miss_streak = 0
            self.update_bot_word_display()
        else:
            self.bot_miss_streak += 1
            self.bot_wrong_guesses += 1
            self.bot_health.set(self.max_parts - self.bot_wrong_guesses)
            self._redraw_bot_body()

            if self.bot_wrong_guesses >= self.max_parts:
                self._bot_loses()
                return

        if self.bot_miss_streak >= 2:
            self.bot_miss_streak = 0
            self._set_turn("player")
            return

        self._cancel_bot_after()
        self._bot_after_id = self.after(550, self.bot_turn)

    def _bot_correct_chance(self) -> float:
        if self.difficulty == "hard":
            p = 0.65
        elif self.difficulty == "medium":
            p = 0.50
        else:
            p = 0.35

        parts_left = self.max_parts - self.bot_wrong_guesses
        if parts_left <= 2:
            p += 0.20
        elif parts_left <= 3:
            p += 0.10

        if p < 0.05:
            p = 0.05
        if p > 0.90:
            p = 0.90

        return p

    def _bot_choose_letter(self):
        p = self._bot_correct_chance()

        unguessed_in_word = [
            ch for ch in set(self.word)
            if ch.isalpha() and ch not in self.bot.guessed
        ]

        if unguessed_in_word and random.random() < p:
            return random.choice(unguessed_in_word)

        return self.bot.make_guess()

    def _bot_should_guess_phrase(self) -> bool:
        unique_letters = [ch for ch in set(self.word) if ch.isalpha()]
        if not unique_letters:
            return False

        correct_hits = sum(1 for ch in unique_letters if ch in self.bot.guessed)
        ratio = correct_hits / max(1, len(unique_letters))

        parts_left = self.max_parts - self.bot_wrong_guesses

        if self.difficulty == "hard":
            base = 0.25
            need_ratio = 0.45
        elif self.difficulty == "medium":
            base = 0.18
            need_ratio = 0.55
        else:
            base = 0.12
            need_ratio = 0.65

        if parts_left <= 2:
            base += 0.25
        elif parts_left <= 3:
            base += 0.15

        if base > 0.60:
            base = 0.60

        return ratio >= need_ratio and random.random() < base
