import os

from PySide6.QtCore import Qt, QRect, QSize, QPoint
from PySide6.QtGui import QColor, QPainter, QFont
from PySide6.QtGui import QTextCursor, QTextCharFormat
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QPlainTextEdit, QWidget
# from PySide6.QtGui import QTextBlock


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class CustomTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setPlaceholderText(
            'Drag and drop the file here or click the button above to paste it from the clipboard.'
        )
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def set_diff_map(self, diff_map):
        self._diff_map = diff_map

    def line_number_area_width(self):
        digits = len(str(self.blockCount())) + 1
        return 10 + self.fontMetrics().horizontalAdvance('9') * digits

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(245, 245, 245))  # light gray

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.darkGray)
                symbol = ''
                if hasattr(self, '_diff_map') and self._diff_map.get(block_number) == 'added':
                    symbol = '+'

                painter.drawText(
                    0, top, self.line_number_area.width() - 5, self.fontMetrics().height(),
                    Qt.AlignRight, symbol + number
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        self.viewport().update()

    def paintEvent(self, event):
        super().paintEvent(event)

        if not self.isReadOnly():
            painter = QPainter(self.viewport())
            painter.setPen(QColor(180, 180, 180))  # светло-серый цвет линий
            cursor = self.textCursor()
            block = cursor.block()

            block_geometry = self.blockBoundingGeometry(block).translated(self.contentOffset())
            top = int(block_geometry.top())
            bottom = int(block_geometry.bottom())

            # Рисуем тонкие линии сверху и снизу активного блока
            painter.drawLine(0, top, self.viewport().width(), top)
            painter.drawLine(0, bottom, self.viewport().width(), bottom)

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
                    self.setPlainText(f'Error reading the file:\n{e}')

    def fold_unmodified_blocks(self, modified_blocks: set, context_lines: int = 3):
        """Скрывает блоки, кроме изменённых и их окружения."""
        block = self.document().firstBlock()
        visible_blocks = set()

        for block_num in modified_blocks:
            for i in range(block_num - context_lines, block_num + context_lines + 1):
                if i >= 0:
                    visible_blocks.add(i)

        while block.isValid():
            block_number = block.blockNumber()
            block.setVisible(block_number in visible_blocks)
            block = block.next()

        self.document().markContentsDirty(0, self.document().characterCount())
        self.updateGeometry()

    def unfold_all(self):
        """Показать все строки"""
        block = self.document().firstBlock()
        while block.isValid():
            block.setVisible(True)
            block = block.next()
        self.document().markContentsDirty(0, self.document().characterCount())
        self.updateGeometry()
