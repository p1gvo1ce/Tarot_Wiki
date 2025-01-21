"""
viewer_screen.py

Экран для просмотра карт.
"""

import re
from io import StringIO

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty
import database

from pygments import lex
from pygments.lexers import guess_lexer, TextLexer
from pygments.formatter import Formatter
from pygments.styles import get_style_by_name
from pygments.token import Token


def markdown_to_kivy(markdown_text):
    """
    Простейший конвертер Markdown в Kivy-разметку, включая заголовки, жирный курсив,
    списки, горизонтальные разделители, вставки кода и цитаты.
    """
    text = markdown_text or ""

    # Обработка блоков кода (``` ... ```)
    def repl_code_block(match):
        code_content = match.group(1)
        code_content = code_content.replace('[', '\\[').replace(']', '\\]')
        return f"[color=#AAAAAA]{code_content}[/color]"

    text = re.sub(r'```(.*?)```', repl_code_block, text, flags=re.DOTALL)

    # Обработка встроенного кода (`...`)
    def repl_inline_code(match):
        code_text = match.group(1)
        code_text = code_text.replace('[', '\\[').replace(']', '\\]')
        return f"[color=#111111]{code_text}[/color]"

    text = re.sub(r'`([^`]+?)`', repl_inline_code, text)

    # Цитаты: строки, начинающиеся с "> "
    text = re.sub(r'(?m)^> (.+)$', r'[i][color=gray]> \1[/color][/i]', text)

    # Горизонтальные разделители: строки с тремя и более дефисами
    text = re.sub(r'(?m)^---+$', r'[color=gray]──────────────────────────[/color]', text)

    # Заголовки: преобразование строк, начинающихся с #
    text = re.sub(r'(?m)^# (.+)$', r'[size=34][b]\1[/b][/size]', text)
    text = re.sub(r'(?m)^## (.+)$', r'[size=30][b]\1[/b][/size]', text)
    text = re.sub(r'(?m)^### (.+)$', r'[size=26][b]\1[/b][/size]', text)
    text = re.sub(r'(?m)^#### (.+)$', r'[size=22][b]\1[/b][/size]', text)
    text = re.sub(r'(?m)^##### (.+)$', r'[size=18][b]\1[/b][/size]', text)
    text = re.sub(r'(?m)^###### (.+)$', r'[size=16][b]\1[/b][/size]', text)

    # Жирный текст: **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'[b]\1[/b]', text)
    # Курсив: *text*
    text = re.sub(r'\*(.+?)\*', r'[i]\1[/i]', text)
    # Маркированные списки: строки, начинающиеся с "- "
    text = re.sub(r'(?m)^- (.+)', r'• \1', text)

    return text

class ViewerScreen(Screen):
    selected_deck = StringProperty("")
    available_decks = ListProperty([])
    card_image = StringProperty("")
    card_description = StringProperty("")

    # Полный список карт
    arcana_options = ListProperty([
        "0 - Шут", "I - Маг", "II - Жрица", "III - Императрица", "IV - Император",
        "V - Иерофант", "VI - Влюблённые", "VII - Колесница", "VIII - Сила",
        "IX - Отшельник", "X - Колесо Фортуны", "XI - Справедливость",
        "XII - Повешенный", "XIII - Смерть", "XIV - Умеренность", "XV - Дьявол",
        "XVI - Башня", "XVII - Звезда", "XVIII - Луна", "XIX - Солнце",
        "XX - Суд", "XXI - Мир"
    ])
    wands_options = ListProperty([
        "Туз Жезлов", "2 Жезлов", "3 Жезлов", "4 Жезлов", "5 Жезлов",
        "6 Жезлов", "7 Жезлов", "8 Жезлов", "9 Жезлов", "10 Жезлов",
        "Рыцарь Жезлов", "Королева Жезлов", "Принц Жезлов", "Принцесса Жезлов"
    ])
    swords_options = ListProperty([
        "Туз Мечей", "2 Мечей", "3 Мечей", "4 Мечей", "5 Мечей",
        "6 Мечей", "7 Мечей", "8 Мечей", "9 Мечей", "10 Мечей",
        "Рыцарь Мечей", "Королева Мечей", "Принц Мечей", "Принцесса Мечей"
    ])
    cups_options = ListProperty([
        "Туз Чаш", "2 Чаш", "3 Чаш", "4 Чаш", "5 Чаш",
        "6 Чаш", "7 Чаш", "8 Чаш", "9 Чаш", "10 Чаш",
        "Рыцарь Чаш", "Королева Чаш", "Принц Чаш", "Принцесса Чаш"
    ])
    pentacles_options = ListProperty([
        "Туз Пентаклей", "2 Пентаклей", "3 Пентаклей", "4 Пентаклей", "5 Пентаклей",
        "6 Пентаклей", "7 Пентаклей", "8 Пентаклей", "9 Пентаклей", "10 Пентаклей",
        "Рыцарь Пентаклей", "Королева Пентаклей", "Принц Пентаклей", "Принцесса Пентаклей"
    ])

    def on_pre_enter(self):
        self.refresh_decks()

    def refresh_decks(self):
        self.available_decks = database.get_all_decks()

    def select_deck(self, deck_name: str):
        self.selected_deck = deck_name
        self.card_image = ""
        self.card_description = ""

    def on_card_select(self, card_name: str):
        if not self.selected_deck:
            self.card_description = "Сначала нужно выбрать колоду, а потом карту."
            print("Сначала выберите колоду!")
            return

        deck_id = database.get_deck_id(self.selected_deck)
        if not deck_id:
            print(f"Колода '{self.selected_deck}' не найдена.")
            return

        row = database.get_card(deck_id, card_name)
        if row:
            desc, img_path = row
            # Преобразование описания из Markdown в разметку Kivy
            self.card_description = markdown_to_kivy(desc) if desc else "Нет описания"
            self.card_image = img_path if img_path else ""
        else:
            self.card_description = "Карта не найдена/не заполнена"
            self.card_image = ""

    def reset_spinners(self, current_spinner):
        spinners = []
        try:
            spinners = [
                self.ids.spinner_arcana_view,
                self.ids.spinner_wands_view,
                self.ids.spinner_swords_view,
                self.ids.spinner_cups_view,
                self.ids.spinner_pentacles_view
            ]
        except Exception as e:
            print(f"Ошибка при получении спиннеров: {e}")
        for spinner in spinners:
            if spinner and spinner != current_spinner:
                spinner.text = "Выберите карту"
