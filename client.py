import socket
from time import sleep
import pickle


class Client:

    def __init__(self, address: str, port: int):
        self.address = address
        self.port = port
        self.player_number = None
        self.number_of_players = None
        self.max_number = None
        self.number_chosen = False

    def connect_to_server(self):
        """A function that establishes a connection to the server."""

        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.connect((self.address, self.port))

    def p1_cycle(self):
        """Loop for the first player. The first player conceives a number and sends it to the server. Then the first
        player waits for the second player trying to guess the number. If second player guesses the number, the first
        player will get a positive response from the server -> change places with the second player. If the answer is
        negative, the first player waits for the next attempt from the second player."""

        while True:
            print('\nWaiting for 2nd player to guess the number...')
            message = pickle.loads(self.client.recv(2048))
            print(message)
            if message[0] == 'True':
                if message[1] > 0:
                    print(f'\nAnother player guessed the num in {5 - message[1]} attempts. U lost...')
                else:
                    print("\nAnother player didn't guess the num. U won!")
                self.player_number, self.number_of_players, self.max_number = pickle.loads(self.client.recv(2048))
                print("Now u'r player 2!\n")
                break
            print(f"Second player didn't guess the correct num. He thought, it was {message[3]} and now"
                  f"has {message[1]} attempts!\n")

    def p2_cycle(self):
        """Loop for the second player. The second player tries to guess the number conceived by the first player and
        sends it to the server. Then the second player waits for a response from the server. If the answer is positive,
        then the second player won -> wait for a response from the server, to change places. If the answer is negative,
        the second player tries to guess again."""

        while True:
            guess = pickle.dumps(self.check_input(input('Guess num: ')))
            self.client.send(guess)
            message = pickle.loads(self.client.recv(2048))
            if message[0] == 'True':
                print(f'\n{message[2]}')
                self.player_number, self.number_of_players, self.max_number = pickle.loads(self.client.recv(2048))
                print("Now u'r player 1!")
                break
            print(f'\n{message[2]}')

    def check_input(self, user_input: str) -> int:
        """This method checks the user's input for the validity of the data format: only integers in valid in
        range from zero to the maximum number, specified when the server was created."""

        while not user_input.isdecimal():
            user_input = input(f'U made mistake. U should enter an integer number between 0 and {self.max_number} '
                               f'inclusively. Pls, try again: ')
        while not 0 <= int(user_input) <= self.max_number:
            user_input = self.check_input(input(f'U made mistake. U should enter an integer number between 0 and '
                                                f'{self.max_number} inclusively. Pls, try again: '))
        return int(user_input)

    def main(self):
        """The main function of the client side. Connects to the server and sends a start message. Next gets player
        number and number of players in the game. If we are the only player, send a request to update information
        about the players on the server. If there are two players, the game starts."""

        self.connect_to_server()
        self.client.send(pickle.dumps('__join_server'))
        self.player_number, self.number_of_players, self.max_number = pickle.loads(self.client.recv(2048))

        while True:
            if self.player_number == 1 and self.number_of_players == 2:
                number_to_guess = pickle.dumps(self.check_input(input(f'Enter an integer number to guess between 0 and '
                                                                      f'{self.max_number} inclusively: ')))
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
                self.player_number, self.number_of_players, self.max_number = pickle.loads(self.client.recv(2048))


if __name__ == '__main__':
    client = Client('', 5001)
    client.main()
