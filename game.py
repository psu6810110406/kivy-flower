# game.py
import os
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty
from kivy.animation import Animation
from kivy.core.window import Window

class LevelScreen(Screen):
    pass

class GameScreen(Screen):
    growth_progress = NumericProperty(0)
    flower_image_source = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_flower = ""
        # 1. Property Binding: ผูกค่า property เข้ากับฟังก์ชันอัตโนมัติ (Day 3-5 Callback)
        self.bind(growth_progress=self.on_growth_change)
        
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if not self.parent or self.parent.current != self.name:
            return
        
        # ถ่ายทอดตำแหน่งเมาส์ในหน้าต่างไปยัง Widget เพื่อเช็คแรงเงา
        stamina_box = self.ids.stamina_box
        growth_box = self.ids.get('growth_box')
        # แปลงพิกัด mouse เป็นพิกัดของ stamina_box (ถ้ามันถูกครอบด้วย layout อื่น)
        # เนื่องจากกล่องพิกัดอาจคาดเคลื่อน ให้หาว่าพิกัดนั้นชนกับ Bounding box ของ widget หรือไม่
        if stamina_box.collide_point(*pos):
            self.ids.tooltip_lbl.opacity = 1
            self.ids.tooltip_lbl.pos = (pos[0] + 15, pos[1] + 15)
            self.ids.tooltip_lbl.text = f"พลังงานเหลือ: {App.get_running_app().stamina} / 100"
        elif growth_box and growth_box.collide_point(*pos):
            self.ids.tooltip_lbl.opacity = 1
            self.ids.tooltip_lbl.pos = (pos[0] - self.ids.tooltip_lbl.width - 15, pos[1] + 15)
            self.ids.tooltip_lbl.text = f"ความเติบโต: {self.growth_progress:.1f} / 100"
        else:
            self.ids.tooltip_lbl.opacity = 0

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.current_flower = app.current_playing_flower
        
        flowers_th = {"rose": "กุหลาบ", "tulip": "ทิวลิป", "daisy": "เดซี่", "sunflower": "ทานตะวัน", "hibiscus": "ชบา"}
        self.ids.title_lbl.text = f"ด่าน: กำลังปลูก {flowers_th.get(self.current_flower, self.current_flower)}"
        
        # ฟื้นฟูความก้าวหน้าถ้าเคยปลูกไว้
        if self.current_flower in app.flower_progress:
            self.growth_progress = app.flower_progress[self.current_flower]
            self.ids.result_lbl.text = "กลับมาดูแลต่อแล้ว!"
            self.ids.flower_scatter.scale = 1.5
            self.ids.flower_scatter.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        else:
            self.reset_game()

    def reset_game(self):
        self.growth_progress = 0
        self.flower_image_source = self.get_flower_image(0)
        self.ids.result_lbl.text = "เริ่มปลูกต้นไม้กันเลย!"
        # คืนค่าสเกลให้ต้นไม้
        self.ids.flower_scatter.scale = 2.0
        self.ids.flower_scatter.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

    def temp_exit(self):
        # บันทึกสถานะการเติบโตของดอกไม้ปัจจุบันก่อนออก
        app = App.get_running_app()
        app.flower_progress[self.current_flower] = self.growth_progress
        app.save_app_state()
        app.root.current = "levels"

    def get_flower_image(self, state):
        if state == 0:
            return "assets/images/seed.png"
        elif state == 1:
            return "assets/images/sprout.png"
            
        path = f"assets/images/{self.current_flower}_{state}.png"
        
        # เพิ่ม 2 บรรทัดนี้เพื่อเช็คตำแหน่งที่ Python มองหาไฟล์
        import os
        print(f"[Debug] กำลังค้นหาไฟล์ที่: {os.path.abspath(path)}") 
        
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
            sc = self.ids.flower_scatter
            anim = Animation(scale=sc.scale * 1.2, duration=0.1) + Animation(scale=sc.scale, duration=0.1)
            anim.start(sc)
            
            self.check_win()
            app.save_app_state()
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
            app.save_app_state()
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
            app.save_app_state()
        else:
            self.update_status("พลังงานไม่พอ! ต้องพักก่อน")

    def update_status(self, msg):
        self.ids.result_lbl.text = msg

    def check_win(self):
        if self.growth_progress >= 100:
            self.growth_progress = 100 # กันเกิน
            self.update_status("ยินดีด้วย! ดอกไม้บานเต็มที่แล้ว เก็บเกี่ยวได้เลย!")
            app = App.get_running_app()
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
            if self.current_flower in app.flower_progress:
                del app.flower_progress[self.current_flower]
            app.save_app_state()
            print("You won!")

    def give_up(self):
        self.reset_game()
        app = App.get_running_app()
        if self.current_flower in app.flower_progress:
            del app.flower_progress[self.current_flower]
        app.save_app_state()
        app.root.current = "levels"

    def next_day(self):
        app = App.get_running_app()
        app.stamina = 100  # รีเซ็ตพลังงาน
        # อาจจะมีการสุ่มสภาพอากาศ หรือเหตุการณ์พิเศษตรงนี้
        self.update_status("เช้าวันใหม่! พลังงานเต็มแล้ว")