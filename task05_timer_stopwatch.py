"""Задание 5 (повышенная сложность): программа таймер/секундомер.

Tkinter-секундомер с точностью до десятых долей секунды: «Старт»,
«Пауза», «Сброс», «Круг» (отсечки). Время отсчитывается по монотонным
часам time.monotonic(), а не по числу срабатываний after(), поэтому
не плавает при подвисаниях GUI. StopwatchModel - чистая логика с
инъекцией часов, тестируется без окон.

Запуск: python task05_timer_stopwatch.py
"""

from __future__ import annotations

import time
import tkinter as tk
from tkinter import ttk
from typing import Callable

REFRESH_MS = 100


def format_elapsed(seconds: float) -> str:
    """Форматирует секунды как ММ:СС.Д (десятые доли)."""
    if seconds < 0:
        raise ValueError("время не может быть отрицательным")
    tenths = int(seconds * 10)
    minutes, rest = divmod(tenths, 600)
    whole_seconds, tenth = divmod(rest, 10)
    return f"{minutes:02d}:{whole_seconds:02d}.{tenth}"


class StopwatchModel:
    """Логика секундомера: старт, пауза, сброс, круги."""

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        self._clock = clock or time.monotonic
        self._accumulated = 0.0
        self._started_at: float | None = None
        self.laps: list[float] = []

    @property
    def running(self) -> bool:
        """True, если секундомер идёт."""
        return self._started_at is not None

    def elapsed(self) -> float:
        """Полное время: накопленное + текущий отрезок."""
        total = self._accumulated
        if self._started_at is not None:
            total += self._clock() - self._started_at
        return total

    def start(self) -> None:
        """Запускает или продолжает отсчёт (повторный старт - no-op)."""
        if self._started_at is None:
            self._started_at = self._clock()

    def pause(self) -> float:
        """Останавливает отсчёт, возвращает накопленное время."""
        if self._started_at is not None:
            self._accumulated += self._clock() - self._started_at
            self._started_at = None
        return self._accumulated

    def reset(self) -> None:
        """Обнуляет время и список кругов."""
        self._accumulated = 0.0
        self._started_at = None
        self.laps.clear()

    def lap(self) -> float:
        """Фиксирует отсечку, возвращает её время."""
        current = self.elapsed()
        self.laps.append(current)
        return current


class StopwatchApp:
    """GUI задания 5: секундомер с кругами."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.model = StopwatchModel()
        root.title("Задание 5 - Секундомер")
        root.minsize(320, 300)

        main = ttk.Frame(root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)
        self.time_var = tk.StringVar(value=format_elapsed(0))
        ttk.Label(main, textvariable=self.time_var,
                  font=("Consolas", 36)).pack()
        self.state_var = tk.StringVar(value="Остановлен")
        ttk.Label(main, textvariable=self.state_var).pack()

        buttons = ttk.Frame(main)
        buttons.pack(pady=8)
        ttk.Button(buttons, text="Старт",
                   command=self.start).grid(row=0, column=0, padx=4)
        ttk.Button(buttons, text="Пауза",
                   command=self.pause).grid(row=0, column=1, padx=4)
        ttk.Button(buttons, text="Круг",
                   command=self.lap).grid(row=0, column=2, padx=4)
        ttk.Button(buttons, text="Сброс",
                   command=self.reset).grid(row=0, column=3, padx=4)

        self.laps_list = tk.Listbox(main, height=6)
        self.laps_list.pack(fill=tk.BOTH, expand=True)

        self._running_after = False

    def refresh(self) -> None:
        """Обновляет табло и состояние."""
        self.time_var.set(format_elapsed(self.model.elapsed()))
        self.state_var.set("Идёт отсчёт" if self.model.running
                           else "Остановлен")

    def start(self) -> None:
        """Запускает секундомер и обновление табло."""
        self.model.start()
        self.refresh()
        if not self._running_after:
            self._running_after = True
            self.root.after(REFRESH_MS, self.on_tick)

    def pause(self) -> None:
        """Ставит секундомер на паузу."""
        self.model.pause()
        self._running_after = False
        self.refresh()

    def reset(self) -> None:
        """Сбрасывает секундомер и отсечки."""
        self.model.reset()
        self._running_after = False
        self.laps_list.delete(0, tk.END)
        self.refresh()

    def lap(self) -> None:
        """Добавляет отсечку в список."""
        value = self.model.lap()
        self.laps_list.insert(
            tk.END, f"Круг {len(self.model.laps)}: "
                    f"{format_elapsed(value)}")

    def on_tick(self) -> None:
        """Периодическое обновление табло."""
        self.refresh()
        if self._running_after:
            self.root.after(REFRESH_MS, self.on_tick)


def main() -> None:
    """Точка входа: создаёт окно и запускает mainloop."""
    root = tk.Tk()
    StopwatchApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
