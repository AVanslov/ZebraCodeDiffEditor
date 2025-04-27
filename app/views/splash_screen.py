import os

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect, QGraphicsBlurEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QTimer
from PySide6.QtGui import QPixmap, QFont, QPainterPath, QPainter

from app.utils.paths import get_images_path

base_path = get_images_path()


def set_rounded_pixmap(label, pixmap, radius):
    """Делает маску с закругленными краями."""
    rounded = QPixmap(pixmap.size())
    rounded.fill(Qt.transparent)

    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    label.setPixmap(rounded)


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(960, 540)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Фон
        self.background_label = QLabel(self)
        original_pixmap = QPixmap(os.path.join(base_path, "zebra_1920x1080px.jpg")).scaled(
            self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
        )
        set_rounded_pixmap(self.background_label, original_pixmap, 60)
        self.background_label.setGeometry(0, 0, self.width(), self.height())

        # Эффект прозрачности
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)  # Начинаем с полной прозрачности

    def start_sequence(self, on_finished):
        # 1. Плавное появление (fade in)
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(700)  # 1 секунда
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.start()

        # 2. После появления — подождать 3 секунды
        def start_fade_out():
            # 3. Плавное исчезновение (fade out)
            self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.fade_out_animation.setDuration(700)  # 1.5 секунды
            self.fade_out_animation.setStartValue(1)
            self.fade_out_animation.setEndValue(0)
            self.fade_out_animation.finished.connect(on_finished)
            self.fade_out_animation.start()

        # Таймер на 2.7 секунды (общее время на показ минус переходы)
        QTimer.singleShot(4000, start_fade_out)
