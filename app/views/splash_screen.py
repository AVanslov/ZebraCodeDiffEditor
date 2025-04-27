import os

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QPropertyAnimation
from PySide6.QtGui import QPixmap

from app.utils.paths import get_images_path

base_path = get_images_path()


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Картинка зебры
        self.label = QLabel(self)
        self.label.setPixmap(QPixmap(os.path.join(base_path, "zebra.jpg")).scaled(800, 700, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.label.setStyleSheet("""
            QLabel {
                border-radius: 20px;
                background-color: rgba(255, 255, 255, 0.15);
                padding: 10px;
            }
        """)
        layout.addWidget(self.label)

        # Эффект прозрачности для плавного исчезновения
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1)

    def fade_and_close(self, on_finished):
        animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        animation.setDuration(1500)  # 1.5 секунды затухания
        animation.setStartValue(1)
        animation.setEndValue(0)
        animation.finished.connect(on_finished)
        animation.start()
        self.animation = animation  # сохраняю ссылку для анимации
