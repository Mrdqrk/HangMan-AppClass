import tkinter as tk
from security import load_secrets
load_secrets()
from supabase_client import db
from gameboard import HangmanGame
from security import authenticate, create_user
from tkinter import messagebox

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

        tk.Label(self, text="Password:", font=("Arial", 18)).pack(pady=10)
        self.password_entry = tk.Entry(self, font=("Arial", 16), show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self, text="Login (Use Account)", command=self.login).pack(pady=20)
        tk.Button(self, text="Create Account", command=self.create_account).pack(pady=5)

        tk.Button(self, text="Play as Guest", command=self.login_guest).pack(pady=20)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Enter both username and password.")
            return
        
        if authenticate(username, password):
            self.username = username
            self.show_difficulty(username)
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def create_account(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter a username and password.")
            return

        try:
            create_user(username, password)
            messagebox.showinfo("Success", "Account created. You can now log in.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not create account: {e}")

    def login_guest(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Enter a username to continue as guest.")
            return
        
        db.get_or_create_player(username)

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
