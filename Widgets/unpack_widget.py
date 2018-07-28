__author__ = 'piotrek'

import zipfile
import tarfile

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

from Threads import UnpackThread


class UnpackWidget(QtWidgets.QDialog):

    def __init__(self, path, list_info, target_path, parent=None):
        super(UnpackWidget, self).__init__(parent)

        self.setWindowModality(QtCore.Qt.NonModal)
        self.window_name = QtCore.QFileInfo(path).fileName()
        self.setWindowTitle(self.window_name)
        self.resize(400, 150)
        self.setMinimumSize(self.size())
        self.setMaximumSize(self.size())

        self.create_components()
        self.create_layout()

        self.target_folder_lbl.setText(target_path)
        self.target_folder_lbl.setToolTip(target_path)

        self.file = None

        if zipfile.is_zipfile(path):
            self.file = zipfile.ZipFile(path, 'r')
        elif tarfile.is_tarfile(path):
            self.file = tarfile.open(path, 'r:*')

        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(len(list_info))

        self.unpack_thread = UnpackThread(self.file, list_info, target_path)
        self.unpack_thread.progress_signal.connect(self.progress_bar.setValue)  # TODO
        self.unpack_thread.progress_signal.connect(self.set_num_progress)
        self.unpack_thread.unpacked_signal.connect(self.set_source)
        self.unpack_thread.end_signal.connect(self.end)
        self.unpack_thread.start()

    def set_source(self, file_name):
        file_name = file_name
        length = len(file_name)
        if length > 50:
            file_name = '<b>' + '...' + file_name[40 - length:] + '</b>'
            self.show_source_lbl.setToolTip(file_name)
        else:
            file_name = '<b>' + file_name + '</b>'
        self.show_source_lbl.setText(file_name)

    def end(self, string):
        self.information.setText(string)
        self.stop_btn.setText('Zamknij')
        self.stop_btn.clicked.connect(self.close)

    def set_num_progress(self, nr):
        self.num_progress.setText('{0}/{1}'.format(nr, self.progress_bar.maximum()))

    def create_components(self):
        self.progress_bar = QtWidgets.QProgressBar()
        self.num_progress = QtWidgets.QLabel()

        self.information = QtWidgets.QLabel('Wypakowywanie...')

        self.source_lbl = QtWidgets.QLabel('plik: ')
        self.source_lbl.setFrameShadow(QtWidgets.QFrame.Raised)

        self.show_source_lbl = QtWidgets.QLabel()
        self.show_source_lbl.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.show_source_lbl.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.show_source_lbl.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.target_lbl = QtWidgets.QLabel('do:  ')
        self.target_lbl.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.target_lbl.setFrameShadow(QtWidgets.QFrame.Raised)

        self.target_folder_lbl = QtWidgets.QLabel()
        self.target_folder_lbl.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.target_folder_lbl.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.target_folder_lbl.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.stop_btn = QtWidgets.QPushButton('Zatrzymaj', clicked=self.stop)

    def stop(self):
        if self.unpack_thread.is_in_progress():
            self.unpack_thread.stop()
            self.stop_btn.setText('Wznow')
        else:
            self.unpack_thread.resume()
            self.stop_btn.setText('Zatrzymaj')

    def create_layout(self):
        main_layout = QtWidgets.QGridLayout()
        v_layout = QtWidgets.QVBoxLayout()

        v_layout.addWidget(self.information)

        h_progress_layout = QtWidgets.QHBoxLayout()
        h_progress_layout.addWidget(self.progress_bar)
        h_progress_layout.addWidget(self.num_progress)
        v_layout.addLayout(h_progress_layout)

        h_source_layout = QtWidgets.QHBoxLayout()
        h_source_layout.addWidget(self.source_lbl)
        h_source_layout.addWidget(self.show_source_lbl)
        v_layout.addLayout(h_source_layout)

        h_target_layout = QtWidgets.QHBoxLayout()
        h_target_layout.addWidget(self.target_lbl)
        h_target_layout.addWidget(self.target_folder_lbl)
        v_layout.addLayout(h_target_layout)

        v_layout.addWidget(self.stop_btn)

        main_layout.addLayout(v_layout, 0, 0, 1, 1)

        self.setLayout(main_layout)

    def closeEvent(self, QCloseEvent):
        if self.unpack_thread.isRunning():
            self.unpack_thread.stop()
            answer = QtWidgets.QMessageBox.question(self, 'Zatrzymanie wypakowywania',
                                                    'Czy napewno chcesz zatrzymac wypakowywanie?',
                                                    QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                                    QtGui.QMessageBox.Cancel)

            if answer == QtWidgets.QMessageBox.Cancel:
                QCloseEvent.setAccepted(False)
                self.unpack_thread.resume()
                return

        self.unpack_thread.terminate()
        self.file.close()
        self.parent().unpack_file.setEnabled(True)
        self.parent().unpack_all.setEnabled(True)
