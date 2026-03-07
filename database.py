import json
import os

SAVE_FILE = "save_data.json"

# 1. ยุบค่าเริ่มต้นมาไว้ที่เดียว! อนาคตอยากเพิ่มค่าอะไร (เช่น money, exp, level) มาเติมตรงนี้ที่เดียวจบ
DEFAULT_SAVE = {
    "unlocked_flowers": [],
    "flower_progress": {},
    "stamina": 100,
    "weather": "แดดจัด"
}

def load_data():
    if not os.path.exists(SAVE_FILE):
        return DEFAULT_SAVE.copy()  # ใช้ .copy() เพื่อไม่ให้ค่าต้นฉบับโดนแก้
        
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        try:
            loaded_data = json.load(f)
            
            final_data = DEFAULT_SAVE.copy()
            final_data.update(loaded_data)
            return final_data
            
        except json.JSONDecodeError:
            return DEFAULT_SAVE.copy()

def save_data(app_data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(app_data, f, ensure_ascii=False, indent=4)