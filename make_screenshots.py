"""Делает скриншоты окон всех пяти программ в каталог screenshots/.

Tkinter-окна открываются на короткое время и снимаются через
PIL.ImageGrab по координатам окна; PyQt5-окна рендерятся в
offscreen-режиме через QWidget.grab() - на экране не появляются.

Запуск: python make_screenshots.py
"""

from __future__ import annotations

from pathlib import Path

OUT = Path("screenshots")
OUT.mkdir(exist_ok=True)


def shoot_tkinter(filename: str, build, prepare=None) -> None:
    """Открывает Tkinter-окно, снимает его область экрана."""
    import ctypes
    import tkinter as tk
    from PIL import ImageGrab

    ctypes.windll.user32.SetProcessDPIAware()
    root = tk.Tk()
    app = build(root)
    if prepare is not None:
        prepare(app)
    root.update_idletasks()
    root.geometry("+200+200")
    root.deiconify()
    root.lift()
    root.attributes("-topmost", True)
    root.focus_force()
    # Даём оконному менеджеру время реально нарисовать окно.
    for _ in range(20):
        root.update()
        ctypes.windll.kernel32.Sleep(25)
    root.update_idletasks()
    x, y = root.winfo_rootx(), root.winfo_rooty()
    width = root.winfo_width()
    height = root.winfo_height()
    image = ImageGrab.grab(bbox=(x, y, x + width, y + height))
    image.save(OUT / filename)
    root.destroy()
    print(f"  {filename}: {width}x{height}")


def shoot_pyqt(filename: str, window, app) -> None:
    """Снимает PyQt-окно через Win32 PrintWindow (без фокуса)."""
    import ctypes
    import time

    import win32con
    import win32gui
    import win32ui
    from PIL import Image

    window.show()
    for _ in range(20):
        app.processEvents()
        time.sleep(0.025)
    hwnd = int(window.winId())
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    width, height = right - left, bottom - top
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    src_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    mem_dc = src_dc.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(src_dc, width, height)
    mem_dc.SelectObject(bitmap)
    result = ctypes.windll.user32.PrintWindow(
        hwnd, mem_dc.GetSafeHdc(), 2)
    if result != 1:
        mem_dc.BitBlt((0, 0), (width, height), src_dc, (0, 0),
                      win32con.SRCCOPY)
    info = bitmap.GetInfo()
    bits = bitmap.GetBitmapBits(True)
    image = Image.frombuffer(
        "RGB", (info["bmWidth"], info["bmHeight"]), bits,
        "raw", "BGRX", 0, 1)
    image.save(OUT / filename)
    win32gui.DeleteObject(bitmap.GetHandle())
    mem_dc.DeleteDC()
    src_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)
    window.close()
    print(f"  {filename}: {width}x{height}")


def main() -> None:
    """Снимает все пять окон."""
    import ctypes

    ctypes.windll.user32.SetProcessDPIAware()

    from task04_listbox import ListboxApp
    from task05_timer_stopwatch import StopwatchApp
    from task06_progressbar import ProgressbarApp
    from task09_pyqt_table import StudentTableWindow
    from task10_pyqt_hello import GreeterWindow

    print("Tkinter-окна (кратковременно появятся на экране):")

    def prepare_listbox(app: ListboxApp) -> None:
        app.listbox.selection_set(0)
        app.show_selection()

    shoot_tkinter("task04_listbox.png", ListboxApp, prepare_listbox)
    shoot_tkinter("task05_stopwatch.png", StopwatchApp)

    def prepare_progress(app: ProgressbarApp) -> None:
        app.model.start()
        app.model.tick(65)
        app.model.pause()
        app.refresh()

    shoot_tkinter("task06_progressbar.png", ProgressbarApp,
                  prepare_progress)

    print("PyQt5-окна (тоже кратковременно появятся на экране):")
    from PyQt5.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])

    greeter = GreeterWindow()
    greeter.name_edit.setText("Ярослав")
    greeter.greet()
    greeter.resize(420, 220)
    shoot_pyqt("task10_pyqt_hello.png", greeter, app)
    shoot_pyqt("task09_pyqt_table.png", StudentTableWindow(), app)
    print("Готово: 5 скриншотов в", OUT)


if __name__ == "__main__":
    main()
