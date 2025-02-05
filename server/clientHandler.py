import pickle
from threading import Thread

EOF = b'///'


class ClientHandler(Thread):
    def __init__(self, client, rooms):
        super().__init__()
        self.client = client
        self.rooms = rooms
        self.room = None
        self.name = ''
        self.get_rooms()
        self.start()

    def run(self):
        while True:
            try:
                data = self.recv()
                if not data:
                    break
                data = pickle.loads(data)
                package_type = data['type']
                package_data = data['data']
                match package_type:
                    case 'enter':
                        self.name = data['name']
                        self.enter_room(package_data, self.name)
                    case 'area_update':
                        self.room.broadcast(data, except_client=self.client)
                    case 'chat_msg':
                        self.room.broadcast(dict(type='chat_msg', data=self.name + ': ' + package_data),
                                            except_client=self.client)
                        self.room.check(package_data, self.name)
                    case 'start_game':
                        if package_data:
                            self.room.start_game()
                    case 'access_start':
                        self.room.broadcast(dict(type='access_start', data=True))
                    case 'free_rooms':
                        self.get_rooms()
            except Exception as e:
                print(e)
                self.room.remove(self.name)
                print(f'Клиент {self.name} отключен от сервера')
                break

    def get_rooms(self):
        self.client.send(pickle.dumps(dict(data=[(r.name, r.ready) for r in self.rooms],
                                           type='rooms')) + EOF)

    def enter_room(self, room, name):
        self.room = self.rooms[room - 1]
        self.room.add_client(self.client, name)

    def recv(self):
        result = bytearray()
        while True:
            data: bytes = self.client.recv(1024)
            result.extend(data)
            if result.endswith(EOF):
                break
        return result[:-3]
