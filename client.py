import socket
from time import sleep


class Client:

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.player_number = None
        self.number_of_players = None

    def connect_to_server(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.connect((self.address, self.port))

    def main(self):
        self.connect_to_server()
        self.client.send('__join_server'.encode('utf-8'))
        self.player_number, self.number_of_players = self.client.recv(2048).decode('utf-8').split(',')

        while True:
            if int(self.player_number) == 1 and int(self.number_of_players) == 2:
                number_to_guess = input('Enter num to guess: ').encode('utf-8')
                self.client.send(number_to_guess)
                while True:
                    message = self.client.recv(2048).decode('utf-8')
                    print(message)
                    if message == 'True':
                        print('Another player guessed the num')
                        break
                    print("Second player didn't guess the correct num")
            elif int(self.player_number) == 2 and int(self.number_of_players) == 2:
                while True:
                    guess = int(input('Guess num: '))
                    self.client.send(guess)
                    message = self.client.recv(2048).decode('utf-8')
                    if message == 'True':
                        print('u won')
                        break
                    print('Nope, try again')
            else:
                print('Waiting for second player')
                self.client.send('get_data'.encode('utf-8'))
                sleep(5)
                self.player_number, self.number_of_players = self.client.recv(2048).decode('utf-8').split(',')


if __name__ == '__main__':
    client = Client('', 5001)
    client.main()
