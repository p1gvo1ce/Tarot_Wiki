"""
flowlayout.py

Кастомный Layout, который располагает виджеты в строке,
автоматически перенося их на новую, если не хватает места.
"""

from kivy.uix.layout import Layout
from kivy.properties import NumericProperty, OptionProperty, VariableListProperty
from kivy.clock import Clock
from kivy.metrics import dp


class FlowLayout(Layout):
    """
    Простой FlowLayout:
    - orientation='lr-tb': располагаем детей слева-направо, затем перенос вниз.
    - spacing: отступы между детьми.
    """

    spacing = VariableListProperty([dp(5), dp(5)], length=2)  # Горизонтальный и вертикальный отступы
    orientation = OptionProperty('lr-tb', options=('lr-tb',))
    minimum_height = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._trigger_layout = Clock.create_trigger(self.do_layout, -1)
        self.bind(
            children=self._trigger_layout,
            parent=self._trigger_layout,
            pos=self._trigger_layout,
            size=self._trigger_layout
        )

    def do_layout(self, *args):
        x_off = self.x
        y_off = self.top
        line_max_height = 0
        total_height = 0

        for child in reversed(self.children):
            # Учитываем только видимые/имеющие размер виджеты
            if not child.size_hint_x and not child.size:
                continue

            cw, ch = child.size

            if x_off + cw > self.right:
                x_off = self.x
                y_off -= line_max_height + self.spacing[1]
                total_height += line_max_height + self.spacing[1]
                line_max_height = 0

            child.pos = (x_off, y_off - ch)
            x_off += cw + self.spacing[0]

            if ch > line_max_height:
                line_max_height = ch

        total_height += line_max_height
        self.minimum_height = total_height
