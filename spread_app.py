import os, random, asyncio, re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty
from kivy.core.window import Window
import database
import gpt_call

Window.size = (1800, 850)

# Функция для преобразования Markdown в Kivy-разметку
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



Builder.load_file('spread_ui.kv')


class SpreadScreen(BoxLayout):
    decks = ListProperty([])
    spread_types = ListProperty(["3 карты", "Крест", "4 карты"])
    selected_deck = StringProperty("")
    selected_spread = StringProperty("")
    result_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh_decks()
        self.analysis_spinners = []

    def refresh_decks(self):
        self.decks = database.get_all_decks()

    def perform_spread(self, question):
        if not self.selected_deck or not self.selected_spread:
            self.result_text = "[color=ff0000]Выберите колоду и тип расклада![/color]"
            return
        if not question.strip():
            self.result_text = "[color=ff0000]Введите вопрос![/color]"
            return

        # Настройка количества карт и компоновки
        num_cards = 0
        if self.selected_spread == "3 карты":
            num_cards = 3
            self.ids.cards_layout.cols = 3
        elif self.selected_spread == "Крест":
            num_cards = 5
            self.ids.cards_layout.cols = 5
        elif self.selected_spread == "4 карты":
            num_cards = 4
            self.ids.cards_layout.cols = 4
        else:
            num_cards = 3
            self.ids.cards_layout.cols = 3

        deck_id = database.get_deck_id(self.selected_deck)
        if not deck_id:
            self.result_text = "[color=ff0000]Колода не найдена![/color]"
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT card_name, description, image_path FROM cards WHERE deck_id=?", (deck_id,))
        all_cards = cursor.fetchall()

        if len(all_cards) < num_cards:
            self.result_text = "[color=ff0000]Недостаточно карт в колоде для данного расклада![/color]"
            return

        selected_cards = random.sample(all_cards, num_cards)

        # Отображаем карты с подписями
        cards_layout = self.ids.cards_layout
        cards_layout.clear_widgets()
        positions = []
        if self.selected_spread == "Крест":
            positions = ["Верхняя", "Правая", "Центральная", "Левая", "Нижняя"]
        for idx, (card_name, description, image_path) in enumerate(selected_cards):
            container = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150))
            img_source = image_path if image_path and os.path.exists(image_path) else "resources/images/default.jpg"
            img_widget = Image(source=img_source, allow_stretch=True, keep_ratio=True)
            label_text = card_name
            if self.selected_spread == "Крест" and idx < len(positions):
                label_text = f"{positions[idx]}: {card_name}"
            label = Label(text=label_text, size_hint_y=None, height=dp(30))
            container.add_widget(img_widget)
            container.add_widget(label)
            cards_layout.add_widget(container)

        # Готовим описание для GPT
        card_details = "\n".join(f"{name}: {desc}" for name, desc, _ in selected_cards)
        description_for_gpt = (f"Вопрос: {question}\n"
                               f"Расклад: {self.selected_spread}\n"
                               f"Колода: {self.selected_deck}\n"
                               f"Карты:\n{card_details}"
                               f"Помимо анализа карт, ты должен дать расширенный вывод и рекомендации. Ответ стилизуй, будто ты умолишенная гадалка")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(gpt_call.gpt_call(description_for_gpt, role="Обезумевшая гадалка таро. Даёшь правильные и точные интерпретации раскладов и незаметно иронизируешь и слегка по доброму троллишь. К вопрошающему только в мужском роде - Ищущий ответы странник. или просто 'дорогуша'"))
        loop.close()

        md_response = markdown_to_kivy(
            response) if response else "[color=ff0000]Ошибка при получении ответа от GPT[/color]"
        self.result_text = f"[b]Интерпретация:[/b]\n{md_response}"

    def start_analysis(self, question):
        if not self.selected_deck or not self.selected_spread:
            self.result_text = "[color=ff0000]Выберите колоду и тип расклада![/color]"
            return
        if not question.strip():
            self.result_text = "[color=ff0000]Введите вопрос![/color]"
            return

        num_cards = 0
        if self.selected_spread == "3 карты":
            num_cards = 3
            self.ids.cards_layout.cols = 3
        elif self.selected_spread == "Крест":
            num_cards = 5
            self.ids.cards_layout.cols = 5
        elif self.selected_spread == "4 карты":
            num_cards = 4
            self.ids.cards_layout.cols = 4
        else:
            num_cards = 3
            self.ids.cards_layout.cols = 3

        deck_id = database.get_deck_id(self.selected_deck)
        if not deck_id:
            self.result_text = "[color=ff0000]Колода не найдена![/color]"
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT card_name, description, image_path FROM cards WHERE deck_id=?", (deck_id,))
        all_cards = cursor.fetchall()

        if len(all_cards) < num_cards:
            self.result_text = "[color=ff0000]Недостаточно карт в колоде для анализа![/color]"
            return

        # Уточненные инструкции для креста
        instructions = "[b]Инструкция:[/b] Выберите карты для каждой позиции и нажмите 'Отправить анализ'."
        if self.selected_spread == "Крест":
            instructions = ("[b]Инструкция для Крест:[/b]\n"
                            "1. Верхняя: выберите карту для верхней позиции.\n"
                            "2. Правая: выберите карту для правой позиции.\n"
                            "3. Центральная: выберите карту для центральной позиции.\n"
                            "4. Левая: выберите карту для левой позиции.\n"
                            "5. Нижняя: выберите карту для нижней позиции.")
        self.ids.instruction_label.text = instructions

        self.ids.result_label.text = ""
        cards_layout = self.ids.cards_layout
        cards_layout.clear_widgets()
        self.analysis_spinners = []

        card_image_map = {card[0]: card[2] for card in all_cards}
        all_card_names = [card[0] for card in all_cards]
        print("Количество доступных карт:", len(all_card_names))
        print("Список карт:", all_card_names)
        for i in range(num_cards):
            spinner = Spinner(
                text="Выберите карту",
                values=all_card_names,
                size_hint=(None, None),
                size=(dp(200), dp(40)),
                background_color=(0.5, 0.5, 0.5, 1)  # временно для отладки
            )
            img_preview = Image(source="resources/images/default.jpg",
                                size_hint=(None, None), size=(dp(100), dp(150)))
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(185))
            box.add_widget(Label(text=f"Позиция {i + 1}", size_hint_y=None, height=dp(30)))
            box.add_widget(spinner)
            box.add_widget(img_preview)
            self.analysis_spinners.append(spinner)
            cards_layout.add_widget(box)
            spinner.bind(text=self.make_update_image(img_preview, card_image_map))

            # Создаем и добавляем кнопку после цикла
        analyze_button = Button(
            text="Отправить анализ",
            size_hint_y=None,
            height=dp(40)
        )
        analyze_button.bind(on_release=lambda instance: self.submit_analysis(question))
        cards_layout.add_widget(analyze_button)

    def make_update_image(self, img_widget, mapping):
        def update_image(spinner, text):
            img_widget.source = mapping.get(text, "resources/images/default.jpg")

        return update_image

    def submit_analysis(self, question):
        selected_names = [spinner.text for spinner in self.analysis_spinners if spinner.text != "Выберите карту"]
        if len(selected_names) != len(self.analysis_spinners):
            self.result_text = "[color=ff0000]Выберите все карты![/color]"
            return

        card_details = "\n".join(selected_names)
        description_for_gpt = (f"Вопрос: {question}\n"
                               f"Анализ расклада: {self.selected_spread}\n"
                               f"Колода: {self.selected_deck}\n"
                               f"Выбранные карты:\n{card_details}"
                               f"Помимо анализа карт, ты должен дать расширенный вывод и рекомендации. Ответ стилизуй, будто ты умолишенная гадалка")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(gpt_call.gpt_call(description_for_gpt, role="Обезумевшая гадалка таро. Даёшь правильные и точные интерпретации раскладов и незаметно иронизируешь и слегка по доброму троллишь. К вопрошающему только в мужском роде - Ищущий ответы странник. или просто 'дорогуша"))
        loop.close()

        md_response = markdown_to_kivy(response) if response else "[color=ff0000]Ошибка при анализе![/color]"
        self.result_text = f"[b]Результат анализа:[/b]\n{md_response}"


class SpreadApp(App):
    def build(self):
        return SpreadScreen()


if __name__ == '__main__':
    database.init_db()
    SpreadApp().run()
