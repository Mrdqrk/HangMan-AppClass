import os
import tkinter as tk
from supabase_client import db

def load_local_character(characterid):
    # Query character_parts for this character
    result = (
        db.client
        .from_("character_parts")
        .select("part_type, image_path, partid")
        .eq("characterid", characterid)
        .execute()
    )

    parts = {}
    if result.data:
        for row in result.data:
            path = row["image_path"]
            if not os.path.isabs(path):
                # assume relative to ./images folder
                path = os.path.join("images", path)

            try:
                img = tk.PhotoImage(file=path)
                parts[row["part_type"]] = (img, row["partid"])
            except Exception as e:
                print(f"[ERROR] Failed to load image {path}: {e}")

    return parts
