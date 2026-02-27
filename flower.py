import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, StringProperty, ListProperty, BooleanProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window


# ตั้งค่าสีพื้นหลังเล็กน้อย (ไม่จำเป็นต้องใส่ก็ได้)
Window.clearcolor = (0.9, 0.95, 0.8, 1)  # สีเขียวอ่อนๆ

# --- Global Data ---
# เพิ่มข้อมูล Preferences (ความชอบ) และเส้นทางรูปภาพ (images)
GAME_DATA = {
    'level_1': {
        'name': 'Sunflower (ทานตะวัน)', 'emoji': '🌻', 
        'desc': 'ชอบแสงแดดจัดมาก ไม่ต้องการน้ำเยอะ',
        'preferences': {'water': 'low', 'sun': 'high', 'fertilizer': 'medium'},
        'images': {'seed': 'assets/seed.png', 'sprout': 'assets/sprout_sunflower.png', 'full': 'assets/sunflower.png'},
        'unlocked': False
    },
    'level_2': {
        'name': 'Rose (กุหลาบ)', 'emoji': '🌹', 
        'desc': 'ต้องการน้ำและปุ๋ยมากเพื่อให้ออกดอกสวยงาม',
        'preferences': {'water': 'high', 'sun': 'medium', 'fertilizer': 'high'},
        'images': {'seed': 'assets/seed.png', 'sprout': 'assets/sprout_rose.png', 'full': 'assets/rose.png'},
        'unlocked': False
    },
    'level_3': {
        'name': 'Tulip (ทิวลิป)', 'emoji': '🌷', 
        'desc': 'ดูแลแบบพอดีๆ ไม่ชอบอะไรที่มากเกินไป',
        'preferences': {'water': 'medium', 'sun': 'medium', 'fertilizer': 'medium'},
        'images': {'seed': 'assets/seed.png', 'sprout': 'assets/sprout_tulip.png', 'full': 'assets/tulip.png'},
        'unlocked': False
    },
    'level_4': {
        'name': 'Cactus (กระบองเพชร)', 'emoji': '🌵', 
        'desc': 'เกลียดน้ำมาก! ชอบแดดเปรี้ยงๆ',
        'preferences': {'water': 'low', 'sun': 'high', 'fertilizer': 'low'},
        'images': {'seed': 'assets/seed.png', 'sprout': 'assets/sprout_cactus.png', 'full': 'assets/cactus.png'},
        'unlocked': False
    },
    'level_5': {
        'name': 'Orchid (กล้วยไม้)', 'emoji': '🌸', 
        'desc': 'ต้องการปุ๋ยค่อนข้างเยอะ แสงแดดรำไร',
        'preferences': {'water': 'medium', 'sun': 'low', 'fertilizer': 'high'},
        'images': {'seed': 'assets/seed.png', 'sprout': 'assets/sprout_orchid.png', 'full': 'assets/orchid.png'},
        'unlocked': False
    },
    'level_6': {
        'name': 'Mushroom (เห็ด)', 'emoji': '🍄', 
        'desc': 'ต้องการแค่ความชื้นและที่ร่ม (น้ำเยอะ แดดน้อย)',
        'preferences': {'water': 'high', 'sun': 'low', 'fertilizer': 'low'},
        'images': {'seed': 'assets/seed.png', 'sprout': 'assets/sprout_mushroom.png', 'full': 'assets/mushroom.png'},
        'unlocked': False
    },
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
            font_size: '20sp'
            size_hint: (0.8, 0.2)
            pos_hint: {'center_x': 0.5}
            background_color: 0.4, 0.8, 0.4, 1
            on_release: app.root.current = 'level_select'

        Button:
            text: 'Catalog (Collection)'
            font_size: '20sp'
            size_hint: (0.8, 0.2)
            pos_hint: {'center_x': 0.5}
            background_color: 0.4, 0.6, 0.8, 1
            on_release: app.root.current = 'catalog'

        Button:
            text: 'Exit'
            font_size: '20sp'
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
            text: 'Select Seed to Plant'
            font_size: '30sp'
            size_hint_y: 0.2
            color: 0.3, 0.3, 0.3, 1

        GridLayout:
            cols: 2
            spacing: 20
            padding: 20
            
            Button:
                text: 'Level 1: Sunflower'
                on_release: root.show_level_info('level_1')
            Button:
                text: 'Level 2: Rose'
                on_release: root.show_level_info('level_2')
            Button:
                text: 'Level 3: Tulip'
                on_release: root.show_level_info('level_3')
            Button:
                text: 'Level 4: Cactus'
                on_release: root.show_level_info('level_4')
            Button:
                text: 'Level 5: Orchid'
                on_release: root.show_level_info('level_5')
            Button:
                text: 'Level 6: Mushroom'
                on_release: root.show_level_info('level_6')

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

        # Header Info (Day & Name)
        BoxLayout:
            size_hint_y: 0.1
            Label:
                text: root.current_flower_name
                font_size: '24sp'
                color: 0.4, 0.4, 0.4, 1
            Label:
                text: 'Day: ' + str(root.current_day) + ' / ' + str(root.max_days)
                font_size: '24sp'
                color: 0.8, 0.4, 0.2, 1
                bold: True

        # ส่วนแสดงผลการเติบโต (ภาพวาดตัวเอง หรือ อิโมจิแทน)
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.5
            
            FloatLayout:
                # แสดงอิโมจิถ้ารูปภาพไม่มี
                Label:
                    text: root.display_emoji
                    font_size: '100sp'
                    opacity: 0 if root.has_image else 1
                
                # แสดงรูปภาพถ้ากำหนดไฟล์ไว้
                Image:
                    source: root.display_image_path
                    allow_stretch: True
                    keep_ratio: True
                    opacity: 1 if root.has_image else 0
            
            Label:
                text: 'Growth: ' + str(int(root.growth_progress)) + '%'
                font_size: '20sp'
                color: 0.2, 0.2, 0.2, 1
                size_hint_y: 0.2

        ProgressBar:
            value: root.growth_progress
            max: 100
            size_hint_y: 0.05

        # ปุ่มควบคุม (แอคชั่นในแต่ละวัน)
        Label:
            text: 'What will you do today?'
            color: 0.3, 0.3, 0.3, 1
            size_hint_y: 0.05
            
        BoxLayout:
            size_hint_y: 0.2
            spacing: 10
            Button:
                text: '💧 Water'
                background_color: 0.2, 0.6, 1, 1
                on_release: root.take_action('water')
            Button:
                text: '☀️ Sun'
                background_color: 1, 0.6, 0.2, 1
                on_release: root.take_action('sun')
            Button:
                text: '✨ Fertilizer'
                background_color: 0.6, 0.8, 0.2, 1
                on_release: root.take_action('fertilizer')

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
                row_default_height: 120
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
    def show_level_info(self, level_id):
        data = GAME_DATA[level_id]
        
        # สร้างเนื้อหา Popup สำหรับบอกความชอบของต้นไม้
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # ชื่อและอิโมจิ
        content.add_widget(Label(text=f"{data['emoji']} {data['name']}", font_size='24sp', bold=True))
        content.add_widget(Label(text=data['desc'], text_size=(300, None), halign='center'))
        
        # แสดงความชอบ
        prefs = data['preferences']
        pref_text = (
            f"💧 Water Needs: [b]{prefs['water'].upper()}[/b]\\n"
            f"☀️ Sun Needs: [b]{prefs['sun'].upper()}[/b]\\n"
            f"✨ Fertilizer Needs: [b]{prefs['fertilizer'].upper()}[/b]"
        )
        content.add_widget(Label(text=pref_text, markup=True, halign='center'))
        
        # ปุ่มเริ่มเกม
        btn_start = Button(text="Plant Seed!", size_hint_y=None, height=50, background_color=(0.4, 0.8, 0.4, 1))
        content.add_widget(btn_start)
        
        popup = Popup(title="Plant Info", content=content, size_hint=(0.8, 0.6))
        
        def start_game(instance):
            popup.dismiss()
            # ดึงหน้าจอ GameScreen มาตั้งค่า
            game_screen = self.manager.get_screen('game')
            game_screen.setup_level(level_id)
            self.manager.current = 'game'

        btn_start.bind(on_release=start_game)
        popup.open()


class GameScreen(Screen):
    growth_progress = NumericProperty(0)
    current_day = NumericProperty(1)
    max_days = NumericProperty(6)  # สมมติว่ามีเวลา 6 วันในการทำให้ดอกไม้โตเต็มที่ร้อยเปอร์เซ็นต์
    
    current_flower_name = StringProperty("")
    display_emoji = StringProperty("🌱")
    
    # ระบบรูปภาพ
    display_image_path = StringProperty("")
    has_image = BooleanProperty(False)
    
    current_level_id = StringProperty("")

    def setup_level(self, level_id):
        self.current_level_id = level_id
        self.current_flower_name = f"Growing: {GAME_DATA[level_id]['name']}"
        self.growth_progress = 0
        self.current_day = 1
        
        self.update_visuals()

    def update_visuals(self):
        # เปลี่ยนรูปหรืออิโมจิตามระยะการโต (Simulation)
        images = GAME_DATA[self.current_level_id]['images']
        emoji_fallback = GAME_DATA[self.current_level_id]['emoji']
        
        target_image = ""
        target_emoji = ""
        
        if self.growth_progress < 30:
            target_emoji = "🌱" # เริ่มต้นเป็นเมล็ด/ต้นกล้า
            target_image = images['seed']
        elif self.growth_progress >= 30 and self.growth_progress < 80:
            target_emoji = "🌿" # เริ่มมีใบ/กิ่ง
            target_image = images['sprout']
        else:
            target_emoji = emoji_fallback # ตูมหรือบาน
            target_image = images['full']
            
        self.display_emoji = target_emoji
        self.display_image_path = target_image
        
        # เช็คว่ารูปภาพมีจริงอยู่ในโฟลเดอร์ไหม ถ้ามีถึงจะเปลี่ยนโหมดไปแสดงรูปวาด
        self.has_image = os.path.exists(target_image)

    def take_action(self, action_type):
        if self.current_day > self.max_days or self.growth_progress >= 100:
            return  # จบเกมหรือโตเต็มที่แล้ว กดอะไรไม่ได้
            
        preferences = GAME_DATA[self.current_level_id]['preferences']
        action_rating = preferences[action_type]
        
        # คำนวณ Point ที่ได้จากการที่ต้นไม้ชอบ (ยิ่งตรงใจยิ่งโตไว)
        # วันนึงกดได้ 1 ครั้ง เป้าหมาย 6 วัน ต้องได้คะแนนรวม 100% 
        # (เฉลี่ยได้ครั้งละ 15-30% ถึงจะชนะ)
        if action_rating == 'high':
            added_growth = 25
            msg = "Perfect Match!"
        elif action_rating == 'medium':
            added_growth = 15
            msg = "Not bad."
        else: # low
            added_growth = 5
            msg = "It doesn't like this..."
            
        self.growth_progress += added_growth
        if self.growth_progress > 100:
            self.growth_progress = 100
            
        self.update_visuals()
        
        # บวกวันเพิ่ม
        self.current_day += 1
        
        # ตรวจสอบการผ่านด่าน
        if self.growth_progress >= 100:
            self.game_over(success=True)
        elif self.current_day > self.max_days and self.growth_progress < 100:
            self.game_over(success=False)

    def game_over(self, success):
        if success:
            # สำเร็จ! บันทึกข้อมูลลง Catalog
            GAME_DATA[self.current_level_id]['unlocked'] = True
            title = "Success! 🎉"
            text_msg = f"You beautiful grew a {GAME_DATA[self.current_level_id]['name']}!"
        else:
            # ไม่รอด โตไม่ทัน
            title = "Oh no... 🥀"
            text_msg = "Your plant didn't grow fully in time. Try again!"
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=text_msg, font_size='20sp', halign='center'))
        
        btn_next = Button(text="Level Select", background_color=(0.4, 0.8, 0.4, 1))
        content.add_widget(btn_next)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.5), auto_dismiss=False)
        
        def go_next(instance):
            popup.dismiss()
            self.manager.current = 'level_select'
            
        btn_next.bind(on_release=go_next)
        popup.open()


class CatalogScreen(Screen):
    def on_pre_enter(self):
        # รีเฟรชข้อมูลใน Catalog ทุกครั้งที่เข้ามาหน้านี้
        grid = self.ids.catalog_grid
        grid.clear_widgets()
        
        for key, data in GAME_DATA.items():
            # สร้างกล่องสำหรับแต่ละรายการ 
            row = BoxLayout(spacing=10, padding=10)
            
            if data['unlocked']:
                # ถ้าปลดล็อคแล้ว ตรวจสอบว่ามีรูปวาดไหม
                full_image_path = data['images']['full']
                has_img = os.path.exists(full_image_path)
                
                if has_img:
                    icon_widget = Image(source=full_image_path, size_hint_x=0.3)
                else:
                    icon_widget = Label(text=data['emoji'], font_size='50sp', size_hint_x=0.3)
                
                lbl_name = Label(text=data['name'], font_size='24sp', size_hint_x=0.7, halign='left', valign='middle')
                lbl_name.bind(size=lbl_name.setter('text_size'))
                
                row.add_widget(icon_widget)
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