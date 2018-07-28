__author__ = 'piotrek'

import zipfile
import tarfile
import os
import json

import dropbox
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from oauth2client.client import OAuth2WebServerFlow

from Widgets.login_panel import LoginPanel
from Threads.GoogleThread import GoogleThread
from Threads.DropboxThread import DropboxThread
from Widgets.archive_widget import ArchiveWidget
from Widgets.create_archive import CreateArchive


class MainWidget(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.window_size = self.widthWindow, self.heightWindow = 700, 500
        self.setWindowTitle('PyArchiver')
        self.setWindowIcon(QtGui.QIcon('icons/package.png'))

        self.resize(*self.window_size)
        self.setMinimumSize(*self.window_size)

        self.create_components()
        self.create_layout()
        self.create_connection()

    def create_components(self):
        self.main_widget = QtWidgets.QWidget()
        self.login_widget = LoginPanel(self)

        self.create_actions()
        self.create_catalog_list()
        self.create_completer()
        self.create_toolbar()
        self.create_buttons()
        self.create_icon()
        self.status_bar = self.statusBar()

        self.send_google_thread = GoogleThread()
        self.send_google_thread.sent_signal.connect(self.sent)

        self.send_dropbox_thread = DropboxThread()
        self.send_dropbox_thread.sent_signal.connect(self.sent)

    def create_connection(self):
        with open('secrets_data.json') as j_file:
            sec_data = json.load(j_file)
            sec_data_google = sec_data['google']
            google_flow = OAuth2WebServerFlow(sec_data_google['CLIENT_GOOGLE_ID'],
                                              sec_data_google['CLIENT_GOOGLE_SECRET'],
                                              sec_data_google['OAUTH_GOOGLE_SCOPE'],
                                              sec_data_google['REDIRECT_GOOGLE_URI'])
            authorize_url = google_flow.step1_get_authorize_url()
            self.login_widget.google_edit.setText(authorize_url)
            self.login_widget.set_google_flow(google_flow)

            sec_data_dropbox = sec_data['dropbox']
            dropbox_flow = dropbox.client.DropboxOAuth2FlowNoRedirect(sec_data_dropbox['CLIENT_DROPBOX_ID'],
                                                                      sec_data_dropbox['CLIENT_DROPBOX_SECRET'])
            authorize_url = dropbox_flow.start()
            self.login_widget.dropbox_edit.setText(authorize_url)
            self.login_widget.set_dropbox_flow(dropbox_flow)

    def create_catalog_list(self):
        self.catalog_list = QtWidgets.QTableView()
        self.model_list = QtWidgets.QDirModel()
        self.model_list.setFilter(QtCore.QDir.AllEntries | QtCore.QDir.NoDot)
        self.model_list.setSorting(QtCore.QDir.DirsFirst
                                   | QtCore.QDir.IgnoreCase
                                   | QtCore.QDir.Name)

        self.index = self.model_list.index(QtCore.QDir.homePath())
        self.catalog_list.setModel(self.model_list)
        self.catalog_list.setCurrentIndex(self.index)
        self.catalog_list.setRootIndex(self.index)
        self.catalog_list.horizontalHeader().setStretchLastSection(False)
        self.catalog_list.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.catalog_list.resizeColumnsToContents()
        self.catalog_list.setIconSize(QtCore.QSize(15, 15))
        self.catalog_list.resizeRowsToContents()
        self.catalog_list.setShowGrid(False)
        self.catalog_list.verticalHeader().setVisible(False)

        self.catalog_list.clicked.connect(self.on_click_catalog_list)
        self.catalog_list.doubleClicked.connect(self.on_double_click_catalog_list)

    def on_click_catalog_list(self):
        index = self.catalog_list.currentIndex()
        if index.isValid():
            index = self.file_index(index)
            path = self.model_list.filePath(index)

            if not QtCore.QFileInfo(path).isDir():
                self.send_toolbar.show()
                return

        self.send_toolbar.hide()

    def on_double_click_catalog_list(self):
        index = self.catalog_list.currentIndex()
        if index.isValid():
            index = self.file_index(index)
            path = self.model_list.filePath(index)

            if self.model_list.isDir(index):
                self.send_toolbar.hide()
                self.catalog_list.setRootIndex(index)
                self.path_completer.setText(os.path.abspath(self.model_list.filePath(index)))
            elif self.is_archive(path):
                archive_widget = ArchiveWidget(path, self)
                archive_widget.show()

    @staticmethod
    def is_archive(path: str) -> bool:
        return zipfile.is_zipfile(path) or tarfile.is_tarfile(path)

    @staticmethod
    def file_index(index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        return index.model().index(index.row(), 0, index.parent())

    def enter_click(self):
        path = self.path_completer.text()

        if QtCore.QDir(path).exists():
            self.path_completer.setText(QtCore.QFileInfo(path).absoluteFilePath())
            index = self.model_list.index(path)
            self.catalog_list.scrollTo(index)
            self.catalog_list.setRootIndex(index)
            self.send_toolbar.hide()

    def create_completer(self):
        path = self.model_list.filePath(self.catalog_list.rootIndex())
        self.path_completer = QtWidgets.QLineEdit(path)

        completer = QtWidgets.QCompleter(self)

        file_system_model = QtWidgets.QFileSystemModel(completer)
        file_system_model.setRootPath(self.model_list.filePath((self.catalog_list.rootIndex())))
        file_system_model.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)

        completer.setModel(file_system_model)
        completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.path_completer.setCompleter(completer)
        self.path_completer.returnPressed.connect(self.enter_click)
        self.path_completer.setFocus()

    def create_layout(self):
        main_layout = QtWidgets.QGridLayout()

        horizontal_layout = QtWidgets.QHBoxLayout()
        horizontal_layout.addWidget(self.go_home_btn)
        horizontal_layout.addWidget(self.go_previous_btn)
        horizontal_layout.addWidget(self.path_completer)
        horizontal_layout.addWidget(self.go_next_btn)

        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.addLayout(horizontal_layout)
        vertical_layout.addWidget(self.catalog_list)

        main_layout.addLayout(vertical_layout, 0, 0, 1, 1)

        self.main_widget.setLayout(main_layout)
        self.setCentralWidget(self.main_widget)

    def create_buttons(self):
        self.go_home_btn = QtWidgets.QToolButton(clicked=self.go_home)
        self.go_home_btn.setIcon(QtGui.QIcon('icons/home_folder.png'))

        self.go_previous_btn = QtWidgets.QToolButton(clicked=self.go_previous)
        self.go_previous_btn.setIcon(QtGui.QIcon('icons/previous_folder.png'))

        self.go_next_btn = QtWidgets.QToolButton(clicked=self.on_double_click_catalog_list)
        self.go_next_btn.setIcon(QtGui.QIcon('icons/next_folder.png'))

    def go_previous(self):
        index = self.catalog_list.rootIndex()
        path = os.path.abspath(os.path.join(self.model_list.filePath(index),
                                            os.pardir))
        index = self.model_list.index(path)
        self.catalog_list.setCurrentIndex(index)
        self.catalog_list.setRootIndex(index)
        self.path_completer.setText(path)

    def go_home(self):
        home_path = QtCore.QDir.homePath()
        index = self.model_list.index(home_path)
        self.catalog_list.setCurrentIndex(index)
        self.catalog_list.setRootIndex(index)
        self.path_completer.setText(home_path)

    def create_toolbar(self):
        self.toolbar = self.addToolBar('Opcje')
        self.toolbar.addAction(self.add_catalog_acn)
        self.toolbar.addAction(self.remove_catalog_acn)
        self.toolbar.addAction(self.create_archive_acn)
        self.toolbar.addAction(self.connect_with_drive_acn)

        self.send_toolbar = self.addToolBar('Wyslij')
        self.send_toolbar.addAction(self.send_google_acn)
        self.send_toolbar.addAction(self.send_dropbox_acn)
        self.send_toolbar.hide()

    def create_icon(self):
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon.fromTheme('applications-science'))
        self.tray_icon.setToolTip('PyArchiver')

        tray_menu = QtWidgets.QMenu()
        tray_menu.addAction(self.minimize_window)
        tray_menu.addAction(self.show_window)
        tray_menu.addSeparator()
        tray_menu.addAction(self.close_window)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def create_actions(self):
        # utworz katalog
        add_key_sqn = QtGui.QKeySequence('Ctrl+D')
        self.add_catalog_acn = QtWidgets.QAction(QtGui.QIcon('icons/add_folder.png'), 'Utworz katalog',
                                                 self, triggered=self.create_catalog)
        self.add_catalog_acn.setShortcut(add_key_sqn)

        # usun katalog
        remove_key_sqn = QtGui.QKeySequence('Ctrl+R')
        self.remove_catalog_acn = QtWidgets.QAction(QtGui.QIcon('icons/remove_folder.png'), 'Usun plik',
                                                    self, triggered=self.remove_file)
        self.remove_catalog_acn.setShortcut(remove_key_sqn)

        # stworz archiwum
        create_key_sqn = QtGui.QKeySequence('Ctrl+A')
        self.create_archive_acn = QtWidgets.QAction(QtGui.QIcon('icons/lock_folder.png'),
                                                    'Uwtorz archiwum',
                                                    self,
                                                    triggered=self.create_archive)
        self.create_archive_acn.setShortcut(create_key_sqn)

        # polacz z dyskiem
        connect_key_sqn = QtGui.QKeySequence('Ctrl+C')
        self.connect_with_drive_acn = QtWidgets.QAction(QtGui.QIcon('icons/clouds.png'), 'Polacz z dyskiem', self,
                                                        triggered=self.login_widget.show)
        self.connect_with_drive_acn.setShortcut(connect_key_sqn)

        # wyslij do google drive
        send_google_key_sqn = QtGui.QKeySequence('Alt+G')
        self.send_google_acn = QtWidgets.QAction(QtGui.QIcon('icons/google_drive_2.png'), 'Google Drive', self,
                                                 triggered=self.send_google)
        self.send_google_acn.setShortcut(send_google_key_sqn)

        # wyslij do dropbox
        send_dropbox_key_sqn = QtGui.QKeySequence('Alt+D')

        self.send_dropbox_acn = QtWidgets.QAction(QtGui.QIcon('icons/dropbox_2.png'), 'Dropbox', self,
                                                  triggered=self.send_dropbox)
        self.send_dropbox_acn.setShortcut(send_dropbox_key_sqn)

        # minimalzacja, zamkniecie i maxymalizacja okna
        self.close_window = QtWidgets.QAction('Zamknij aplikacje', self, triggered=self.exit_application)
        self.minimize_window = QtWidgets.QAction('Minimalizuj aplikacje', self, triggered=self.hide)
        self.show_window = QtWidgets.QAction('Pokaz aplikacje', self, triggered=self.showNormal)
        self.show_window.setEnabled(False)

    def send_dropbox(self):
        if self.login_widget.if_dropbox():
            if not self.send_dropbox_thread.isRunning():

                path = self.model_list.filePath(self.catalog_list.currentIndex())

                self.send_dropbox_thread.set(self.loginWidget.dajDyskDropBox(), path)
                self.send_dropbox_thread.start()
                self.statusbar.showMessage('Wysylanie...', 2000)
            else:
                self.statusbar.showMessage('Aktualnie wysyłane są pliki', 2000)
        else:
            self.login_widget.panel_widget.setCurrentIndex(1)
            self.login_widget.show()

    def send_google(self):
        if self.login_widget.if_google():
            if not self.send_google_thread.isRunning():
                self.statusbar.showMessage('Wysylanie...', 2000)
                path = self.modelListy.filePath(self.listaKatalogow.currentIndex())
                self.wyslijGoogleThread.set(self.loginWidget.dajDyskGoogle(), path)
                self.wyslijGoogleThread.start()
            else:
                self.statusbar.showMessage('Aktualnie wysyłane są pliki', 2000)
        else:
            self.loginWidget.panelWidget.setCurrentIndex(0)
            self.loginWidget.show()

    def sent(self, info):
        self.statusbar.showMessage('Wyslano', 2000)
        self.tray_icon.showMessage('Wyslano', info, QtWidgets.QSystemTrayIcon.Information, 2000)

    def create_archive(self):
        index = self.catalog_list.currentIndex()
        path = os.path.abspath(self.model_list.filePath(self.catalog_list.rootIndex()))
        create_archive = CreateArchive(self.model_list, index, path, self)
        create_archive.show()

    def hideEvent(self, *args, **kwargs):
        self.show_window.setEnabled(True)
        self.minimize_window.setEnabled(False)

    def showEvent(self, *args, **kwargs):
        self.show_window.setEnabled(False)
        self.minimize_window.setEnabled(True)

    def closeEvent(self, event):
        self.exit_application()
        event.ignore()

    def exit_application(self):
        answer = QtWidgets.QMessageBox.question(self, 'Zamknięcie', 'Czy napeno chcesz zamknac aplikacje?',
                                                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                                                QtWidgets.QMessageBox.Cancel)
        if answer == QtWidgets.QMessageBox.Ok:
            QtWidgets.qApp.quit()

    def create_catalog(self):
        index = self.file_index(self.catalog_list.rootIndex())

        if not index.isValid():
            return

        if self.model_list.isDir(index):
            name, ok = QtWidgets.QInputDialog.getText(self, 'Dodaj katalog', 'Podaj nazwe katalogu')

            if ok and name:
                self.model_list.mkdir(index, name)
                self.catalog_list.setModel(self.model_list)
                self.status_bar.showMessage('Dodano katalog {name}'.format(name=name))
        else:
            return

    def remove_file(self):
        index = self.file_index(self.catalog_list.currentIndex())

        if not index.isValid():
            return

        if self.model_list.isDir(index):
            answer = QtWidgets.QMessageBox.question(self, 'Usuwanie katalogu',
                                                    'Czy napewno chcesz usunac katalog {name}'.format(
                                                                                name=self.model_list.fileName(index)),
                                                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                                                    QtWidgets.QMessageBox.Cancel)
            if answer == QtWidgets.QMessageBox.Ok:
                if self.model_list.rmdir(index):
                    self.status_bar.showMessage('Usunieto katalog {name}'.format(name=self.model_list.fileName(index)),
                                                1000)
                else:
                    self.status_bar.showMessage('Nie udalo sie usunac katalogu {name}'.format(name=self.model_list.fileName(index)),
                                                1000)
        else:
            answer = QtWidgets.QMessageBox.question(self, 'Usuwanie pliku',
                                                    'Czy napewno chcesz usunac plik {name}'.format(
                                                        name=self.model_list.fileName(index)),
                                                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
                                                    QtWidgets.QMessageBox.Cancel)
            if answer == QtWidgets.QMessageBox.Ok:
                if self.model_list.remove(index):
                    self.status_bar.showMessage('Usunieto pliku {name}'.format(name=self.model_list.fileName(index)),
                                                1000)
                else:
                    self.status_bar.showMessage('Nie udalo sie usunac pliku {name}'.format(name=self.model_list.fileName(index)),
                                                1000)

        self.catalog_list.setModel(self.model_list)
        self.model_list.refresh(self.catalog_list.rootIndex())
