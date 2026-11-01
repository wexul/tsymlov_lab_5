"""Задание 10 (средняя сложность): простейший GUI на PyQt5.

Окно QApplication с QLineEdit, QPushButton и QLabel: вводишь имя -
получаешь приветствие. Логика приветствия вынесена в make_greeting(),
поэтому проверяется тестами без запуска окон.

Запуск: python task10_pyqt_hello.py
"""

from __future__ import annotations

import sys

from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def make_greeting(name: str) -> str:
    """Возвращает приветствие; пустое имя - подсказка."""
    clean = name.strip()
    if not clean:
        return "Введите имя в поле выше."
    return f"Привет, {clean}! Это простейший GUI на PyQt5."


class GreeterWindow(QMainWindow):
    """Главное окно приложения-приветствия."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Задание 10 - PyQt5")
        self.setMinimumWidth(380)

        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        layout.addWidget(QLabel("Как вас зовут?"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Имя")
        layout.addWidget(self.name_edit)

        self.greet_button = QPushButton("Поздороваться")
        self.greet_button.clicked.connect(self.greet)
        layout.addWidget(self.greet_button)

        self.result_label = QLabel("Нажмите кнопку после ввода имени.")
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

        self.name_edit.returnPressed.connect(self.greet)

    def greet(self) -> None:
        """Обновляет метку приветствием по тексту из поля."""
        self.result_label.setText(make_greeting(self.name_edit.text()))


def main() -> None:
    """Точка входа: QApplication, окно, цикл событий."""
    app = QApplication(sys.argv)
    window = GreeterWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
