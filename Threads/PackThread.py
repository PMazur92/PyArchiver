__author__ = 'piotrek'

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal


class PackThread(QtCore.QThread):

    status_signal = pyqtSignal()
    progress_signal = pyqtSignal(str)
    access_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ended = True

    def set(self, func, name, target_path, listaSciezek):
        self.func = func
        self.name = name
        self.target_path = target_path
        self.path_list = listaSciezek

    def run(self):
        self.ended = False
        self.func(self, self.name, self.target_path, self.path_list)
        self.ended = True
        self.status_signal.emit()
