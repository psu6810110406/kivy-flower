import os
os.environ['KIVY_TEXT'] = 'pil'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
import random

# 1. สร้างหน้าจอต่างๆ เตรียมไว้ก่อน
class MenuScreen(Screen):
    pass

class LevelScreen(Screen):
    pass

class ShopScreen(Screen):
    def buy_seed(self, seed_name, price):
        app = App.get_running_app()
        if app.money >= price:
            app.money -= price
            print(f"ซื้อ {seed_name} สำเร็จ!")
            app.unlocked_flowers.add(seed_name) # ซื้อแล้วได้ปลดล็อคใน Collection ทันที
        else:
            print("เงินไม่พอ!")

    def buy_item(self, item_name, price):
        app = App.get_running_app()
        if app.money >= price:
            app.money -= price
            print(f"ซื้อ {item_name} สำเร็จ!")
        else:
            print("เงินไม่พอ!")

class CollectionScreen(Screen):
    def on_pre_enter(self, *args):
        app = App.get_running_app()
        if len(app.unlocked_flowers) == 0:
            self.ids.collection_lbl.text = "ยังไม่มีดอกไม้เลย ไปปลูกกันเถอะ!"
        else:
            flowers_th = {"rose": "กุหลาบ", "tulip": "ทิวลิป", "daisy": "เดซี่", "sunflower": "ทานตะวัน", "hibiscus": "ชบา", "กล้วยไม้": "กล้วยไม้", "มะลิ": "มะลิ", "กระบองเพชร": "กระบองเพชร"}
            unlocked_names = [flowers_th.get(f, f) for f in app.unlocked_flowers]
            self.ids.collection_lbl.text = "ปลูกสำเร็จ:\n" + "\n".join(unlocked_names)

class GameScreen(Screen):
    growth_progress = NumericProperty(0)
    flower_image_source = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_flower = ""
        # 1. Property Binding: ผูกค่า property เข้ากับฟังก์ชันอัตโนมัติ (Day 3-5 Callback)
        self.bind(growth_progress=self.on_growth_change)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.current_flower = app.current_playing_flower
        
        flowers_th = {"rose": "กุหลาบ", "tulip": "ทิวลิป", "daisy": "เดซี่", "sunflower": "ทานตะวัน", "hibiscus": "ชบา"}
        self.ids.title_lbl.text = f"ด่าน: กำลังปลูก {flowers_th.get(self.current_flower, self.current_flower)}"
        self.reset_game()

    def reset_game(self):
        self.growth_progress = 0
        self.flower_image_source = f"{self.current_flower}_0.png"
        self.ids.result_lbl.text = "เริ่มปลูกต้นไม้กันเลย!"
        # จัดตำแหน่งต้นไม้กลับตรงกลางเมื่อเริ่มด่านใหม่
        self.ids.flower_scatter.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

    def on_growth_change(self, instance, value):
        # เปลี่ยนรูปภาพอัตโนมัติตามความเติบโต
        if value >= 100:
            self.flower_image_source = f"{self.current_flower}_3.png"
        elif value >= 60:
            self.flower_image_source = f"{self.current_flower}_2.png"
        elif value >= 30:
            self.flower_image_source = f"{self.current_flower}_1.png"
        else:
            self.flower_image_source = f"{self.current_flower}_0.png"

    # Action Callbacks ตอบสนองต่อปุ่ม
    def water_plant(self):
        app = App.get_running_app()
        if self.growth_progress >= 100: return
        if app.stamina >= 10:
            app.stamina -= 10
            self.growth_progress += 15
            self.update_status("รดน้ำแล้ว! ต้นไม้สดชื่น (+15%)")
            self.check_win()
        else:
            self.update_status("พลังงานไม่พอ! ต้องพักก่อน")

    def fertilize_plant(self):
        app = App.get_running_app()
        if self.growth_progress >= 100: return
        if app.stamina >= 15:
            app.stamina -= 15
            self.growth_progress += 25
            self.update_status("ใส่ปุ๋ยแล้ว! ต้นไม้โตไวมาก (+25%)")
            self.check_win()
        else:
            self.update_status("พลังงานไม่พอ! ต้องพักก่อน")

    def till_soil(self):
        app = App.get_running_app()
        if self.growth_progress >= 100: return
        if app.stamina >= 20:
            app.stamina -= 20
            self.growth_progress += 10
            self.update_status("พรวนดินเรียบร้อย! ดินร่วนซุย (+10%)")
            self.check_win()
        else:
            self.update_status("พลังงานไม่พอ! ต้องพักก่อน")

    def update_status(self, msg):
        self.ids.result_lbl.text = msg

    def check_win(self):
        if self.growth_progress >= 100:
            self.growth_progress = 100 # กันเกิน
            self.update_status("ยินดีด้วย! ดอกไม้บานเต็มที่แล้ว!")
            app = App.get_running_app()
            app.unlocked_flowers.add(self.current_flower)
            app.money += 50
            app.stamina += 30 # ได้โบนัสพลังงานคืน
            print("You won!")

    def give_up(self):
        self.reset_game()
        app = App.get_running_app()
        app.root.current = "levels"

# 2. สร้างตัวจัดการหน้าจอ
class WindowManager(ScreenManager):
    pass

# 3. ตัวหลักของแอปพลิเคชัน
class FlowerApp(App):
    money = NumericProperty(100)
    stamina = NumericProperty(100)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_playing_flower = "rose" 
        self.unlocked_flowers = set()

    def build(self):
        # โหลดไฟล์ garden.kv ตามข้อกำหนด
        return Builder.load_file('garden.kv')

    def start_game(self, flower_name):
        self.current_playing_flower = flower_name
        self.root.current = "game"
        
    def show_how_to_play(self):
        # Popup สำหรับโชว์วิธีการเล่น
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        box.add_widget(Label(
            text="วิธีเล่น:\n1. ใช้พลังงานเพื่อรดน้ำ ใส่ปุ๋ย หรือพรวนดิน\n2. หลอดการเติบโต ProgressBar ครบ 100% จะได้ดอกไม้\n3. เงินใช้อัปเกรดหรือซื้อเมล็ดเพิ่มเติม\n4. สามารถซูม/ย้ายต้นไม้ด้้วย Scatter Widget",
            font_name='font.ttf', 
            font_size='18sp'
        ))
        close_btn = Button(text="ปิดหน้าต่าง", font_name='font.ttf', size_hint_y=None, height=50)
        box.add_widget(close_btn)
        
        popup = Popup(title="วิธีการเล่น (Settings)", content=box, size_hint=(0.8, 0.6), title_font='font.ttf')
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    FlowerApp().run()