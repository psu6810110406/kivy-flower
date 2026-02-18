from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window

# ตั้งค่าสีพื้นหลังเล็กน้อย (ไม่จำเป็นต้องใส่ก็ได้)
Window.clearcolor = (0.9, 0.95, 0.8, 1)  # สีเขียวอ่อนๆ

# --- Global Data ---
# เก็บข้อมูลว่าดอกไม้ไหนด่านไหน ปลดล็อคหรือยัง
GAME_DATA = {
    'level_1': {'name': 'Sunflower', 'emoji': '🌻', 'unlocked': False},
    'level_2': {'name': 'Rose', 'emoji': '🌹', 'unlocked': False},
    'level_3': {'name': 'Tulip', 'emoji': '🌷', 'unlocked': False},
    'level_4': {'name': 'Tulip', 'emoji': '🌷', 'unlocked': False},
    'level_5': {'name': 'Tulip', 'emoji': '🌷', 'unlocked': False},
    'level_6': {'name': 'Tulip', 'emoji': '🌷', 'unlocked': False},
}

# --- KV Language (UI Design) ---
kv = """
ScreenManager:
    MenuScreen:
    LevelSelectScreen:
    GameScreen:
    CatalogScreen:

<MenuScreen>:
    name: 'menu'
    BoxLayout:
        orientation: 'vertical'
        padding: 50
        spacing: 20
        
        Label:
            text: '🌸 Dream Garden 🌸'
            font_size: '40sp'
            color: 0.2, 0.6, 0.2, 1
            bold: True

        Button:
            text: 'Play Game'
            size_hint: (0.8, 0.2)
            pos_hint: {'center_x': 0.5}
            background_color: 0.4, 0.8, 0.4, 1
            on_release: app.root.current = 'level_select'

        Button:
            text: 'Catalog (Collection)'
            size_hint: (0.8, 0.2)
            pos_hint: {'center_x': 0.5}
            background_color: 0.4, 0.6, 0.8, 1
            on_release: app.root.current = 'catalog'

        Button:
            text: 'Exit'
            size_hint: (0.8, 0.2)
            pos_hint: {'center_x': 0.5}
            background_color: 0.8, 0.4, 0.4, 1
            on_release: app.stop()

<LevelSelectScreen>:
    name: 'level_select'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        
        Label:
            text: 'Select Level'
            font_size: '30sp'
            size_hint_y: 0.2
            color: 0.3, 0.3, 0.3, 1

        GridLayout:
            cols: 2
            spacing: 20
            padding: 20
            
            Button:
                text: 'Level 1: Sunflower'
                on_release: root.start_level('level_1')
            Button:
                text: 'Level 2: Rose'
                on_release: root.start_level('level_2')
            Button:
                text: 'Level 3: Tulip'
                on_release: root.start_level('level_3')
            Button:
                text: 'Level 4: Tulip'
                on_release: root.start_level('level_4')
            Button:
                text: 'Level 5: Tulip'
                on_release: root.start_level('level_5')
            Button:
                text: 'Level 6: Tulip'
                on_release: root.start_level('level_6')

        Button:
            text: 'Back to Menu'
            size_hint_y: 0.15
            background_color: 0.6, 0.6, 0.6, 1
            on_release: app.root.current = 'menu'

<GameScreen>:
    name: 'game'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10

        Label:
            text: root.current_flower_name
            font_size: '24sp'
            size_hint_y: 0.1
            color: 0.4, 0.4, 0.4, 1

        # ส่วนแสดงผลการเติบโต
        BoxLayout:
            orientation: 'vertical'
            Label:
                text: root.display_emoji
                font_size: '100sp'
            
            Label:
                text: 'Growth: ' + str(int(root.growth_progress)) + '%'
                font_size: '20sp'
                color: 0.2, 0.2, 0.2, 1

        ProgressBar:
            value: root.growth_progress
            max: 100
            size_hint_y: 0.05

        # ปุ่มควบคุม
        BoxLayout:
            size_hint_y: 0.2
            spacing: 20
            Button:
                text: '💧 Water'
                background_color: 0.2, 0.6, 1, 1
                on_release: root.grow_flower(15)
            Button:
                text: '✨ Fertilizer'
                background_color: 1, 0.8, 0.2, 1
                on_release: root.grow_flower(30)

        Button:
            text: 'Give Up (Back)'
            size_hint_y: 0.1
            background_color: 0.8, 0.4, 0.4, 1
            on_release: app.root.current = 'level_select'

<CatalogScreen>:
    name: 'catalog'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        
        Label:
            text: 'My Garden Collection'
            font_size: '30sp'
            size_hint_y: 0.2
            color: 0.2, 0.5, 0.2, 1

        ScrollView:
            GridLayout:
                id: catalog_grid
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                row_default_height: 100
                spacing: 10

        Button:
            text: 'Back to Menu'
            size_hint_y: 0.15
            background_color: 0.6, 0.6, 0.6, 1
            on_release: app.root.current = 'menu'
"""

# --- Python Logic Classes ---

class MenuScreen(Screen):
    pass

class LevelSelectScreen(Screen):
    def start_level(self, level_id):
        # ดึงหน้าจอ GameScreen มาตั้งค่า
        game_screen = self.manager.get_screen('game')
        game_screen.setup_level(level_id)
        self.manager.current = 'game'

class GameScreen(Screen):
    growth_progress = NumericProperty(0)
    current_flower_name = StringProperty("")
    display_emoji = StringProperty("🌱")
    current_level_id = StringProperty("")

    def setup_level(self, level_id):
        self.current_level_id = level_id
        self.current_flower_name = f"Growing: {GAME_DATA[level_id]['name']}"
        self.growth_progress = 0
        self.display_emoji = "🌱" # เริ่มต้นเป็นต้นกล้า

    def grow_flower(self, amount):
        if self.growth_progress < 100:
            self.growth_progress += amount
            
            # เปลี่ยนรูปตามระยะการโต (Simulation)
            if self.growth_progress >= 30 and self.growth_progress < 70:
                self.display_emoji = "🌿" # เริ่มมีใบ
            elif self.growth_progress >= 70 and self.growth_progress < 100:
                self.display_emoji = "🥀" # ตูม (รอปาน)
            
            if self.growth_progress >= 100:
                self.growth_progress = 100
                # ดอกไม้บานเต็มที่
                target_emoji = GAME_DATA[self.current_level_id]['emoji']
                self.display_emoji = target_emoji
                self.level_complete()

    def level_complete(self):
        # บันทึกข้อมูลลง Catalog
        GAME_DATA[self.current_level_id]['unlocked'] = True
        
        # สร้าง Popup เลือกทางไปต่อ
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f"You grew a {GAME_DATA[self.current_level_id]['name']}!", font_size='20sp'))
        
        btn_next = Button(text="Next Level / Level Select", background_color=(0.4, 0.8, 0.4, 1))
        btn_menu = Button(text="Main Menu", background_color=(0.4, 0.6, 0.8, 1))
        
        content.add_widget(btn_next)
        content.add_widget(btn_menu)
        
        popup = Popup(title="Success! 🎉", content=content, size_hint=(0.8, 0.5), auto_dismiss=False)
        
        # ผูกปุ่มเข้ากับฟังก์ชันเปลี่ยนหน้า
        def go_next(instance):
            popup.dismiss()
            self.manager.current = 'level_select' # หรือจะเขียน logic ให้ไป level ถัดไปอัตโนมัติก็ได้
            
        def go_menu(instance):
            popup.dismiss()
            self.manager.current = 'menu'

        btn_next.bind(on_release=go_next)
        btn_menu.bind(on_release=go_menu)
        
        popup.open()

class CatalogScreen(Screen):
    def on_pre_enter(self):
        # รีเฟรชข้อมูลใน Catalog ทุกครั้งที่เข้ามาหน้านี้
        grid = self.ids.catalog_grid
        grid.clear_widgets()
        
        for key, data in GAME_DATA.items():
            # สร้างกล่องแนวนอนสำหรับแต่ละรายการ
            row = BoxLayout(spacing=10, padding=10)
            
            if data['unlocked']:
                # ถ้าปลดล็อคแล้ว ให้โชว์รูปและชื่อ
                lbl_icon = Label(text=data['emoji'], font_size='50sp', size_hint_x=0.3)
                lbl_name = Label(text=data['name'], font_size='24sp', size_hint_x=0.7, halign='left', valign='middle')
                lbl_name.bind(size=lbl_name.setter('text_size')) # จัดข้อความชิดซ้าย
                row.add_widget(lbl_icon)
                row.add_widget(lbl_name)
            else:
                # ถ้ายังไม่ปลดล็อค
                lbl_icon = Label(text="🔒", font_size='40sp', size_hint_x=0.3)
                lbl_name = Label(text="???", font_size='24sp', size_hint_x=0.7)
                row.add_widget(lbl_icon)
                row.add_widget(lbl_name)
                
            grid.add_widget(row)

class FlowerGameApp(App):
    def build(self):
        return Builder.load_string(kv)

if __name__ == '__main__':
    FlowerGameApp().run()