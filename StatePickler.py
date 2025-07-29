import pickle
import json
from pathlib import Path

SAVE_DIR = Path("save_info")
USER_SETTINGS_FILE_PATH = SAVE_DIR / "usersettings.json"
CARD_INFO_FILE_PATH = SAVE_DIR / "card_db.pkl"
CAT_INFO_FILE_PATH = SAVE_DIR / "cat_db.pkl"

SAVE_DIR.mkdir(parents=True, exist_ok=True)

def save_user_settings(user_settings_json):
	USER_SETTINGS_FILE_PATH.write_text(json.dumps(user_settings_json, indent=2))

def load_user_settings():
	user_settings_json = USER_SETTINGS_FILE_PATH.read_text(encoding='utf-8')
	return json.loads(user_settings_json)

# Unpickling the object from the file
with open(file_path, 'rb') as f:
	loaded_data = pickle.load(f)

print(loaded_data)