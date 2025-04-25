from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QPlainTextEdit,
    QVBoxLayout,
    QPushButton,
    QToolBar,
    QLineEdit,
)

from app.views.custom_text_edit import CustomTextEdit


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Zebra Code Diff Editor')
        self.resize(1000, 600)

        # Main widget
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Toolbar with prompt input and buttons
        toolbar = QToolBar('Main Toolbar')
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # Editors fields
        self.editor_left = CustomTextEdit()
        self.editor_right = QPlainTextEdit()

        # Past from clipboard
        paste_clipboard_action = QAction("Paste from Clipboard", self)
        paste_clipboard_action.triggered.connect(self.paste_from_clipboard)
        toolbar.addAction(paste_clipboard_action)

        # Prompt input
        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText("Enter your prompt here...")
        self.prompt_input.setFixedWidth(300)
        toolbar.addWidget(self.prompt_input)

        # Run
        run_action = QAction('Run', self)
        run_action.triggered.connect(self.on_run)
        toolbar.addAction(run_action)

        # Save
        save_action = QAction('Save', self)
        save_action.triggered.connect(self.on_save)
        toolbar.addAction(save_action)

        # Undo / Redo
        undo_action = QAction('Undo', self)
        undo_action.triggered.connect(self.editor_right.undo)
        toolbar.addAction(undo_action)

        redo_action = QAction('Redo', self)
        redo_action.triggered.connect(self.editor_right.redo)
        toolbar.addAction(redo_action)

        # Inline view
        toggle_action = QAction('Toggle View', self)
        toggle_action.triggered.connect(self.on_toggle_view)
        toolbar.addAction(toggle_action)

        editors_layout = QHBoxLayout()
        editors_layout.addWidget(self.editor_left)
        editors_layout.addWidget(self.editor_right)

        main_layout.addLayout(editors_layout)

    def on_run(self):
        """A stub for code generation."""

        left_text = self.editor_left.toPlainText()

        def update_ui():
            new_text = left_text + "\n# Generated line"
            self.editor_right.setPlainText(new_text)

        # AI response simulation
        QTimer.singleShot(1000, update_ui)

    def on_save(self):
        print("Saving code...")
        print("Prompt:", self.prompt_input.text())
        print("Left:\n", self.editor_left.toPlainText())
        print("Right:\n", self.editor_right.toPlainText())

    def on_toggle_view(self):
        print("Toggle View clicked (not implemented yet)")

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.editor_left.setPlainText(text)
        else:
            self.editor_left.setPlainText("⚠️ Буфер обмена пуст.")