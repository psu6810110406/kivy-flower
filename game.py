# game.py
import os
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
#from kivy.core.audio import SoundLoader

class LevelScreen(Screen):
    pass

class GameScreen(Screen):
    growth_score = NumericProperty(0)
    satisfaction_score = NumericProperty(0)
    current_phase = NumericProperty(1)
    care_days = NumericProperty(0)
    flower_image_source = StringProperty('')
    phase_limit = NumericProperty(100)
    satisfaction_score = NumericProperty(100)
    health_score = NumericProperty(100)
    neglect_streak = NumericProperty(0)
    action_today = False
    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_flower = ""
        # ผูก property ข้ามเฟส
        
        self.action_cooldown = False # ป้องกันการกดรัว
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if not self.parent or self.parent.current != self.name:
            return
        
        app = App.get_running_app()
        # แปลงพิกัดจากหน้าต่างเป็นพิกัด Widget
        local_pos = self.to_widget(*pos)
        
        stamina_box = self.ids.stamina_box
        growth_box = self.ids.get('growth_box')
        care_box = self.ids.get('care_box')
        health_box = self.ids.get('health_box')
        day_lbl = self.ids.get('day_lbl')

        found_widget = None
        tooltip_text = ""

        if stamina_box.collide_point(*local_pos):
            found_widget = stamina_box
            tooltip_text = f"พลังงานเหลือ: {int(app.stamina)} / 100"
        elif care_box and care_box.collide_point(*local_pos):
            found_widget = care_box
            tooltip_text = f"ความเอาใจใส่: {int(self.satisfaction_score)} / {int(self.phase_limit)}"
        elif growth_box and growth_box.collide_point(*local_pos):
            found_widget = growth_box
            tooltip_text = f"ความเติบโต: {self.growth_score:.1f} / {self.phase_limit}"
        elif health_box and health_box.collide_point(*local_pos):
            found_widget = health_box
            tooltip_text = f"พลังชีวิต: {int(self.health_score)} / 100"
        elif day_lbl and day_lbl.collide_point(*local_pos):
            found_widget = day_lbl
            tooltip_text = f"วันที่ดูแลสะสมมาทั้งหมด: {self.care_days + 1} วัน"

        if found_widget:
            lbl = self.ids.tooltip_lbl
            lbl.text = tooltip_text
            lbl.texture_update() # บังคับอัปเดตขนาดตัวอักษรทันทีเพื่อคำนวณตำแหน่งที่ถูกต้อง
            
            # คำนวณทิศทาง tooltip ตามตำแหน่งหน้าจอ (ซ้ายดีดขวา ขวาดีดซ้าย)
            if pos[0] < window.width / 2:
                x_off = 15
            else:
                x_off = -lbl.width - 15
                
            lbl.pos = (pos[0] + x_off, pos[1] + 15)
            lbl.opacity = 1
        else:
            self.ids.tooltip_lbl.opacity = 0

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.current_flower = app.current_playing_flower
        
        flowers_th = {
            "rose": "กุหลาบ", "tulip": "ทิวลิป", "daisy": "เดซี่", 
            "sunflower": "ทานตะวัน", "hibiscus": "ชบา", "lilly": "ลิลลี่"
        }
        self.ids.title_lbl.text = f"กำลังปลูก: {flowers_th.get(self.current_flower, self.current_flower)}"
        
        # ฟื้นฟูความก้าวหน้าถ้าเคยปลูกไว้
        self.watered_today = False
        self.action_today = False
        if self.current_flower in app.flower_progress:
            progress_data = app.flower_progress[self.current_flower]
            # รองรับเซฟเก่าที่เป็นตัวเลข
            if isinstance(progress_data, (int, float)):
                self.growth_score = progress_data
                self.satisfaction_score = 100
                self.health_score = 100
                self.neglect_streak = 0
                self.current_phase = 1
                self.care_days = 0
            else:
                self.growth_score = progress_data.get("growth_score", 0)
                self.satisfaction_score = progress_data.get("satisfaction_score", 100)
                self.health_score = progress_data.get("health_score", 100)
                self.neglect_streak = progress_data.get("neglect_streak", 0)
                self.current_phase = progress_data.get("current_phase", 1)
                self.care_days = progress_data.get("care_days", 0)

            self.phase_limit = self.get_phase_limit()
            self.flower_image_source = self.get_flower_image(self.current_phase - 1)
            
            self.ids.result_lbl.text = "กลับมาดูแลต่อแล้ว!"
            self.ids.flower_scatter.scale = 1.0
        else:
            self.reset_game()

    def reset_game(self):
        self.watered_today = False
        self.action_today = False
        self.current_phase = 1
        self.growth_score = 0
        self.satisfaction_score = 100
        self.health_score = 100
        self.neglect_streak = 0
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
            "health_score": self.health_score,
            "neglect_streak": self.neglect_streak,
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
            
        # ตรวจสอบทั้ง .png และ .PNG
        path_lower = f"assets/images/{self.current_flower}_{state}.png"
        path_upper = f"assets/images/{self.current_flower}_{state}.PNG"

        if os.path.exists(path_lower):
            return path_lower
        if os.path.exists(path_upper):
            return path_upper
            
        return f"assets/images/seed.png"  # Fallback พื้นฐานที่สุด

    def on_current_phase(self, instance, value):
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
        # ให้ค่าออร่าแสดงผลตามความเอาใจใส่ที่เกิน 100 (เหมือนระบบ Growth) 
        # โดยไม่ต้องรอให้ถึง Phase 4 เพื่อให้เห็นพัฒนาการ
        return max(0, self.satisfaction_score - 100)

    # Action Callbacks ตอบสนองต่อปุ่ม
    def water_plant(self):
        if self.action_cooldown: return
        print("Action: water_plant called")
        self.action_today = True
        app = App.get_running_app()
        
        # เริ่ม Cooldown
        self.start_cooldown(0.3)
        
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
                self.update_status(f"รดน้ำต้นไม้ (+{bonus} เติบโต | +5 เอาใจใส่ | -10 พลังงาน)")
            
            self.growth_score += bonus
            
            sc = self.ids.flower_scatter
            # แก้ไข: ใช้ค่า Scale สัมบูรณ์ (1.2 และ 1.0) แทนการคูณค่าปัจจุบัน เพื่อป้องกันดอกไม้ขยายใหญ่เกินคุม
            Animation.stop_all(sc) # หยุดเอนิเมชันเก่าทันที
            anim = Animation(scale=1.15, duration=0.1, t='out_quad') + Animation(scale=1.0, duration=0.1, t='in_quad')
            anim.start(sc)
            
            app.save_app_state()
        else:
            self.update_status("พลังงานไม่พอ! กดยอมพักผ่อนได้แล้ว")

    def fertilize_plant(self):
        if self.action_cooldown: return
        print("Action: fertilize_plant called")
        self.action_today = True
        app = App.get_running_app()
        if self.current_phase >= 4: return
        
        self.start_cooldown(0.3)
        
        if app.stamina >= 20:
            app.stamina -= 20
            self.growth_score += 30
            self.satisfaction_score += 15
            self.update_status("ใส่ปุ๋ยบำรุงขั้นสุด! (+30 เติบโต | +15 เอาใจใส่ | -20 พลังงาน)")
            
            # ใส่เอนิเมชันเด้งเล็กน้อย
            sc = self.ids.flower_scatter
            Animation.stop_all(sc)
            (Animation(scale=1.1, duration=0.1) + Animation(scale=1.0, duration=0.1)).start(sc)
            
            app.save_app_state()
        else:
            self.update_status("พลังงานไม่พอ! กดยอมพักผ่อนได้แล้ว")

    def till_soil(self):
        if self.action_cooldown: return
        print("Action: till_soil called")
        self.action_today = True
        app = App.get_running_app()
        if self.current_phase >= 4: return
        
        self.start_cooldown(0.3)
        
        if app.stamina >= 15:
            app.stamina -= 15
            self.growth_score += 20
            self.satisfaction_score += 10
            self.update_status("พรวนดินร่วนซุยดีมาก (+20 เติบโต | +10 เอาใจใส่ | -15 พลังงาน)")
            
            # ใส่เอนิเมชันเด้งเล็กน้อย
            sc = self.ids.flower_scatter
            Animation.stop_all(sc)
            (Animation(scale=1.1, duration=0.1) + Animation(scale=1.0, duration=0.1)).start(sc)
            
            app.save_app_state()
        else:
            self.update_status("พลังงานไม่พอ! กดยอมพักผ่อนได้แล้ว")

    def start_cooldown(self, duration):
        from kivy.clock import Clock
        self.action_cooldown = True
        Clock.schedule_once(self.end_cooldown, duration)

    def end_cooldown(self, dt):
        self.action_cooldown = False

    def on_growth_score(self, instance, value):
        self.check_phase_up()

    def on_satisfaction_score(self, instance, value):
        self.check_phase_up()

    def apply_penalty(self):
        # โลจิก: ถ้าความเอาใจใส่หมด ให้ไปหักพลังชีวิตแทน
        if self.satisfaction_score <= 0:
            penalty = 20 # หักพลังชีวิตครั้งละ 20
            self.health_score = max(0, self.health_score - penalty)
            self.ids.result_lbl.text = f"ดอกไม้ขาดการดูแล! พลังชีวิตลดลง {penalty}%"
            
            # เช็คเงื่อนไขความตาย
            if self.health_score <= 0:
                self.trigger_death()

    def trigger_death(self):
        self.ids.result_lbl.text = "เสียใจด้วย... ดอกไม้ของคุณตายแล้ว"
        self.show_death_alert()

    def show_death_alert(self):
        # 1. ดึงเนื้อหาจาก KV
        from kivy.factory import Factory
        content = Factory.DeathPopupContent()
        
        # 2. สร้าง Popup โดยเอาพื้นหลังออกเพื่อให้เห็นดีไซน์จาก Content ชัดเจน
        popup = Popup(
            title="", 
            content=content,
            size_hint=(0.85, 0.55),
            auto_dismiss=False,
            separator_height=0,
            background='',  # เอา default background ออก
            background_color=(0, 0, 0, 0) # โปร่งใส
        )

        # 3. เชื่อมต่อ Logic ผ่าน IDs ที่เราตั้งไว้ใน KV
        # ปุ่มหลัก: "ปลูกใหม่" (Reset game and stay)
        content.ids.retry_btn.bind(on_release=lambda x: self.reset_game_logic(popup))
        # ปุ่มรอง: "ออกจากการปลูก" (Go to menu)
        content.ids.home_btn.bind(on_release=lambda x: self.exit_to_menu(popup))
        
        popup.open()

    def reset_game_logic(self, popup):
        popup.dismiss()
        # รีเซ็ตค่าตัวแปรต่างๆ กลับเป็นค่าเริ่มต้น
        self.reset_game()
        # บันทึกสถานะที่รีเซ็ตแล้วลงไฟล์
        app = App.get_running_app()
        app.save_app_state()

    def exit_to_menu(self, popup):
        popup.dismiss()
        # ส่งผู้เล่นกลับไปหน้าเมนู
        self.manager.current = 'menu'
        # บันทึกสถานะ และอาจจะลบโปรเกรสของดอกไม้ตัวที่ตายไปแล้วเพื่อให้เริ่มใหม่ได้จากหน้าเลือกเลเวล
        app = App.get_running_app()
        if self.current_flower in app.flower_progress:
            del app.flower_progress[self.current_flower]
        app.save_app_state()

    def update_status(self, msg):
        self.ids.result_lbl.text = msg

    def check_phase_up(self):
        limit = self.get_phase_limit()
        if self.current_phase < 4 and (self.growth_score >= limit or self.satisfaction_score >= limit):
            self.current_phase += 1
            self.growth_score = 0 
            self.satisfaction_score = 100 
            
            # --- เพิ่มโค้ดเสียง Level Up ตรงนี้ ---
            sound = SoundLoader.load('assets/sound/levelup.mp3') # ปรับ path ให้ตรงกับที่เก็บไฟล์จริง เช่น 'assets/sounds/levelup.mp3'
            if sound:
                sound.play()
            # ---------------------------------

            if self.current_phase == 4:
                self.update_status("ยินดีด้วย! ดอกไม้บานเต็มที่แล้ว มีออร่าพุ่งขึ้นมา! เก็บเกี่ยวได้เลย!")
            else:
                self.update_status(f"เติบโตขึ้นเข้าสู่เฟสที่ {self.current_phase} แล้ว!")
            app = App.get_running_app()
            app.save_app_state()

    def collect_flower(self):
        if self.current_phase >= 4:
            app = App.get_running_app()
            # เพิ่มดอกไม้ลงใน Collection พร้อมเก็บข้อมูลสถิติ
            flower_data = {
                "type": self.current_flower,
                "care_days": self.care_days,
                "extra_affection": self.extra_affection
            }
            app.unlocked_flowers.append(flower_data)
            self.update_status("เก็บเข้า Collection แล้ว!")
            # กลับไปหน้าหลัก
            app.root.current = "menu"
            app.stamina += 30 # ได้โบนัสพลังงานคืน
            if self.current_flower in app.flower_progress:
                del app.flower_progress[self.current_flower]
            app.save_app_state()
            print("You won!")   

    def show_exit_popup(self):
        from kivy.factory import Factory
        from kivy.uix.popup import Popup
        
        content = Factory.ModernPopupContent(
            title_text="ยืนยันการออก",
            desc_text="คุณต้องการออกชั่วคราวหรือจะยอมแพ้เพื่อเริ่มใหม่?"
        )
        
        temp_btn = Factory.MinimalButton(
            text="ออกชั่วคราว (เซฟข้อมูล)",
            btn_color=(0.2, 0.5, 0.8, 1),
            size_hint_y=None, height=60
        )
        
        giveup_btn = Factory.MinimalButton(
            text="ยอมแพ้ (เริ่มใหม่ทั้งหมด)",
            btn_color=(0.8, 0.3, 0.3, 1),
            size_hint_y=None, height=60
        )
        
        close_btn = Factory.MinimalButton(
            text="กลับไปดูแลต้นไม้",
            btn_color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None, height=60
        )
        
        content.ids.button_area.add_widget(temp_btn)
        content.ids.button_area.add_widget(giveup_btn)
        content.ids.button_area.add_widget(close_btn)
        
        popup = Popup(
            title="", separator_height=0,
            content=content, size_hint=(0.7, 0.6),
            auto_dismiss=True, background_color=(0,0,0,0)
        )
        
        temp_btn.bind(on_release=lambda x: [popup.dismiss(), self.temp_exit()])
        giveup_btn.bind(on_release=lambda x: [popup.dismiss(), self.confirm_give_up()])
        close_btn.bind(on_release=popup.dismiss)
        
        popup.open()

    def confirm_give_up(self):
        from kivy.factory import Factory
        from kivy.uix.popup import Popup

        content = Factory.ModernPopupContent(
            title_text="คำเตือน!",
            desc_text="หากคุณยอมแพ้ ข้อมูลการเติบโตจะหายไปทั้งหมด\nต้องการยืนยันใช่หรือไม่?"
        )
        
        yes_btn = Factory.MinimalButton(
            text="ใช่, ยอมแพ้",
            btn_color=(0.8, 0.2, 0.2, 1),
            size_hint_y=None, height=60
        )
        no_btn = Factory.MinimalButton(
            text="ไม่, ย้อนกลับ",
            btn_color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None, height=60
        )
        
        content.ids.button_area.add_widget(yes_btn)
        content.ids.button_area.add_widget(no_btn)
        
        popup = Popup(
            title="", separator_height=0,
            content=content, size_hint=(0.6, 0.45),
            background_color=(0,0,0,0)
        )
        
        yes_btn.bind(on_release=lambda x: [popup.dismiss(), self.give_up()])
        no_btn.bind(on_release=popup.dismiss)
        popup.open()

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
        
        is_neglected = False
        neglect_detail = ""
        
        # 1. หักถ้าปล่อยให้ต้นขาดน้ำในวันที่แดดออก
        if yesterday_weather == "แดดจัด" and not getattr(self, "watered_today", False):
            self.satisfaction_score = max(0, self.satisfaction_score - penalty)
            neglect_detail += f"ขาดน้ำในวันแดดจัด (-{penalty}) "
            is_neglected = True
        
        # 2. หักถ้าไม่ทำอะไรเลย
        if not getattr(self, "action_today", False):
            neglect_detail += "ไม่ได้ดูแลดอกไม้เลย (-15) "
            is_neglected = True
            
        if is_neglected:
            self.neglect_streak += 1
            penalty_msg = f"[color=FF5252]ละเลยการดูแล: {neglect_detail}[/color]"
        else:
            self.neglect_streak = 0
            penalty_msg = "[color=A5D6A7]ดูแลได้ดีมาก ราบรื่น![/color]"
            
        # Passive Decay: หักค่าความเอาใจใส่ 15 ทุกวัน
        self.satisfaction_score = max(0, self.satisfaction_score - 15)
        
        # หักพลังชีวิตโดยตรงถ้าละเลยติดต่อกัน 3 วัน
        if self.neglect_streak >= 3:
            self.health_score = max(0, self.health_score - 30)
            penalty_msg += "\n[color=FF4444]ละเลยติดต่อกัน 3 วัน! พลังชีวิตลดฮวบ 30%[/color]"
            
        self.apply_penalty() # ตรวจสอบเงื่อนไขสุขภาพ
        
        if self.health_score <= 0:
            return # ไม่ต้องเปิด popup สรุปวันถ้าตายแล้ว (trigger_death จะเรียก popup เอง)

        self.watered_today = False
        self.action_today = False
        self.care_days += 1
        
        # เพิ่มพลังงานเต็ม 100 ทุกครั้งที่พักผ่อน
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
            markup=True, font_name='assets/fonts/font.ttf', font_size='18sp', halign='center'
        ))
        content.add_widget(Label(
            text=f"พยากรณ์อากาศวันนี้: [b]{app.weather}[/b]\n(พลังงานฟื้นฟูพื้นฐาน +100 แล้ว!)",
            markup=True, font_name='assets/fonts/font.ttf', font_size='22sp', halign='center'
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