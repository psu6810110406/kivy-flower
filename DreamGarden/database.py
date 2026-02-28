import json
import os

SAVE_FILE = "save_data.json"

def load_data():
    if not os.path.exists(SAVE_FILE):
        return {
            "unlocked_flowers": [],
            "flower_progress": {},
            "stamina": 100,
            "weather": "แดดจัด"
        }
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {
                "unlocked_flowers": [],
                "flower_progress": {},
                "stamina": 100,
                "weather": "แดดจัด"
            }

def save_data(app_data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(app_data, f, ensure_ascii=False, indent=4)