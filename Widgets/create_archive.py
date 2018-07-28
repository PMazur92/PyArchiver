__author__ = 'piotrek'

import os
import zipfile
import tarfile

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from Widgets.list_view import ListView
from Threads.PackThread import PackThread


class CreateArchive(QtWidgets.QDialog):

    def __init__(self, model, index, path, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Utworz archiwum')
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.resize(350, 400)

        self.path = path
        self.file_model = model
        self.index = index

        self.create_components()
        self.create_layout()

        self.pack_thread = PackThread()
        self.pack_thread.status_signal.connect(self.ended)
        self.pack_thread.progress_signal.connect(self.progress)
        self.pack_thread.access_signal.connect(self.access)

    def create_item(self, index):
        path = os.path.abspath(self.file_model.filePath(index))
        item = QtGui.QStandardItem(os.path.basename(path))
        item.setIcon(self.file_model.fileIcon(index))
        item.setCheckable(True)
        item.setEditable(False)
        return item

    def create_components(self):
        self.option_widget = QtWidgets.QWidget()

        self.name_lbl = QtWidgets.QLabel('Nazwa')

        self.name_edit = QtWidgets.QLineEdit('untitled')
        self.name_edit.setMaxLength(30)
        self.name_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('\w{30}'), self.name_edit))

        self.archive_type_cb = QtWidgets.QComboBox()
        self.archive_type_cb.addItem('.zip')
        self.archive_type_cb.addItem('.tar')

        self.path_lbl = QtWidgets.QLabel(self.path)
        self.path_lbl.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        self.path_lbl.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.path_lbl.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.set_path_btn = QtWidgets.QPushButton('Sciezka', clicked=self.set_path)

        self.file_list = ListView('Pliki do zapakowania')
        self.file_list.add_element(self.index)
        self.file_list.add_to_model(self.create_item(self.index))

        self.add_folder_btn = QtWidgets.QPushButton('Dodaj katalog', clicked=self.add_catalog)
        self.add_file_btn = QtWidgets.QPushButton('Dodaj plik', clicked=self.add_file)
        self.remove_selected_btn = QtWidgets.QPushButton('Usun zaznaczone', clicked=self.file_list.remove_selected)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMinimum(0)

        self.progress_lbl = QtWidgets.QLabel()

        self.pack_btn = QtWidgets.QPushButton('Zapakuj', clicked=self.pack_files)

    def set_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Wybierz katalog', QtCore.QDir.homePath())

        if path:
            self.path = path
            self.path_lbl.setText(self.path)

    def create_layout(self):
        option_layout = QtWidgets.QGridLayout()
        v_option_layout = QtWidgets.QVBoxLayout()

        main_layout = QtWidgets.QGridLayout()
        v_main_layout = QtWidgets.QVBoxLayout()

        h_name_layout = QtWidgets.QHBoxLayout()
        h_name_layout.addWidget(self.name_lbl)
        h_name_layout.addWidget(self.name_edit)
        h_name_layout.addWidget(self.archive_type_cb)

        v_option_layout.addLayout(h_name_layout)

        h_path_layout = QtWidgets.QHBoxLayout()
        h_path_layout.addWidget(self.path_lbl)
        h_path_layout.addWidget(self.set_path_btn)

        v_option_layout.addLayout(h_path_layout)

        v_option_layout.addWidget(self.file_list)

        h_remove_layout = QtWidgets.QHBoxLayout()
        h_remove_layout.addWidget(self.add_folder_btn)
        h_remove_layout.addWidget(self.add_file_btn)
        h_remove_layout.addWidget(self.remove_selected_btn)

        v_option_layout.addLayout(h_remove_layout)

        option_layout.addLayout(v_option_layout, 0, 0, 1, 1)

        self.option_widget.setLayout(option_layout)

        v_main_layout.addWidget(self.option_widget)

        v_main_layout.addWidget(self.progress_bar)

        v_main_layout.addWidget(self.pack_btn)

        main_layout.addLayout(v_main_layout, 0, 0, 1, 1)

        self.setLayout(main_layout)

    def pack_files(self):
        if not self.name_edit.text():
            return
        if not self.file_list.get_quantity():
            return
        self.option_widget.setEnabled(False)
        self.progress_bar.setMaximum(0)

        name = self.name_edit.text() + self.archive_type_cb.itemData(self.archive_type_cb.currentIndex(),
                                                                     QtCore.Qt.DisplayRole)
        path = self.path_lbl.text()
        list_index = self.file_list.get_index_list()

        path_list = [self.file_model.filePath(index) for index in list_index]

        if self.archive_type_cb.currentText() == '.zip':
            self.pack_thread.set(pack_zip, name, path, path_list)
        elif self.archive_type_cb.currentText() == '.tar':
            self.pack_thread.set(pack_tar, name, path, path_list)

        self.pack_thread.start()

    def add_catalog(self):
        catalog = QtWidgets.QFileDialog.getExistingDirectory(self, 'Wybierz katalog', QtCore.QDir.homePath())

        if catalog and not QtCore.QFileInfo(catalog).isSymLink():
            index = self.file_model.index(catalog)
            if index not in self.file_list:
                self.file_list.add_element(index)
                self.file_list.add_to_model(self.create_item(index))

    def add_file(self):
        file, _filter = QtWidgets.QFileDialog.getOpenFileName(self, 'Wybierz plik', QtCore.QDir.homePath())

        if file:
            index = self.file_model.index(file)
            if index not in self.file_list:
                self.file_list.add_element(index)
                self.file_list.add_to_model(self.create_item(index))

    def ended(self):
        self.parent().trayIcon.showMessage('Zakonczono',
                                           'Zakonczono zapakowywanie pliku {0}'.format(self.pack_thread.name),
                                           QtWidgets.QSystemTrayIcon.Information, 2000)
        self.pack_btn.setText('Zamknij')
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(1)
        self.pack_thread.terminate()
        self.pack_btn.clicked.connect(self.close)

    def access(self):
        self.setWindowTitle('Brak dostepu')
        self.pack_btn.setText('Zamknij')
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(1)
        self.pack_thread.terminate()
        self.pack_btn.clicked.connect(self.close)

    def progress(self, info):
        print('info', info)  # remove
        self.setWindowTitle(info)

    def closeEvent(self, QCloseEvent):
        if not self.pack_thread.ended:
            QCloseEvent.ignore()
        self.parent().catalog_list.setRootIndex(self.parent().catalog_list.rootIndex())
        self.parent().catalog_list.scrollTo(self.parent().catalog_list.currentIndex())
        self.parent().model_list.refresh(self.parent().catalog_list.rootIndex())


def pack_tar(thread, name, target_path, path_list):
    tar_path = os.path.join(os.path.abspath(target_path), name)
    try:
        with tarfile.open(tar_path, 'w') as tar_file:
            for file_path in path_list:
                if not os.path.isdir(file_path):
                    thread.progress_signal.emit(file_path)
                    tar_file.add(file_path, arcname=os.path.basename(file_path))
                else:
                    catalog_path = os.path.dirname(os.path.abspath(file_path))
                    for root_folder, subfolders, files in os.walk(file_path):
                        for file in files:
                            thread.in_progress_signal.emit(os.path.join(root_folder, file))
                            tar_file.add(os.path.join(root_folder, file),
                                         arcname=os.path.join(root_folder[len(catalog_path) + 1:], file))
    except IOError:
        thread.access_signal.emit()


def pack_zip(thread, name, target_path, path_list):
    zip_path = os.path.join(os.path.abspath(target_path), name)
    try:
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for path_file in path_list:
                if not os.path.isdir(path_file):
                    thread.progress_signal.emit(path_file)
                    zip_file.write(path_file, arcname=os.path.basename(path_file))
                else:
                    path_folder = os.path.dirname(os.path.abspath(path_file))
                    for root_folder, subfolders, files in os.walk(path_file):
                        for file in files:
                            thread.emit(os.path.join(root_folder, file))
                            zip_file.write(os.path.join(root_folder, file),
                                           arcname=os.path.join(root_folder[len(path_folder) + 1:], file))
    except IOError:
        thread.access_signal.emit()
