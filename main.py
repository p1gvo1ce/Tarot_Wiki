"""
main.py

Главный скрипт, запускающий Kivy-приложение.
Загружает kv-файл, создает ScreenManager, подключает базу данных.
"""

import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

import database
from screens.viewer_screen import ViewerScreen
from screens.editor_screen import EditorScreen

# Грузим kv-разметку
Builder.load_file('ui.kv')

class TarotScreenManager(ScreenManager):
    pass

class TarotApp(App):
    def build(self):
        # Инициализируем базу
        database.init_db()

        sm = TarotScreenManager()
        sm.add_widget(ViewerScreen(name='viewer'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm

    def on_stop(self):
        database.close_db()

if __name__ == '__main__':
    TarotApp().run()
