import math
import re
from decimal import Decimal, getcontext, ROUND_CEILING

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox
from PyQt5.QtCore import Qt, QSize


class ParseError(Exception):
    pass


def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)


class FinancialCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Финансовый калькулятор")
        self.setGeometry(100, 100, 1200, 200)

        self.layout = QGridLayout()
        self.setFixedSize(QSize(1200, 200))

        # Add an informative text label
        info_label = QLabel("Самосюк Екатерина Александровна. 4 курс, 4 группа (КТС). 2023 год.")
        info_label.setAlignment(Qt.AlignCenter)  # Center the text
        self.layout.addWidget(info_label, 0, 1, 1, 13)  # Span two columns

        # Add input fields and labels in line
        self.value1_label = QLabel("Значение 1:")
        self.value1_input = QLineEdit("0")
        self.layout.addWidget(self.value1_label, 1, 0)
        self.layout.addWidget(self.value1_input, 1, 1)

        self.operation_dropdown1 = QComboBox()
        self.operation_dropdown1.addItems(["+", "-", "*", "/"])
        self.layout.addWidget(self.operation_dropdown1, 1, 2)

        self.value2_label = QLabel("( Значение 2:")
        self.value2_input = QLineEdit("0")
        self.layout.addWidget(self.value2_label, 1, 3)
        self.layout.addWidget(self.value2_input, 1, 4)

        self.operation_dropdown2 = QComboBox()
        self.operation_dropdown2.addItems(["+", "-", "*", "/"])
        self.layout.addWidget(self.operation_dropdown2, 1, 5)

        self.value3_label = QLabel("Значение 3:")
        self.value3_input = QLineEdit("0")
        self.layout.addWidget(self.value3_label, 1, 6)
        self.layout.addWidget(self.value3_input, 1, 7)
        self.scope_label = QLabel(")")
        self.layout.addWidget(self.scope_label, 1, 8)

        self.operation_dropdown3 = QComboBox()
        self.operation_dropdown3.addItems(["+", "-", "*", "/"])
        self.layout.addWidget(self.operation_dropdown3, 1, 9)

        self.value4_label = QLabel("Значение 4:")
        self.value4_input = QLineEdit("0")
        self.layout.addWidget(self.value4_label, 1, 10)
        self.layout.addWidget(self.value4_input, 1, 11)

        self.calculate_button = QPushButton("Посчитать!")
        self.calculate_button.clicked.connect(self.calculate)
        self.layout.addWidget(self.calculate_button, 4, 0, 1, 13)  # Span 13 columns

        self.result_label = QLabel("Результат: ")
        self.layout.addWidget(self.result_label, 5, 0, 1, 13)  # Span 13 columns

        self.output_type = QComboBox()
        self.output_type.addItems(
            [
                "Математическое округление",
                "Банковское округление",
                "Усечение"
            ]
        )
        self.layout.addWidget(self.output_type, 6, 0, 1, 6)

        self.rounded_result_label = QLabel("Округленный результат: ")
        self.layout.addWidget(self.rounded_result_label, 6, 6, 1, 6)  # Span 6 columns

        self.setLayout(self.layout)

    def get_input(self, source_name):
        value_str = self.__getattribute__(source_name).text().replace(',', '.')
        if "e" in value_str:
            raise ParseError(f"Невозможно ввести экспоненциальное представление.")
        if len(value_str) == 0:
            raise ParseError(f"Проверьте входные числа, невозможно обработать пустое значение.")
        if not re.match(r'^-?\d+(\s\d{3})*(\.\d+)?$', value_str):
            raise ParseError(f"Проверьте входные числа на недопустимые символы: {value_str}!")
        else:
            value_str = value_str.replace(" ", "")
        value = Decimal(value_str)
        if math.fabs(value) > 1e12:
            raise ArithmeticError(
                "Переполнение: значения должны быть меньше 1 000 000 000 000.000000 и больше -1 000 000 000 000.000000")
        return value

    @staticmethod
    def _do_calc(value_1, value_2, operation):
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
        if result - Decimal(1e12) > 0:
            raise ArithmeticError("Переполнение: результат больше 1 000 000 000 000.000000")
        if result + Decimal(1e12) < 0:
            raise ArithmeticError("Переполнение: результат меньше -1 000 000 000 000.000000")

        return round(result, 10)

    def _round_result(self, result: Decimal):
        output_type = self.output_type.currentIndex()
        if output_type == 0:  # math round
            return normal_round(result)
        elif output_type == 1:  # bankers round
            return round(result)
        elif output_type == 2:
            return math.trunc(result)
        else:
            ValueError("Не поддерживаемый тип округления.")

    def calculate(self):
        try:
            value_1 = self.get_input("value1_input")
            value_2 = self.get_input("value2_input")
            value_3 = self.get_input("value3_input")
            value_4 = self.get_input("value4_input")

            operation1 = self.operation_dropdown1.currentText()
            operation2 = self.operation_dropdown2.currentText()
            operation3 = self.operation_dropdown3.currentText()

            result = self._do_calc(value_2, value_3, operation2)
            if operation1 in ["*", "/"]:
                result = self._do_calc(value_1, result, operation1)
                result = self._do_calc(result, value_4, operation3)
            else:
                result = self._do_calc(result, value_4, operation3)
                result = self._do_calc(value_1, result, operation1)

            # Another check just to fit task description

            rounded_result = self._round_result(result)
            rounded_result_str = "{:,.6f}".format(rounded_result)
            rounded_result_str = rounded_result_str.replace(",", " ").rstrip('0').rstrip('.')
            self.rounded_result_label.setText(f"Округленный результат: {rounded_result_str}")

            result_str = "{:,.6f}".format(result)
            result_str = result_str.replace(",", " ").rstrip('0').rstrip('.')
            self.result_label.setText(f"Результат: {result_str}")
        except (ArithmeticError, ValueError, ParseError) as exc:
            self.result_label.setText(f"Неправильный ввод: {str(exc)}")
