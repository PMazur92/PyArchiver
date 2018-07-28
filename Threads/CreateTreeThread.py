__author__ = 'piotrek'

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal


class CreateTreeThread(QtCore.QThread):

    status_signal = pyqtSignal()

    def __init__(self, func, *args):
        super().__init__(None)
        self.action = func
        self.arguments = args

    def run(self):
        self.action(*self.arguments)
        self.status_signal.emit()
