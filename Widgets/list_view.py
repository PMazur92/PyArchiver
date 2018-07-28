__author__ = 'piotrek'

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui


class ListView(QtWidgets.QListView):

    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        model = QtGui.QStandardItemModel()
        model.itemChanged.connect(self.select_click)
        self.setModel(model)
        self.setWordWrap(True)

        self.header_item = QtGui.QStandardItem()
        self.header_item.setCheckable(True)
        self.header_item.setBackground(QtCore.Qt.gray)
        self.header_item.setForeground(QtCore.Qt.white)
        self.header_item.setEditable(False)
        self.header_item.setSelectable(False)
        self.header_item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.header_item.setToolTip('Nacisnij aby zaznaczyc/odznaczyc wszystki pliki na liscie')
        model.appendRow(self.header_item)

        self.file_list = []
        self.count_selected = 0

        self.clicked.connect(self.click_element)

    def get_index_list(self):
        return self.file_list

    def name_with_count(self):
        return self.name.format(len(self.file_list))

    def get_quantity(self):
        return len(self.file_list)

    def add_to_model(self, element):
        self.model().appendRow(element)

    def set_header(self, header):
        self.header_item.setText(header)

    def set_header_status(self):
        return self.header_item.checkState()

    def add_element(self, element):
        self.file_list.append(element)

    def __contains__(self, element):
        return element in self.file_list

    def remove_selected(self):
        for i in range(self.model().rowCount()-1, 0, -1):
            if self.model().item(i).checkState():
                self.file_list.pop(i - 1)
                self.model().removeRow(i)

        if self.model().rowCount():
            self.header_item.setCheckState(False)

    def select_click(self, standard_item):
        if standard_item.index().row():
            self.count_selected += 1 if standard_item.checkState() else -1

    def get_quantity_selected(self):
        print(self.count_selected)
        return self.count_selected

    def click_element(self, index):
        if not index.row():
            change = self.header_item.checkState()
            for i in range(self.model().rowCount()-1, 0, -1):
                self.model().item(i).setCheckState(change)
            self.count_selected = len(self.file_list) if change else 0

    def get_item_with_index(self):
        i = self.get_quantity() - 1
        while True:
            if i == -1:
                raise StopIteration
            yield self.model().item(i+1), self.file_list[i]
            i -= 1
