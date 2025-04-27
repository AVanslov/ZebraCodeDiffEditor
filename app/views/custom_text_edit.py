import os
from functools import partial

from PySide6.QtCore import Qt, QRect, QSize, QEvent
from PySide6.QtGui import QColor, QPainter, QTextCursor, QPainterPath
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QPushButton


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor
        self.setAttribute(Qt.WA_StyledBackground, True)

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()

        path = QPainterPath()
        # path.addRoundedRect(rect, 12, 12)
        radius = 12
        w, h = rect.width(), rect.height()

        path.moveTo(radius, 0)
        path.lineTo(w, 0)
        path.lineTo(w, h)
        path.lineTo(radius, h)
        path.quadTo(0, h, 0, h - radius)
        path.lineTo(0, radius)
        path.quadTo(0, 0, radius, 0)
        painter.setClipPath(path)
        painter.fillRect(rect, QColor(204, 227, 222))  # фон

        # Отрисовать текст нумерации вручную здесь
        block = self.code_editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.code_editor.blockBoundingGeometry(block).translated(self.code_editor.contentOffset()).top())
        bottom = top + int(self.code_editor.blockBoundingRect(block).height())

        has_diff = hasattr(self.code_editor, '_diff_map') and self.code_editor._diff_map

        while block.isValid() and top <= rect.bottom():
            if block.isVisible() and bottom >= rect.top():
                painter.setPen(Qt.darkGray)
                number = str(block_number + 1)
                symbol = ''
                if has_diff:
                    status = self.code_editor._diff_map.get(block_number)
                    if status == 'added':
                        symbol = '+'
                    elif status == 'removed' and self.code_editor.is_left_editor:
                        symbol = '-'
                    elif status == 'modified':
                        symbol = '~'
                painter.drawText(
                    0, top,
                    self.width(),
                    self.code_editor.fontMetrics().height(),
                    Qt.AlignCenter,
                    symbol + number
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.code_editor.blockBoundingRect(block).height())
            block_number += 1


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

        # Для группировки непромодифицированных строк
        self.folded_blocks = {}          # {start: (start,end)}

        self.viewport().installEventFilter(self)

    def set_diff_map(self, diff_map):
        self._diff_map = diff_map

    def line_number_area_width(self):
        return 50
        # digits = len(str(self.blockCount())) + 1
        # return 10 + self.fontMetrics().horizontalAdvance('9') * digits

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
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

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
                    0, top,
                    self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    symbol + number
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        self.viewport().update()

    def paintEvent(self, event):
        # 1) фон диффа
        painter = QPainter(self.viewport())
        if hasattr(self, '_diff_map') and not self.isReadOnly():
            block = self.firstVisibleBlock()
            while block.isValid():
                num = block.blockNumber()
                top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
                h   = int(self.blockBoundingRect(block).height())
                status = self._diff_map.get(num)
                if block.isVisible() and status:
                    painter.save()
                    painter.setPen(Qt.NoPen)
                    if status=='removed':
                        painter.setBrush(QColor(188,71,73))
                        painter.drawRect(0, top, self.viewport().width(), h)
                    elif status=='added':
                        painter.setBrush(QColor(88,129,87))
                        painter.drawRect(0, top, self.viewport().width(), h)
                    else:  # modified
                        painter.setPen(QColor(244,162,89))
                        spacing=5; right=self.viewport().width()
                        for x in range(-h, right, spacing):
                            painter.drawLine(x, top, x+h, top+h)
                    painter.restore()
                block = block.next()
        painter.end()

        # 2) текст
        super().paintEvent(event)

        # 3) placeholder-группы
        painter = QPainter(self.viewport())
        painter.setPen(Qt.gray)
        painter.setBrush(QColor(230,230,230))
        for start,(s,e) in self.folded_blocks.items():
            block = self.document().findBlockByNumber(start)
            r = self.blockBoundingGeometry(block).translated(self.contentOffset()).toRect()
            painter.drawRect(r)
            painter.drawText(r, Qt.AlignCenter, f"... {e-s+1} lines hidden ...")
        painter.end()

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
                        self.setPlainText(f.read())
                except Exception as e:
                    self.setPlainText(f'Error reading file:\n{e}')

    def fold_unmodified_blocks(self, modified_blocks: set, context: int = 0):
        # сворачиваем только в правом редакторе
        if self.is_left_editor:
            return

        doc   = self.document()
        total = doc.blockCount()

        # 1) Собираем номера видимых блоков (модифицированные + их контекст)
        visible = set()
        for m in modified_blocks:
            for i in range(m - context, m + context + 1):
                if 0 <= i < total:
                    visible.add(i)

        # 2) Ищем непрерывные диапазоны «скрыть»
        self.folded_blocks.clear()
        i = 0
        while i < total:
            if i in visible:
                i += 1
                continue

            start = i
            # двигаемся, пока попадаем в «скрывать»
            while i < total and i not in visible:
                i += 1
            end = i - 1

            # только группы длиной >1 линии сворачиваем
            if end - start + 1 > 1:
                self.folded_blocks[start] = (start, end)

        # 3) Скрываем все блоки, которые попали в любой из диапазонов,
        #    кроме их первого (`start`)
        for s, e in self.folded_blocks.values():
            for num in range(s + 1, e + 1):
                doc.findBlockByNumber(num).setVisible(False)

        # 4) Гарантируем, что блоки вне свёртки видимы
        for idx in range(total):
            if not any(s <= idx <= e for s, e in self.folded_blocks.values()):
                doc.findBlockByNumber(idx).setVisible(True)

        # 5) Обновляем рендер
        doc.markContentsDirty(0, doc.characterCount())
        self.updateGeometry()

    def unfold_all(self):
        block = self.firstVisibleBlock()
        while block.isValid():
            block.setVisible(True)
            block = block.next()
        self.document().markContentsDirty(0, self.document().characterCount())
        self.updateGeometry()

    def unfold_range(self, start, end):
        block = self.document().findBlockByNumber(start)
        # показать все
        idx = start
        while idx <= end:
            b = self.document().findBlockByNumber(idx)
            b.setVisible(True)
            idx += 1
        self.document().markContentsDirty(0, self.document().characterCount())
        self.updateGeometry()

    def apply_editor_theme(self, theme: str):
        scrollbar_style = """
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 2px 0 2px 0;
            }
            QScrollBar::handle:vertical {
                background: #a0a0a0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                background: transparent;
                height: 8px;
                margin: 0 2px 0 2px;
            }
            QScrollBar::handle:horizontal {
                background: #a0a0a0;
                border-radius: 4px;
                min-width: 20px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """

        if theme == 'light':
            self.setStyleSheet(f"""
                QPlainTextEdit {{
                    background-color: #EAF4F4;
                    color: black;
                    border: none;
                    border-radius: 12px;
                }}
                QPlainTextEdit > viewport {{
                    background: transparent;
                    border-radius: 12px;
                }}
                {scrollbar_style}
            """)
        else:
            self.setStyleSheet(f"""
                QPlainTextEdit {{
                    background-color: #354f52;
                    color: #dee2e6;
                    border: none;
                    border-radius: 12px;
                }}
                QPlainTextEdit > viewport {{
                    background: transparent;
                    border-radius: 12px;
                }}
                {scrollbar_style}
            """)

    def eventFilter(self, obj, event):
        # ловим клики именно по viewport
        if obj is self.viewport() and event.type() == QEvent.MouseButtonPress:
            pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
            # ищем, попали ли мы на placeholder-прямоугольник
            for start, (s, e) in list(self.folded_blocks.items()):
                block = self.document().findBlockByNumber(start)
                r = self.blockBoundingGeometry(block).translated(self.contentOffset()).toRect()
                if r.contains(pos):
                    # разворачиваем этот диапазон
                    self.unfold_range(s, e)
                    del self.folded_blocks[start]
                    self.document().markContentsDirty(0, self.document().characterCount())
                    self.updateGeometry()
                    return True   # поглотили клик
            # если клик не по заглушке — пропускаем дальше
        return super().eventFilter(obj, event)
