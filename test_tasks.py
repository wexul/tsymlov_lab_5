"""Модульные тесты всех заданий лабораторной №5 (unittest).

Логика моделей проверяется без окон; GUI-тесты: Tkinter - на скрытом
окне (withdraw), PyQt5 - в offscreen-режиме, поэтому тесты не
мелькают окнами и не требуют действий пользователя.

Запуск: python -m unittest -v
"""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from task04_listbox import ItemListModel  # noqa: E402
from task05_timer_stopwatch import (  # noqa: E402
    StopwatchModel,
    format_elapsed,
)
from task06_progressbar import ProgressModel  # noqa: E402
from task09_pyqt_table import StudentRow, StudentTableModel  # noqa: E402
from task10_pyqt_hello import make_greeting  # noqa: E402


class TestItemListModel(unittest.TestCase):
    """Задание 4: модель списка для Listbox."""

    def test_add_and_get(self) -> None:
        model = ItemListModel()
        model.add("  Математика  ")
        self.assertEqual(model.items, ["Математика"])
        self.assertEqual(model.get(0), "Математика")

    def test_empty_and_duplicate_rejected(self) -> None:
        model = ItemListModel(["Физика"])
        with self.assertRaises(ValueError):
            model.add("   ")
        with self.assertRaises(ValueError):
            model.add("Физика")

    def test_remove(self) -> None:
        model = ItemListModel(["A", "B"])
        self.assertEqual(model.remove(0), "A")
        self.assertEqual(model.items, ["B"])
        with self.assertRaises(IndexError):
            model.remove(5)
        with self.assertRaises(IndexError):
            model.get(-1)


class TestProgressModel(unittest.TestCase):
    """Задание 6: модель прогресса."""

    def test_ticks_to_completion(self) -> None:
        model = ProgressModel()
        model.start()
        for _ in range(100):
            model.tick()
        self.assertEqual(model.value, 100)
        self.assertFalse(model.running)

    def test_pause_keeps_value(self) -> None:
        model = ProgressModel()
        model.start()
        model.tick(30)
        model.pause()
        model.tick(30)
        self.assertEqual(model.value, 30)

    def test_reset(self) -> None:
        model = ProgressModel()
        model.start()
        model.tick(50)
        model.reset()
        self.assertEqual(model.value, 0)
        self.assertFalse(model.running)

    def test_restart_after_completion(self) -> None:
        model = ProgressModel()
        model.start()
        model.tick(100)
        model.start()
        self.assertEqual(model.value, 0)
        self.assertTrue(model.running)

    def test_invalid_maximum(self) -> None:
        with self.assertRaises(ValueError):
            ProgressModel(0)


class TestStopwatchModel(unittest.TestCase):
    """Задание 5 (повышенная): логика секундомера."""

    def make_model(self) -> tuple[StopwatchModel, list[float]]:
        moments = [0.0]
        model = StopwatchModel(clock=lambda: moments[0])
        return model, moments

    def test_format_elapsed(self) -> None:
        self.assertEqual(format_elapsed(0), "00:00.0")
        self.assertEqual(format_elapsed(59.99), "00:59.9")
        self.assertEqual(format_elapsed(61.25), "01:01.2")
        self.assertEqual(format_elapsed(600), "10:00.0")
        with self.assertRaises(ValueError):
            format_elapsed(-1)

    def test_start_elapsed_pause(self) -> None:
        model, moments = self.make_model()
        model.start()
        moments[0] = 5.5
        self.assertAlmostEqual(model.elapsed(), 5.5)
        model.pause()
        moments[0] = 100.0
        self.assertAlmostEqual(model.elapsed(), 5.5)

    def test_resume_accumulates(self) -> None:
        model, moments = self.make_model()
        model.start()
        moments[0] = 5.0
        model.pause()
        moments[0] = 10.0
        model.start()
        moments[0] = 12.0
        self.assertAlmostEqual(model.elapsed(), 7.0)

    def test_double_start_is_noop(self) -> None:
        model, moments = self.make_model()
        model.start()
        moments[0] = 3.0
        model.start()
        moments[0] = 4.0
        self.assertAlmostEqual(model.elapsed(), 4.0)

    def test_laps_and_reset(self) -> None:
        model, moments = self.make_model()
        model.start()
        moments[0] = 2.0
        model.lap()
        moments[0] = 5.0
        model.lap()
        self.assertEqual(model.laps, [2.0, 5.0])
        model.reset()
        self.assertEqual(model.elapsed(), 0.0)
        self.assertEqual(model.laps, [])
        self.assertFalse(model.running)


class TestGreeting(unittest.TestCase):
    """Задание 10: логика приветствия."""

    def test_greeting(self) -> None:
        self.assertIn("Привет, Ярослав!", make_greeting(" Ярослав "))

    def test_empty_name(self) -> None:
        self.assertIn("Введите имя", make_greeting("   "))


class TestStudentTableModel(unittest.TestCase):
    """Задание 9 (повышенная): модель таблицы студентов."""

    def make_model(self) -> StudentTableModel:
        return StudentTableModel([
            StudentRow("Борисов Борис", "221341", 4),
            StudentRow("Андреев Андрей", "220042-11", 5),
        ])

    def test_add_validates(self) -> None:
        model = StudentTableModel()
        model.add(" Иванов Иван ", " 220042-11 ", 5)
        self.assertEqual(model.rows[0].full_name, "Иванов Иван")
        for args in [("", "Г", 5), ("Иванов", "", 5), ("Иванов", "Г", 6)]:
            with self.assertRaises(ValueError):
                model.add(*args)

    def test_remove(self) -> None:
        model = self.make_model()
        model.remove(0)
        self.assertEqual(len(model.rows), 1)
        with self.assertRaises(IndexError):
            model.remove(10)

    def test_average(self) -> None:
        self.assertAlmostEqual(self.make_model().average_grade(), 4.5)
        self.assertIsNone(StudentTableModel().average_grade())

    def test_sorting(self) -> None:
        model = self.make_model()
        by_name = model.sorted_rows(0)
        self.assertEqual(by_name[0].full_name, "Андреев Андрей")
        by_grade = model.sorted_rows(2, reverse=True)
        self.assertEqual(by_grade[0].grade, 5)
        with self.assertRaises(IndexError):
            model.sorted_rows(7)


class TestTkinterGui(unittest.TestCase):
    """Smoke-тесты Tkinter-окон на скрытом root."""

    def setUp(self) -> None:
        import tkinter as tk
        try:
            self.root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"нет графического окружения: {error}")
        self.root.withdraw()

    def tearDown(self) -> None:
        self.root.destroy()

    def test_listbox_app(self) -> None:
        from task04_listbox import ListboxApp
        app = ListboxApp(self.root)
        self.assertEqual(app.listbox.size(), 5)
        app.listbox.selection_set(0)
        app.show_selection()
        self.assertIn("Методы", app.selection_var.get())
        app.remove_selected()
        self.assertEqual(app.listbox.size(), 4)

    def test_progressbar_app(self) -> None:
        from task06_progressbar import ProgressbarApp
        app = ProgressbarApp(self.root)
        app.start()
        self.assertTrue(app.model.running)
        app.on_tick()
        self.assertGreater(app.model.value, 0)
        app.pause()
        self.assertFalse(app.model.running)
        app.reset()
        self.assertEqual(app.bar["value"], 0)

    def test_stopwatch_app(self) -> None:
        from task05_timer_stopwatch import StopwatchApp
        app = StopwatchApp(self.root)
        app.start()
        self.assertTrue(app.model.running)
        app.lap()
        self.assertEqual(app.laps_list.size(), 1)
        app.pause()
        app.reset()
        self.assertEqual(app.time_var.get(), "00:00.0")
        self.assertEqual(app.laps_list.size(), 0)


class TestPyQtGui(unittest.TestCase):
    """Smoke-тесты PyQt5-окон в offscreen-режиме."""

    @classmethod
    def setUpClass(cls) -> None:
        from PyQt5.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def test_greeter_window(self) -> None:
        from task10_pyqt_hello import GreeterWindow
        window = GreeterWindow()
        window.name_edit.setText("Ярослав")
        window.greet()
        self.assertIn("Привет, Ярослав!", window.result_label.text())
        window.close()

    def test_table_window(self) -> None:
        from task09_pyqt_table import StudentTableWindow
        window = StudentTableWindow()
        self.assertEqual(window.table.rowCount(), 3)
        window.name_edit.setText("Сидоров Сидор")
        window.group_edit.setText("220042-11")
        window.add_row()
        self.assertEqual(window.table.rowCount(), 4)
        self.assertIn("Записей: 4", window.stats_label.text())
        window.table.selectRow(3)
        window.remove_selected()
        self.assertEqual(window.table.rowCount(), 3)
        window.close()


if __name__ == "__main__":
    unittest.main()
