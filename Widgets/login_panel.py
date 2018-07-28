__author__ = 'piotrek'

import webbrowser

from googleapiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
import oauth2client
import dropbox
import httplib2

from PyQt5 import QtWidgets
from PyQt5 import QtCore


class LoginPanel(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(400, 300)
        self.setMinimumSize(self.size())
        self.setMaximumSize(self.size())
        self.setWindowTitle('Zaloguj')

        self.connected_with_google = False
        self.connected_with_dropbox = False

        self.panel_widget = QtWidgets.QTabWidget()

        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.create_panel_google()
        self.create_panel_dropbox()
        self.create_layout_google()
        self.create_layout_dropbox()

        main_layout = QtWidgets.QGridLayout()
        main_layout.addWidget(self.panel_widget, 0, 1, 1, 1)
        self.setLayout(main_layout)
        self.panel_widget.setCurrentIndex(0)

    def if_google(self):
        return self.connected_with_google

    def if_dropbox(self):
        return self.connected_with_dropbox

    def create_panel_google(self):

        self.google_widget = QtWidgets.QWidget()
        self.google_edit = QtWidgets.QLineEdit()
        self.google_edit.installEventFilter(self)
        self.google_btn = QtWidgets.QPushButton('Przejdz')
        self.google_btn.clicked.connect(self.go_to_google)  # slot
        self.google_lbl = QtWidgets.QLabel('Podaj kod weryfikacyjny')
        self.google_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.google_lbl.setWordWrap(True)
        self.google_wer_edit = QtWidgets.QLineEdit()
        self.google_accept_btn = QtWidgets.QPushButton('Akceptuj', clicked=self.google_accept)
        self.google_close_btn = QtWidgets.QPushButton('Zamknij', clicked=self.close)
        self.google_flow = None
        self.google_drive = None

        self.panel_widget.addTab(self.google_widget, 'Google Drive')
        self.google_accepted = False

    def create_panel_dropbox(self):
        self.dropbox_widget = QtWidgets.QWidget()
        self.dropbox_edit = QtWidgets.QLineEdit()
        self.dropbox_edit.installEventFilter(self)
        self.dropbox_btn = QtWidgets.QPushButton('Przejdz')
        self.dropbox_btn.clicked.connect(self.go_to_dropbox)
        self.dropbox_lbl = QtWidgets.QLabel('Podaj kod weryfikacyjny')
        self.dropbox_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.dropbox_lbl.setWordWrap(True)
        self.dropbox_wer_edit = QtWidgets.QLineEdit()
        self.dropbox_accept_btn = QtWidgets.QPushButton('Akceptuj', clicked=self.dropbox_accept)
        self.dropbox_close_btn = QtWidgets.QPushButton('Zamknij', clicked=self.close)
        self.dropbox_flow = None
        self.dropbox_drive = None

        self.panel_widget.addTab(self.dropbox_widget, 'Dropbox')
        self.dropbox_accepted = False

    def eventFilter(self, Object, Event):
        if Object == self.google_edit or Object == self.dropbox_edit:
            if Event.type() == QtCore.QEvent.MouseButtonPress:
                Object.selectAll()
                return True
        return False

    def page_click(self):
        self.sender().selectAll()

    def set_google_flow(self, flow):
        self.google_flow = flow

    def set_dropbox_flow(self, flow):
        self.dropbox_flow = flow

    def google_accept(self):
        self.google_accepted = True
        self.google_verify()

    def showEvent(self, QShowEvent):
        if not self.google_accepted:
            self.google_lbl.setText('Podaj kod weryfikacyjny')

        if not self.dropbox_accepted:
            self.dropbox_lbl.setText('Podaj kod weryfikacyjny')

    def dropbox_accept(self):
        self.dropbox_flow.setEnabled(False)
        self.dropbox_accepted = self.dropbox_verify()
        self.dropbox_flow.setEnabled(True)

    def go_to_google(self):
        webbrowser.open(self.google_edit.text())

    def go_to_dropbox(self):
        webbrowser.open(self.dropbox_edit.text())

    def create_layout_google(self):
        main_layout_gle = QtWidgets.QVBoxLayout()

        h_layout_gle = QtWidgets.QHBoxLayout()
        h_layout_gle.addWidget(self.google_edit)
        h_layout_gle.addWidget(self.google_btn)

        space_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Minimum)
        space_2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Minimum)
        space_3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Minimum)
        space_4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Minimum)
        main_layout_gle.addItem(space_1)
        main_layout_gle.addLayout(h_layout_gle)
        main_layout_gle.addItem(space_2)
        main_layout_gle.addWidget(self.google_lbl)
        main_layout_gle.addItem(space_3)
        main_layout_gle.addWidget(self.google_wer_edit)
        main_layout_gle.addItem(space_4)
        main_layout_gle.addWidget(self.google_accept_btn)
        main_layout_gle.addWidget(self.google_close_btn)
        self.google_widget.setLayout(main_layout_gle)

    def create_layout_dropbox(self):
        main_layout_box = QtWidgets.QVBoxLayout()

        h_layout_box = QtWidgets.QHBoxLayout()
        h_layout_box.addWidget(self.dropbox_edit)
        h_layout_box.addWidget(self.dropbox_btn)

        space_1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Minimum)
        space_2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Minimum)
        space_3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Minimum)
        space_4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Minimum)
        main_layout_box.addItem(space_1)
        main_layout_box.addLayout(h_layout_box)
        main_layout_box.addItem(space_2)
        main_layout_box.addWidget(self.dropbox_lbl)
        main_layout_box.addItem(space_3)
        main_layout_box.addWidget(self.dropbox_wer_edit)
        main_layout_box.addItem(space_4)
        main_layout_box.addWidget(self.dropbox_accept_btn)
        main_layout_box.addWidget(self.dropbox_close_btn)
        self.dropbox_widget.setLayout(main_layout_box)

    def google_verify(self):
        code = self.google_wer_edit.text().strip()
        try:
            credentials = self.google_flow.step2_exchange(code)
        except oauth2client.client.FlowExchangeError:
            self.google_lbl.setText('Podano bledny kod weryfikacyjny')
            return False
        http = httplib2.Http()
        http = credentials.authorize(http)
        drive = build('drive', 'v2', http=http)
        self.google_drive = drive
        google_client = self.google_drive.about().get().execute()['name']
        self.google_lbl.setText('Zalogowano: {0}'.format(google_client))
        self.google_accept_btn.setEnabled(False)
        self.connected_with_google = True
        return True

    def dropbox_verify(self):
        code = self.dropbox_wer_edit.text().strip()
        try:
            access_token, user_id = self.dropbox_flow.finish(code)
        except dropbox.rest.ErrorResponse:
            self.dropbox_lbl.setText('Podano bledny kod weryfikacyjny')
            return False
        self.dropbox_drive = dropbox.client.DropboxClient(access_token)
        dropbox_client = self.dropbox_drive.account_info()['display_name']
        self.dropbox_lbl.setText('Zalogowano: {0}'.format(dropbox_client))
        self.dropbox_accept_btn.setEnabled(False)
        self.connected_with_dropbox = True

        return True

    def get_dropbox_drive(self):
        return self.dropbox_drive

    def get_google_drive(self):
        return self.google_drive
