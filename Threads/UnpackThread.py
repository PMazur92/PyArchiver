__author__ = 'piotrek'

import os
import tarfile

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal


class UnpackThread(QtCore.QThread):

    progress_signal = pyqtSignal(int)
    unpacked_signal = pyqtSignal(str)
    end_signal = pyqtSignal(str)

    def __init__(self, file, info_list, target_path, parent=None):
        super().__init__(parent)
        self.file = file
        self.info_list = info_list
        self.target_path = target_path
        self.in_progress = True

    def stop(self):
        self.in_progress = False

    def resume(self):
        self.in_progress = True

    def run(self):
        iter_list = iter(enumerate(self.info_list, 1))
        end = False
        while not end:
            if self.in_progress:
                for i, info in iter_list:
                    self.progress_signal.emit(i)
                    if isinstance(info, tarfile.TarInfo):
                        self.unpacked_signal.emit(UnpackThread.name(info.name))
                    else:
                        self.unpacked_signal.emit(UnpackThread.name(info.filename))
                    try:
                        self.file.extract(info, str(self.target_path))
                    except Exception:
                        self.end_signal.emit('Nie udalo sie wypakowac pliku')
                    if not self.in_progress:
                        break
                if self.in_progress:
                    self.end_signal.emit('Wypakowano')
                    end = True

    def is_in_progress(self):
        return self.in_progress

    @staticmethod
    def name(pelnaNazwa):
        name = UnpackThread.file_list(pelnaNazwa)[-1]
        return name

    @staticmethod
    def file_list(pelnaNazwa):
        pelnaNazwa = pelnaNazwa.rstrip(os.sep)
        return tuple(pelnaNazwa.split(os.sep))
