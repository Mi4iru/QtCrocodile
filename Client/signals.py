from PyQt6.QtCore import QObject, QByteArray, pyqtSignal


class Signals(QObject):
    area_update = pyqtSignal(QByteArray)
    change_role = pyqtSignal(bool)
    chat = pyqtSignal(str)
    access_start = pyqtSignal(bool)
    secret_word = pyqtSignal(str)
