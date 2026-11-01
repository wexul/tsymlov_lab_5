"""Собирает demo_output.txt: тесты, flake8 и съёмка скриншотов окон."""

import datetime
import subprocess

SEP = "-" * 70
out = []
out.append("Лабораторная работа №5, вариант 4 - протокол проверки")
out.append("=" * 70)
out.append("")
out.append("Дата выполнения: " + datetime.date.today().strftime("%d.%m.%Y"))
out.append("Python: 3.11.1, Tkinter 8.6, PyQt5 (Qt 5.15.2)")
out.append("ОС: Windows 10")
out.append("")
out.append("GUI-программы интерактивны, поэтому вместо текстового вывода")
out.append("каждое окно снято на скриншот (каталог screenshots/, скрипт")
out.append("make_screenshots.py). Ниже - фактический вывод модульных")
out.append("тестов (включая GUI smoke-тесты), проверки стиля и съёмки.")
out.append("")


def run(title, cmd):
    res = subprocess.run(cmd, capture_output=True, text=True,
                         encoding="utf-8")
    out.append(SEP)
    out.append(title)
    out.append(SEP)
    out.append("$ " + " ".join(cmd))
    out.append("")
    if res.stdout.strip():
        out.append(res.stdout.rstrip("\n"))
    if res.stderr.strip():
        out.append(res.stderr.rstrip("\n"))
    out.append("")
    out.append(f"код возврата: {res.returncode}")
    out.append("")


run("Модульные тесты: модели + GUI smoke (Tkinter и PyQt5)",
    ["py", "-3", "-m", "unittest", "-v"])
run("Проверка стиля кода (flake8)",
    ["py", "-3", "-m", "flake8", ".", "--statistics"])
run("Съёмка скриншотов всех пяти окон",
    ["py", "-3", "make_screenshots.py"])

with open("demo_output.txt", "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(out).rstrip("\n") + "\n")
print("demo_output.txt записан, строк:", len(out))
