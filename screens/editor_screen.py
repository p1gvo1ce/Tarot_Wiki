"""
editor_screen.py

Экран для создания/редактирования колод:
- Ввод названия колоды (TextInput)
- 5 Spinner'ов для выбора карты
- Поле описания
- Кнопка выбора изображения
- Кнопка сохранения
"""

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty
import os
import database
from filepopup import FileChooserPopup

class EditorScreen(Screen):
    deck_input = StringProperty("")         # название колоды
    card_name = StringProperty("")          # текущая выбранная карта
    card_description = StringProperty("")   # описание карты
    image_path = StringProperty("")         # путь к изображению

    arcana_options = [
        "0 - Шут", "I - Маг", "II - Жрица", "III - Императрица",
        "IV - Император", "V - Иерофант", "VI - Влюблённые",
        "VII - Колесница", "VIII - Сила", "IX - Отшельник",
        "X - Колесо Фортуны", "XI - Справедливость", "XII - Повешенный",
        "XIII - Смерть", "XIV - Умеренность", "XV - Дьявол",
        "XVI - Башня", "XVII - Звезда", "XVIII - Луна",
        "XIX - Солнце", "XX - Суд", "XXI - Мир"
    ]

    wands_options = [
        "Туз Жезлов", "2 Жезлов", "3 Жезлов", "4 Жезлов", "5 Жезлов",
        "6 Жезлов", "7 Жезлов", "8 Жезлов", "9 Жезлов", "10 Жезлов",
        "Рыцарь Жезлов", "Королева Жезлов", "Принц Жезлов", "Принцесса Жезлов"
    ]

    swords_options = [
        "Туз Мечей", "2 Мечей", "3 Мечей", "4 Мечей", "5 Мечей",
        "6 Мечей", "7 Мечей", "8 Мечей", "9 Мечей", "10 Мечей",
        "Рыцарь Мечей", "Королева Мечей", "Принц Мечей", "Принцесса Мечей"
    ]

    cups_options = [
        "Туз Чаш", "2 Чаш", "3 Чаш", "4 Чаш", "5 Чаш",
        "6 Чаш", "7 Чаш", "8 Чаш", "9 Чаш", "10 Чаш",
        "Рыцарь Чаш", "Королева Чаш", "Принц Чаш", "Принцесса Чаш"
    ]

    pentacles_options = [
        "Туз Пентаклей", "2 Пентаклей", "3 Пентаклей", "4 Пентаклей", "5 Пентаклей",
        "6 Пентаклей", "7 Пентаклей", "8 Пентаклей", "9 Пентаклей", "10 Пентаклей",
        "Рыцарь Пентаклей", "Королева Пентаклей", "Принц Пентаклей", "Принцесса Пентаклей"
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_chooser_popup = None

    def open_file_chooser(self):
        """
        Открываем всплывающее окно для выбора картинки.
        """
        if not self.file_chooser_popup:
            self.file_chooser_popup = FileChooserPopup(select_callback=self.on_file_selected)
        self.file_chooser_popup.open()

    def on_file_selected(self, file_path):
        """
        Коллбэк при выборе файла. Копируем его в resources/images
        и запоминаем в image_path.
        """
        if not file_path:
            print("Файл не выбран.")
            return

        target_dir = os.path.join("resources", "images")
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        filename = os.path.basename(file_path)
        new_path = os.path.join(target_dir, filename)

        try:
            with open(file_path, 'rb') as src, open(new_path, 'wb') as dst:
                dst.write(src.read())
            self.image_path = new_path
            print(f"Изображение скопировано: {new_path}")
        except Exception as e:
            print(f"Ошибка копирования файла: {e}")

    def on_card_select(self, card_name: str):
        """
        Коллбэк при выборе карты в одном из Spinner'ов.
        Если колода уже есть и карта заполнена – подгружаем описание/картинку.
        """
        self.card_name = card_name
        if not self.deck_input:
            print("Сначала введите название колоды, иначе не из чего загружать.")
            return

        deck_id = database.get_deck_id(self.deck_input)
        if deck_id is None:
            # Значит, колода ещё не существует — пустая форма
            self.card_description = ""
            self.image_path = ""
            return

        row = database.get_card(deck_id, card_name)
        if row:
            desc, img = row
            self.card_description = desc if desc else ""
            self.image_path = img if img else ""
        else:
            self.card_description = ""
            self.image_path = ""

    def save_card(self):
        """
        Сохраняем текущую карту (и колоду) в базу.
        """
        if not self.deck_input.strip():
            print("Не задано название колоды!")
            return
        if not self.card_name.strip():
            print("Не выбрана карта!")
            return

        # Создаём или достаём колоду
        row_id = database.create_deck(self.deck_input.strip())
        if row_id == 0:
            # Значит, уже была, получим её id
            deck_id = database.get_deck_id(self.deck_input.strip())
        else:
            deck_id = row_id

        database.create_or_update_card(deck_id, self.card_name, self.card_description, self.image_path)
        print(f"Карта '{self.card_name}' сохранена в колоду '{self.deck_input}'!")
