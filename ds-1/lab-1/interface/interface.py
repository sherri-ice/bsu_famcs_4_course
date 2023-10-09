from PyQt5.QtWidgets import *
import sys


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Hello, world")
        self.move(300, 300)
        self.resize(200, 200)
        self.lbl = QLabel('Hello, world!!!', self)
        self.lbl.move(30, 30)



