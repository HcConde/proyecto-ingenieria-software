import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PROFILES_DIR = os.path.join(ASSETS_DIR, "profiles")
DEFAULT_PROFILE = os.path.join(PROFILES_DIR, "default.png")
