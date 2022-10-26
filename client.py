import socket
from time import sleep


class Client:

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.player_number = None
        self.number_of_players = None
        self.number_chosen = False

    def connect_to_server(self):
        """Функция, устанавливающая соединение с сервером."""
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.connect((self.address, self.port))

    def p1_cycle(self):
        """Цикл для первого игрока. Он загадывает число и отправляет его на сервер. Далее ждет, когда второй игрок
        попробует отгадать число. Если он угадывает, получаем от сервера положительный ответ -> меняемся местами
        со вторым игроком. Если ответ отрицательный - ждем очередной попытки от второго игрока."""
        while True:
            print('\nWaiting for 2nd player to guess the number...')
            message = self.client.recv(2048).decode('utf-8')
            if message == 'True':
                print('Another player guessed the num')
                self.player_number, self.number_of_players = self.client.recv(2048).decode('utf-8').split(',')
                print("Now u'r player 2!\n")
                break
            print("Second player didn't guess the correct num\n")

    def p2_cycle(self):
        """Цикл для второго игрока. Он пробует угадать загаданное первым игроком число и отправляет его на сервер.
        Далее ждет от сервера ответа. Если ответ положительный, то второй игрок победил -> Ждем ответа от сервера,
        чтобы поменяться местами. Если ответ положительный - пытаемся угадать снова."""
        while True:
            guess = input('Guess num: ').encode('utf-8')
            self.client.send(guess)
            message = self.client.recv(2048).decode('utf-8')
            if message == 'True':
                print('\nU won')
                self.player_number, self.number_of_players = self.client.recv(2048).decode('utf-8').split(',')
                print("Now u'r player 1!")
                break
            print('\nNope, try again')

    def main(self):
        """Основная функция клиентской части. Подключается к серверу и отправляет стартовое сообщение. Далее получает
        номер игрока и количество игроков в игре. Если мы единственный игрок, отправляем запрос на обновлении информации
        об игроках на сервер. Если игроков двое - начинается игра."""
        self.connect_to_server()
        self.client.send('__join_server'.encode('utf-8'))
        self.player_number, self.number_of_players = self.client.recv(2048).decode('utf-8').split(',')

        while True:
            if int(self.player_number) == 1 and int(self.number_of_players) == 2:
                number_to_guess = input('Enter num to guess: ').encode('utf-8')
                self.client.send(number_to_guess)
                self.p1_cycle()

            elif int(self.player_number) == 2 and int(self.number_of_players) == 2:
                print('Waiting for 1st player to choose the number...')
                self.number_chosen = bool(self.client.recv(2048).decode('utf-8'))
                print('\nNumber was chosen! Now, try to guess it!')
                self.p2_cycle()

            else:
                print('Waiting for second player...')
                self.client.send('get_data'.encode('utf-8'))
                sleep(5)
                self.player_number, self.number_of_players = self.client.recv(2048).decode('utf-8').split(',')


if __name__ == '__main__':
    client = Client('', 5001)
    client.main()
