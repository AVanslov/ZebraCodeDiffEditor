import os
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QPlainTextEdit, QWidget


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class CustomTextEdit(QPlainTextEdit):
    def __init__(self, parent=None, is_left_editor=False):
        super().__init__(parent)
        self.is_left_editor = is_left_editor
        self.setAcceptDrops(True)
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
        painter.fillRect(event.rect(), QColor(204, 227, 222))  # светлый фон

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        has_diff = hasattr(self, '_diff_map') and self._diff_map

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(Qt.darkGray)

                number = str(block_number + 1)
                symbol = ''

                if has_diff:
                    status = self._diff_map.get(block_number)
                    if status == 'added':
                        symbol = '+'
                    elif status == 'removed' and self.is_left_editor:
                        symbol = '-'
                    elif status == 'modified':
                        symbol = '~'

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
        if hasattr(self, '_diff_map') and not self.isReadOnly():
            painter = QPainter(self.viewport())
            block = self.firstVisibleBlock()

            while block.isValid():
                block_number = block.blockNumber()
                top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
                bottom = top + int(self.blockBoundingRect(block).height())

                status = self._diff_map.get(block_number)

                if block.isVisible():
                    if status == 'removed':
                        painter.save()
                        painter.setPen(Qt.NoPen)
                        painter.setBrush(QColor(188, 71, 73))  # Теракотовый
                        painter.drawRect(0, top, self.viewport().width(), bottom - top)
                        painter.restore()

                    if status == 'added':
                        painter.save()
                        painter.setPen(Qt.NoPen)
                        painter.setBrush(QColor(88, 129, 87))  # Зелёный
                        painter.drawRect(0, top, self.viewport().width(), bottom - top)
                        painter.restore()

                    if status == 'modified':
                        painter.save()
                        painter.setPen(QColor(244, 162, 89))  # цвет линий штриховки
                        spacing = 5

                        right = self.viewport().width()
                        height = bottom - top

                        for x in range(-height, right, spacing):
                            painter.drawLine(x, top, x + height, bottom)

                        painter.restore()

                block = block.next()

        super().paintEvent(event)

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
        """Скрывает все неизменённые блоки, оставляя изменённые и их окружение."""
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
        block = self.document().firstBlock()
        while block.isValid():
            block.setVisible(True)
            block = block.next()
        self.document().markContentsDirty(0, self.document().characterCount())
        self.updateGeometry()

    def apply_editor_theme(self, theme: str):
        if theme == 'light':
            self.setStyleSheet("""
                QPlainTextEdit {
                    background-color: #EAF4F4;
                    color: black;
                }
            """)
        else:  # dark
            self.setStyleSheet("""
                QPlainTextEdit {
                    background-color: #354f52;
                    color: #dee2e6;
                }
            """)
