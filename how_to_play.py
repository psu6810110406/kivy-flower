# how_to_play.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

def show_how_to_play_popup():
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
        background='assets/images/bg_garden.png', # ใช้รูปสวนจางๆ เป็นพื้นหลัง Popup
        background_color=(1, 1, 1, 0.9) # ปรับความสว่างให้เนื้อหาอ่านง่าย
    )
    
    close_btn.bind(on_release=popup.dismiss)
    popup.open()