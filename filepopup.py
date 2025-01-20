"""
filepopup.py

Окно Popup c FileChooser для выбора изображения.
"""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.button import Button
from kivy.properties import ObjectProperty

class FileChooserPopup(Popup):
    file_chooser = ObjectProperty(None)
    select_callback = ObjectProperty(None)

    def __init__(self, select_callback, **kwargs):
        super().__init__(**kwargs)
        self.select_callback = select_callback
        self.title = "Выберите файл"
        self.size_hint = (0.9, 0.9)

        root_layout = BoxLayout(orientation='vertical', spacing=5)
        self.file_chooser = FileChooserListView()
        root_layout.add_widget(self.file_chooser)

        btn_layout = BoxLayout(size_hint_y=None, height='40dp', spacing=5)
        select_btn = Button(text="Выбрать")
        cancel_btn = Button(text="Отмена")

        select_btn.bind(on_release=self.on_select)
        cancel_btn.bind(on_release=self.dismiss)

        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)

        root_layout.add_widget(btn_layout)
        self.add_widget(root_layout)

    def on_select(self, instance):
        selection = self.file_chooser.selection
        if selection and len(selection) > 0:
            selected_path = selection[0]
            if self.select_callback:
                self.select_callback(selected_path)
        self.dismiss()
