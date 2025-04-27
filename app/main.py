import sys

from PySide6.QtWidgets import QApplication

from app.views.main_window import MainWindow
from app.views.splash_screen import SplashScreen

if __name__ == '__main__':
    app = QApplication(sys.argv)

    splash = SplashScreen()
    splash.show()

    main_window = MainWindow()
    main_window.hide()

    def show_main_window():
        splash.close()
        main_window.show()

    splash.start_sequence(show_main_window)

    sys.exit(app.exec())
