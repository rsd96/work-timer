from pandas import DataFrame, read_csv
from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableView, QPushButton, QHeaderView
from Util import UI_DIR


class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])

class LogWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_DIR + "work_timer_log.ui", self)
        self.table: QTableView = self.findChild(QTableView, 'tableView')
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.btnClear = self.findChild(QPushButton, 'btnClearLog')
        self.btnClear.clicked.connect(self.clearLog)
        self.btnDone = self.findChild(QPushButton, 'btnDone')
        self.btnDone.clicked.connect(self.dismissLog)

        self.loadLog()

        self.show()

    def loadLog(self):
        try:
            data = read_csv('work_timer_log.csv', header=None)
            data.columns = ['Date', 'Started Work At', 'Took Break For', 'Ended Work At', 'Total Work Time', 'Notes']
        except:
            data = DataFrame()

        self.model = TableModel(data)
        self.table.setModel(self.model)

    def clearLog(self):
        open("work_timer_log.csv", "w+").close()
        self.loadLog()

    def dismissLog(self):
        self.close()