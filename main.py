import tkinter as tk
from supabase_client import db
from gameboard import HangmanGame

class HangmanApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hangman Game")
        self.geometry("800x600")
        self.username = None

        self.show_login()

    # -----------------------------
    # Login screen
    # -----------------------------
    def show_login(self):
        self.clear_window()
        tk.Label(self, text="Enter Username:", font=("Arial", 18)).pack(pady=20)
        self.username_entry = tk.Entry(self, font=("Arial", 16))
        self.username_entry.pack(pady=10)
        tk.Button(self, text="Login", command=self.login).pack(pady=20)

    def login(self):
        username = self.username_entry.get().strip()
        if not username:
            return
        self.username = username
        self.show_difficulty(username)

    # -----------------------------
    # Difficulty chooser
    # -----------------------------
    def show_difficulty(self, username):
        self.clear_window()
        tk.Label(self, text=f"Welcome {username}!", font=("Arial", 20)).pack(pady=20)
        tk.Label(self, text="Choose Difficulty:", font=("Arial", 18)).pack(pady=10)

        difficulty_var = tk.StringVar(value="medium")

        for diff in ["easy", "medium", "hard"]:
            tk.Radiobutton(self, text=diff.capitalize(),
                           variable=difficulty_var, value=diff,
                           font=("Arial", 16)).pack(anchor="w")

        tk.Button(self, text="Start Game",
                  command=lambda: self.start_game(username, difficulty_var.get())).pack(pady=20)

        tk.Button(self, text="Leaderboard",
                  command=lambda: self.show_leaderboard(difficulty_var.get())).pack(pady=10)

        tk.Button(self, text="Back to Login", command=self.show_login).pack(pady=10)

    # -----------------------------
    # Start game
    # -----------------------------
    def start_game(self, username, difficulty):
        self.clear_window()
        game = HangmanGame(self, username, difficulty=difficulty)
        game.pack(fill="both", expand=True)

    # -----------------------------
    # Leaderboard screen
    # -----------------------------
    def show_leaderboard(self, difficulty):
        self.clear_window()
        tk.Label(self, text=f"Leaderboard ({difficulty.capitalize()})",
                 font=("Arial", 20), fg="blue").pack(pady=20)

        lb = db.get_leaderboard(difficulty)
        if not lb:
            tk.Label(self, text="No leaderboard data available.",
                     font=("Arial", 16)).pack(pady=10)
        else:
            for row in lb:
                tk.Label(self,
                         text=f"{row['playername']} - Score: {row['total_score']} - Games: {row['games_played']}",
                         font=("Arial", 16)).pack(anchor="w")

        tk.Button(self, text="Back to Login", command=self.show_login).pack(pady=20)

    # -----------------------------
    # Utility
    # -----------------------------
    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    app = HangmanApp()
    app.mainloop()
