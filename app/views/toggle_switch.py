from PySide6.QtCore import Qt, QPropertyAnimation, QPoint, Signal, Property, QRect
from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QPainter, QColor, QFont, QFontMetrics


class ToggleSwitch(QWidget):
    toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._circle_position = 3
        self._animation = QPropertyAnimation(self, b"circle_position", self)
        self._animation.setDuration(200)
        self.active = False

        self.setCursor(Qt.PointingHandCursor)

        self.font = QFont()
        self.font.setBold(True)
        self.font.setPointSize(10)

        self.label_left = QLabel("Side-by-Side", self)
        self.label_right = QLabel("Inline", self)

        for label in (self.label_left, self.label_right):
            label.setFont(self.font)
            label.setAlignment(Qt.AlignCenter)
            label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Вычисляем ширину по самому длинному тексту
        metrics = QFontMetrics(self.font)
        left_text_width = metrics.horizontalAdvance("Side-by-Side")
        right_text_width = metrics.horizontalAdvance("Inline")

        max_text_width = max(left_text_width, right_text_width) + 20  # +20 пикселей отступы

        # Задаем итоговый размер тогла
        self.toggle_width = max_text_width * 2
        self.toggle_height = 40

        self.setFixedSize(self.toggle_width, self.toggle_height)

        # Расставляем лейблы
        self.label_left.setGeometry(0, 0, self.toggle_width // 2, self.toggle_height)
        self.label_right.setGeometry(self.toggle_width // 2, 0, self.toggle_width // 2, self.toggle_height)

        self.update_labels()

    def mousePressEvent(self, event):
        self.active = not self.active
        self.start_transition()
        self.toggled.emit(self.active)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QColor("#000"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), self.toggle_height // 2, self.toggle_height // 2)

        # Белый ползунок
        circle_rect = self._circle_geometry()
        painter.setBrush(QColor("#fff"))
        painter.drawRoundedRect(circle_rect, self.toggle_height // 2 - 5, self.toggle_height // 2 - 5)

        painter.end()

    def _circle_geometry(self):
        return QRect(
            int(self._circle_position),
            5,
            self.toggle_width // 2 - 10,
            self.toggle_height - 10
        )

    def start_transition(self):
        self._animation.stop()
        if self.active:
            self._animation.setEndValue(self.width() - self.toggle_width // 2 + 3)
        else:
            self._animation.setEndValue(3)
        self._animation.start()
        self.update_labels()

    def update_labels(self):
        if not self.active:
            self.label_left.setStyleSheet("color: black;")
            self.label_right.setStyleSheet("color: gray;")
        else:
            self.label_left.setStyleSheet("color: gray;")
            self.label_right.setStyleSheet("color: black;")

    @Property(float)
    def circle_position(self):
        return self._circle_position

    @circle_position.setter
    def circle_position(self, pos):
        self._circle_position = pos
        self.update()
