import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPlainTextEdit


class CustomTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setPlaceholderText("💡 Перетащите сюда файл или нажмите кнопку выше, чтобы вставить из буфера обмена.")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        self.setPlainText(text)
                except Exception as e:
                    self.setPlainText(f"Ошибка при чтении файла:\n{e}")
