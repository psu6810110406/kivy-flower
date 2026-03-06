# settings_screen.py
from kivy.uix.screenmanager import Screen
from kivy.app import App

class SettingsScreen(Screen):
    def on_volume_change(self, instance, value):
        app = App.get_running_app()
        if hasattr(app, 'set_volume'):
            app.set_volume(value)
