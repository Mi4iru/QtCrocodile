import pickle
import socket
import threading
from queue import Queue

from PyQt6 import QtCore
from PyQt6.QtCore import QMetaObject, Qt


class Client:
    EOF = b'///'

    def __init__(self, host, port, signals):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.connected = True
        self.queue = Queue()
        self.rooms = None
        self.room = None
        self.role = False
        self.signals = signals
        threading.Thread(target=self.receive, daemon=True).start()
        threading.Thread(target=self.send, daemon=True).start()

    def get_role(self):
        return self.role

    def receive(self):
        while self.connected:
            try:
                data = self.recv()
                if not data:
                    break
                data = pickle.loads(data)
                match data['type']:
                    case 'rooms':
                        rooms = data['data']
                        self.rooms = rooms
                    case 'role':
                        QMetaObject.invokeMethod(
                            self.signals,
                            "change_role",
                            Qt.ConnectionType.QueuedConnection,
                            QtCore.Q_ARG(bool, data['data'])
                        )
                    case 'area_update':
                        new_area = data['data']
                        self.signals.area_update.emit(new_area)
                    case 'chat_msg':
                        self.signals.chat.emit(data['data'])
                    case 'access_start':
                        self.signals.access_start.emit(bool(data['data']))
                    case 'secret_word':
                        self.signals.secret_word.emit(str(data['data']))
                    case 'end_game':
                        self.signals.chat.emit(data['data'])

            except ConnectionError:
                self.connected = False
                self.socket.close()
                print('Вы были отключены')

    def send(self):
        while self.connected:
            try:
                message = self.queue.get(block=True)
                self.socket.send(message + Client.EOF)
            except ConnectionError:
                self.connected = False
                self.socket.close()
                print('Вы были отключены')

    def recv(self):
        result = bytearray()
        while True:
            data: bytes = self.socket.recv(1024)
            result.extend(data)
            if result.endswith(Client.EOF):
                break
        return result[:-3]

    def add_msg_to_queue(self, data):
        self.queue.put(pickle.dumps(data), block=False)
