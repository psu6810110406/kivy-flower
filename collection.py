# collection.py
import os
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image

class DraggableFlower(Scatter):
    def __init__(self, flower_type, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (400, 400)
        self.do_rotation = False
        img_src = f"assets/images/{flower_type}_4.png"
        if not os.path.exists(img_src): img_src = "assets/images/flower_3.png"
        self.add_widget(Image(source=img_src, size=self.size))

class InventoryFlower(Image):
    def __init__(self, flower_type, **kwargs):
        super().__init__(**kwargs)
        self.flower_type = flower_type
        self.size_hint = (None, None)
        self.size = (250, 250)
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