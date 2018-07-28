#!/usr/bin/python
__author__ = 'piotrek'
__version__ = '3.0'

import sys

from PyQt5.Qt import QApplication
from Widgets.main_widget import MainWidget

app = None


def main():
    global app
    app = QApplication(sys.argv)

    main_widget = MainWidget()
    main_widget.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
