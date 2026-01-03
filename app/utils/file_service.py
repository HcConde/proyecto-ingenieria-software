import os
import shutil
from app.config.paths import BASE_DIR, PROFILES_DIR


class FileService:
    def save_profile_photo(self, user_id, photo_src):
        os.makedirs(PROFILES_DIR, exist_ok=True)

        ext = os.path.splitext(photo_src)[1].lower()
        if ext not in (".png", ".jpg", ".jpeg", ".webp"):
            ext = ".png"

        dest_abs = os.path.join(PROFILES_DIR, f"user_{user_id}{ext}")
        shutil.copy2(photo_src, dest_abs)

        return os.path.relpath(dest_abs, BASE_DIR).replace("\\", "/")
