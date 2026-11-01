"""Задание 9 (повышенная сложность): приложение PyQt с таблицей.

QTableWidget со списком студентов: добавление записи, удаление
выбранной строки, сортировка по столбцам, средний балл группы.
Данные и расчёты вынесены в StudentTableModel - тестируются без GUI.

Запуск: python task09_pyqt_table.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from operator import attrgetter

from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

COLUMNS = ["ФИО", "Группа", "Оценка"]


@dataclass
class StudentRow:
    """Одна строка таблицы: ФИО, группа, оценка."""

    full_name: str
    group: str
    grade: int


class StudentTableModel:
    """Модель таблицы студентов: добавление, удаление, статистика."""

    def __init__(self, rows: list[StudentRow] | None = None) -> None:
        self.rows = list(rows or [])

    def add(self, full_name: str, group: str, grade: int) -> StudentRow:
        """Добавляет строку после валидации полей."""
        name = full_name.strip()
        group_name = group.strip()
        if not name:
            raise ValueError("ФИО не может быть пустым")
        if not group_name:
            raise ValueError("группа не может быть пустой")
        if not 2 <= grade <= 5:
            raise ValueError("оценка должна быть от 2 до 5")
        row = StudentRow(name, group_name, grade)
        self.rows.append(row)
        return row

    def remove(self, index: int) -> StudentRow:
        """Удаляет строку по индексу."""
        if not 0 <= index < len(self.rows):
            raise IndexError(f"нет строки с индексом {index}")
        return self.rows.pop(index)

    def average_grade(self) -> float | None:
        """Средний балл по таблице или None, если строк нет."""
        if not self.rows:
            return None
        return sum(row.grade for row in self.rows) / len(self.rows)

    def sorted_rows(self, column: int,
                    reverse: bool = False) -> list[StudentRow]:
        """Возвращает строки, отсортированные по столбцу 0..2."""
        if column == 2:
            key = attrgetter("grade")
        elif column == 1:
            key = attrgetter("group")
        elif column == 0:
            key = attrgetter("full_name")
        else:
            raise IndexError(f"нет столбца с индексом {column}")
        return sorted(self.rows, key=key, reverse=reverse)


class StudentTableWindow(QMainWindow):
    """Главное окно: таблица студентов и панель добавления."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Задание 9 - Таблица студентов")
        self.setMinimumSize(560, 420)
        self.model = StudentTableModel()
        for row in [StudentRow("Полошков Ярослав Витальевич",
                               "220042-11", 5),
                    StudentRow("Иванов Иван Иванович", "220042-11", 4),
                    StudentRow("Петрова Анна Сергеевна", "221341", 5)]:
            self.model.rows.append(row)

        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        form = QHBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("ФИО")
        self.group_edit = QLineEdit()
        self.group_edit.setPlaceholderText("Группа")
        self.grade_spin = QSpinBox()
        self.grade_spin.setRange(2, 5)
        form.addWidget(self.name_edit)
        form.addWidget(self.group_edit)
        form.addWidget(self.grade_spin)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        add_button = QPushButton("Добавить")
        add_button.clicked.connect(self.add_row)
        remove_button = QPushButton("Удалить выбранную")
        remove_button.clicked.connect(self.remove_selected)
        buttons.addWidget(add_button)
        buttons.addWidget(remove_button)
        layout.addLayout(buttons)

        self.stats_label = QLabel()
        layout.addWidget(self.stats_label)
        self.reload()

    def reload(self) -> None:
        """Перерисовывает таблицу по модели и обновляет статистику."""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.model.rows))
        for index, row in enumerate(self.model.rows):
            values = [row.full_name, row.group, str(row.grade)]
            for column, text in enumerate(values):
                item = QTableWidgetItem(text)
                self.table.setItem(index, column, item)
        self.table.setSortingEnabled(True)
        average = self.model.average_grade()
        text = (f"Записей: {len(self.model.rows)}; средний балл: "
                + (f"{average:.2f}" if average is not None else "нет"))
        self.stats_label.setText(text)

    def add_row(self) -> None:
        """Добавляет студента из полей ввода."""
        try:
            self.model.add(self.name_edit.text(), self.group_edit.text(),
                           self.grade_spin.value())
        except ValueError as error:
            QMessageBox.warning(self, "Добавление", str(error))
            return
        self.name_edit.clear()
        self.group_edit.clear()
        self.reload()

    def remove_selected(self) -> None:
        """Удаляет выбранную строку таблицы."""
        row = self.table.currentRow()
        if row < 0 or row >= len(self.model.rows):
            QMessageBox.information(self, "Удаление",
                                    "Сначала выберите строку")
            return
        name_item = self.table.item(row, 0)
        full_name = name_item.text() if name_item else ""
        index = next((i for i, item in enumerate(self.model.rows)
                      if item.full_name == full_name), None)
        if index is None:
            return
        self.model.remove(index)
        self.reload()


def main() -> None:
    """Точка входа: QApplication, окно, цикл событий."""
    app = QApplication(sys.argv)
    window = StudentTableWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
