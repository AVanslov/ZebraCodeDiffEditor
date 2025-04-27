import os
import random

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QSizePolicy,
    QGraphicsBlurEffect,
    QTextEdit,
)

from app.views.custom_text_edit import CustomTextEdit
from app.views.diff_highlighter import DiffHighlighter
from app.views.toggle_switch import ToggleSwitch
from app.views.syntax_highlighter import PythonHighlighter
from app.utils.paths import get_icons_path

base_path = get_icons_path()


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
        self.left_menu_layout.setContentsMargins(0, 10, 0, 10)
        self.left_menu_layout.setSpacing(0)
        self.left_menu.setLayout(self.left_menu_layout)
        self.left_menu.setFixedWidth(60)

        # Кнопка меню для ввода промпта
        self.menu_button = QPushButton()
        self.menu_button.setIcon(QIcon(os.path.join(base_path, 'edit.svg')))
        self.menu_button.setIconSize(QSize(18, 18))
        self.menu_button.setFixedSize(40, 40)
        self.menu_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: none;
                border-radius: 10;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.menu_button.clicked.connect(self.toggle_sidebar)

        # Кнопка переключения темы с двумя иконками
        self.theme_button = QPushButton()
        self.theme_button.setIcon(QIcon(os.path.join(base_path, 'sun.svg')))
        self.theme_button.setIconSize(QSize(24, 24))
        self.theme_button.setFixedSize(40, 40)
        self.theme_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.theme_button.clicked.connect(self.toggle_theme)

        self.left_menu_layout.addWidget(self.menu_button, alignment=Qt.AlignHCenter)
        self.left_menu_layout.addStretch()
        self.left_menu_layout.addWidget(self.theme_button, alignment=Qt.AlignHCenter)

        # Sidebar (Toggleable)
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10)
        self.sidebar.setLayout(self.sidebar_layout)
        # self.sidebar.setFixedWidth(250)
        self.sidebar.setMaximumWidth(250)

        self.sidebar_animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_animation.setDuration(300)  # 300 мс на анимацию
        self.sidebar_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.sidebar_animation.finished.connect(self.on_sidebar_animation_finished)

        self.prompt_container = QWidget()
        self.prompt_layout = QHBoxLayout()
        self.prompt_layout.setContentsMargins(0, 0, 0, 0)
        self.prompt_layout.setSpacing(10)
        self.prompt_container.setLayout(self.prompt_layout)
        self.prompt_container.setStyleSheet("""
            background: transparent;
        """)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText('Enter your prompt here...')
        self.prompt_input.setFixedHeight(150)
        self.prompt_input.setFixedWidth(180)
        self.prompt_input.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: none;
                border-radius: 14;
                padding: 10px 10px;
                font-size: 16px;
            }
        """)

        self.run_button = QPushButton()
        self.run_button.setIcon(QIcon(os.path.join(base_path, 'play_button.svg')))
        self.run_button.setIconSize(QSize(32, 32))
        self.run_button.setFixedSize(40, 40)
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.run_button.clicked.connect(self.on_run)

        self.prompt_layout.addWidget(self.prompt_input, alignment=Qt.AlignTop)
        self.prompt_layout.addWidget(self.run_button, alignment=Qt.AlignTop)
        self.prompt_layout.addStretch()

        self.sidebar_layout.addWidget(self.prompt_container)
        self.sidebar_layout.addStretch()

        # Right Panel
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_panel.setLayout(self.right_layout)

        # Top Toolbar with actions
        self.toolbar_layout = QHBoxLayout()

        # Создание кнопок с иконками вместо текста
        self.save_button = QPushButton()
        self.save_button.setIcon(QIcon(os.path.join(base_path, 'save_icon.svg')))
        self.save_button.setIconSize(QSize(24, 24))
        self.save_button.clicked.connect(self.on_save)

        self.save_as_button = QPushButton()
        self.save_as_button.setIcon(QIcon(os.path.join(base_path, 'save_as_icon.svg')))
        self.save_as_button.setIconSize(QSize(24, 24))
        self.save_as_button.clicked.connect(self.on_save_as)

        self.undo_button = QPushButton()
        self.undo_button.setIcon(QIcon(os.path.join(base_path, 'undo_icon.svg')))
        self.undo_button.setIconSize(QSize(24, 24))
        self.undo_button.clicked.connect(self.on_undo)

        self.redo_button = QPushButton()
        self.redo_button.setIcon(QIcon(os.path.join(base_path, 'redo_icon.svg')))
        self.redo_button.setIconSize(QSize(24, 24))
        self.redo_button.clicked.connect(self.on_redo)

        # Общий стиль для всех кнопок панели
        toolbar_button_style = """
            QPushButton {
                background-color: white;
                border: none;
                border-radius: 20px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton::icon {
                color: black;
            }
        """

        self.toolbar_layout.addStretch()

        for button in [self.save_button, self.save_as_button, self.undo_button, self.redo_button]:
            button.setFixedSize(40, 40)
            button.setStyleSheet(toolbar_button_style)
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.toolbar_layout.addWidget(button)

        self.toggle_switch = ToggleSwitch()
        self.toggle_switch.toggled.connect(self.toggle_inline_view)

        self.toolbar_layout.addWidget(self.toggle_switch)

        # Editors
        self.editor_left = CustomTextEdit(is_left_editor=True)
        self.editor_right = CustomTextEdit(is_left_editor=False)

        self.highlighter_right = DiffHighlighter(
            self.editor_right.document(),
            self.editor_left.toPlainText().splitlines(),
            self.editor_right.toPlainText().splitlines(),
            mode='right'
        )
        self.highlighter_left = DiffHighlighter(
            self.editor_left.document(),
            self.editor_left.toPlainText().splitlines(),
            self.editor_right.toPlainText().splitlines(),
            mode='left'
        )

        self.editor_right.textChanged.connect(self.delayed_diff_highlight)
        self.editor_left.textChanged.connect(self.delayed_diff_highlight)

        self.editors_layout = QHBoxLayout()
        self.editors_layout.addWidget(self.editor_left)
        self.editors_layout.addWidget(self.editor_right)

        self.right_layout.addLayout(self.toolbar_layout)
        self.right_layout.addLayout(self.editors_layout)

        self.highlighter_left = PythonHighlighter(self.editor_left.document())
        self.highlighter_right = PythonHighlighter(self.editor_right.document())

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
        self.current_theme = 'light'  # по умолчанию

        self.apply_theme()

    def toggle_sidebar(self):
        if self.sidebar.maximumWidth() > 0:
            # Свернуть плавно
            self.sidebar_animation.stop()
            self.sidebar_animation.setStartValue(self.sidebar.width())
            self.sidebar_animation.setEndValue(0)
            self.sidebar_animation.start()
        else:
            # Развернуть плавно
            self.sidebar.setVisible(True)
            self.sidebar_animation.stop()
            self.sidebar_animation.setStartValue(self.sidebar.width())
            self.sidebar_animation.setEndValue(250)  # ширина развернутого sidebar
            self.sidebar_animation.start()

    def on_sidebar_animation_finished(self):
        if self.sidebar.maximumWidth() == 0:
            self.sidebar.setVisible(False)

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

        if not right_text.strip():
            # Если в правом поле ничего нет — очистить подсветку
            self.editor_left.set_diff_map({})
            self.editor_right.set_diff_map({})
            self.editor_left.unfold_all()
            self.editor_right.unfold_all()
            return

        # Иначе — пересчитать дифф
        self.highlighter_right.update_diff(left_text, right_text)
        self.highlighter_left.update_diff(left_text, right_text)

        self.editor_right.set_diff_map(self.highlighter_right.diff_map)
        self.editor_left.set_diff_map(self.highlighter_left.diff_map)

        modified_blocks = self.highlighter_right.get_modified_blocks()

        self.editor_left.unfold_all()  # без свёртки
        self.editor_right.unfold_all()
        self.editor_right.fold_unmodified_blocks(modified_blocks)

    def on_run(self):
        left_text = self.editor_left.toPlainText()
        lines = left_text.splitlines()

        if lines:
            # Выбираем случайный индекс строки для удаления
            remove_idx = random.randrange(len(lines))
            del lines[remove_idx]

        processed_lines = []
        for idx, line in enumerate(lines):
            # Каждая вторая строка (индексация с 0 -> строки 1, 3, 5 и т.д.)
            if (idx + 1) % 2 == 0:
                line = line[::-1]  # Переворачиваем строку

            processed_lines.append(line)

            # Каждая третья строка (после изменения порядка букв)
            if (idx + 1) % 6 == 0:
                processed_lines.append('')  # Добавляем пустую строку

        # Проверка, есть ли в оригинале пустая строка в конце
        if left_text and not left_text.endswith('\n'):
            processed_lines.append('')

        new_text = '\n'.join(processed_lines)

        def update_ui():
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
        if self.current_theme == 'light':
            # Градиентный фон
            self.central_widget.setStyleSheet("""
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #DAD7CD,
                    stop: 1 #344E41
                );
            """)

            # Полупрозрачный стеклянный эффект для панелей
            panel_style = """
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            """
            self.left_menu.setStyleSheet(panel_style)
            self.sidebar.setStyleSheet(panel_style)
            self.right_panel.setStyleSheet(panel_style)

            # Эффект размытия на панелях
            blur = QGraphicsBlurEffect()
            blur.setBlurRadius(10)

            self.central_widget.setGraphicsEffect(None)  # Главное окно без блюра
            self.left_menu.setGraphicsEffect(blur)
            self.sidebar.setGraphicsEffect(blur)
            self.right_panel.setGraphicsEffect(blur)

        else:  # dark theme
            self.central_widget.setStyleSheet('background-color: #212529;')
            self.left_menu.setStyleSheet('background-color: #343a40;')
            self.sidebar.setStyleSheet('background-color: #343a40;')
            self.right_panel.setStyleSheet('background-color: transparent;')

            # Убираем размытие в тёмной теме
            self.left_menu.setGraphicsEffect(None)
            self.sidebar.setGraphicsEffect(None)
            self.right_panel.setGraphicsEffect(None)

        self.editor_left.apply_editor_theme(self.current_theme)
        self.editor_right.apply_editor_theme(self.current_theme)

    def toggle_theme(self):
        if self.current_theme == 'light':
            self.current_theme = 'dark'
            self.theme_button.setIcon(QIcon(os.path.join(base_path, 'moon.svg')))
        else:
            self.current_theme = 'light'
            self.theme_button.setIcon(QIcon(os.path.join(base_path, 'sun.svg')))
        self.apply_theme()
