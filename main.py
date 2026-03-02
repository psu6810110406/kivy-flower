import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['KIVY_TEXT'] = 'pil'

import database
import random

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.core.audio import SoundLoader

# นำเข้าส่วนที่แยกออกไปแต่ละหน้า
from collection import CollectionScreen
from game import LevelScreen, GameScreen
from how_to_play import show_how_to_play_popup

# เพื่อให้ Kivy ค้นหาคลาสเหล่านี้เจอเมื่อโหลดไฟล์ .kv
from kivy.factory import Factory
Factory.register('LevelScreen', cls=LevelScreen)
Factory.register('GameScreen', cls=GameScreen)
Factory.register('CollectionScreen', cls=CollectionScreen)

class MenuScreen(Screen):
    pass

# 2. สร้างตัวจัดการหน้าจอ
class WindowManager(ScreenManager):
    pass

# 3. ตัวหลักของแอปพลิเคชัน
class FlowerApp(App):
    stamina = NumericProperty(100)
    weather = StringProperty("แดดจัด")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.icon = 'assets/images/sunflower_3.png'
        self.current_playing_flower = "rose" 
        
        data = database.load_data()
        self.unlocked_flowers = data.get("unlocked_flowers", [])
        self.flower_progress = data.get("flower_progress", {})
        self.stamina = data.get("stamina", 100)
        self.weather = data.get("weather", "แดดจัด")

    def save_app_state(self):
        database.save_data({
            "unlocked_flowers": self.unlocked_flowers,
            "flower_progress": self.flower_progress,
            "stamina": self.stamina,
            "weather": self.weather
        })

    def build(self):
        # โหลดไฟล์ garden.kv ตามข้อกำหนด
        return Builder.load_file('garden.kv')

    def next_day(self):
        self.stamina = 100
        weathers = ["แดดจัด", "ฝนตก", "เมฆมาก", "พายุเข้า"]
        self.weather = random.choice(weathers)
        # แจ้งเตือนผ่านหน้า GameScreen (ถ้าอยู่ในหน้านั้น)
        curr_screen = self.root.get_screen('game')
        curr_screen.update_status(f"เริ่มต้นวันใหม่! สภาพอากาศวันนี้: {self.weather}")
        self.save_app_state()

    def start_game(self, flower_name):
        self.current_playing_flower = flower_name
        self.root.current = "game"
        
    def show_how_to_play(self):
        show_how_to_play_popup()

    def on_start(self):
        # โหลดไฟล์เสียง
        self.bg_music = SoundLoader.load('assets/sound/soundbg1.mp3')
        
        # ตรวจสอบว่าโหลดไฟล์สำเร็จไหม
        if self.bg_music:
            self.bg_music.loop = True  # สั่งให้เล่นวนลูปไปเรื่อยๆ
            self.bg_music.volume = 0.3 # ปรับระดับความดัง (0.0 ถึง 1.0)
            self.bg_music.play()
        self.click_sound = SoundLoader.load('assets/sound/click.mp3')

    def play_click(self):
        if self.click_sound:
            # สั่งหยุดก่อนเผื่อผู้เล่นกดปุ่มรัวๆ แล้วค่อยสั่งเล่นใหม่
            self.click_sound.stop() 
            self.click_sound.play()

if __name__ == '__main__':
    FlowerApp().run()