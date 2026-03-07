# collection.py
import os
import time
import random
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.animation import Animation

BUFFS = [
    "10% flower enlargement buff", "Special aura", "Watering efficiency", "Faster growth",
    "Weather resistant", "Extra seeds", "Sunlight +5%", "Bug repellent",
    "Strong roots", "Vibrant colors", "Night bloom", "Fragrance boost",
    "Pollinator attractant", "Frost resistance", "Drought tolerance", "Extended bloom",
    "Self-healing", "Bonus care points", "Golden petals", "Rainbow glow"
]

class DraggableFlower(Scatter):
    def __init__(self, flower_data, **kwargs):
        super().__init__(**kwargs)
        # flower_data: {"type": "rose", "care_days": 5, "extra_affection": 120}
        if isinstance(flower_data, str):
            self.flower_info = {"type": flower_data, "care_days": 0, "extra_affection": 0}
        else:
            self.flower_info = flower_data
            
        self.flower_type = self.flower_info["type"]
        self.size_hint = (None, None)
        self.size = (300, 300)
        self.do_rotation = False
        
        img_src = f"assets/images/{self.flower_type}_4.png"
        if not os.path.exists(img_src): img_src = f"assets/images/{self.flower_type}_4.PNG"
        if not os.path.exists(img_src): img_src = "assets/images/flower_3.png"
        
        # 1.2 แก้ให้โหลดออร่าขึ้นมาเลยตามที่เล่นได้
        # ระดับออร่าคำนวณจาก extra_affection
        aura_opacity = min(self.flower_info.get("extra_affection", 0) / 100.0, 1.0)
        self.aura_image = Image(source="assets/images/aura_effect.png", size=self.size, opacity=aura_opacity)
        self.add_widget(self.aura_image)

        self.flower_image = Image(source=img_src, size=self.size)
        self.add_widget(self.flower_image)
        
        self.stored_time = time.time()
        
        # คำนวณมูลค่า (50G + โบนัสจากออร่า)
        # เนื่องจากเฟส 4 คือคูณ 4 ถ้าตามตรรกะคือ เฟส 2คูณ2 3คูณ3 4คูณ4
        # สูตร: 50 + (extra_affection * 4) 
        self.value = 50 + int(self.flower_info.get("extra_affection", 0) * 4)
            
        self.hovered = False
        Window.bind(mouse_pos=self.on_mouse_pos)
        
    def on_mouse_pos(self, window, pos):
        if not self.parent:
            return
            
        app = App.get_running_app()
        if not app or not app.root or app.root.current != 'collection':
            return
            
        if self.collide_point(*pos):
            if not self.hovered:
                self.hovered = True
                screen = app.root.get_screen('collection')
                
                # 1.3 แสดงข้อมูล 3 อย่าง
                text = (
                    f"[b]{self.flower_type.upper()}[/b]\n"
                    f"ใช้เวลาปลูก: {self.flower_info['care_days']} วัน\n"
                    f"ระดับออร่า: {int(self.flower_info['extra_affection'])}%\n"
                    f"มูลค่า: {self.value} G"
                )
                if hasattr(screen, 'show_tooltip'):
                    screen.show_tooltip(pos, text)
            else:
                screen = app.root.get_screen('collection')
                text = (
                    f"[b]{self.flower_type.upper()}[/b]\n"
                    f"ใช้เวลาปลูก: {self.flower_info['care_days']} วัน\n"
                    f"ระดับออร่า: {int(self.flower_info['extra_affection'])}%\n"
                    f"มูลค่า: {self.value} G"
                )
                if hasattr(screen, 'update_tooltip'):
                    screen.update_tooltip(pos, text)
        else:
            if self.hovered:
                self.hovered = False
                screen = app.root.get_screen('collection')
                if hasattr(screen, 'hide_tooltip'):
                    screen.hide_tooltip()
                
    def activate_driving_effect(self):
        self.driving_effect_activated = True
        anim = Animation(scale=self.scale * 1.1, duration=0.3)
        anim.start(self)
        self.aura_image.opacity = 1

    def on_touch_down(self, touch):
        # Prevent popup on right click (watering drag)
        if self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            distance = ((touch.x - touch.ox)**2 + (touch.y - touch.oy)**2)**0.5
            if distance < 5 and touch.button == 'left':
                app = App.get_running_app()
                screen = app.root.get_screen('collection')
                if hasattr(screen, 'show_stats_popup'):
                    screen.show_stats_popup(self)
                    return True
        return super().on_touch_up(touch)


class InventoryFlower(Image):
    def __init__(self, flower_data, **kwargs):
        super().__init__(**kwargs)
        self.flower_data = flower_data
        if isinstance(flower_data, str):
            self.flower_type = flower_data
        else:
            self.flower_type = flower_data["type"]
            
        self.size_hint = (None, 1)
        self.width = 120
        img_src = f"assets/images/{self.flower_type}_3.png"
        if not os.path.exists(img_src): img_src = f"assets/images/{self.flower_type}_3.PNG"
        if not os.path.exists(img_src): img_src = "assets/images/flower_3.png"
        self.source = img_src

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            app = App.get_running_app()
            screen = app.root.get_screen('collection')
            
            flower = DraggableFlower(flower_data=self.flower_data)
            flower.center = touch.pos
            screen.ids.garden_area.add_widget(flower)
            
            # Make the new scatter widget grab the touch to start dragging immediately
            flower.on_touch_down(touch)
            
            # Remove from inventory
            if self.flower_data in app.unlocked_flowers:
                app.unlocked_flowers.remove(self.flower_data)
                app.save_app_state()
            if self.parent:
                self.parent.remove_widget(self)
                
            return True
        return super().on_touch_down(touch)


class CollectionScreen(Screen):
    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.ids.inventory_grid.clear_widgets()
        
        total_value = 0
        if len(app.unlocked_flowers) > 0:
            for f_data in app.unlocked_flowers:
                # คำนวณมูลค่ารวมใน Inventory
                if isinstance(f_data, dict):
                    val = 50 + int(f_data.get("extra_affection", 0) * 4)
                    total_value += val
                    flower = InventoryFlower(flower_data=f_data)
                else:
                    total_value += 50
                    flower = InventoryFlower(flower_data=f_data)
                self.ids.inventory_grid.add_widget(flower)
        
        # เพิ่มมูลค่าดอกไม้ที่วางอยู่ในสวนด้วย
        for child in self.ids.garden_area.children:
            if hasattr(child, 'value'):
                total_value += child.value

        # อัปเดตยอดเงินรวม (ใช้ ID จาก KV เพื่อตำแหน่งที่ถูกต้อง)
        self.ids.total_money_lbl.text = f"รวมทั้งหมด: {total_value} G"
                
        if not hasattr(self, 'tooltip'):
            self.tooltip = Label(
                text="", font_name='assets/fonts/font.ttf', font_size='18sp',
                size_hint=(None, None), size=(150, 60), opacity=0, markup=True
            )
            with self.tooltip.canvas.before:
                Color(0, 0, 0, 0.8)
                self.tooltip_bg = RoundedRectangle(pos=self.tooltip.pos, size=self.tooltip.size, radius=[5])
            self.tooltip.bind(pos=self._update_tooltip_bg, size=self._update_tooltip_bg)
            self.add_widget(self.tooltip)

    def _update_tooltip_bg(self, instance, value):
        self.tooltip_bg.pos = instance.pos
        self.tooltip_bg.size = instance.size

    def show_tooltip(self, pos, text):
        self.tooltip.text = text
        self.tooltip.opacity = 1
        self.tooltip.texture_update()
        self.tooltip.size = (self.tooltip.texture_size[0] + 20, self.tooltip.texture_size[1] + 10)
        self.tooltip.pos = (pos[0] + 15, pos[1] + 15)

    def update_tooltip(self, pos, text):
        if self.tooltip.opacity == 1:
            self.tooltip.text = text
            self.tooltip.texture_update()
            self.tooltip.size = (self.tooltip.texture_size[0] + 20, self.tooltip.texture_size[1] + 10)
            self.tooltip.pos = (pos[0] + 15, pos[1] + 15)

    def hide_tooltip(self):
        self.tooltip.opacity = 0

    def show_stats_popup(self, flower):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        # แปลงชื่อประเภทเป็นภาษาไทยแบบง่าย
        flower_thai = {
            "rose": "กุหลาบ", "tulip": "ทิวลิป", "daisy": "เดซี่",
            "sunflower": "ทานตะวัน", "hibiscus": "ชบา", "lilly": "ลิลลี่"
        }.get(flower.flower_type, flower.flower_type)

        stats_text = (
            f"ประเภท: {flower_thai}\n"
            f"ใช้เวลาปลูก: {flower.flower_info['care_days']} วัน\n"
            f"ระดับออร่า: {int(flower.flower_info['extra_affection'])}%\n"
            f"มูลค่าประเมิน: {flower.value} G\n"
        )
        lbl = Label(text=stats_text, font_name='assets/fonts/font.ttf', font_size='18sp')
        content.add_widget(lbl)
        
        btn_box = BoxLayout(size_hint_y=0.2, spacing=10)
        close_btn = Button(text="ปิดหน้าต่าง", font_name='assets/fonts/font.ttf', background_color=(0.8, 0.3, 0.3, 1))
        btn_box.add_widget(close_btn)
        content.add_widget(btn_box)

        popup = Popup(title="ข้อมูลสถิติของดอกไม้", title_font='assets/fonts/font.ttf', content=content, size_hint=(0.6, 0.5))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def on_touch_move(self, touch):
        if 'button' in touch.profile and touch.button == 'right':
            self.canvas.after.clear()
            with self.canvas.after:
                Color(0.4, 0.7, 1, 0.5) # สีน้ำฟ้าใส
                Line(points=[touch.ox, touch.oy, touch.x, touch.y], width=2)
            
            for child in self.ids.garden_area.children:
                if child.collide_point(*touch.pos):
                    anim = Animation(scale=child.scale * 1.05, duration=0.1) + Animation(scale=child.scale, duration=0.1)
                    anim.start(child)
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if 'button' in touch.profile and touch.button == 'right':
            self.canvas.after.clear()
        return super().on_touch_up(touch)