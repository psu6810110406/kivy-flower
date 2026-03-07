import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['KIVY_AUDIO'] = 'sdl2'

from kivy.config import Config
# กำหนดขนาดหน้าต่างให้ชัดเจนเพื่อแก้ ZeroDivisionError ใน Kivy
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'resizable', '1')
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ColorProperty, StringProperty, NumericProperty

# --- Custom UI components defined in Python for better property support ---
class MinimalButton(Button):
    # Custom property to store the intended color
    btn_color = ColorProperty([0.1, 0.4, 0.15, 1])

class StatusGauge(BoxLayout):
    label_text = StringProperty("")
    val = NumericProperty(0)
    max_v = NumericProperty(100)
    color = ColorProperty([1, 1, 1, 1])

import database
import random

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.core.audio import SoundLoader

# นำเข้าไฟล์ที่แยกออกไป
from collection import CollectionScreen
from game import LevelScreen, GameScreen
from how_to_play import show_how_to_play_popup
from settings_screen import SettingsScreen

# ค้นหาคลาสเมื่อโหลดไฟล์
from kivy.factory import Factory
Factory.register('LevelScreen', cls=LevelScreen)
Factory.register('GameScreen', cls=GameScreen)
Factory.register('CollectionScreen', cls=CollectionScreen)
Factory.register('SettingsScreen', cls=SettingsScreen)
Factory.register('MinimalButton', cls=MinimalButton)
Factory.register('StatusGauge', cls=StatusGauge)

class MenuScreen(Screen):
    pass

# 2. สร้างตัวจัดการหน้าจอ
class WindowManager(ScreenManager):
    pass

# 3. ตัวหลักของแอปพลิเคชัน
class FlowerApp(App):
    stamina = NumericProperty(100)
    weather = StringProperty("แดดจัด")
    music_volume = NumericProperty(0.3)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.icon = 'assets/images/sunflower_3.png'
        self.current_playing_flower = "rose" 
        
        data = database.load_data()
        self.unlocked_flowers = data.get("unlocked_flowers", [])
        self.flower_progress = data.get("flower_progress", {})
        self.stamina = data.get("stamina", 100)
        self.weather = data.get("weather", "แดดจัด")
        self.music_volume = data.get("music_volume", 0.3)

    def save_app_state(self):
        database.save_data({
            "unlocked_flowers": self.unlocked_flowers,
            "flower_progress": self.flower_progress,
            "stamina": self.stamina,
            "weather": self.weather,
            "music_volume": float(self.music_volume)
        })

    def set_volume(self, value):
        self.music_volume = value
        if getattr(self, 'bg_music', None) and self.bg_music:
            self.bg_music.volume = value

    def build(self):
        from kivy.uix.label import Label
        from kivy.uix.screenmanager import Screen
        from kivy.uix.floatlayout import FloatLayout
        from kivy.graphics import Color, Rectangle
        from kivy.core.window import Window
        
        # เปลี่ยนสีพื้นหลังหน้าต่าง 
        Window.clearcolor = (0.1, 0.25, 0.1, 1)
        
        self.sm = WindowManager()
        loading = Screen(name='loading')
        
        layout = FloatLayout()
        
        # วาดพื้นหลังสีเขียวเข้มให้ Layout นี้
        with layout.canvas.before:
            Color(0.1, 0.25, 0.1, 1)
            self.bg_rect = Rectangle(size=(2000, 2000), pos=(0, 0))
            
        def update_rect(instance, value):
            self.bg_rect.size = instance.size
            self.bg_rect.pos = instance.pos
        layout.bind(size=update_rect, pos=update_rect)
        
        tips = [
            "TIP: ดอกไม้แต่ละชนิดชอบสภาพอากาศไม่เหมือนกันนะ",
            "TIP: ควรดูแลแต้ม 'ความเอาใจใส่' ให้สูงเข้าไว้!",
            "TIP: ถ้าฝนตกอยู่แล้วก็ไม่เปลี่ยนใจรดน้ำหรอกนะ ต้นไม้จะแฉะ!",
            "TIP: ระวังอย่าลืมรดน้ำในวันแดดจัดนะ ต้นไม้จะเหี่ยวเฉาได้!"
        ]
        chosen_tip = random.choice(tips)
        
        lbl = Label(
            text=f'[b]Loading Dream Garden...[/b]\n\n[color=A5D6A7]{chosen_tip}[/color]', 
            markup=True,
            font_name='assets/fonts/font.ttf', 
            font_size='28sp',
            halign='center',
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        layout.add_widget(lbl)
        loading.add_widget(layout)
        
        self.sm.add_widget(loading)
        return self.sm

    def load_main_ui(self, dt):
        # โหลดไฟล์ภาพและกราฟิกจาก KV
        loaded_sm = Builder.load_file('garden.kv')
        
        # ดึงหน้าจอที่โหลดเสร็จแล้วมายัดใส่ Manager ตัวหลัก
        screens = list(loaded_sm.screens)
        loaded_sm.clear_widgets()
        for s in screens:
            self.sm.add_widget(s)
            
        # ลบหน้าจอโหลดทิ้ง และเปิดเมนูเกม
        self.sm.transition = NoTransition()
        self.sm.current = 'menu'
        self.sm.remove_widget(self.sm.get_screen('loading'))
        self.sm.transition = SlideTransition()

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
        from kivy.clock import Clock
        
        self.bg_music = None
        self.click_sound = None
        
        # ให้มันโชว์หน้าจอ Loading + ทิปไปสัก 2.5 วินาที ก่อนจะเริ่มโหลดภาพหนักๆ
        Clock.schedule_once(self.load_main_ui, 1.0)
        # ส่วนเพลงเล่นช้าไปอีกหน่อย
        Clock.schedule_once(self.load_sounds, 1.0)

    def load_sounds(self, dt):
        self.bg_music = SoundLoader.load('assets/sound/soundbg1.mp3')
        if self.bg_music:
            self.bg_music.loop = True
            self.bg_music.volume = self.music_volume
            self.bg_music.play()
        self.click_sound = SoundLoader.load('assets/sound/click.mp3')

    def play_click(self):
        if self.click_sound:
            # สั่งหยุดก่อนเผื่อผู้เล่นกดปุ่มรัวๆ แล้วค่อยสั่งเล่นใหม่
            self.click_sound.stop() 
            self.click_sound.play()

if __name__ == '__main__':
    FlowerApp().run()