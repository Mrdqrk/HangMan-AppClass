import tkinter as tk
from tkinter import ttk
import os
#from PIL import Image, ImageTk

IMAGE_ROOT = "Images"

CATEGORIES = {
    "Cowboy": {
        "player": "Arthur",
        "easy": "clip_art",
        "medium": "Destiny Cowboy",
        "hard": "Rango"
    },
    "Pixar": {
        "player": "Buzzlight_year",
        "easy": "Darla",
        "medium": "Sid",
        "hard": "Syndrome"
    },
    "Videogames": {
        "player": "Steve",
        "easy": "Fazbear",
        "medium": "Slenderman",
        "hard": "Bowser"
    }
}

BODY_PARTS = [
    "head.png",
    "chest.png",
    "left_arm.png",
    "right_arm.png",
    "left_leg.png",
    "right_leg.png"
]


# ========================================================
# MAIN APP
# ========================================================

class HangmanGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hangman Game Board")
        self.geometry("900x600")

        self.category = None
        self.difficulty = None
        self.player_images = {}
        self.enemy_images = {}

        self.show_category_screen()

    # ----------------------------------------------------
    # CATEGORY SELECT SCREEN
    # ----------------------------------------------------
    def show_category_screen(self):
        self.clear_window()
        tk.Label(self, text="SELECT CATEGORY", font=("Arial", 26)).pack(pady=30)

        for cat in CATEGORIES.keys():
            ttk.Button(self, text=cat, width=20,
                       command=lambda c=cat: self.select_category(c)).pack(pady=10)

    def select_category(self, category):
        self.category = category
        self.show_difficulty_screen()

    # ----------------------------------------------------
    # DIFFICULTY SELECT SCREEN
    # ----------------------------------------------------
    def show_difficulty_screen(self):
        self.clear_window()
        tk.Label(self, text=f"{self.category} - SELECT DIFFICULTY", font=("Arial", 24)).pack(pady=30)

        for diff in ("easy", "medium", "hard"):
            ttk.Button(
                self, text=diff.capitalize(), width=20,
                command=lambda d=diff: self.start_game(d)
            ).pack(pady=10)

    # ----------------------------------------------------
    # GAME START + IMAGE LOADING
    # ----------------------------------------------------
    def start_game(self, difficulty):
        self.difficulty = difficulty

        # Load all images for player and enemy
        self.player_images = self.load_character_images(
            CATEGORIES[self.category]["player"]
        )

        self.enemy_images = self.load_character_images(
            CATEGORIES[self.category][difficulty]
        )

        self.show_game_board()

    # ----------------------------------------------------
    # LOAD IMAGES FROM FOLDER
    # ----------------------------------------------------
    def load_character_images(self, folder_name):
        folder_path = os.path.join(IMAGE_ROOT, self.category, folder_name)
        images = {}

        for part in BODY_PARTS:
            full_path = os.path.join(folder_path, part)
            try:
                #images[part] = tk.PhotoImage(file=full_path)
                img = tk.PhotoImage(file=full_path)
                img = img.subsample(5, 5)
                images[part] = img
            except Exception as e:
                print("Error loading:", full_path, e)
                images[part] = None

        return images

    # ----------------------------------------------------
    # GAME BOARD LAYOUT
    # ----------------------------------------------------
    def show_game_board(self):
        self.clear_window()

        tk.Label(self, text=f"{self.category} - {self.difficulty.capitalize()} Mode",
                 font=("Arial", 22)).pack(pady=20)

        board = tk.Frame(self)
        board.pack(pady=20)

        # Player frame
        player_frame = tk.Frame(board)
        player_frame.grid(row=0, column=0, padx=40)

        tk.Label(player_frame, text="PLAYER", font=("Arial", 18)).pack()
        self.display_character(player_frame, self.player_images)

        # Enemy frame
        enemy_frame = tk.Frame(board)
        enemy_frame.grid(row=0, column=1, padx=40)

        tk.Label(enemy_frame, text="ENEMY AI", font=("Arial", 18)).pack()
        self.display_character(enemy_frame, self.enemy_images)

    # ----------------------------------------------------
    # DISPLAY CHARACTER (STACKED IMAGES)
    # ----------------------------------------------------
    def display_character(self, parent, images):
        canvas = tk.Canvas(parent, width=320, height=500, bg="white")
        canvas.pack()

        spacing = 30

        y = 30
        for part in BODY_PARTS:
            img = images.get(part)
            if img:
                canvas.create_image(160, y, image=img, anchor="n")
           # y += img.height() if img else 20
            y += spacing

    # ----------------------------------------------------
    # CLEAR WINDOW
    # ----------------------------------------------------
    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()


# ========================================================
# RUN APP
# ========================================================
if __name__ == "__main__":
    HangmanGame().mainloop()
