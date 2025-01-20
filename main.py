"""
main.py

Главный запускной скрипт Kivy-приложения. Управляет ScreenManager'ом
и инициализацией/закрытием базы данных.
"""

import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

import database
from screens.viewer_screen import ViewerScreen
from screens.editor_screen import EditorScreen

Builder.load_file('ui.kv')  # Подгружаем kv-разметку

class TarotScreenManager(ScreenManager):
    pass

class TarotApp(App):
    def build(self):
        # Инициализируем базу
        database.init_db()

        sm = TarotScreenManager()
        # Добавляем экраны
        sm.add_widget(ViewerScreen(name='viewer'))
        sm.add_widget(EditorScreen(name='editor'))

        return sm

    def on_stop(self):
        # Закрываем базу перед выходом
        database.close_db()

if __name__ == '__main__':
    TarotApp().run()
