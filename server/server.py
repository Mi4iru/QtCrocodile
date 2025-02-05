import socket
from room import Room
from clientHandler import ClientHandler

class Server:
    EOF = b'///'

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(10)
        self.active = False
        self.room_list = [Room(1),
                          Room(2),
                          Room(3),
                          Room(4),
                          Room(5)]

    def start(self):
        self.active = True
        print('Сервер активен, ожидание подключения игроков')
        while self.active:
            client_socket, client_address = self.socket.accept()
            print(f'Подключился клиент {client_address}')
            ClientHandler(client_socket, self.room_list)


def main():
    server = Server('127.0.0.1', port=8482)
    server.start()


if __name__ == "__main__":
    main()
