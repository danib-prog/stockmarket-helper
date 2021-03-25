import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import scraper
import pandas as pd


apikey = None

#This window retrieves the api key of the user for further usage
class ApiKeyWindow(QMainWindow):
    def __init__(self):
        super(ApiKeyWindow, self).__init__()
        self.setWindowTitle("Stockmarket Helper/API key entry")

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
    aspects_ = scraper.all_columns
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("Stockmarket Helper")

        self.symbols = []   #The symbols of businesses that need to be shown
        self.symbols_loaded = {} #symbols in memory {symbol: scraper.Stock instance}

        self.stockstable = pd.DataFrame()
        self.stocksmodel = StocksTableModel(self)
        self.sortingmodel = QSortFilterProxyModel(self)
        self.sortingmodel.setSourceModel(self.stocksmodel)
        self.tableView.setModel(self.sortingmodel)
        self.tableView.setSortingEnabled(True)

        #What aspects are currently showing in the table
        self.aspects_shown = []
        for a in self.aspects_:
            tup = (a, Qt.CheckState.Checked)
            self.aspects_shown.append(tup)

        self.toolBar.addWidget(QLabel('You can sort by clicking on column headers'))

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

    #It's called when the Stockselector dialog is accepted
    def onSymbolsChanged(self):
        stocks = []
        if self.symbols:
            for symbol in self.symbols:
                if symbol not in self.symbols_loaded:
                    self.symbols_loaded.update({symbol: scraper.Stock(symbol, apikey)})

                stocks.append(self.symbols_loaded[symbol])

            self.stockstable = scraper.overviewboard(stocks)
            #print(self.stockstable)
            self.stocksmodel.layoutChanged.emit()


class StocksTableModel(QAbstractTableModel):
    def __init__(self, parent_, *args, **kwargs):
        super(StocksTableModel, self).__init__(*args, **kwargs)
        self.parent_ = parent_

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self.parent_.stockstable.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        #print(self.table.shape)
        return self.parent_.stockstable.shape[0]

    def columnCount(self, index):
        return self.parent_.stockstable.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.parent_.stockstable.columns[section])


class SymbolListModel(QAbstractListModel):
    def __init__(self, parent_, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.symbols = parent_.symbolsbuffer

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

        self.parent_ = parent_
        self.symbolsbuffer = parent_.symbols.copy()   #So as not to mess with the actual symbols in case the dialog is rejected

        self.symbolmodel = SymbolListModel(self)
        self.listView.setModel(self.symbolmodel)

        self.symbolAddButton.clicked.connect(self.onAddButtonClicked)
        self.symbolDeleteButton.clicked.connect(self.onDeleteButtonClicked)

    def onAddButtonClicked(self, s):
        symbol = self.symbolEdit.text()
        if symbol:
            self.symbolsbuffer.append(symbol)
            self.symbolmodel.layoutChanged.emit()
            self.symbolEdit.setText("")

    def onDeleteButtonClicked(self, s):
        indexes = self.listView.selectedIndexes()
        if indexes:
            for i in indexes:
                del self.symbolsbuffer[i.row()]

            self.symbolmodel.layoutChanged.emit()
            self.listView.clearSelection()

    def accept(self):
        self.parent_.symbols = self.symbolsbuffer #Refreshing the actual symbols
        self.parent_.onSymbolsChanged()
        super(StockSelectorDialog, self).accept()


class AspectsDialog(QDialog, aspects_ui):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_ = parent
        self.setupUi(self)

        layout = self.aspectsIntoLayout()
        self.aspectsWidget.setLayout(layout)

    def aspectsIntoLayout(self):
        musts = ['Symbol', 'Currency']
        rowcount = (len(self.parent_.aspects_shown) // 2) + 1

        layout = QGridLayout()
        layout.addWidget(QLabel('  '), rowcount, 2) #Presetting the dimendions of the layout

        for i, a in enumerate(self.parent_.aspects_shown):
            if a[0] not in musts:
                checkbox = QCheckBox(a[0])
                checkbox.setCheckState(a[1])
                checkbox.stateChanged.connect(lambda s, i=i, aspect=a[0]: self.checkSateChanged(s, i, aspect))
                layout.addWidget(checkbox)

        return layout

    def checkSateChanged(self, state, index, aspect):
        self.parent_.aspects_shown[index] = (aspect, state)
        if state == Qt.CheckState.Checked:
            self.parent_.tableView.showColumn(index)
        else:
            self.parent_.tableView.hideColumn(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ApiKeyWindow()
    window.show()
    app.exec_()

    mainapp = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    mainapp.exec_()

