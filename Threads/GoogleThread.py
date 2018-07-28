__author__ = 'piotrek'

import mimetypes

from PyQt5 import QtCore
from googleapiclient.http import MediaFileUpload


class GoogleThread(QtCore.QThread):

    sent_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def ustaw(self, drive, path):
        self.drive = drive
        self.path = path

    def run(self):
        name = str(QtCore.QFileInfo(self.path).fileName())

        mime_type = mimetypes.guess_type(self.path)[0]
        media_body = MediaFileUpload(self.path, mimetype=mime_type, resumable=True)
        body = {
            'title': name,
            'description': 'Dokument z PyArchiver 3',
            'mimeType': mime_type,
        }

        self.drive.files().insert(body=body, media_body=media_body).execute()

        self.sent_signal.emit('Wyslano plik na dysk Google Drive')
