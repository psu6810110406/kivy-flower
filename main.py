import os
os.environ['KIVY_TEXT'] = 'pil'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
import random

# 1. สร้างหน้าจอต่างๆ เตรียมไว้ก่อน
class MenuScreen(Screen):
    pass

class LevelScreen(Screen):
    pass

class CollectionScreen(Screen):
    def on_pre_enter(self, *args):
        app = App.get_running_app()
        if len(app.unlocked_flowers) == 0:
            self.ids.collection_lbl.text = "ยังไม่มีดอกไม้เลย ไปปลูกกันเถอะ!"
        else:
            flowers_th = {"rose": "กุหลาบ", "tulip": "ทิวลิป", "daisy": "เดซี่", "sunflower": "ทานตะวัน", "hibiscus": "ชบา"}
            unlocked_names = [flowers_th[f] for f in app.unlocked_flowers]
            self.ids.collection_lbl.text = "ปลูกสำเร็จ:\n" + "\n".join(unlocked_names)

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target_water = 0
        self.target_sun = 0
        self.target_fert = 0
        self.current_flower = ""

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.current_flower = app.current_playing_flower
        
        flowers_th = {"rose": "กุหลาบ", "tulip": "ทิวลิป", "daisy": "เดซี่", "sunflower": "ทานตะวัน", "hibiscus": "ชบา"}
        self.ids.title_lbl.text = f"ด่าน: กำลังปลูก {flowers_th[self.current_flower]}"
        self.reset_game()

    def reset_game(self):
        self.target_water = random.randint(1, 5)
        self.target_sun = random.randint(1, 8)
        self.target_fert = random.randint(1, 4)
        
        self.ids.flower_img.source = f"{self.current_flower}_0.png"
        self.ids.result_lbl.text = "รอการตรวจสอบ..."
        
        self.ids.spin_water.text = 'น้ำ (1-5)'
        self.ids.spin_sun.text = 'แดด (1-8)'
        self.ids.spin_fert.text = 'ปุ๋ย (1-4)'

    def check_answer(self):
        try:
            w = int(self.ids.spin_water.text)
            s = int(self.ids.spin_sun.text)
            f = int(self.ids.spin_fert.text)
            
            feedback = []
            correct_count = 0
            
            if w < self.target_water: feedback.append("น้ำน้อย")
            elif w > self.target_water: feedback.append("น้ำมาก")
            else:
                feedback.append("น้ำพอดี")
                correct_count += 1
            
            if s < self.target_sun: feedback.append("แดดน้อย")
            elif s > self.target_sun: feedback.append("แดดมาก")
            else:
                feedback.append("แดดพอดี")
                correct_count += 1
            
            if f < self.target_fert: feedback.append("ปุ๋ยน้อย")
            elif f > self.target_fert: feedback.append("ปุ๋ยมาก")
            else:
                feedback.append("ปุ๋ยพอดี")
                correct_count += 1
            
            self.ids.flower_img.source = f"{self.current_flower}_{correct_count}.png"
            self.ids.result_lbl.text = " | ".join(feedback)
            
            if correct_count == 3:
                self.ids.result_lbl.text = "ยินดีด้วย! ดอกไม้บานแล้ว!"
                app = App.get_running_app()
                app.unlocked_flowers.add(self.current_flower)

        except ValueError:
            self.ids.result_lbl.text = "กรุณาเลือกให้ครบ!"

# 2. สร้างตัวจัดการหน้าจอ
class WindowManager(ScreenManager):
    pass

# 3. ตัวหลักของแอปพลิเคชัน
class FlowerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_playing_flower = "rose" 
        self.unlocked_flowers = set()

    def build(self):
        # ย้ายคำสั่งโหลดไฟล์หน้าตามาไว้ตรงนี้! ให้โหลดหลังจากที่คลาสทั้งหมดถูกสร้างแล้ว
        return Builder.load_file('flower.kv')

    def start_game(self, flower_name):
        self.current_playing_flower = flower_name
        self.root.current = "game"

if __name__ == '__main__':
    FlowerApp().run()