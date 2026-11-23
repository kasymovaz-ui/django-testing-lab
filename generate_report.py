
import os
import django
import re
from datetime import datetime
from io import StringIO

from django.core.management import call_command
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH


# Django initialization
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


# Run tests and collect results
output = StringIO()

print("Running Django tests...")

failures = call_command(
    'test',
    'accounts',
    verbosity=2,
    stdout=output,
    stderr=output
)

test_results = output.getvalue()

# Create Word document
doc = Document()

section = doc.sections[0]
section.top_margin = Cm(2)
section.bottom_margin = Cm(2)
section.left_margin = Cm(2.5)
section.right_margin = Cm(2)

style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(12)

# Title
title = doc.add_heading('ОТЧЁТ ПО ЛАБОРАТОРНОЙ РАБОТЕ', 1)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

subtitle = doc.add_paragraph(
    'Тестирование Django-приложения'
)
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph(
    f'Дата выполнения: {datetime.now().strftime("%d.%m.%Y %H:%M")}'
)

doc.add_heading('1. Цель работы', level=2)
doc.add_paragraph(
    'Реализация регистрации пользователей, авторизации '
    'с использованием CAPTCHA, личного кабинета и '
    'автоматизированного тестирования приложения Django.'
)

doc.add_heading('2. Выполненные проверки', level=2)

tests = [
    'Открытие страницы регистрации',
    'Успешная регистрация пользователя',
    'Открытие страницы авторизации',
    'Авторизация с правильной CAPTCHA',
    'Авторизация с неправильной CAPTCHA',
    'Авторизация без CAPTCHA',
    'Авторизация с неправильным паролем',
    'Защита личного кабинета от неавторизованных пользователей',
    'Доступ к личному кабинету авторизованного пользователя',
    'Выход из аккаунта'
]

for test in tests:
    doc.add_paragraph(test, style='List Number')

doc.add_heading('3. Результаты автоматического тестирования', level=2)

match = re.search(r'Ran (\d+) tests?', test_results)

if match:
    total_tests = int(match.group(1))
else:
    total_tests = 0

if failures == 0 and total_tests > 0:
    status = 'ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО'
else:
    status = 'ОБНАРУЖЕНЫ ОШИБКИ'

doc.add_paragraph(f'Количество тестов: {total_tests}')
doc.add_paragraph(f'Количество ошибок: {failures}')
doc.add_paragraph(f'Результат: {status}')

doc.add_heading('4. Полный вывод Django Test Runner', level=2)

for line in test_results.splitlines():
    paragraph = doc.add_paragraph()
    run = paragraph.add_run(line)
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

doc.add_heading('5. Заключение', level=2)

doc.add_paragraph(
    'В ходе лабораторной работы было реализовано Django-приложение '
    'с регистрацией, авторизацией с CAPTCHA и личным кабинетом. '
    'Для проверки функциональности были разработаны автоматические '
    'тесты. Результаты тестирования сохранены в документ Word.'
)

# Save report
filename = 'Test_Report_Django_Lab.docx'
doc.save(filename)

print(f'\nWord report saved: {filename}')
print(f'Tests: {total_tests}')
print(f'Failures: {failures}')
print(f'Status: {status}')
