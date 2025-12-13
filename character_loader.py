import os
import random
import tkinter as tk

BASE_IMAGES_DIR = os.path.join("images", "images")

CATEGORY_MAP = {
    "cowboy": "cowboys",
    "cowboys": "cowboys",
    "pixar": "pixar",
    "social": "social",
}

PART_FILES = {
    "torso": "body.png",
    "head": "head.png",
    "left_arm": "leftA.png",
    "right_arm": "rightA.png",
    "left_leg": "leftL.png",
    "right_leg": "rightL.png",
}


def _normalize_category(category: str) -> str:
    return category.strip().lower() if category else ""


def _load_character_folder(folder_path: str):
    parts = {}
    for part_name, filename in PART_FILES.items():
        full_path = os.path.join(folder_path, filename)
        if not os.path.exists(full_path):
            return None
        try:
            img = tk.PhotoImage(file=full_path)
            parts[part_name] = (img, full_path)
        except Exception:
            return None
    return parts


def _get_character_folders_for_category(category: str):
    norm = _normalize_category(category)
    subdir = CATEGORY_MAP.get(norm)
    base = os.path.join(BASE_IMAGES_DIR, subdir) if subdir else BASE_IMAGES_DIR

    if not os.path.isdir(base):
        return []

    return [
        os.path.join(base, name)
        for name in os.listdir(base)
        if os.path.isdir(os.path.join(base, name))
    ]


def load_two_random_characters(category: str):
    folders = _get_character_folders_for_category(category)
    random.shuffle(folders)

    valid_characters = []
    for folder in folders:
        parts = _load_character_folder(folder)
        if parts:
            char_name = os.path.basename(folder)
            valid_characters.append((char_name, parts))

    if len(valid_characters) == 0:
        return load_two_random_characters("pixar")

    if len(valid_characters) == 1:
        return valid_characters[0], valid_characters[0]

    return random.sample(valid_characters, 2)
