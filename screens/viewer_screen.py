"""
viewer_screen.py

Экран просмотра колод: выпадающий список колод, и пять Spinner'ов,
каждый для своей группы (Козыри, Жезлы, Мечи, Чаши, Пентакли).
При выборе карты отображаются картинка и описание.
"""

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty
import database

class ViewerScreen(Screen):
    selected_deck = StringProperty("")  # выбрана ли колода
    available_decks = ListProperty([])  # список колод для Spinner-а колод
    card_image = StringProperty("")
    card_description = StringProperty("")

    # Списки карт по группам (можно расширять)
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



    def on_pre_enter(self):
        """
        При входе на экран — обновляем список доступных колод.
        """
        self.refresh_decks()

    def refresh_decks(self):
        decks = database.get_all_decks()
        self.available_decks = decks

    def select_deck(self, deck_name: str):
        """
        Коллбэк при выборе колоды. Сбрасываем картинку/описание,
        чтобы пользователь видел, что новая колода.
        """
        self.selected_deck = deck_name
        self.card_image = ""
        self.card_description = ""

    def on_card_select(self, card_name: str):
        """
        Коллбэк при выборе карты в Spinner (любой группы).
        Подгружаем из базы данные, если есть.
        """
        if not self.selected_deck:
            print("Сначала выберите колоду, а уже потом карту.")
            return
        deck_id = database.get_deck_id(self.selected_deck)
        if not deck_id:
            print(f"Колода '{self.selected_deck}' не найдена. Пусто в базе.")
            return

        row = database.get_card(deck_id, card_name)
        if row:
            desc, img_path = row
            self.card_description = desc if desc else "Описание отсутствует."
            self.card_image = img_path if img_path else ""
        else:
            self.card_description = "Такой карты нет (не заполнено)."
            self.card_image = ""
