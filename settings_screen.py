# settings_screen.py
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.properties import BooleanProperty, NumericProperty, StringProperty

class SettingsScreen(Screen):
    is_muted = BooleanProperty(False)
    previous_volume = NumericProperty(1.0) 
    
    speaker_icon = StringProperty('assets/images/loud.png') 

    def on_volume_change(self, instance, value):
        app = App.get_running_app()
        if hasattr(app, 'set_volume'):
            app.set_volume(value)
            
        # ลอจิกเสริม: ถ้าผู้เล่นเลื่อนหลอดเสียงเองตอนที่โดน Mute อยู่ ให้ยกเลิก Mute อัตโนมัติ
        if value > 0 and self.is_muted:
            self.is_muted = False
            self.speaker_icon = 'assets/images/loud.png'
        # ลอจิกเสริม: ถ้าผู้เล่นเลื่อนหลอดเสียงไปที่ 0 เอง ให้เปลี่ยนรูปเป็นปิดเสียง
        elif value == 0 and not self.is_muted:
            self.is_muted = True
            self.speaker_icon = 'assets/images/silen.png'

    def toggle_mute(self, slider_widget):
        if not self.is_muted:
            # กำลังจะ Mute (ปิดเสียง)
            # 1. จำค่าเสียงปัจจุบันไว้ก่อน
            if slider_widget.value > 0:
                self.previous_volume = slider_widget.value
            # 2. ปรับหลอดเสียงเป็น 0
            slider_widget.value = 0 
            self.speaker_icon = 'assets/images/silen.png'
            self.is_muted = True
        else:
            # ยกเลิก Mute (เปิดเสียง)
            slider_widget.value = self.previous_volume if self.previous_volume > 0 else 0.5
            self.speaker_icon = 'assets/images/loud.png'
            self.is_muted = False