import pickle
import random
import time

from PyQt6.QtCore import QByteArray, QBuffer
from PyQt6 import QtWidgets

EOF = b'///'


class Room:
    def __init__(self, name):
        self.name = name
        self.ready = True
        self.clients = []
        self.clients_names = []
        self.word = ''
        self.timer = None
        self.drawer = None

    def broadcast(self, package, except_client=None):
        for client in self.clients:
            if client != except_client:
                client.send(pickle.dumps(package) + EOF)

    def add_client(self, client, name):
        self.clients.append(client)
        self.clients_names.append(name)
        if not self.drawer:
            self.drawer = name
            client.send(pickle.dumps(dict(type='role', data=True)) + EOF)
        if len(self.clients) > 1 and self.ready:
            self.broadcast(dict(type='access_start', data=True))

    def start_game(self):
        self.ready = False
        with open("words.txt", 'r') as f:
            database = [w.rstrip() for w in f.readlines()]
        self.word = random.choice(database)
        print(self.word)
        self.clients[self.clients_names.index(self.drawer)].send(pickle.dumps(dict(
            type='secret_word',
            data=self.word)) + EOF)
        self.broadcast(dict(type='access_start', data=False))

    def remove(self, client):
        if self.drawer == client:
            self.drawer = None
        index = self.clients_names.index(client)
        del self.clients[index]
        del self.clients_names[index]

    def check(self, word, client):
        if word == self.word and client != self.drawer:
            self.broadcast(dict(type='end_game', data=f'Игрок: {client} угадал слово!'))
            time.sleep(0.1)
            self.broadcast(dict(type='role', data=False))
            time.sleep(0.1)
            next_drawer = self.clients[self.clients_names.index(client)]
            next_drawer.send(pickle.dumps(dict(type='role', data=True)) + EOF)
            time.sleep(0.1)
            self.drawer = client
            self.end_game()

    def end_game(self):
        self.ready = True
        self.broadcast(dict(type='chat_msg',
                            data=f'Игра окончена, следующий ведущий {self.drawer}'))
        time.sleep(0.1)
        self.broadcast(dict(type='access_start', data=True))

