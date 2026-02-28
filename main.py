import os
os.environ['KIVY_TEXT'] = 'pil'

from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.animation import Animation
import random

# 1. สร้างหน้าจอต่างๆ เตรียมไว้ก่อน
class MenuScreen(Screen):
    pass

class LevelScreen(Screen):
    pass

from kivy.uix.scatter import Scatter
from kivy.uix.image import Image

class DraggableFlower(Scatter):
    def __init__(self, flower_type, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (100, 100)
        self.do_rotation = False
        img_src = f"assets/images/{flower_type}_3.png"
        if not os.path.exists(img_src): img_src = "assets/images/flower_3.png"
        self.add_widget(Image(source=img_src, size=self.size))

class InventoryFlower(Image):
    def __init__(self, flower_type, **kwargs):
        super().__init__(**kwargs)
        self.flower_type = flower_type
        self.size_hint = (None, None)
        self.size = (100, 100)
        img_src = f"assets/images/{flower_type}_3.png"
        if not os.path.exists(img_src): img_src = "assets/images/flower_3.png"
        self.source = img_src

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            app = App.get_running_app()
            screen = app.root.get_screen('collection')
            
            flower = DraggableFlower(flower_type=self.flower_type)
            flower.center = touch.pos
            screen.ids.garden_area.add_widget(flower)
            
            # Make the new scatter widget grab the touch to start dragging immediately
            flower.on_touch_down(touch)
            return True
        return super().on_touch_down(touch)

class CollectionScreen(Screen):
    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.ids.inventory_grid.clear_widgets()
        if len(app.unlocked_flowers) == 0:
            pass # No flowers yet
        else:
            for f in app.unlocked_flowers:
                flower = InventoryFlower(flower_type=f)
                self.ids.inventory_grid.add_widget(flower)
    def on_touch_move(self, touch):
        if 'button' in touch.profile and touch.button == 'right':
            self.canvas.after.clear()
            with self.canvas.after:
                from kivy.graphics import Color, Line
                Color(0.4, 0.7, 1, 0.5) # สีน้ำฟ้าใส
                Line(points=[touch.ox, touch.oy, touch.x, touch.y], width=2)
            
            for child in self.ids.garden_area.children:
                if child.collide_point(*touch.pos):
                    from kivy.animation import Animation
                    anim = Animation(scale=1.1, duration=0.1) + Animation(scale=1.0, duration=0.1)
                    anim.start(child)
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if 'button' in touch.profile and touch.button == 'right':
            self.canvas.after.clear()
        return super().on_touch_up(touch)

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
        self.flower_image_source = self.get_flower_image(0)
        self.ids.result_lbl.text = "เริ่มปลูกต้นไม้กันเลย!"
        # จัดตำแหน่งต้นไม้กลับตรงกลางเมื่อเริ่มด่านใหม่
        self.ids.flower_scatter.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

    def get_flower_image(self, state):
        path = f"assets/images/{self.current_flower}_{state}.png"
        if os.path.exists(path):
            return path
        return f"assets/images/flower_{state}.png"

    def on_growth_change(self, instance, value):
        # เปลี่ยนรูปภาพอัตโนมัติตามความเติบโต
        if value >= 100:
            self.flower_image_source = self.get_flower_image(3)
        elif value >= 60:
            self.flower_image_source = self.get_flower_image(2)
        elif value >= 30:
            self.flower_image_source = self.get_flower_image(1)
        else:
            self.flower_image_source = self.get_flower_image(0)

    # Action Callbacks ตอบสนองต่อปุ่ม
    def water_plant(self):
        app = App.get_running_app()
        if self.growth_progress >= 100: return
        if app.stamina >= 10:
            app.stamina -= 10
            bonus = 20 if app.weather == "แดดจัด" else 10
            self.growth_progress += bonus
            self.update_status(f"รดน้ำในวัน {app.weather} (+{bonus}%)")
            
            # Animation สั่นต้นไม้เมื่อรดน้ำ
            anim = Animation(scale=1.2, duration=0.1) + Animation(scale=1.0, duration=0.1)
            anim.start(self.ids.flower_scatter)
            
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
            self.update_status("ยินดีด้วย! ดอกไม้บานเต็มที่แล้ว เก็บเกี่ยวได้เลย!")
            app = App.get_running_app()
            app.money += 50
            # ดอกไม้บานแล้ว จะมีปุ่มเก็บเกี่ยวโผล่ขึ้นมาตาม logic ใน garden.kv

    def collect_flower(self):
        if self.growth_progress >= 100:
            app = App.get_running_app()
            # เพิ่มดอกไม้ลงใน Collection
            app.unlocked_flowers.append(self.current_flower)
            self.update_status("เก็บเข้า Collection แล้ว!")
            # กลับไปหน้าหลัก
            app.root.current = "menu"
            app.stamina += 30 # ได้โบนัสพลังงานคืน
            print("You won!")

    def give_up(self):
        self.reset_game()
        app = App.get_running_app()
        app.root.current = "levels"

    def next_day(self):
        app = App.get_running_app()
        app.stamina = 100  # รีเซ็ตพลังงาน
        # อาจจะมีการสุ่มสภาพอากาศ หรือเหตุการณ์พิเศษตรงนี้
        self.update_status("เช้าวันใหม่! พลังงานเต็มแล้ว")

# 2. สร้างตัวจัดการหน้าจอ
class WindowManager(ScreenManager):
    pass

# 3. ตัวหลักของแอปพลิเคชัน
class FlowerApp(App):
    money = NumericProperty(100)
    stamina = NumericProperty(100)
    weather = StringProperty("แดดจัด")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_playing_flower = "rose" 
        self.unlocked_flowers = []

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

    def start_game(self, flower_name):
        self.current_playing_flower = flower_name
        self.root.current = "game"
        
    def show_how_to_play(self):
        # สร้าง Layout หลัก
        content = BoxLayout(orientation='vertical', padding=25, spacing=15)
        
        # --- 1. ส่วนหัว (Header) ---
        header = Label(
            text="[color=2E7D32][b]MANUAL: APARTMENT GARDENER[/b][/color]",
            markup=True,
            font_name='assets/fonts/font.ttf',
            font_size='32sp',
            size_hint_y=0.15
        )
        content.add_widget(header)

        # --- 2. ส่วนเนื้อหาแบบละเอียด (Detailed Info) ---
        # ใช้ GridLayout เพื่อจัดวางไอคอนและคำอธิบาย
        grid = GridLayout(cols=1, spacing=10, size_hint_y=0.7)
        
        def add_info_row(title, desc):
            row = BoxLayout(orientation='vertical', spacing=2)
            row.add_widget(Label(
                text=f"[color=388E3C][b]• {title}[/b][/color]",
                markup=True, font_name='assets/fonts/font.ttf',
                font_size='22sp', halign='left', size_hint_x=1
            ))
            row.add_widget(Label(
                text=desc,
                font_name='assets/fonts/font.ttf',
                font_size='18sp', color=(0.4, 0.4, 0.4, 1),
                halign='left', size_hint_x=1
            ))
            grid.add_widget(row)

        add_info_row("ระบบพลังงาน (Stamina)", 
                     "การกระทำทุกอย่างใช้พลังงาน หากหมดต้องกด 'พักผ่อน' เพื่อเริ่มวันใหม่")
        add_info_row("ปัจจัยการเติบโต (Growth Factors)", 
                     "พืชแต่ละชนิดชอบ 'แดด' และ 'น้ำ' ต่างกัน สังเกตจากสภาพอากาศในแต่ละวัน")
        add_info_row("การจัดการสวน (Gallery Mode)", 
                     "ลากดอกไม้ที่ปลูกเสร็จแล้วไปวางบนชั้น และคลิกขวาเพื่อฉีดน้ำทำความสะอาด")
        add_info_row("เศรษฐกิจ (Economy)", 
                     "ปลูกดอกไม้สำเร็จเพื่อรับเงินรางวัล และนำไปซื้อเมล็ดพันธุ์หายากใน Shop")

        content.add_widget(grid)

        # --- 3. ส่วนท้ายและปุ่มปิด (Footer) ---
        btn_layout = BoxLayout(size_hint_y=0.15, padding=[40, 0])
        close_btn = Button(
            text="เข้าสู่สวนของคุณ",
            font_name='assets/fonts/font.ttf',
            font_size='22sp',
            background_normal='',
            background_color=(0.18, 0.49, 0.2, 1), # เขียวเข้ม Forest Green
            color=(1, 1, 1, 1)
        )
        btn_layout.add_widget(close_btn)
        content.add_widget(btn_layout)

        # สร้าง Popup แบบไร้ขอบเดิม (Custom Styling)
        popup = Popup(
            title="", # ซ่อน Title เดิม
            separator_height=0, # ซ่อนเส้นคั่นเดิม
            content=content,
            size_hint=(0.85, 0.85),
            background='assets/images/ui_bg.png', # ใช้รูปสวนจางๆ เป็นพื้นหลัง Popup
            background_color=(1, 1, 1, 0.9) # ปรับความสว่างให้เนื้อหาอ่านง่าย
        )
        
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    FlowerApp().run()