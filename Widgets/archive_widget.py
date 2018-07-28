__author__ = 'piotrek'

import os
import zipfile
import tarfile
import datetime
import mimetypes

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.Qt import QApplication

from Widgets.unpack_widget import UnpackWidget
from Threads.CreateTreeThread import CreateTreeThread


class ArchiveWidget(QtWidgets.QMainWindow):

    def __init__(self, path, parent=None):
        super().__init__(parent)

        self.setWindowIcon(QtGui.QIcon.fromTheme('applications-science'))
        self.setWindowModality(QtCore.Qt.NonModal)
        self.path = path
        self.file_name = QtCore.QFileInfo(path).fileName()
        self.resize(800, 600)
        self.setWindowTitle('PyArchiver - (wczytywanie) {name}'.format(name=self.file_name))
        self.main_widget = QtWidgets.QWidget()
        self.unpack_widget = None

        self.create_tree(self.path)
        self.create_toolbar()
        self.create_information()

        self.create_layouts()
        self.create_actions()
        self.add_actions()

    def create_information(self):
        self.information_widget = QtWidgets.QWidget()
        self.information_icon_lbl = QtWidgets.QLabel()
        self.information_icon_lbl.setPixmap(
            QtWidgets.QFileIconProvider().icon(QtCore.QFileInfo(self.path)).pixmap(80, 80))
        self.information_icon_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.information_name_lbl = QtWidgets.QLabel()

        if len(self.file_name) < 25:
            name = '<b>{name}</b>'.format(name=self.file_name)
        else:
            name = '<b>{name:.5}...</b>'.format(name=self.file_name)
            self.information_name_lbl.setToolTip(self.file_name)

        self.information_name_lbl.setText(name)
        self.information_name_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.information_mimetype_lbl = QtWidgets.QLabel(mimetypes.guess_type(self.path)[0])
        self.information_mimetype_lbl.setAlignment(QtCore.Qt.AlignCenter)

    def name(self, full_name: str):
        return self.file_list(full_name)[-1]

    @staticmethod
    def file_list(fullname_file: str) -> tuple:
        full_name = fullname_file.rstrip(os.sep)
        return tuple(full_name.split(os.sep))

    def create_node(self, file_name: str, size, date: datetime.datetime, folder=False) -> tuple:
        if folder:
            icon = QtWidgets.QFileIconProvider().icon(QtWidgets.QFileIconProvider.Folder)
        else:
            file_info = QtCore.QFileInfo(file_name)
            icon = QtWidgets.QFileIconProvider().icon(file_info)
        item_name = QtGui.QStandardItem(icon, self.name(file_name))
        item_date = QtGui.QStandardItem('{:%d.%m.%Y  %H:%M:%S}'.format(date))

        return item_name, item_date

    def _create_tree_zip(self, root_node, root_name, info_list, file_dict):
        for zipInfo in info_list:
            if zipInfo not in file_dict.values():
                if isdirzipinfo(zipInfo):
                    if zipInfo.filename.startswith(root_name):
                        count_files = len([info for info in info_list if info.filename.startswith(zipInfo.filename)
                                           and info.filename != zipInfo.filename])
                        # count_files = len(list(filter(lambda info: info.filename.startswith(zipInfo.filename)
                        #                                       and info.filename != zipInfo.filename, info_list)))
                        items = self.create_node(zipInfo.filename, count_files,
                                                 datetime.datetime(*zipInfo.date_time),
                                                 True)
                        root_node.appendRow(items)
                        file_dict[self.file_list(zipInfo.filename)] = zipInfo
                        self._create_tree_zip(items[0], zipInfo.filename, info_list, file_dict)
                else:
                    if zipInfo.filename.startswith(root_name):
                        item = self.create_node(zipInfo.filename, zipInfo.file_size,
                                                datetime.datetime(*zipInfo.date_time))
                        root_node.appendRow(item)
                        file_dict[self.file_list(zipInfo.filename)] = zipInfo

    def _create_tree_tar(self, root_node, root_name, info_list, file_dict):
        for tarInfo in info_list:
            if tarInfo not in file_dict.values():
                if tarInfo.isdir():
                    if tarInfo.name.startswith(root_name):
                        count_files = len([info for info in info_list if info.name.startswith(tarInfo.name)
                                           and info.name != tarInfo.name])
                        # count_files = len(list(filter(lambda info: info.name.startswith(tarInfo.name)
                        #                                       and info.name != tarInfo.name, info_list)))
                        items = self.create_node(tarInfo.name, count_files,
                                                 datetime.datetime.fromtimestamp(tarInfo.mtime),
                                                 True)
                        root_node.appendRow(items)
                        file_dict[self.file_list(tarInfo.name)] = tarInfo
                        self._create_tree_tar(items[0], tarInfo.name, info_list, file_dict)
                else:
                    if tarInfo.name.startswith(root_name):
                        item = self.create_node(tarInfo.name, tarInfo.size,
                                                datetime.datetime.fromtimestamp(tarInfo.mtime))
                        root_node.appendRow(item)
                        file_dict[self.file_list(tarInfo.name)] = tarInfo

    def create_tree_zip(self, model, path, file_dict):
        rootNode = model.invisibleRootItem()
        self.opened_file = zipfile.ZipFile(path, 'r')
        self._create_tree_zip(rootNode, '', self.opened_file.infolist(), file_dict)

    def createTreeTar(self, model, path, fileDict):
        rootNode = model.invisibleRootItem()
        self.opened_file = tarfile.open(path, 'r|*')
        self._create_tree_tar(rootNode, '', self.otwartyPlik.getmembers(), fileDict)

    def create_tree(self, path):
        self.files_tree = QtWidgets.QTreeView()
        self.files_tree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.standardModel = QtGui.QStandardItemModel()
        self.standardModel.setHorizontalHeaderLabels(['Nazwa', 'Data'])

        self.file_dict = dict()

        # KGlobal.locale()
        self.tree_thread = None
        if zipfile.is_zipfile(path):
            self.tree_thread = CreateTreeThread(self.create_tree_zip, self.standardModel, path, self.file_dict)
        elif tarfile.is_tarfile(path):
            self.tree_thread = CreateTreeThread(self.createTreeTar, self.standardModel, path, self.file_dict)

        self.tree_thread.status_signal.connect(self.loaded)
        self.tree_thread.start()
        self.files_tree.setModel(self.standardModel)
        self.files_tree.expand(self.standardModel.index(0, 0))

        self.files_tree.setAnimated(True)
        self.files_tree.header().setStretchLastSection(False)
        self.files_tree.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.files_tree.expanded.connect(self.align)

    def align(self):
        self.files_tree.resizeColumnToContents(0)
        self.files_tree.resizeColumnToContents(1)
        self.files_tree.resizeColumnToContents(2)
        self.files_tree.resizeColumnToContents(0)

    def create_toolbar(self):
        self.toolbar = QtWidgets.QToolBar(self)
        self.toolbar.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolbar.setFloatable(True)

    def create_layouts(self):
        self.main_layout = QtWidgets.QGridLayout()

        v_d_layout = QtWidgets.QVBoxLayout()
        v_d_layout.addWidget(self.toolbar)
        h_d_layout = QtWidgets.QHBoxLayout()
        h_d_layout.addWidget(self.files_tree)

        space_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        space_2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        space_3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        space_4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)

        # utworzenie layoutu dla widgetu informacji
        h_l_layout = QtWidgets.QHBoxLayout()
        h_l_layout.addSpacerItem(space_1)
        h_l_layout.addWidget(self.information_icon_lbl)  # information icon
        h_l_layout.addSpacerItem(space_2)

        v_l_layout = QtWidgets.QVBoxLayout()
        v_l_layout.addSpacerItem(space_3)
        v_l_layout.addLayout(h_l_layout)
        v_l_layout.addWidget(self.information_name_lbl)
        v_l_layout.addWidget(line)
        v_l_layout.addWidget(self.information_mimetype_lbl)
        v_l_layout.addSpacerItem(space_4)

        self.information_widget.setLayout(v_l_layout)

        h_d_layout.addWidget(self.information_widget)
        v_d_layout.addLayout(h_d_layout)

        self.main_layout.addLayout(v_d_layout, 0, 0, 1, 1)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    def create_actions(self):
        self.unpack_file_acn = QtWidgets.QAction(QtGui.QIcon.fromTheme(''), 'Wypakuj plik', self,
                                                 triggered=self.unpack_file)

        self.unpack_all_acn = QtWidgets.QAction(QtGui.QIcon.fromTheme(''), 'Wypakuj wszystko', self,
                                                triggered=self.unpack_all)

        self.informacje = QtWidgets.QAction(QtGui.QIcon.fromTheme(''), 'Informacje', self,
                                            triggered=self.show_information)

    def show_information(self):
        if self.information_widget.isHidden():
            self.information_widget.show()
        else:
            self.information_widget.hide()

    @staticmethod
    def list_files_tree(index):
        list_above = list()
        list_above.append(index.data(QtCore.Qt.DisplayRole))

        while index.parent().isValid():
            list_above.append(str(index.parent().data(QtCore.Qt.DisplayRole).toString()))
            index = index.parent()

        list_above.reverse()
        return tuple(list_above)

    def unpack_file(self):
        index = self.files_tree.currentIndex()

        if index.model() is None:
            return

        file_index = index.model().index(index.row(), 0, index.parent())

        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Wybierz katalog', os.path.dirname(self.path))

        print(self.list_files_tree(file_index))
        try:
            info_root = self.file_dict[self.list_files_tree(file_index)]
        except KeyError:
            return

        list_info = list()
        if zipfile.is_zipfile(self.path):
            if isdirzipinfo(info_root):
                list_info = [info for info in self.file_dict.values() if info.filename.startswith(info_root.filename)]
            else:
                list_info.append(info_root)
        elif tarfile.is_tarfile(self.path):
            if info_root.isdir():
                list_info = [info for info in self.file_dict.values() if info.name.startswith(info_root.name)]
            else:
                list_info.append(info_root)

        if dir_path:
            self.unpack_widget = UnpackWidget(self.path, list_info, dir_path, self)
            self.unpack_widget.show()

    def unpack_all(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Wybierz katalog', os.path.dirname(self.sciezka))
        if dir_path:
            unpack_widget = UnpackWidget(self.sciezka, self.file_dict.values(), dir_path, self)
            unpack_widget.show()
            self.unpack_file_acn.setEnabled(False)
            self.unpack_all_acn.setEnabled(False)

    def add_actions(self):
        self.toolbar.addAction(self.unpack_file_acn)
        self.toolbar.addAction(self.unpack_all_acn)
        self.toolbar.addAction(self.informacje)

    def closeEvent(self, QCloseEvent):
        if self.tree_thread.isRunning():
            self.tree_thread.terminate()
        if self.unpack_widget is not None:
            self.unpack_widget.close()

    def loaded(self):
        self.setWindowTitle('PyArchiver 3 - ' + self.nazwaPliku)

        self.files_tree.expand(self.standardModel.index(0, 0))

        self.files_tree.resizeColumnToContents(0)
        self.files_tree.resizeColumnToContents(1)
        self.files_tree.resizeColumnToContents(2)

        self.files_tree.expanded.connect(self.align)


def isdirzipinfo(zipInfo):
    return ((zipInfo.external_attr & 0xff) & 0x10) != 0


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    widget = ArchiveWidget('C:/Users/PMazur/Python/untitled.zip')
    widget.show()

    sys.exit(app.exec_())
