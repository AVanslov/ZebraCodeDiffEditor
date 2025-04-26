from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QSizePolicy,
)

from app.views.custom_text_edit import CustomTextEdit
from app.views.diff_highlighter import DiffHighlighter
from app.views.toggle_switch import ToggleSwitch


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Zebra Code Diff Editor')
        self.resize(1400, 800)

        self.inline_mode = False
        self.sidebar_visible = True

        # Central widget
        central_widget = QWidget()
        self.main_layout = QHBoxLayout()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        self.central_widget = central_widget

        # Left Menu
        self.left_menu = QWidget()
        self.left_menu_layout = QVBoxLayout()
        self.left_menu_layout.setContentsMargins(0, 0, 0, 0)
        self.left_menu_layout.setSpacing(0)
        self.left_menu.setLayout(self.left_menu_layout)
        self.left_menu.setFixedWidth(60)

        self.menu_button = QPushButton("🦓")
        self.menu_button.setFixedHeight(60)
        self.menu_button.clicked.connect(self.toggle_sidebar)

        self.theme_button = QPushButton('🌖')
        self.theme_button.setFixedHeight(40)
        self.theme_button.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; }
            QPushButton:hover { background-color: #e0e0e0; }
        """)
        self.theme_button.clicked.connect(self.toggle_theme)

        self.left_menu_layout.addWidget(self.menu_button)
        self.left_menu_layout.addStretch()
        self.left_menu_layout.addWidget(self.theme_button)

        # Sidebar (Toggleable)
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10)
        self.sidebar.setLayout(self.sidebar_layout)
        self.sidebar.setFixedWidth(250)

        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText('Enter your prompt here...')
        self.run_button = QPushButton('Run')
        self.run_button.clicked.connect(self.on_run)

        self.sidebar_layout.addWidget(self.prompt_input)
        self.sidebar_layout.addWidget(self.run_button)
        self.sidebar_layout.addStretch()

        # Right Panel
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_panel.setLayout(self.right_layout)

        # Top Toolbar with actions
        self.toolbar_layout = QHBoxLayout()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.on_save)

        self.save_as_button = QPushButton("Save As")
        self.save_as_button.clicked.connect(self.on_save_as)

        self.undo_button = QPushButton("Undo")
        self.undo_button.clicked.connect(self.on_undo)

        self.redo_button = QPushButton("Redo")
        self.redo_button.clicked.connect(self.on_redo)

        self.toggle_switch = ToggleSwitch()
        self.toggle_switch.toggled.connect(self.toggle_inline_view)

        self.toolbar_layout.addStretch()

        for button in [
            self.save_button, self.save_as_button,
            self.undo_button, self.redo_button
        ]:
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.toolbar_layout.addWidget(button)

        self.toolbar_layout.addWidget(self.toggle_switch)

        # Editors
        self.editor_left = CustomTextEdit()
        self.editor_right = CustomTextEdit()

        self.highlighter = DiffHighlighter(
            self.editor_right.document(),
            self.editor_left.toPlainText().splitlines(),
            self.editor_right.toPlainText().splitlines()
        )

        self.editor_right.textChanged.connect(self.delayed_diff_highlight)

        self.editors_layout = QHBoxLayout()
        self.editors_layout.addWidget(self.editor_left)
        self.editors_layout.addWidget(self.editor_right)

        self.right_layout.addLayout(self.toolbar_layout)
        self.right_layout.addLayout(self.editors_layout)

        # Add to main layout
        self.main_layout.addWidget(self.left_menu)
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.right_panel)

        # Diff timer
        self.diff_timer = QTimer()
        self.diff_timer.setInterval(200)
        self.diff_timer.setSingleShot(True)
        self.diff_timer.timeout.connect(self.apply_diff_highlight)

        # Set Up Theme
        self.current_theme = "light"  # по умолчанию

        self.apply_theme()

    def toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def toggle_inline_view(self, active):
        if not active:
            if not self.editor_left.parent():
                self.editors_layout.insertWidget(0, self.editor_left)
        else:
            self.editors_layout.removeWidget(self.editor_left)
            self.editor_left.setParent(None)
        self.inline_mode = active

    def delayed_diff_highlight(self):
        self.diff_timer.start()

    def apply_diff_highlight(self):
        left_text = self.editor_left.toPlainText()
        right_text = self.editor_right.toPlainText()
        self.highlighter.update_diff(left_text, right_text)

        self.editor_right.set_diff_map(self.highlighter.diff_map)

        modified_blocks = self.highlighter.get_modified_blocks()
        self.editor_right.unfold_all()
        self.editor_right.fold_unmodified_blocks(modified_blocks)

    def on_run(self):
        left_text = self.editor_left.toPlainText()

        def update_ui():
            new_text = left_text + "\n# Generated line"
            self.editor_right.blockSignals(True)
            self.editor_right.setPlainText(new_text)
            self.editor_right.blockSignals(False)
            self.apply_diff_highlight()

        QTimer.singleShot(1000, update_ui)

    def on_save(self):
        print('Saving...')
        print('Prompt:', self.prompt_input.text())
        print('Left:\n', self.editor_left.toPlainText())
        print('Right:\n', self.editor_right.toPlainText())

    def on_save_as(self):
        print('Save As clicked (not implemented)')

    def on_undo(self):
        self.editor_right.undo()

    def on_redo(self):
        self.editor_right.redo()

    def apply_theme(self):
        if self.current_theme == "light":
            self.central_widget.setStyleSheet("background-color: #f8f9fa;")
            self.left_menu.setStyleSheet("background-color: #f1f3f5;")
            self.sidebar.setStyleSheet("background-color: #f1f3f5;")
            self.right_panel.setStyleSheet("background-color: transparent;")
        else:  # dark theme
            self.central_widget.setStyleSheet("background-color: #212529;")
            self.left_menu.setStyleSheet("background-color: #343a40;")
            self.sidebar.setStyleSheet("background-color: #343a40;")
            self.right_panel.setStyleSheet("background-color: transparent;")

    def toggle_theme(self):
        if self.current_theme == "light":
            self.current_theme = "dark"
        else:
            self.current_theme = "light"
        self.apply_theme()
