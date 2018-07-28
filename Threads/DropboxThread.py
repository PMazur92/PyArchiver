__author__ = 'piotrek'

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal


class DropboxThread(QtCore.QThread):

    sent_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def set(self, drive, path):
        self.drive = drive
        self.path = path

    def run(self):
        name = str(QtCore.QFileInfo(self.path).fileName())

        file = open(self.path)
        self.drive.put_file('/' + name, file)
        file.close()
        self.sent_signal.emit('Wyslano plik na dysk dropbox')
