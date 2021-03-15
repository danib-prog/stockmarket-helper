import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

apikey = None

class ApiKeyWindow(QMainWindow):
    def __init__(self):
        super(ApiKeyWindow, self).__init__()

        layout = QHBoxLayout()
        layout.addWidget(QLabel("Your Alpha Vantage API key: "))
        self.lineedit = QLineEdit()
        self.lineedit.returnPressed.connect(self.onOkButtonClicked)
        layout.addWidget(self.lineedit)
        self.okbutton = QPushButton('Ok')
        self.okbutton.clicked.connect(self.onOkButtonClicked)
        layout.addWidget(self.okbutton)

        centralwidget = QWidget()
        centralwidget.setLayout(layout)
        self.setCentralWidget(centralwidget)

    def onOkButtonClicked(self, s):
        global apikey
        apikey = self.lineedit.text()
        self.close()

import mainwindow
import stockselector
import aspects

mainwindow_ui = mainwindow.Ui_MainWindow
stockselector_ui = stockselector.Ui_Dialog
aspects_ui = aspects.Ui_Dialog


def aspectsIntoLayout(aspects):
    tristates = ['Symbol', 'Currency']
    rowcount = (len(aspects) // 2) + 1

    layout = QGridLayout()
    layout.addWidget(QLabel('  '), rowcount, 2)

    for a in aspects:
        if a not in tristates:
            checkbox = QCheckBox(a)
            checkbox.setCheckState(2)
            layout.addWidget(checkbox)

    return layout


class MainWindow(QMainWindow, mainwindow_ui):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.toolBar.addWidget(QLabel('Sort by:'))
        sortby_combo = QComboBox()
        sortby_combo.addItems(["Graham's number", "Market Capitalization",
                               "Number of shares", "Total Assets"])
        sortby_combo.currentIndexChanged.connect(self.onSortByComboIndexChange)
        sortby_combo.setStatusTip("A selection menu for on what aspects the sorting is based")
        sortby_combo.setToolTip("Aspects to sort by")
        self.toolBar.addWidget(sortby_combo)

        self.actionBusinesses.setIcon(QIcon("./icons-shadowless-32/document-text.png"))
        self.actionBusinesses.triggered.connect(self.onActionBusinessesTriggered)

        self.actionAspectsShown.setIcon(QIcon("./icons-shadowless-32/table.png"))
        self.actionAspectsShown.triggered.connect(self.onActionAspectsTriggered)

    def onActionBusinessesTriggered(self, s):
        pass

    def onActionAspectsTriggered(self, s):
        pass

    def onSortByComboIndexChange(self, i):
        index_to_aspect = {0: 'Graham Number',
                           1: 'MarketCapitalization',
                           2: 'SharesOutstanding',
                           3: 'totalAssets'}


class StockSelectorDialog(QDialog, stockselector_ui):
    def __init__(self, symbols, *args, **kwargs):
        super(StockSelectorDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.symbols = symbols


class AspectsDialog(QDialog, aspects_ui):
    def __init__(self, aspects, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        layout = aspectsIntoLayout(aspects)
        self.aspectsWidget.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ApiKeyWindow()
    window.show()
    app.exec_()

