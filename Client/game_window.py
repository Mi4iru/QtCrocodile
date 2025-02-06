from design.game import Ui_Game

from PyQt6 import QtGui
from PyQt6.QtCore import QByteArray, QBuffer, pyqtSlot
from PyQt6.QtGui import QPixmap, QTextCursor
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt
from random import randint


class Game(QMainWindow, Ui_Game):
    def __init__(self, client):
        super().__init__()
        self.last_y = None
        self.last_x = None
        self.client = client
        self.enable_start = False
        self.role = False
        self.drawing_access = False
        self.setupUi(self)
        self.client.signals.area_update.connect(self.area_update)
        self.client.signals.change_role.connect(self.set_role)
        self.client.signals.chat.connect(self.update_chat)
        self.client.signals.access_start.connect(self.access_start_button)
        self.client.signals.secret_word.connect(self.out_secret_word)
        self.send.clicked.connect(self.send_msg_chat)
        self.input.returnPressed.connect(self.send_msg_chat)
        self.startGame.clicked.connect(self.start_game)
        self.startGame.setDisabled(True)
        self.pen = QtGui.QPen(QtGui.QColor(randint(0, 255), randint(0, 255), randint(0, 255)))
        self.pen.setWidth(3)
        self.drawer()
        self.show()

    def drawer(self):
        canvas = QtGui.QPixmap(800, 600)
        canvas.fill(Qt.GlobalColor.white)
        self.label.setPixmap(canvas)
        self.last_x, self.last_y = None, None

    def mouseMoveEvent(self, e):
        if not self.last_x or not self.role or not self.drawing_access:
            self.last_x = int(e.position().x())
            self.last_y = int(e.position().y())
            return

        canvas = self.label.pixmap()
        painter = QtGui.QPainter(canvas)
        painter.setPen(self.pen)
        painter.drawLine(self.last_x, self.last_y, int(e.position().x()), int(e.position().y()))
        painter.end()
        self.label.setPixmap(canvas)

        self.last_x = int(e.position().x())
        self.last_y = int(e.position().y())

        self.pixmap_to_bytes()

    def mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None

    def start_game(self):
        self.client.add_msg_to_queue(dict(type='start_game', data=True))

    def pixmap_to_bytes(self):
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QBuffer.OpenModeFlag.WriteOnly)
        self.label.pixmap().save(buffer, "PNG")
        self.client.add_msg_to_queue(dict(type='area_update', data=byte_array.data()))

    @pyqtSlot(QByteArray)
    def area_update(self, canvas):
        pixmap = QPixmap()
        pixmap.loadFromData(canvas, "PNG")
        self.label.setPixmap(QtGui.QPixmap(pixmap))

    @pyqtSlot(bool)
    def set_role(self, role):
        self.role = role
        if self.enable_start and role:
            self.startGame.setEnabled(True)
        if not role:
            self.drawing_access = False

    def send_msg_chat(self):
        text = self.input.text()
        self.input.clear()
        if text:
            self.chat.append('you: ' + text)
            self.chat.moveCursor(QTextCursor.MoveOperation.End)
            self.client.add_msg_to_queue(dict(data=text, type='chat_msg'))

    @pyqtSlot(str)
    def update_chat(self, msg):
        self.chat.append(msg)
        self.chat.moveCursor(QTextCursor.MoveOperation.End)

    @pyqtSlot(bool)
    def access_start_button(self, state):
        canvas = QtGui.QPixmap(800, 600)
        canvas.fill(Qt.GlobalColor.white)
        self.label.setPixmap(canvas)

        self.enable_start = state
        if self.role:
            self.startGame.setEnabled(True)
        if not state:
            self.startGame.setDisabled(True)

    @pyqtSlot(str)
    def out_secret_word(self, word):
        self.chat.append(f'Ваше слово на эту игру: {word}')
        self.drawing_access = True
