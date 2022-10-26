import socket
from game import Game
from time import sleep


class Server:

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.game = Game()
        self.players = []
        self.number = None
        self.guess = None
        self.send_num = True

    def check_client_on_existence(self, client_addr):
        """Функция проверяет, есть ли игрок в списке игроков. Если игрок новый - то он добавляется в список и информация
        об этом выводится в консоль сервера."""
        if client_addr not in self.players:
            self.players.append(client_addr)
            print(self.players)

    def create_server(self):
        """Функция создает сервер и начинает ждать подключения пользователей."""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.address, self.port))
        print(f'Server with address "{self.address}" and port "{self.port}" is running and waiting for connecting')

    def play(self):
        """Основная функция, запускающая игровую логику. Получаем загаданное число и обновляем атрибуты игры (кол-во
        попыток, а также передаем загаданное число в игру) и отправляем уведомление второму игроку, что число загадано
        первым игроком. Пока попытка отгадать не равна загаданному числу, запрашиваем его у второго игрока. Если второй
        игрок угадал число, уведомляем игроков об этом и меняем их местами (1 становится 2, а 2 становится 1) и
        уведомляем об этом. Затем игра повторяется."""
        while True:
            self.number = self.server.recv(2048).decode('utf-8')
            self.game.reset_attributes(self.number)
            self.guess = None
            self.server.sendto('True'.encode('utf-8'), self.players[1])
            while not self.number == self.guess:
                self.guess = self.server.recv(2048).decode('utf-8')
                check_on_correctness = str(self.game.guess(self.guess)).encode('utf-8')
                self.server.sendto(check_on_correctness, self.players[0])
                self.server.sendto(check_on_correctness, self.players[1])
            self.players[0], self.players[1] = self.players[1], self.players[0]
            print(self.players)
            self.server.sendto('1,2'.encode('utf-8'), self.players[0])
            self.server.sendto('2,2'.encode('utf-8'), self.players[1])

    def main(self):
        """Основной метод серверной части приложения. Создается сервер, затем в цикле начинаем принимать сообщения от
        игроков и проверяем их на наличие в списке. Дальше смотрим, сколько игроков подключено. Если один, то отправляем
        ему количество игроков и его номер, а затем ждем второго игрока. Когда подключится второй игрок, отправляем
        обоим игрокам их номер и количество игроков в игре, после чего начинается игра."""
        self.create_server()
        while True:
            self.message, self.client_addr = self.server.recvfrom(2048)
            self.check_client_on_existence(self.client_addr)

            self.client_id = self.client_addr[1]
            if self.message.decode('utf-8') == '__join_server':
                print(f'Client{self.client_id} has joined the chat!')

            if len(self.players) == 1:
                self.server.sendto('1,1'.encode('utf-8'), self.players[0])
                continue
            elif len(self.players) == 2 and self.send_num:
                self.server.sendto('1,2'.encode('utf-8'), self.players[0])
                self.server.sendto('2,2'.encode('utf-8'), self.players[1])
                self.send_num = False
                continue

            # Обработка ожидания первым игроком второго, чтобы приложение корректно работало:
            if len(self.players) == 2 and self.message == "get_data":
                continue
            elif len(self.players) == 2:
                self.play()

        self.server.close()


if __name__ == '__main__':
    server = Server('', 5001)
    server.main()
