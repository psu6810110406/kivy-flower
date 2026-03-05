# how_to_play.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.app import App

def show_how_to_play_popup():
    app = App.get_running_app()
    weather_now = app.weather if app else "ไม่ทราบ"

    # สร้าง Layout หลัก
    content = BoxLayout(orientation='vertical', padding=25, spacing=15)
    
    # --- 1. ส่วนหัว (Header) ---
    header = Label(
        text="[color=2E7D32][b]คู่มือการเล่น (MANUAL)[/b][/color]",
        markup=True,
        font_name='assets/fonts/font.ttf',
        font_size='32sp',
        size_hint_y=0.15
    )
    content.add_widget(header)

    # --- 2. ส่วนเนื้อหาแบบละเอียด (Detailed Info) ---
    grid = GridLayout(cols=1, spacing=10, size_hint_y=0.7)
    
    def add_info_row(title, desc):
        row = BoxLayout(orientation='vertical', spacing=2)
        
        lbl_title = Label(
            text=f"[color=388E3C][b]• {title}[/b][/color]",
            markup=True, font_name='assets/fonts/font.ttf',
            font_size='22sp', halign='left', valign='bottom'
        )
        lbl_title.bind(size=lbl_title.setter('text_size'))
        row.add_widget(lbl_title)
        
        lbl_desc = Label(
            text=desc,
            markup=True, font_name='assets/fonts/font.ttf',
            font_size='18sp', color=(0.1, 0.1, 0.1, 1),
            halign='left', valign='top'
        )
        lbl_desc.bind(size=lbl_desc.setter('text_size'))
        row.add_widget(lbl_desc)

        grid.add_widget(row)

    add_info_row("สภาพอากาศวันนี้ (Today's Weather)", 
                 f"ตอนนี้อากาศ: [color=D32F2F][b]{weather_now}[/b][/color] (ระวัง! มีผลกับความไวในการเติบโตเมื่อรดน้ำ)")
    add_info_row("ระบบพักผ่อน (Stamina System)", 
                 "แต่ละวันคุณมีพลังงาน 100 จุด (หลอดสีฟ้า) หากหมดจะต้องกด 'พักผ่อน' เพื่อเริ่มเช้าวันใหม่")
    add_info_row("รดน้ำ (Water)", 
                 "[color=1976D2][b]ใช้พลังงาน 10[/b][/color] | วันปกติเพิ่มความเติบโต +15 (ถ้าเป็น[b]วันแดดจัด[/b] หรือ [b]ฝนตก[/b] จะได้โบนัสเป็น [b]+30[/b])")
    add_info_row("พรวนดิน (Till Soil)", 
                 "[color=F57C00][b]ใช้พลังงาน 15[/b][/color] | ดินร่วนซุยทำให้รากเดินดี เพิ่มการเติบโตสม่ำเสมอ +20 จุด")
    add_info_row("ใส่ปุ๋ย (Fertilize)", 
                 "[color=7B1FA2][b]ใช้พลังงาน 20[/b][/color] | บำรุงดินแบบจัดเต็ม! ต้นไม้จะโตไวมาก เพิ่มการเติบโตถึง +30 จุด")

    content.add_widget(grid)

    # --- 3. ส่วนท้ายและปุ่มปิด (Footer) ---
    btn_layout = BoxLayout(size_hint_y=0.15, padding=[40, 0])
    close_btn = Button(
        text="เข้าสู่สวนของคุณ",
        font_name='assets/fonts/font.ttf',
        font_size='22sp',
        background_normal='',
        background_color=(0.18, 0.49, 0.2, 1),
        color=(1, 1, 1, 1)
    )
    btn_layout.add_widget(close_btn)
    content.add_widget(btn_layout)

    # สร้าง Popup แบบไร้ขอบเดิม (Custom Styling) และใช้พื้นขาว
    popup = Popup(
        title="",
        separator_height=0,
        content=content,
        size_hint=(0.85, 0.85),
        background='',
        background_color=(0.95, 0.95, 0.95, 1) # สีขาวอมเทานิดๆ เพื่อให้ไม่แสบตาและอ่านตัวอักษรง่าย
    )
    
    close_btn.bind(on_release=popup.dismiss)
    popup.open()