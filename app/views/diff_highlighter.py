import difflib

from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor


class DiffHighlighter(QSyntaxHighlighter):
    def __init__(self, document, left_lines, right_lines, mode='right'):
        super().__init__(document)
        self.left_lines = left_lines
        self.right_lines = right_lines
        self.mode = mode  # 'left' или 'right'
        self.diff_map = {}
        self._is_diff_running = False

        # Форматы
        self.added_format = QTextCharFormat()
        self.added_format.setBackground(QColor(163, 177, 138))  # Светло-зелёный

        self.removed_format = QTextCharFormat()
        self.removed_format.setBackground(QColor(215, 152, 140))  # Розоватый

        # self.modified_format = QTextCharFormat()
        # self.modified_format.setBackground(QColor(244, 178, 100))  # Светло теракотовый

        self.recompute_diff()

    def similarity(self, a: str, b: str) -> float:
        """Вычисляет коэффициент похожести двух строк (от 0 до 1)."""
        return difflib.SequenceMatcher(None, a, b).ratio()

    def update_diff(self, left_text: str, right_text: str):
        if self._is_diff_running:
            return

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

        max_len = max(len(self.left_lines), len(self.right_lines))
        for i in range(max_len):
            left = self.left_lines[i] if i < len(self.left_lines) else ''
            right = self.right_lines[i] if i < len(self.right_lines) else ''

            if self.mode == 'left':
                if left and not right:
                    self.diff_map[i] = 'removed'
            elif self.mode == 'right':
                if not left and right:
                    self.diff_map[i] = 'added'
                else:
                    if left and right:
                        # 1. Полное совпадение
                        if left.strip() == right.strip():
                            continue  # ничего не делать — строки совпадают
                        # 2. Те же символы, другой порядок
                        elif sorted(left.strip()) == sorted(right.strip()):
                            self.diff_map[i] = 'modified'
                        else:
                            sim = self.similarity(left.strip(), right.strip())
                            # 3. Большое отличие
                            if sim < 0.5:
                                self.diff_map[i] = 'added'
                            # 4. Среднее отличие
                            elif 0.5 <= sim <= 0.8:
                                self.diff_map[i] = 'modified'
                            # 5. Иначе считаем без изменений

    def highlightBlock(self, text):
        block_number = self.currentBlock().blockNumber()
        status = self.diff_map.get(block_number)

        if status == 'added':
            self.setFormat(0, max(1, len(text)), self.added_format)
        elif status == 'removed':
            self.setFormat(0, max(1, len(text)), self.removed_format)
        # modified — без полной заливки через setFormat, будем рисовать вручную штриховку

    def get_modified_blocks(self):
        return set(self.diff_map.keys())
