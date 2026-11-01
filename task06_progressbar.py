"""Задание 6 (средняя сложность): прогрессбар.

Tkinter-приложение с ttk.Progressbar: кнопки «Старт», «Пауза»,
«Сброс», имитация длительной операции через after() без блокировки
цикла событий. Логика счёта вынесена в ProgressModel.

Запуск: python task06_progressbar.py
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

TICK_MS = 50
STEP_PERCENT = 1


class ProgressModel:
    """Модель прогресса 0..100 с паузой и сбросом."""

    def __init__(self, maximum: int = 100) -> None:
        if maximum < 1:
            raise ValueError("maximum должен быть положительным")
        self.maximum = maximum
        self.value = 0
        self.running = False

    def start(self) -> None:
        """Запускает или продолжает отсчёт."""
        if self.value >= self.maximum:
            self.value = 0
        self.running = True

    def pause(self) -> None:
        """Ставит отсчёт на паузу."""
        self.running = False

    def reset(self) -> None:
        """Останавливает и обнуляет прогресс."""
        self.running = False
        self.value = 0

    def tick(self, step: int = STEP_PERCENT) -> int:
        """Продвигает прогресс на шаг; 100% останавливает отсчёт."""
        if self.running:
            self.value = min(self.value + step, self.maximum)
            if self.value >= self.maximum:
                self.running = False
        return self.value


class ProgressbarApp:
    """GUI задания 6: прогрессбар с управлением."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.model = ProgressModel()
        root.title("Задание 6 - Прогрессбар")
        root.minsize(380, 150)

        main = ttk.Frame(root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main, text="Имитация длительной операции:").pack(
            anchor=tk.W)
        self.bar = ttk.Progressbar(main, maximum=self.model.maximum,
                                   length=340)
        self.bar.pack(fill=tk.X, pady=8)
        self.status_var = tk.StringVar(value="Готово к запуску")
        ttk.Label(main, textvariable=self.status_var).pack(anchor=tk.W)

        buttons = ttk.Frame(main)
        buttons.pack(pady=(10, 0))
        ttk.Button(buttons, text="Старт",
                   command=self.start).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Пауза",
                   command=self.pause).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Сброс",
                   command=self.reset).pack(side=tk.LEFT, padx=4)

        self._job: str | None = None
        self.refresh()

    def refresh(self) -> None:
        """Обновляет виджеты по состоянию модели."""
        self.bar["value"] = self.model.value
        if self.model.value >= self.model.maximum:
            self.status_var.set("Завершено: 100%")
        elif self.model.running:
            self.status_var.set(f"Выполняется: {self.model.value}%")
        else:
            self.status_var.set(f"Пауза: {self.model.value}%")

    def start(self) -> None:
        """Запускает отсчёт и таймер after()."""
        self.model.start()
        self.refresh()
        if self._job is None:
            self._job = self.root.after(TICK_MS, self.on_tick)

    def pause(self) -> None:
        """Останавливает таймер, сохраняя прогресс."""
        self.model.pause()
        self.cancel_job()
        self.refresh()

    def reset(self) -> None:
        """Сбрасывает прогресс."""
        self.model.reset()
        self.cancel_job()
        self.refresh()
        self.status_var.set("Готово к запуску")

    def cancel_job(self) -> None:
        """Отменяет pending-вызов after(), если он есть."""
        if self._job is not None:
            self.root.after_cancel(self._job)
            self._job = None

    def on_tick(self) -> None:
        """Обработчик таймера: шаг модели и перерисовка."""
        self._job = None
        self.model.tick()
        self.refresh()
        if self.model.running:
            self._job = self.root.after(TICK_MS, self.on_tick)


def main() -> None:
    """Точка входа: создаёт окно и запускает mainloop."""
    root = tk.Tk()
    ProgressbarApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
