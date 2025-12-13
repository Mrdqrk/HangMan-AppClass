import tkinter as tk
from PIL import Image, ImageTk
import os
import pygame

from supabase_client import db
from gameboard import HangmanGame


class AudioManager:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.sounds_dir = os.path.join(self.base_dir, "sounds")

        self.sound_paths = {
            "duel": os.path.join(self.sounds_dir, "duel.mp3"),
            "good": os.path.join(self.sounds_dir, "good.mp3"),
            "win":  os.path.join(self.sounds_dir, "win.mp3"),
            "lost": os.path.join(self.sounds_dir, "lost.mp3"),
        }

        self.audio_ok = False
        self.sfx = {}

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            self.ch_duel = pygame.mixer.Channel(0)
            self.ch_sfx = pygame.mixer.Channel(1)

            for name, path in self.sound_paths.items():
                if os.path.exists(path):
                    try:
                        self.sfx[name] = pygame.mixer.Sound(path)
                    except Exception:
                        pass

            self.audio_ok = True
        except Exception:
            self.audio_ok = False

    def play_duel_loop(self):
        if not self.audio_ok:
            return
        snd = self.sfx.get("duel")
        if not snd:
            return
        if not self.ch_duel.get_busy():
            self.ch_duel.play(snd, loops=-1)

    def stop_duel(self):
        if not self.audio_ok:
            return
        try:
            self.ch_duel.stop()
        except Exception:
            pass

    def play_good(self):
        if not self.audio_ok:
            return
        snd = self.sfx.get("good")
        if snd:
            self.ch_sfx.play(snd)

    def play_win(self):
        if not self.audio_ok:
            return
        self.stop_duel()
        snd = self.sfx.get("win")
        if snd:
            self.ch_sfx.play(snd)

    def play_lost(self):
        if not self.audio_ok:
            return
        self.stop_duel()
        snd = self.sfx.get("lost")
        if snd:
            self.ch_sfx.play(snd)

    def stop_sfx(self):
        if not self.audio_ok:
            return
        try:
            self.ch_sfx.stop()
        except Exception:
            pass

    def shutdown(self):
        if not self.audio_ok:
            return
        try:
            self.stop_sfx()
            self.stop_duel()
        except Exception:
            pass


class HangmanApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HangVersus")
        self.geometry("900x650")
        self.configure(bg="#4f2b14")

        self.audio = AudioManager(base_dir=os.path.dirname(__file__))
        self.audio.play_duel_loop()

        self._bg_original = None
        self._bg_img = None
        self._bg_label = None

        self.username = None
        self.difficulty_var = tk.StringVar(value="medium")

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.show_login()

    def _on_close(self):
        try:
            self.audio.shutdown()
        except Exception:
            pass
        self.destroy()

    # bg auto resize
    def set_screen_background(self, img_path: str):
        if self._bg_label is None:
            self._bg_label = tk.Label(self, bd=0, highlightthickness=0)
            self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        try:
            self._bg_original = Image.open(img_path)
        except Exception:
            self._bg_original = None
            self._bg_label.configure(image="")
            return

        self.bind("<Configure>", self._resize_background)
        self._resize_background(None)

    def _resize_background(self, event):
        if not self._bg_original or not self._bg_label:
            return

        w = max(400, self.winfo_width())
        h = max(300, self.winfo_height())

        try:
            resized = self._bg_original.resize((w, h), Image.LANCZOS)
            self._bg_img = ImageTk.PhotoImage(resized)
            self._bg_label.configure(image=self._bg_img)
            self._bg_label.lower()
        except Exception:
            pass

    def clear_window(self):
        for widget in self.winfo_children():
            if widget is self._bg_label:
                continue
            widget.destroy()

    # UI helper code
    def _make_overlay_card(self, parent, bg="#b7956b", pad=18):
        card = tk.Frame(parent, bg=bg, bd=0, highlightthickness=0)
        card.place(relx=0.5, rely=0.5, anchor="center")

        inner = tk.Frame(card, bg=bg, bd=0, highlightthickness=0)
        inner.pack(padx=pad, pady=pad)

        return card, inner

    def _make_scrollable_area(self, parent, bg="#b7956b", width=760, height=420):
        outer = tk.Frame(parent, bg=bg, bd=0, highlightthickness=0)
        outer.pack()

        canvas = tk.Canvas(
            outer,
            bg=bg,
            highlightthickness=0,
            bd=0,
            width=width,
            height=height
        )
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        content = tk.Frame(canvas, bg=bg, bd=0, highlightthickness=0)
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        def _on_configure(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(window_id, width=canvas.winfo_width())

        content.bind("<Configure>", _on_configure)

        def _wheel(event):
            try:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass

        canvas.bind("<MouseWheel>", _wheel)

        return outer, content

    # login
    def show_login(self):
        self.clear_window()
        self.set_screen_background(os.path.join("images", "background.png"))

        frame = tk.Frame(self, bg="#d2af80", bd=2, highlightthickness=0)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            frame,
            text="Enter Username:",
            font=("Castellar", 20, "bold"),
            bg="#d2af80"
        ).pack(pady=20)

        self.username_entry = tk.Entry(frame, font=("Castellar", 16), width=20, justify="center")
        self.username_entry.pack(pady=10)

        tk.Button(
            frame,
            text="Login",
            font=("Castellar", 14),
            command=self.login
        ).pack(pady=20)

        try:
            self.audio.stop_sfx()
            self.audio.play_duel_loop()
        except Exception:
            pass

    def login(self):
        username = self.username_entry.get().strip()
        if not username:
            return
        self.username = username
        self.show_rules(username)

    # rules
    def show_rules(self, username):
        self.clear_window()
        self.set_screen_background(os.path.join("images", "bgPlay.jpg"))

        card, inner = self._make_overlay_card(self, bg="#b7956b", pad=18)

        tk.Label(
            inner,
            text="HANGVERSUS",
            font=("Castellar", 30, "bold"),
            bg="#b7956b",
            fg="black"
        ).pack(pady=(6, 2))

        tk.Label(
            inner,
            text="A duel of grit, guesses, and bad decisions.",
            font=("Castellar", 14),
            bg="#b7956b",
            fg="black"
        ).pack(pady=(0, 12))

        scroll_outer, content = self._make_scrollable_area(inner, bg="#b7956b", width=820, height=420)
        scroll_outer.pack(pady=(4, 10))

        tk.Label(
            content,
            text=f"Welcome, {username}.",
            font=("Castellar", 18, "bold"),
            bg="#b7956b",
            fg="black"
        ).pack(anchor="w", pady=(0, 10), padx=10)

        rules_text = [
            "The Rules of the Trail",
            "",
            "1) You guess letters one at a time. If the letter is in the phrase, it shows up.",
            "2) Miss a letter, and you take a hit. A limb shows up on your side.",
            "3) Miss two guesses in a row, and it becomes the villain’s turn.",
            "4) While it’s the villain’s turn, your inputs are locked. You will see BOT'S TURN.",
            "5) The villain guesses letters too. If it guesses a letter in the phrase, you will see X marks on its purple line.",
            "6) The villain does not reveal the real letters. Just X marks where it hit.",
            "7) If the villain misses two guesses in a row, it becomes your turn again. You will see YOUR TURN.",
            "8) First one to fill their full hangman loses the duel.",
            "9) You may try to guess the full phrase. If you’re wrong, it costs extra.",
            "",
            "Pick your difficulty like you mean it:",
            "Easy: the villain plays sloppy.",
            "Medium: the villain plays half-smart.",
            "Hard: the villain aims for the most likely letters.",
        ]

        for line in rules_text:
            if line == "The Rules of the Trail":
                tk.Label(
                    content,
                    text=line,
                    font=("Castellar", 18, "bold"),
                    bg="#b7956b",
                    fg="black"
                ).pack(anchor="w", padx=10, pady=(0, 10))
            else:
                tk.Label(
                    content,
                    text=line,
                    font=("Castellar", 13),
                    bg="#b7956b",
                    fg="black",
                    justify="left",
                    wraplength=780
                ).pack(anchor="w", padx=10, pady=2)

        btn_row = tk.Frame(inner, bg="#b7956b", bd=0, highlightthickness=0)
        btn_row.pack(pady=(10, 0))

        tk.Button(
            btn_row,
            text="Back",
            font=("Castellar", 13),
            bg="#d9c9a3",
            bd=0,
            width=12,
            command=self.show_login
        ).grid(row=0, column=0, padx=8)

        tk.Button(
            btn_row,
            text="Continue",
            font=("Castellar", 13, "bold"),
            bg="#7a3e0c",
            fg="white",
            bd=0,
            width=12,
            command=lambda: self.show_difficulty(username)
        ).grid(row=0, column=1, padx=8)

        try:
            self.audio.stop_sfx()
            self.audio.play_duel_loop()
        except Exception:
            pass

    # difficulty
    def show_difficulty(self, username):
        self.clear_window()
        self.set_screen_background(os.path.join("images", "bgPlay.jpg"))

        container = tk.Frame(self, bg="#b7956b", bd=0, highlightthickness=0)
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            container,
            text=f"Welcome {username}",
            font=("Castellar", 26, "bold"),
            bg="#b7956b",
            fg="black"
        ).pack(pady=(20, 10))

        tk.Label(
            container,
            text="Choose Difficulty",
            font=("Castellar", 18),
            bg="#b7956b",
            fg="black"
        ).pack(pady=(0, 20))

        self.difficulty_var = tk.StringVar(value="medium")
        buttons = {}

        def select(value, btn):
            self.difficulty_var.set(value)
            for b in buttons.values():
                b.configure(bg="#e8d6b0")
            btn.configure(bg="#b95f1f")

        def make_diff_button(label, value):
            btn = tk.Button(
                container,
                text=label,
                font=("Castellar", 16),
                width=14,
                bd=0,
                relief="flat",
                bg="#e8d6b0",
                activebackground="#b95f1f",
                command=lambda: select(value, btn)
            )
            btn.pack(pady=6)
            return btn

        buttons["easy"] = make_diff_button("Easy", "easy")
        buttons["medium"] = make_diff_button("Medium", "medium")
        buttons["hard"] = make_diff_button("Hard", "hard")
        select("medium", buttons["medium"])

        tk.Button(
            container,
            text="Start Game",
            font=("Castellar", 14, "bold"),
            bg="#7a3e0c",
            fg="white",
            bd=0,
            width=16,
            command=lambda: self.start_game(username, self.difficulty_var.get()),
        ).pack(pady=(20, 10))

        tk.Button(
            container,
            text="Leaderboard",
            font=("Castellar", 14),
            bg="#c9b27c",
            bd=0,
            width=16,
            command=lambda: self.show_leaderboard(self.difficulty_var.get()),
        ).pack(pady=5)

        tk.Button(
            container,
            text="Back",
            font=("Castellar", 12),
            bg="#d9c9a3",
            bd=0,
            width=16,
            command=lambda: self.show_rules(username),
        ).pack(pady=(10, 20))

        try:
            self.audio.stop_sfx()
            self.audio.play_duel_loop()
        except Exception:
            pass

    def start_game(self, username, difficulty):
        self.clear_window()
        game = HangmanGame(self, username, difficulty=difficulty)
        game.pack(fill="both", expand=True)

    # leaderboard
    def show_leaderboard(self, difficulty):
        self.clear_window()
        self.set_screen_background(os.path.join("images", "bgPlay.jpg"))

        frame = tk.Frame(self, bg="#b7956b", bd=0, highlightthickness=0)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            frame,
            text=f"Leaderboard ({difficulty.capitalize()})",
            font=("Castellar", 22, "bold"),
            bg="#b7956b",
        ).pack(pady=(20, 10))

        lb = db.get_leaderboard(difficulty)
        if not lb:
            tk.Label(
                frame,
                text="No leaderboard data available.",
                font=("Castellar", 16),
                bg="#b7956b"
            ).pack(pady=10)
        else:
            table = tk.Frame(frame, bg="white", bd=1, relief="solid")
            table.pack(padx=30, pady=10)

            headers = ["Rank", "Player", "Score", "Games Played"]
            for col, text in enumerate(headers):
                tk.Label(
                    table,
                    text=text,
                    font=("Castellar", 12, "bold"),
                    bg="#e0e0e0",
                    width=18,
                    relief="ridge",
                    borderwidth=1,
                ).grid(row=0, column=col, sticky="nsew")

            for row, entry in enumerate(lb, start=1):
                tk.Label(table, text=row, font=("Castellar", 12),
                         width=6, relief="ridge", borderwidth=1).grid(row=row, column=0, sticky="nsew")
                tk.Label(table, text=entry["playername"], font=("Castellar", 12),
                         width=18, relief="ridge", borderwidth=1).grid(row=row, column=1, sticky="nsew")
                tk.Label(table, text=entry["total_score"], font=("Castellar", 12),
                         width=10, relief="ridge", borderwidth=1).grid(row=row, column=2, sticky="nsew")
                tk.Label(table, text=entry["games_played"], font=("Castellar", 12),
                         width=12, relief="ridge", borderwidth=1).grid(row=row, column=3, sticky="nsew")

        tk.Button(
            frame,
            text="Back",
            font=("Castellar", 14),
            command=lambda: self.show_difficulty(self.username),
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        ).pack(pady=(10, 20), ipadx=10, ipady=4)

        try:
            self.audio.stop_sfx()
            self.audio.play_duel_loop()
        except Exception:
            pass


if __name__ == "__main__":
    app = HangmanApp()
    app.mainloop()

