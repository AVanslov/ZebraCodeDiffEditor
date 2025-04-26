import difflib

from PySide6.QtGui import (
    QColor,
    QSyntaxHighlighter,
    QTextCharFormat,
)


class DiffHighlighter(QSyntaxHighlighter):
    def __init__(self, document, left_lines, right_lines=None):
        super().__init__(document)
        self.left_lines = left_lines
        self.right_lines = right_lines or []
        self.diff_map = []
        self._is_diff_running = False

        self.added_format = QTextCharFormat()
        self.added_format.setBackground(QColor(200, 255, 200))  # light green
        self.added_format.setProperty(QTextCharFormat.FullWidthSelection, True)

        self.removed_format = QTextCharFormat()
        self.removed_format.setBackground(QColor(255, 200, 200))  # light red

        self.recompute_diff()

    def update_diff(self, left_text: str, right_text: str):
        if self._is_diff_running:
            return  # защита от повторного вызова, чтоб не было рекурсии

        self._is_diff_running = True
        try:
            self.left_lines = left_text.splitlines()
            self.right_lines = right_text.splitlines()
            self.recompute_diff()
            self.rehighlight()
        finally:
            self._is_diff_running = False

    def recompute_diff(self):
        self.diff_map = {}
        sm = difflib.SequenceMatcher(None, self.left_lines, self.right_lines, autojunk=False)
        opcodes = sm.get_opcodes()

        for tag, i1, i2, j1, j2 in opcodes:
            if tag in ('insert', 'replace'):
                for j in range(j1, j2):
                    self.diff_map[j] = 'added'

    def highlightBlock(self, text):
        block_number = self.currentBlock().blockNumber()
        if self.diff_map.get(block_number) == 'added':
            self.setFormat(0, max(1, len(text)), self.added_format)

    def get_modified_blocks(self):
        """Возвращает номера блоков с изменениями."""
        return set(self.diff_map.keys())
