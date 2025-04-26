import os

from PySide6.QtCore import Qt, QPropertyAnimation, QPoint, Signal, Property, QRect
from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QPainter, QColor, QFont, QFontMetrics
from PySide6.QtSvgWidgets import QSvgWidget

from app.utils.paths import get_icons_path

base_path = get_icons_path()


class ToggleSwitch(QWidget):
    toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._circle_position = 0
        self._animation = QPropertyAnimation(self, b"circle_position", self)
        self._animation.setDuration(200)
        self.active = False

        self.setCursor(Qt.PointingHandCursor)

        self.font = QFont()
        self.font.setBold(True)
        self.font.setPointSize(10)

        self.label_left = QSvgWidget(os.path.join(base_path, "2_columns.svg"), self)
        self.label_left.setFixedSize(25, 25)

        self.label_right = QSvgWidget(os.path.join(base_path, "1_column.svg"), self)
        self.label_right.setFixedSize(25, 25)

        for label in (self.label_left, self.label_right):
            label.setFont(self.font)
            label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Задаем итоговый размер тогла
        self.toggle_width = 90  # фиксированная ширина
        self.toggle_height = 40
        self.setFixedSize(self.toggle_width, self.toggle_height)

        # Расставляем лейблы
        self.label_left.setGeometry(
            (self.toggle_width // 4) - (self.label_left.width() // 2),
            (self.toggle_height // 2) - (self.label_left.height() // 2),
            self.label_left.width(),
            self.label_left.height()
        )

        self.label_right.setGeometry(
            (self.toggle_width * 3 // 4) - (self.label_right.width() // 2),
            (self.toggle_height // 2) - (self.label_right.height() // 2),
            self.label_right.width(),
            self.label_right.height()
        )

        self.update_labels()

    def mousePressEvent(self, event):
        self.active = not self.active
        self.start_transition()
        self.toggled.emit(self.active)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QColor("#495057"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), self.toggle_height // 2, self.toggle_height // 2)

        # Белый ползунок
        circle_rect = self._circle_geometry()
        painter.setBrush(QColor("#fff"))
        painter.drawRoundedRect(circle_rect, self.toggle_height // 2 - 5, self.toggle_height // 2 - 5)

        painter.end()

    def _circle_geometry(self):
        return QRect(
            int(self._circle_position) + 6,  # +3 чтобы сделать зазор слева
            5,
            (self.toggle_width // 2) - 12,    # ширина меньше на 6 пикселей
            self.toggle_height - 10
        )

    def start_transition(self):
        self._animation.stop()
        if self.active:
            self._animation.setEndValue(self.width() // 2)
        else:
            self._animation.setEndValue(0)
        self._animation.start()
        self.update_labels()

    def update_labels(self):
        if not self.active:
            self.label_left.setStyleSheet("color: #CED4DA;")
            self.label_right.setStyleSheet("color: #CED4DA;")
        else:
            self.label_left.setStyleSheet("color: #212529;")
            self.label_right.setStyleSheet("color: #212529;")

    @Property(float)
    def circle_position(self):
        return self._circle_position

    @circle_position.setter
    def circle_position(self, pos):
        self._circle_position = pos
        self.update()
