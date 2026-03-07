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
    def __init__(self, flower_type, **kwargs):
        super().__init__(**kwargs)
        self.flower_type = flower_type
        self.size_hint = (None, None)
        self.size = (300, 300)
        self.do_rotation = False
        img_src = f"assets/images/{flower_type}_4.png"
        if not os.path.exists(img_src): img_src = f"assets/images/{flower_type}_4.PNG"
        if not os.path.exists(img_src): img_src = "assets/images/flower_3.png"
        
        self.aura_image = Image(source="assets/images/aura_effect.png", size=self.size, opacity=0)
        self.add_widget(self.aura_image)

        self.flower_image = Image(source=img_src, size=self.size)
        self.add_widget(self.flower_image)
        
        self.stored_time = time.time()
        self.stats = {"Water": random.randint(50, 100), "Health": random.randint(50, 100), "Care": random.randint(50, 100)}
        self.active_buffs = random.sample(BUFFS, k=3)
        if "10% flower enlargement buff" not in self.active_buffs:
            self.active_buffs[0] = "10% flower enlargement buff"
        if "Special aura" not in self.active_buffs:
            self.active_buffs[1] = "Special aura"
            
        self.hover_count = 0
        self.driving_effect_activated = False
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
                self.hover_count += 1
                
                screen = app.root.get_screen('collection')
                duration = int(time.time() - self.stored_time)
                text = f"Stored: {duration}s\nStats: W:{self.stats['Water']} H:{self.stats['Health']}\nHover count: {self.hover_count}"
                if hasattr(screen, 'show_tooltip'):
                    screen.show_tooltip(pos, text)
                
                if self.hover_count == 4 and not self.driving_effect_activated:
                    self.activate_driving_effect()
            else:
                screen = app.root.get_screen('collection')
                duration = int(time.time() - self.stored_time)
                text = f"Stored: {duration}s\nStats: W:{self.stats['Water']} H:{self.stats['Health']}\nHover count: {self.hover_count}"
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
    def __init__(self, flower_type, **kwargs):
        super().__init__(**kwargs)
        self.flower_type = flower_type
        self.size_hint = (None, 1)
        self.width = 120
        img_src = f"assets/images/{flower_type}_3.png"
        if not os.path.exists(img_src): img_src = f"assets/images/{flower_type}_3.PNG"
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
            
            # Remove from inventory both visually and from save state
            if self.flower_type in app.unlocked_flowers:
                app.unlocked_flowers.remove(self.flower_type)
                app.save_app_state()
            if self.parent:
                self.parent.remove_widget(self)
                
            return True
        return super().on_touch_down(touch)


class CollectionScreen(Screen):
    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.ids.inventory_grid.clear_widgets()
        if len(app.unlocked_flowers) > 0:
            for f in app.unlocked_flowers:
                flower = InventoryFlower(flower_type=f)
                self.ids.inventory_grid.add_widget(flower)
                
        if not hasattr(self, 'tooltip'):
            self.tooltip = Label(
                text="", font_name='assets/fonts/font.ttf', font_size='18sp',
                size_hint=(None, None), size=(150, 60), opacity=0
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
        stats_text = (
            f"Type: {flower.flower_type}\n"
            f"Stored for: {int(time.time() - flower.stored_time)}s\n"
            f"Water: {flower.stats['Water']}/100\n"
            f"Health: {flower.stats['Health']}/100\n"
            f"Care: {flower.stats['Care']}/100\n\n"
            f"Active Buffs:\n" + "\n".join(flower.active_buffs)
        )
        lbl = Label(text=stats_text, font_name='assets/fonts/font.ttf', font_size='18sp')
        content.add_widget(lbl)
        
        btn_box = BoxLayout(size_hint_y=0.3, spacing=10)
        water_btn = Button(text="Water Flower", font_name='assets/fonts/font.ttf', background_color=(0.2, 0.5, 0.8, 1))
        def _water(btn):
            flower.stats['Water'] = min(100, flower.stats['Water'] + 10)
            lbl.text = (
                f"Type: {flower.flower_type}\n"
                f"Stored for: {int(time.time() - flower.stored_time)}s\n"
                f"Water: {flower.stats['Water']}/100\n"
                f"Health: {flower.stats['Health']}/100\n"
                f"Care: {flower.stats['Care']}/100\n\n"
                f"Active Buffs:\n" + "\n".join(flower.active_buffs)
            )
        water_btn.bind(on_release=_water)
        
        stand_btn = Button(text="Check Stand", font_name='assets/fonts/font.ttf', background_color=(0.8, 0.6, 0.2, 1))
        def _stand(btn):
            stand_lbl = Label(text="Stand: Sturdy\nLocation: Theater Store", font_name='assets/fonts/font.ttf', font_size='16sp')
            content.add_widget(stand_lbl)
            stand_btn.disabled = True
        stand_btn.bind(on_release=_stand)
        
        close_btn = Button(text="Close", font_name='assets/fonts/font.ttf', background_color=(0.8, 0.3, 0.3, 1))
        
        btn_box.add_widget(water_btn)
        btn_box.add_widget(stand_btn)
        btn_box.add_widget(close_btn)
        content.add_widget(btn_box)

        popup = Popup(title="Flower Stats & Stand", title_font='assets/fonts/font.ttf', content=content, size_hint=(0.8, 0.8))
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