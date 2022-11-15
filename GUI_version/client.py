import socket
import sys
from docopt import docopt
from time import sleep
import pickle

from configs import CONNECTION_TO_SERVER_TIMEOUT

DOCOPT_USAGE = f"""
    Usage:
        server.py -h | --help
        server.py --ip_address=<nums> --port=<int>

    Options:
        -h --help               Show this screen.
        --ip_address=<nums>     Address of server to connect to (Example:192.168.0.108).
        --port=<int>            Port of server to connect to (Example: 5000).
"""


class Client:

    def __init__(self, address: str, port: int):
        self.address = address
        self.port = port
        self.player_number = None
        self.player_id = None
        self.score = None
        self.number_of_players = None
        self.max_number = None
        self.number_chosen = False
        self.number_to_guess = None

    def connect_to_server(self):
        """A function that establishes a connection to the server. If there is no connection in fixed time, exit
        connection."""

        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.settimeout(CONNECTION_TO_SERVER_TIMEOUT)
        self.client.connect((self.address, self.port))

    def print_score(self):
        """Function, which prints current score in console."""

        opponent_id = [key for key in self.score.keys() if key != self.player_id][0]
        print((f'\n\U0001F451 Current score \U0001F451 \n'
               f'You: {self.score[self.player_id]}\n'
               f'Opponent: {self.score[opponent_id]}'))
        print(f"\n\U0001F501 Now u'r player {self.player_number}! \U0001F501 \n")

    def p1_cycle(self):
        """Loop for the first player. The first player conceives a number and sends it to the server. Then the first
        player waits for the second player trying to guess the number. If second player guesses the number, the first
        player will get a positive response from the server -> change places with the second player. If the answer is
        negative, the first player waits for the next attempt from the second player."""

        while True:
            print('\n\U000023F3 Waiting for second player to guess the number... \U000023F3 ')
            message = pickle.loads(self.client.recv(2048))
            if message == 'exit':
                print('\n\U0001F6AA Second player left the game! You won! See you soon! \U0001F596 \n')
                sys.exit()
            if message[0] == 'True':
                if message[1] >= 0 and self.number_to_guess == message[3]:
                    print(f'\n\U0001F480 Another player guessed the num in {5 - message[1]} attempts. U lost... '
                          f'\U0001F480 ')
                else:
                    print(f"\n\U0001F973 U won! Second player didn't guess the correct num. He thought, "
                          f"it was {message[3]}. \U0001F973 ")
                self.player_number, self.number_of_players, self.max_number, self.score = \
                    pickle.loads(self.client.recv(2048))
                self.print_score()
                break
            print(f"\U0001F514 Second player didn't guess the correct num. He thought, it was {message[3]} and now "
                  f"has {message[1]} attempts! \U0001F514 ")

    def p2_cycle(self):
        """Loop for the second player. The second player tries to guess the number conceived by the first player and
        sends it to the server. Then the second player waits for a response from the server. If the answer is positive,
        then the second player won -> wait for a response from the server, to change places. If the answer is negative,
        the second player tries to guess again."""

        while True:
            guess = self.check_input(input('\U0001F3F9 Guess the num or enter "exit" to end the game: '))
            self.client.send(pickle.dumps(guess))
            if guess == 'exit':
                print('\n\U0001F596 Thanks for the game! See you soon! \U0001F596 \n')
                sys.exit()
            message = pickle.loads(self.client.recv(2048))
            if message == 'exit':
                print('\n\U0001F6AA Second player left the game! See you soon! \U0001F596 \n')
            if message[0] == 'True':
                print(f'\n\U0001F973 {message[2]} \U0001F973 ')
                self.player_number, self.number_of_players, self.max_number, self.score = \
                    pickle.loads(self.client.recv(2048))
                self.print_score()
                break
            print(f'\n\U0001F514 {message[2]} \U0001F514 ')

    def check_input(self, user_input: str) -> int or str:
        """This method checks the user's input for the validity of the data format: only integers in valid in
        range from zero to the maximum number, specified when the server was created."""

        if user_input.lower() == 'exit':
            return 'exit'

        while not user_input.isdecimal():
            user_input = input(f'\n\U000026D4 U made mistake. U should enter an integer number between 0 and '
                               f'{self.max_number} inclusively. Enter "exit" to end the game. Pls, try again: ')
        while not 0 <= int(user_input) <= self.max_number:
            user_input = self.check_input(input(f'\n\U000026D4 U made mistake. U should enter an integer number between'
                                                f' 0 and {self.max_number} inclusively. Enter "exit" to end the game. '
                                                f'Pls, try again: '))
        return int(user_input)

    def main(self):
        """The main function of the client side. Connects to the server and sends a start message. Next gets player
        number and number of players in the game. If we are the only player, send a request to update information
        about the players on the server. If there are two players, the game starts."""

        self.connect_to_server()
        self.client.send(pickle.dumps('__join_server'))
        self.player_number, self.number_of_players, self.max_number, self.player_id = \
            pickle.loads(self.client.recv(2048))

        while True:
            if self.player_number == 1 and self.number_of_players == 2:
                self.number_to_guess = self.check_input(
                    input(f'\U0001F6E1 Enter an integer number between 0 and {self.max_number} '
                          f'inclusively, which second player should guess or enter "exit" to end the game: '))
                self.client.send(pickle.dumps(self.number_to_guess))
                if self.number_to_guess == 'exit':
                    print('\n\U0001F596 Thanks for the game! See you soon! \U0001F596 \n')
                    sys.exit()
                self.p1_cycle()

            elif self.player_number == 2 and self.number_of_players == 2:
                print('\U000023F3 Waiting for first player to choose the number... \U000023F3 ')
                num = pickle.loads(self.client.recv(2048))
                if num == 'exit':
                    print('\n\U0001F6AA First player left the game! See you soon! \U0001F596 \n')
                    sys.exit()
                self.number_chosen = bool(num)
                print('\n\U0001F3AF Number was chosen! Now, try to guess it! \U0001F3AF ')
                self.p2_cycle()

            else:
                print('\U000023F3 Waiting for second player... \U000023F3 ')
                self.client.send(pickle.dumps('get_data'))
                sleep(5)
                self.player_number, self.number_of_players, self.max_number, self.player_id = \
                    pickle.loads(self.client.recv(2048))


if __name__ == '__main__':
    args = docopt(DOCOPT_USAGE)
    client = Client(args['--ip_address'], int(args['--port']))
    client.main()
