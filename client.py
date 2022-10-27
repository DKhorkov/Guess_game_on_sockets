import socket
from time import sleep
import pickle


class Client:

    def __init__(self, address: str, port: int):
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
            message = pickle.loads(self.client.recv(2048))
            if message[0] == 'True':
                if message[1] > 0:
                    print(f'\nAnother player guessed the num in {5 - message[1]} attempts. U lost...')
                else:
                    print("\nAnother player didn't guess the num. U won!")
                self.player_number, self.number_of_players = pickle.loads(self.client.recv(2048))
                print("Now u'r player 2!\n")
                break
            print(f"Second player didn't guess the correct num. He thought, it was {message[3]} and now"
                  f"has {message[1]} attempts!\n")

    def p2_cycle(self):
        """Цикл для второго игрока. Он пробует угадать загаданное первым игроком число и отправляет его на сервер.
        Далее ждет от сервера ответа. Если ответ положительный, то второй игрок победил -> Ждем ответа от сервера,
        чтобы поменяться местами. Если ответ положительный - пытаемся угадать снова."""
        while True:
            guess = pickle.dumps(self.check_input(input('Guess num: ')))
            self.client.send(guess)
            message = pickle.loads(self.client.recv(2048))
            if message[0] == 'True':
                print(f'\n{message[2]}')
                self.player_number, self.number_of_players = pickle.loads(self.client.recv(2048))
                print("Now u'r player 1!")
                break
            print(f'\n{message[2]}')

    @staticmethod
    def check_input(user_input: str) -> int:
        while not user_input.isdecimal():
            user_input = input('U made mistake. U should enter an integer number. Pls, try again: ')
        return int(user_input)

    def main(self):
        """Основная функция клиентской части. Подключается к серверу и отправляет стартовое сообщение. Далее получает
        номер игрока и количество игроков в игре. Если мы единственный игрок, отправляем запрос на обновлении информации
        об игроках на сервер. Если игроков двое - начинается игра."""
        self.connect_to_server()
        self.client.send(pickle.dumps('__join_server'))
        self.player_number, self.number_of_players = pickle.loads(self.client.recv(2048))

        while True:
            if self.player_number == 1 and self.number_of_players == 2:
                number_to_guess = pickle.dumps(self.check_input(input('Enter num to guess: ')))
                self.client.send(number_to_guess)
                self.p1_cycle()

            elif self.player_number == 2 and self.number_of_players == 2:
                print('Waiting for 1st player to choose the number...')
                self.number_chosen = bool(pickle.loads(self.client.recv(2048)))
                print('\nNumber was chosen! Now, try to guess it!')
                self.p2_cycle()

            else:
                print('Waiting for second player...')
                self.client.send(pickle.dumps('get_data'))
                sleep(5)
                self.player_number, self.number_of_players = pickle.loads(self.client.recv(2048))


if __name__ == '__main__':
    client = Client('', 5001)
    client.main()
