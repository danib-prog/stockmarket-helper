import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from aspects import Ui_Dialog

aspects = ["Kiskunfelegyhaza" for x in range(200)]

def aspectsIntoLayout(aspects):
    tristates = ['Symbol', 'Currency']
    rowcount = (len(aspects) / 2) + 1
    rowcount = round(rowcount)

    layout = QGridLayout()
    layout.addWidget(QLabel('  '), rowcount, 2)

    for a in aspects:
        if a not in tristates:
            checkbox = QCheckBox(a)
            checkbox.setCheckState(True)
            layout.addWidget(checkbox)

    return layout

class MainWindow(QMainWindow):
    def __init__(self, aspects, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.aspects = aspects

        button = QPushButton("Click me!")
        button.clicked.connect(self.buttonClicked)
        self.setCentralWidget(button)

    def buttonClicked(self, s):
        dlg = AspectsDialog(self.aspects)
        dlg.exec_()

class AspectsDialog(QDialog, Ui_Dialog):
    def __init__(self, aspects, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        layout = aspectsIntoLayout(aspects)
        self.aspectsWidget.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(aspects)
    window.show()
    app.exec_()
