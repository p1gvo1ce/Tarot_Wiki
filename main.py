import kivy
from kivy.core.window import Window

Window.size = (1800, 850)

kivy.require('2.1.0')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

import database

# Импортируем классы экранов ДО загрузки KV-файла
from screens.viewer_screen import ViewerScreen
from screens.editor_screen import EditorScreen

# Загружаем KV-разметку
Builder.load_file('ui.kv')

class TarotScreenManager(ScreenManager):
    pass

class TarotApp(App):
    def build(self):
        # Инициализация базы данных
        database.init_db()
        # Возвращаем ScreenManager, созданный по KV-разметке
        return TarotScreenManager()

    def on_stop(self):
        database.close_db()

if __name__ == '__main__':
    TarotApp().run()
