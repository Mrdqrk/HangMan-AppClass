import os
import random
import tkinter as tk

# Base folder for images
BASE_IMAGES_DIR = os.path.join("images", "images")

# Map normalized category names to subfolders
CATEGORY_MAP = {
    "cowboy": "cowboys",
    "cowboys": "cowboys",
    "pixar": "pixar",
    "social": "social",
    "music": "cowboys",   # 👈 music phrases now use cowboy models
}

# Required part files
PART_FILES = {
    "torso": "body.png",
    "head": "head.png",
    "left_arm": "leftA.png",
    "right_arm": "rightA.png",
    "left_leg": "leftL.png",
    "right_leg": "rightL.png",
}

def _normalize_category(category: str) -> str:
    """Normalize category name to lowercase and strip spaces."""
    return category.strip().lower() if category else ""

def _load_character_folder(folder_path: str):
    """Load all parts for a character folder. Skip if incomplete."""
    parts = {}
    for part_name, filename in PART_FILES.items():
        full_path = os.path.join(folder_path, filename)
        if not os.path.exists(full_path):
            print(f"[WARN] Missing {filename} in {folder_path}, skipping character")
            return None
        try:
            img = tk.PhotoImage(file=full_path)
            parts[part_name] = (img, full_path)
        except Exception as e:
            print(f"[ERROR] Failed to load image {full_path}: {e}")
            return None
    return parts

def _get_character_folders_for_category(category: str):
    """Return all character folders for a given category."""
    norm = _normalize_category(category)
    subdir = CATEGORY_MAP.get(norm)
    base = os.path.join(BASE_IMAGES_DIR, subdir) if subdir else BASE_IMAGES_DIR

    if not os.path.isdir(base):
        print(f"[WARN] No image directory for category '{category}' (normalized='{norm}'): {base}")
        return []

    folders = [
        os.path.join(base, name)
        for name in os.listdir(base)
        if os.path.isdir(os.path.join(base, name))
    ]
    return folders

def load_two_random_characters(category: str):
    """Load two random characters for the given category."""
    folders = _get_character_folders_for_category(category)
    random.shuffle(folders)

    valid_characters = []
    for folder in folders:
        parts = _load_character_folder(folder)
        if parts:
            char_name = os.path.basename(folder)
            valid_characters.append((char_name, parts))

    if len(valid_characters) == 0:
        print(f"[WARN] No valid characters found for category '{category}', falling back to Pixar")
        return load_two_random_characters("pixar")

    if len(valid_characters) == 1:
        return valid_characters[0], valid_characters[0]

    return random.sample(valid_characters, 2)
