# game.py
import os
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.core.audio import SoundLoader

class LevelScreen(Screen):
    pass

class GameScreen(Screen):
    growth_score = NumericProperty(0)
    satisfaction_score = NumericProperty(0)
    current_phase = NumericProperty(1)
    care_days = NumericProperty(0)
    flower_image_source = StringProperty('')
    phase_limit = NumericProperty(100)
    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_flower = ""
        # ผูก property ข้ามเฟส
        self.bind(current_phase=self.on_phase_change)
        
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if not self.parent or self.parent.current != self.name:
            return
        
        # ถ่ายทอดตำแหน่งเมาส์ในหน้าต่างไปยัง Widget เพื่อเช็คแรงเงา
        stamina_box = self.ids.stamina_box
        growth_box = self.ids.get('growth_box')
        care_box = self.ids.get('care_box')

        if stamina_box.collide_point(*pos):
            self.ids.tooltip_lbl.opacity = 1
            self.ids.tooltip_lbl.pos = (pos[0] + 15, pos[1] + 15)
            self.ids.tooltip_lbl.text = f"พลังงานเหลือ: {App.get_running_app().stamina} / 100"
        elif care_box and care_box.collide_point(*pos):
            self.ids.tooltip_lbl.opacity = 1
            self.ids.tooltip_lbl.pos = (pos[0] + 15, pos[1] + 15)
            self.ids.tooltip_lbl.text = f"ความเอาใจใส่: {self.satisfaction_score} / 100"
        elif growth_box and growth_box.collide_point(*pos):
            self.ids.tooltip_lbl.opacity = 1
            self.ids.tooltip_lbl.pos = (pos[0] - self.ids.tooltip_lbl.width - 15, pos[1] + 15)
            self.ids.tooltip_lbl.text = f"ความเติบโต: {self.growth_score:.1f} / {self.phase_limit}"
        else:
            self.ids.tooltip_lbl.opacity = 0

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.current_flower = app.current_playing_flower
        
        flowers_th = {"rose": "กุหลาบ", "tulip": "ทิวลิป", "daisy": "เดซี่", "sunflower": "ทานตะวัน", "hibiscus": "ชบา"}
        self.ids.title_lbl.text = f"ด่าน: กำลังปลูก {flowers_th.get(self.current_flower, self.current_flower)}"
        
        # ฟื้นฟูความก้าวหน้าถ้าเคยปลูกไว้
        self.watered_today = False
        if self.current_flower in app.flower_progress:
            progress_data = app.flower_progress[self.current_flower]
            # รองรับเซฟเก่าที่เป็นตัวเลข
            if isinstance(progress_data, (int, float)):
                self.growth_score = progress_data
                self.satisfaction_score = 100
                self.current_phase = 1
                self.care_days = 0
            else:
                self.growth_score = progress_data.get("growth_score", 0)
                self.satisfaction_score = progress_data.get("satisfaction_score", 100)
                self.current_phase = progress_data.get("current_phase", 1)
                self.care_days = progress_data.get("care_days", 0)

            self.phase_limit = self.get_phase_limit()
            
            self.ids.result_lbl.text = "กลับมาดูแลต่อแล้ว!"
            self.ids.flower_scatter.scale = 1.0
        else:
            self.reset_game()

    def reset_game(self):
        self.watered_today = False
        self.current_phase = 1
        self.growth_score = 0
        self.satisfaction_score = 100
        self.care_days = 0
        self.phase_limit = self.get_phase_limit()
        self.flower_image_source = self.get_flower_image(0)
        self.ids.result_lbl.text = "เริ่มปลูกต้นไม้กันเลย!"
        self.ids.flower_scatter.scale = 1.0

    def temp_exit(self):
        # บันทึกสถานะการเติบโตของดอกไม้ปัจจุบันก่อนออก
        app = App.get_running_app()
        app.flower_progress[self.current_flower] = {
            "growth_score": self.growth_score,
            "satisfaction_score": self.satisfaction_score,
            "current_phase": self.current_phase,
            "care_days": self.care_days
        }
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
        
        if os.path.exists(path):
            return path
        return f"assets/images/flower_{state}.png"

    def on_phase_change(self, instance, value):
        self.flower_image_source = self.get_flower_image(value - 1)
        self.phase_limit = self.get_phase_limit()

    def get_phase_limit(self):
        limits = {1: 100, 2: 250, 3: 400, 4: 9999}
        return limits.get(self.current_phase, 100)

    def get_phase_penalty(self):
        penalties = {1: 10, 2: 25, 3: 50, 4: 100}
        return penalties.get(self.current_phase, 10)

    @property
    def extra_affection(self):
        if self.current_phase == 4:
            return max(0, self.satisfaction_score - 100)
        return 0

    # Action Callbacks ตอบสนองต่อปุ่ม
    def water_plant(self):
        app = App.get_running_app()
        if self.current_phase >= 4 and self.satisfaction_score >= 100:
            self.satisfaction_score += 10
            self.update_status(f"หมั่นรดน้ำให้ต้นไม้ที่บานแล้ว! (+10 เอาใจใส่)")
            return
            
        if app.stamina >= 10:
            app.stamina -= 10
            self.watered_today = True
            
            penalty = self.get_phase_penalty()
            if app.weather == "ฝนตก":
                self.satisfaction_score = max(0, self.satisfaction_score - penalty)
                bonus = 10
                self.update_status(f"รดน้ำตอนฝนตก! ต้นไม้แฉะ (+{bonus} เติบโต | ความเอาใจใส่ -{penalty})")
            else:
                bonus = 30 if app.weather == "แดดจัด" else 15
                self.satisfaction_score += 5
                self.update_status(f"รดน้ำลูบใบ (+{bonus} เติบโต | +5 พึงพอใจ | -10 พลังงาน)")
            
            self.growth_score += bonus
            
            sc = self.ids.flower_scatter
            anim = Animation(scale=sc.scale * 1.2, duration=0.1) + Animation(scale=sc.scale, duration=0.1)
            anim.start(sc)
            
            self.check_phase_up()
            app.save_app_state()
        else:
            self.update_status("พลังงานไม่พอ! กดยอมพักผ่อนได้แล้ว")

    def fertilize_plant(self):
        app = App.get_running_app()
        if self.current_phase >= 4: return
        if app.stamina >= 20:
            app.stamina -= 20
            self.growth_score += 30
            self.satisfaction_score += 15
            self.update_status("ใส่ปุ๋ยบำรุงขั้นสุด! (+30 เติบโต | +15 พึงพอใจ | -20 พลังงาน)")
            self.check_phase_up()
            app.save_app_state()
        else:
            self.update_status("พลังงานไม่พอ! กดยอมพักผ่อนได้แล้ว")

    def till_soil(self):
        app = App.get_running_app()
        if self.current_phase >= 4: return
        if app.stamina >= 15:
            app.stamina -= 15
            self.growth_score += 20
            self.satisfaction_score += 10
            self.update_status("พรวนดินร่วนซุยดีมาก (+20 เติบโต | +10 พึงพอใจ | -15 พลังงาน)")
            self.check_phase_up()
            app.save_app_state()
        else:
            self.update_status("พลังงานไม่พอ! กดยอมพักผ่อนได้แล้ว")

    def update_status(self, msg):
        self.ids.result_lbl.text = msg

    def check_phase_up(self):
        limit = self.get_phase_limit()
        if self.current_phase < 4 and self.growth_score >= limit:
            self.current_phase += 1
            self.growth_score = 0 # รีเซ็ตแต้ม
            if self.current_phase == 4:
                self.update_status("ยินดีด้วย! ดอกไม้บานเต็มที่แล้ว มีออร่าพุ่งขึ้นมา! เก็บเกี่ยวได้เลย!")
            else:
                self.update_status(f"เติบโตขึ้นเข้าสู่เฟสที่ {self.current_phase} แล้ว!")
            app = App.get_running_app()

    def collect_flower(self):
        if self.current_phase >= 4:
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

    def next_day_action(self):
        import random
        from kivy.animation import Animation
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        app = App.get_running_app()
        
        # เช็คว่าลืมรดน้ำในวันแดดจัดไหม
        yesterday_weather = app.weather
        penalty = self.get_phase_penalty()
        if yesterday_weather == "แดดจัด" and getattr(self, "watered_today", False) == False:
            self.satisfaction_score = max(0, self.satisfaction_score - penalty)
            penalty_msg = f"[color=FF5252]โดนหัก {penalty} แต้ม! (ปล่อยให้ต้นไม้ร้อนในวันแดดจัด)[/color]"
        else:
            penalty_msg = "[color=A5D6A7]ดูแลได้ดีมาก ราบรื่น![/color]"
            
        self.watered_today = False
        self.care_days += 1
        
        app.stamina = 100
        weathers = ["แดดจัด", "ฝนตก", "เมฆมาก", "พายุเข้า"]
        app.weather = random.choice(weathers)
        
        # สร้าง Layout สำหรับ Popup
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(
            text=f"[b]สรุปการดูแลเมื่อวาน (วันที่ {self.care_days - 1})[/b]",
            markup=True, font_name='assets/fonts/font.ttf', font_size='24sp', color=(1, 0.9, 0.2, 1)
        ))
        content.add_widget(Label(
            text=penalty_msg,
            markup=True, font_name='assets/fonts/font.ttf', font_size='20sp'
        ))
        content.add_widget(Label(
            text=f"พยากรณ์อากาศวันนี้: [b]{app.weather}[/b]\n(พลังงานฟื้นฟูเต็ม 100 แล้ว!)",
            markup=True, font_name='assets/fonts/font.ttf', font_size='22sp'
        ))
        btn = Button(
            text="ลุยกันต่อ!",
            font_name='assets/fonts/font.ttf', font_size='22sp',
            size_hint_y=None, height=50,
            background_normal='', background_color=(0.18, 0.49, 0.2, 1)
        )
        content.add_widget(btn)
        
        popup = Popup(
            title="", separator_height=0,
            content=content, size_hint=(0.7, 0.6),
            background='', background_color=(0.2, 0.2, 0.2, 0.95)
        )
        btn.bind(on_release=popup.dismiss)
        popup.open()
        
        # เราต้องเปิด markup ให้ label นี้ด้วย เพื่อแสดงตัวอักษรสีแดงถ้าโดนหักคะแนน
        self.ids.result_lbl.markup = True
        self.update_status(f"เช้าวันใหม่! อากาศ: {app.weather} | วันที่ {self.care_days}")
        
        # เล่นเอนิเมชันกะพริบแจ้งเตือน ให้เห็นความเปลี่ยนแปลงของการข้ามวัน
        lbl = self.ids.result_lbl
        lbl.opacity = 0
        anim = Animation(opacity=1, duration=0.5)
        anim.start(lbl)
        
        # คืนสเกลต้นไม้เป็นปกติในกรณีที่มันค้างจากการรดน้ำ
        sc = self.ids.flower_scatter
        Animation(scale=1.0, duration=0.3).start(sc)
        
        app.save_app_state()