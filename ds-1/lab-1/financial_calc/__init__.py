import math
import re
from decimal import Decimal
from typing import Union

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox
from PyQt5.QtCore import Qt, QSize


class ParseError(Exception):
    pass


class FinancialCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Финансовый калькулятор")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QGridLayout()
        self.setFixedSize(QSize(700, 200))

        # Add an informative text label
        info_label = QLabel("Самосюк Екатерина Александровна. 4 курс, 4 группа (КТС). 2023 год.")
        info_label.setAlignment(Qt.AlignCenter)  # Center the text
        self.layout.addWidget(info_label, 0, 1, 1, 4)  # Span two columns

        # Add input fields and labels in line
        self.value1_label = QLabel("Значение 1:")
        self.value1_input = QLineEdit()
        self.layout.addWidget(self.value1_label, 1, 0)
        self.layout.addWidget(self.value1_input, 1, 1)

        self.operation_dropdown = QComboBox()
        self.operation_dropdown.addItems(["+", "-", "*", "/"])
        self.layout.addWidget(self.operation_dropdown, 1, 2)

        self.value2_label = QLabel("Значение 2:")
        self.value2_input = QLineEdit()
        self.layout.addWidget(self.value2_label, 1, 3)
        self.layout.addWidget(self.value2_input, 1, 4)

        self.calculate_button = QPushButton("Посчитать!")
        self.calculate_button.clicked.connect(self.calculate)
        self.layout.addWidget(self.calculate_button, 4, 0, 1, 5)  # Span two columns

        self.result_label = QLabel("Результат: ")
        self.layout.addWidget(self.result_label, 5, 0, 1, 5)  # Span two columns

        self.setLayout(self.layout)

    def get_input(self, source_name):
        value_str = self.__getattribute__(source_name).text().replace(',', '.')
        if "e" in value_str:
            raise ParseError(f"Невозможно ввести экспоненциальное представление.")
        if len(value_str) == 0:
            raise ParseError(f"Проверьте входные числа, невозможно обработать пустое значение.")
        if not re.match(r'^\d+(\s\d{3})*(\.\d+)?$', value_str):
            raise ParseError(f"Проверьте входные числа на недопустимые символы: {value_str}!")
        else:
            value_str = value_str.replace(" ", "")
        value = Decimal(value_str)
        return value

    def calculate(self):
        try:
            value_1 = self.get_input("value1_input")
            value_2 = self.get_input("value2_input")
            # Check just to fit task description
            if math.fabs(value_1) > 1e12 or math.fabs(value_2) > 1e12:
                raise ArithmeticError(
                    "Переполнение: значения должны быть меньше 1 000 000 000 000.000000 и больше -1 000 000 000 000.000000")
            operation = self.operation_dropdown.currentText()

            result = 0
            if operation == "+":
                result = value_1 + value_2
            elif operation == "-":
                result = value_1 - value_2
            elif operation == "*":
                result = value_1 * value_2
            elif operation == "/":
                if value_2 == 0:
                    raise ValueError("Деление на 0 невозможно.")
                result = value_1 / value_2
            else:
                raise ValueError("Неподдерживаемая операция.")

            # Another check just to fit task description
            if result - Decimal(1e12) > 0:
                raise ArithmeticError("Переполнение: результат больше 1 000 000 000 000.000000")
            if result + Decimal(1e12) < 0:
                raise ArithmeticError("Переполнение: результат меньше -1 000 000 000 000.000000")

            result_str = "{:,.6f}".format(result)
            result_str = result_str.replace(",", " ").rstrip('0').rstrip('.')
            self.result_label.setText(f"Результат: {result_str}")
        except (ArithmeticError, ValueError, ParseError) as exc:
            self.result_label.setText(f"Неправильный ввод: {str(exc)}")
