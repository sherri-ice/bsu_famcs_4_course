import sys

from PyQt5.QtWidgets import QApplication
from financial_calc import FinancialCalculator

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinancialCalculator()
    window.show()
    sys.exit(app.exec_())
