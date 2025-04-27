import re

from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtCore import Qt


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)

        keyword_patterns = [
            r"\bdef\b", r"\bclass\b", r"\breturn\b", r"\bif\b", r"\belse\b",
            r"\belif\b", r"\bwhile\b", r"\bfor\b", r"\bin\b", r"\bimport\b",
            r"\bfrom\b", r"\btry\b", r"\bexcept\b", r"\bwith\b", r"\bas\b",
            r"\bNone\b", r"\bTrue\b", r"\bFalse\b", r"\bpass\b", r"\bbreak\b",
            r"\bcontinue\b", r"\bassert\b", r"\byield\b", r"\blambda\b"
        ]

        self.highlighting_rules = [(re.compile(pattern), keyword_format) for pattern in keyword_patterns]

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append((re.compile(r"\".*?\"|'.*?'"), string_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r"#.*"), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)
