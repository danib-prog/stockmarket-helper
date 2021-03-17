import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import scraper

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





class MainWindow(QMainWindow, mainwindow_ui):
    aspects_ = scraper.aspects
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.symbols = []
        self.symbolmodel = SymbolListModel(self)

        self.aspects_shown = []
        for a in self.aspects_:
            tup = (a, 2)
            self.aspects_shown.append(tup)

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
        dlg = StockSelectorDialog(self)
        dlg.setWindowTitle("Businesses Selector")
        dlg.exec_()

    def onActionAspectsTriggered(self, s):
        dlg = AspectsDialog(self)
        dlg.setWindowTitle("Aspects' Selector")
        dlg.exec_()

    def onSortByComboIndexChange(self, i):
        index_to_aspect = {0: 'Graham Number',
                           1: 'MarketCapitalization',
                           2: 'SharesOutstanding',
                           3: 'totalAssets'}


class SymbolListModel(QAbstractListModel):
    def __init__(self, parent_, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.symbols = parent_.symbols

    def data(self, index, role):
        if role == Qt.DisplayRole:
            symbol = self.symbols[index.row()]
            return symbol

    def rowCount(self, index):
        return len(self.symbols)



class StockSelectorDialog(QDialog, stockselector_ui):
    def __init__(self, parent_, *args, **kwargs):
        super(StockSelectorDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.symbols = parent_.symbols

        self.symbolmodel = parent_.symbolmodel
        self.listView.setModel(parent_.symbolmodel)

        self.symbolAddButton.clicked.connect(self.onAddButtonClicked)
        self.symbolDeleteButton.clicked.connect(self.onDeleteButtonClicked)

    def onAddButtonClicked(self, s):
        symbol = self.symbolEdit.text()
        if symbol:
            self.symbols.append(symbol)
            self.symbolmodel.layoutChanged.emit()
            self.symbolEdit.setText("")

    def onDeleteButtonClicked(self, s):
        indexes = self.listView.selectedIndexes()
        if indexes:
            for i in indexes:
                del self.symbols[i.row()]

            self.symbolmodel.layoutChanged.emit()
            self.listView.clearSelection()


class AspectsDialog(QDialog, aspects_ui):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_ = parent
        self.setupUi(self)

        layout = self.aspectsIntoLayout()
        self.aspectsWidget.setLayout(layout)

    def aspectsIntoLayout(self):
        tristates = ['Symbol', 'Currency']
        rowcount = (len(self.parent_.aspects_shown) // 2) + 1

        layout = QGridLayout()
        layout.addWidget(QLabel('  '), rowcount, 2)

        for i, a in enumerate(self.parent_.aspects_shown):
            if a not in tristates:
                checkbox = QCheckBox(a[0])
                checkbox.setCheckState(a[1])
                checkbox.stateChanged.connect(lambda s, i=i, aspect=a[0]: self.checkSateChanged(s, i, aspect))
                layout.addWidget(checkbox)

        return layout

    def checkSateChanged(self, state, index, aspect):
        self.parent_.aspects_shown[index] = (aspect, state)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()

