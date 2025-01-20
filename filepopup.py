"""
filepopup.py

Окно Popup c FileChooser для выбора файла.
Добавлены:
 - Spinner для выбора диска (только Windows).
 - Чтение/запись последнего каталога в app_settings.json (через app_config).
"""

import os
import platform
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.properties import ObjectProperty, StringProperty

import app_config


def show_all_except_system(folder, filename):
    """
    Показываем все файлы и папки, кроме системных.
    """
    import win32file

    full_path = os.path.join(folder, filename)

    if os.path.isdir(full_path):
        return True

    try:
        attrs = win32file.GetFileAttributes(full_path)
        if attrs & win32file.FILE_ATTRIBUTE_HIDDEN or attrs & win32file.FILE_ATTRIBUTE_SYSTEM:
            return False
    except Exception:
        return False

    return True


class FileChooserPopup(Popup):
    file_chooser = ObjectProperty(None)
    select_callback = ObjectProperty(None)

    last_dir = StringProperty("")

    def __init__(self, select_callback, **kwargs):
        super().__init__(**kwargs)
        self.select_callback = select_callback
        self.title = "Выберите файл"
        self.size_hint = (0.9, 0.9)

        config = app_config.load_config()
        self.last_dir = config.get("last_dir", "C:\\" if platform.system() == "Windows" else "/")

        root_layout = BoxLayout(orientation='vertical', spacing=5)

        # ---------- Верхняя панель ----------
        top_panel = BoxLayout(size_hint_y=None, height='40dp', spacing=5)

        if platform.system() == "Windows":
            drive_list = self.get_windows_drives()
            top_panel.add_widget(
                Spinner(
                    text=self.get_current_drive(),
                    values=drive_list,
                    size_hint=(None, None),
                    size=("100dp", "40dp"),
                    on_text=self.on_drive_select
                )
            )

        root_layout.add_widget(top_panel)

        # ---------- FileChooser ----------
        self.file_chooser = FileChooserListView(
            filters=[show_all_except_system],
            path=self.last_dir,
            dirselect=False
        )
        root_layout.add_widget(self.file_chooser)

        # ---------- Панель кнопок ----------
        btn_layout = BoxLayout(size_hint_y=None, height='40dp', spacing=5)
        select_btn = Button(text="Выбрать")
        cancel_btn = Button(text="Отмена")

        select_btn.bind(on_release=self.on_select)
        cancel_btn.bind(on_release=self.dismiss)

        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)

        root_layout.add_widget(btn_layout)
        self.add_widget(root_layout)

    def on_drive_select(self, spinner, drive):
        """
        Пользователь выбрал диск из Spinner.
        """
        if not drive.endswith("\\"):
            drive += "\\"
        self.file_chooser.path = drive
        self.file_chooser.on_entry_added(self.file_chooser.path)  # Принудительно обновляем содержимое
        self.last_dir = drive

    def on_select(self, instance):
        """
        Обработка выбора файла.
        """
        selection = self.file_chooser.selection
        if selection and len(selection) > 0:
            selected_path = selection[0]
            if self.select_callback:
                self.select_callback(selected_path)

            self.last_dir = os.path.dirname(selected_path)
            self.save_last_dir()

        self.dismiss()

    def on_dismiss(self):
        """
        Сохранение последнего пути при закрытии окна.
        """
        self.last_dir = self.file_chooser.path
        self.save_last_dir()
        super().on_dismiss()

    def save_last_dir(self):
        """
        Сохраняем последний каталог в app_settings.json
        """
        config = app_config.load_config()
        config["last_dir"] = self.last_dir
        app_config.save_config(config)

    def get_windows_drives(self):
        """
        Возвращает список логических дисков на Windows.
        """
        import string
        drives = []
        for letter in string.ascii_uppercase:
            path = f"{letter}:\\"
            if os.path.exists(path):
                drives.append(path)
        return drives

    def get_current_drive(self):
        """
        Определяем текущий диск из last_dir.
        """
        path = self.last_dir
        if len(path) >= 2 and path[1] == ":":
            return path[:2] + "\\"
        return "C:\\"
