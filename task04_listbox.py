"""Задание 4 (средняя сложность): список (Listbox) и выбор элемента.

Tkinter-приложение «Список дисциплин»: Listbox с прокруткой, поле для
добавления своего пункта, кнопки «Показать выбранное», «Добавить»,
«Удалить». Логика работы со списком вынесена в ItemListModel - её
тесты не требуют графического окружения.

Запуск: python task04_listbox.py
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

DEFAULT_ITEMS = [
    "Методы и технологии программирования",
    "Базы данных",
    "Операционные системы",
    "Математический анализ",
    "Архитектура ЭВМ",
]


class ItemListModel:
    """Модель списка: добавление, удаление, выбор без дубликатов."""

    def __init__(self, items: list[str] | None = None) -> None:
        self._items = list(items or [])

    @property
    def items(self) -> list[str]:
        """Текущие элементы списка (копия)."""
        return list(self._items)

    def add(self, text: str) -> str:
        """Добавляет непустой уникальный пункт, возвращает его."""
        item = text.strip()
        if not item:
            raise ValueError("пункт не может быть пустым")
        if item in self._items:
            raise ValueError(f"пункт «{item}» уже есть в списке")
        self._items.append(item)
        return item

    def remove(self, index: int) -> str:
        """Удаляет пункт по индексу, возвращает его текст."""
        if not 0 <= index < len(self._items):
            raise IndexError(f"нет пункта с индексом {index}")
        return self._items.pop(index)

    def get(self, index: int) -> str:
        """Возвращает пункт по индексу."""
        if not 0 <= index < len(self._items):
            raise IndexError(f"нет пункта с индексом {index}")
        return self._items[index]


class ListboxApp:
    """GUI задания 4: Listbox + выбор элемента."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.model = ItemListModel(DEFAULT_ITEMS)
        root.title("Задание 4 - Listbox")
        root.minsize(420, 300)

        main = ttk.Frame(root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        frame = ttk.Frame(main)
        frame.pack(fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(frame, activestyle="dotbox")
        scrollbar = ttk.Scrollbar(frame, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.selection_var = tk.StringVar(value="Ничего не выбрано")
        ttk.Label(main, textvariable=self.selection_var,
                  foreground="#005a9e").pack(anchor=tk.W, pady=(8, 0))

        entry_row = ttk.Frame(main)
        entry_row.pack(fill=tk.X, pady=8)
        self.entry = ttk.Entry(entry_row)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(entry_row, text="Добавить",
                   command=self.add_item).pack(side=tk.LEFT, padx=(6, 0))

        buttons = ttk.Frame(main)
        buttons.pack()
        ttk.Button(buttons, text="Показать выбранное",
                   command=self.show_selection).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Удалить выбранное",
                   command=self.remove_selected).pack(side=tk.LEFT, padx=4)

        self.refresh()
        self.entry.bind("<Return>", lambda event: self.add_item())

    def refresh(self) -> None:
        """Перерисовывает Listbox по модели."""
        self.listbox.delete(0, tk.END)
        for item in self.model.items:
            self.listbox.insert(tk.END, item)

    def show_selection(self) -> None:
        """Показывает выбранный элемент Listbox."""
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showinfo("Выбор", "Сначала выделите пункт списка")
            return
        self.selection_var.set(f"Выбрано: {self.model.get(selected[0])}")

    def add_item(self) -> None:
        """Добавляет пункт из поля ввода."""
        try:
            item = self.model.add(self.entry.get())
        except ValueError as error:
            messagebox.showwarning("Добавление", str(error))
            return
        self.entry.delete(0, tk.END)
        self.refresh()
        self.selection_var.set(f"Добавлено: {item}")

    def remove_selected(self) -> None:
        """Удаляет выделенный пункт."""
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showinfo("Удаление", "Сначала выделите пункт")
            return
        item = self.model.remove(selected[0])
        self.refresh()
        self.selection_var.set(f"Удалено: {item}")


def main() -> None:
    """Точка входа: создаёт окно и запускает mainloop."""
    root = tk.Tk()
    ListboxApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
