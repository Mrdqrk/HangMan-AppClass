import tkinter as tk
from PIL import Image, ImageTk
from supabase_client import db
from gameboard import HangmanGame


class HangmanApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hangman Game")
        self.geometry("900x650")
        self.configure(bg="#f5f5f5")

        self.username = None
        self.original_bg = None
        self.bg_img = None
        self.bg_label = None

        self.show_login()

    # Login
    def show_login(self):
        self.clear_window()

        # --- Load background image ---
        try:
            self.original_bg = Image.open("images/background.png")  # adjust path/filename
            resized = self.original_bg.resize((900, 650), Image.LANCZOS)
            self.bg_img = ImageTk.PhotoImage(resized)

            # Label as background
            self.bg_label = tk.Label(self, image=self.bg_img)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

            # Bind resize event for responsive background
            self.bind("<Configure>", self._resize_background)
        except Exception as e:
            print(f"[WARN] Could not load background image: {e}")

        # --- Overlay frame for login widgets ---
        frame = tk.Frame(self, bg="#f5f5f5", bd=2)
        frame.place(relx=0.5, rely=0.5, anchor="center")  # center on screen

        tk.Label(frame, text="Enter Username:", font=("Arial", 20, "bold"),
                 bg="#f5f5f5").pack(pady=20)
        self.username_entry = tk.Entry(frame, font=("Arial", 16), width=20, justify="center")
        self.username_entry.pack(pady=10)
        tk.Button(frame, text="Login", font=("Arial", 14),
                  command=self.login).pack(pady=20)

    def _resize_background(self, event):
        """Resize background dynamically when window changes size."""
        if self.original_bg and self.bg_label:
            new_width = max(400, event.width)
            new_height = max(300, event.height)
            resized = self.original_bg.resize((new_width, new_height), Image.LANCZOS)
            self.bg_img = ImageTk.PhotoImage(resized)
            self.bg_label.configure(image=self.bg_img)

    def login(self):
        username = self.username_entry.get().strip()
        if not username:
            return
        self.username = username
        self.show_difficulty(username)

    # Difficulty
    def show_difficulty(self, username):
        self.clear_window()

        frame = tk.Frame(self, bg="#f5f5f5")
        frame.pack(expand=True, fill="both")

        tk.Label(frame, text=f"Welcome {username}!",
                 font=("Arial", 22, "bold"), bg="#f5f5f5").pack(pady=20)
        tk.Label(frame, text="Choose Difficulty:",
                 font=("Arial", 18), bg="#f5f5f5").pack(pady=10)

        self.difficulty_var = tk.StringVar(value="medium")

        for diff in ["easy", "medium", "hard"]:
            tk.Radiobutton(
                frame,
                text=diff.capitalize(),
                variable=self.difficulty_var,
                value=diff,
                font=("Arial", 16),
                bg="#f5f5f5",
            ).pack(anchor="w", padx=200)

        tk.Button(
            frame,
            text="Start Game",
            font=("Arial", 14, "bold"),
            command=lambda: self.start_game(username, self.difficulty_var.get()),
        ).pack(pady=20)

        tk.Button(
            frame,
            text="Leaderboard",
            font=("Arial", 14),
            command=lambda: self.show_leaderboard(self.difficulty_var.get()),
        ).pack(pady=10)

        tk.Button(
            frame,
            text="Back to Login",
            font=("Arial", 12),
            command=self.show_login,
        ).pack(pady=10)

    # Start
    def start_game(self, username, difficulty):
        self.clear_window()
        game = HangmanGame(self, username, difficulty=difficulty)
        game.pack(fill="both", expand=True)

    # Leaderboard
    def show_leaderboard(self, difficulty):
        self.clear_window()

        frame = tk.Frame(self, bg="#f5f5f5")
        frame.pack(expand=True, fill="both")

        tk.Label(
            frame,
            text=f"Leaderboard ({difficulty.capitalize()})",
            font=("Arial", 22, "bold"),
            fg="blue",
            bg="#f5f5f5",
        ).pack(pady=20)

        lb = db.get_leaderboard(difficulty)
        if not lb:
            tk.Label(
                frame,
                text="No leaderboard data available.",
                font=("Arial", 16),
                bg="#f5f5f5",
            ).pack(pady=10)
        else:
            table = tk.Frame(frame, bg="white", bd=1, relief="solid")
            table.pack(padx=40, pady=10)

            headers = ["Rank", "Player", "Score", "Games Played"]
            for col, text in enumerate(headers):
                tk.Label(
                    table,
                    text=text,
                    font=("Arial", 14, "bold"),
                    bg="#e0e0e0",
                    width=20,
                    relief="ridge",
                    borderwidth=1,
                ).grid(row=0, column=col, sticky="nsew")

            for row, entry in enumerate(lb, start=1):
                tk.Label(
                    table,
                    text=row,
                    font=("Arial", 14),
                    width=5,
                    relief="ridge",
                    borderwidth=1,
                ).grid(row=row, column=0, sticky="nsew")

                tk.Label(
                    table,
                    text=entry["playername"],
                    font=("Arial", 14),
                    width=20,
                    relief="ridge",
                    borderwidth=1,
                ).grid(row=row, column=1, sticky="nsew")

                tk.Label(
                    table,
                    text=entry["total_score"],
                    font=("Arial", 14),
                    width=10,
                    relief="ridge",
                    borderwidth=1,
                ).grid(row=row, column=2, sticky="nsew")

                tk.Label(
                    table,
                    text=entry["games_played"],
                    font=("Arial", 14),
                    width=12,
                    relief="ridge",
                    borderwidth=1,
                ).grid(row=row, column=3, sticky="nsew")

        tk.Button(
            frame,
            text="Back",
            font=("Arial", 14),
            command=lambda: self.show_difficulty(self.username),
        ).pack(pady=20)

    def clear_window(self):
        self.unbind("<Configure>")  # stop resize callback when switching screens
        for widget in self.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = HangmanApp()
    app.mainloop()
