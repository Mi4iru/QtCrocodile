import pickle
import time

from Client.client import Client
from Client.game_window import Game
from signals import Signals

from PyQt6.QtWidgets import QMainWindow, QApplication

from design.login import Ui_Login


class Login(QMainWindow, Ui_Login):
    def __init__(self):
        super().__init__()
        signals = Signals()
        self.client = Client('127.0.0.1', 8482, signals)
        self.setupUi(self)
        default_name = str(self.client.socket.getsockname()[1])
        self.lineEdit.setPlaceholderText("anonim" + default_name)
        self.game = None
        self.show_free_rooms()
        self.show()

    def mouseMoveEvent(self, e):
        self.client.add_msg_to_queue(dict(type='free_rooms', data=None))
        self.show_free_rooms()
        time.sleep(0.01)

    def show_free_rooms(self):
        btns = [self.pushButton, self.pushButton_2, self.pushButton_3, self.pushButton_4, self.pushButton_5]
        for room in self.client.rooms:
            if not room[1]:
                btns[room[0] - 1].setDisabled(True)
            else:
                btns[room[0] - 1].setEnabled(True)
                btns[room[0] - 1].clicked.connect(lambda clicked, num=room[0]: self.enter(num))

    def enter(self, num):
        name = self.lineEdit.text()
        if not name:
            name = self.lineEdit.placeholderText()
        self.client.add_msg_to_queue(dict(data=num,
                                          name=name,
                                          type='enter'))
        self.hide()
        self.game = Game(self.client)


def main():
    app = QApplication([])

    start_window = Login()
    start_window.show()

    app.exec()


if __name__ == "__main__":
    main()
