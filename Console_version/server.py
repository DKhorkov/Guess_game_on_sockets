import socket
import sys

from game import Game
import pickle


class Server:

    def __init__(self, address: str, port: int, max_number: int, attempts: int):
        self.address = address
        self.port = port
        self.max_number = max_number
        self.attempts = attempts
        self.game = Game(attempts)
        self.players = []
        self.score = {}
        self.number = None
        self.guess = None
        self.send_num = True

    def check_client_on_existence(self, client_addr):
        """The function checks if the player is in the list of players. If the player is new, then it will be added to
        the list and information about it will be displayed in the server console."""

        if client_addr not in self.players:
            self.players.append(client_addr)
            self.score[client_addr[1]] = 0
            print(f'Players list: {self.players}')
            print(f'Current score: {self.score}\n')

    def create_server(self):
        """The function creates a server and starts waiting for users to connect."""

        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.address, self.port))
        print(f'Server with address "{self.address}" and port "{self.port}" is running and waiting for connecting')

    def update_score(self) -> None:
        player_1 = self.players[0][1]
        player_2 = self.players[1][1]
        if self.number == self.guess:
            self.score[player_2] += 1
        else:
            self.score[player_1] += 1

    def play(self):
        """The function that runs the game logic. It gets the conceived number from the first player and update the
        attributes of the game (number of attempts, and also pass the guessed number to the game) and send a
        notification to the second player, that the number is conceived by the first player. While the attempt to guess
        is not equal to the guessed number, the function asks the second player to try again. If the second the player
        guessed the number, the function notifies the players about it, changes players number (1 becomes 2, and 2
        becomes 1) and notifies them about it. Then the game is repeated."""

        while True:
            self.number = pickle.loads(self.server.recv(2048))
            self.game.reset_attributes(self.number, self.attempts)
            self.guess = None
            if self.number == 'exit':
                self.server.sendto(pickle.dumps(self.number), self.players[1])
                break
            self.server.sendto(pickle.dumps('True'), self.players[1])

            while not self.number == self.guess and self.game.attempts > 0:
                self.guess = pickle.loads(self.server.recv(2048))
                if self.guess == 'exit':
                    self.server.sendto(pickle.dumps(self.guess), self.players[0])
                    sys.exit()
                check_on_correctness = pickle.dumps(self.game.guess(self.guess))
                self.server.sendto(check_on_correctness, self.players[0])
                self.server.sendto(check_on_correctness, self.players[1])

            self.update_score()
            self.players[0], self.players[1] = self.players[1], self.players[0]
            print(f'Players list: {self.players}')
            print(f'Current score: {self.score}\n')
            self.server.sendto(pickle.dumps((1, 2,  self.max_number, self.score)), self.players[0])
            self.server.sendto(pickle.dumps((2, 2,  self.max_number, self.score)), self.players[1])

    def main(self):
        """The main server side method of the application. Creates a server, then starts receiving messages from
        players and checks if the players are in the list of players. Next, it looks at how many players are
        connected. If there is only one player, then the server sends him the number of players and his number and
        waiting for the second player to connect. When the second player connects, server sends to both players their
        numbers and the number of players in the game, after which the game begins."""

        self.create_server()
        while True:
            self.message, self.client_addr = self.server.recvfrom(2048)
            self.check_client_on_existence(self.client_addr)

            self.client_id = self.client_addr[1]
            if pickle.loads(self.message) == '__join_server':
                print(f'Client{self.client_id} has joined the chat!\n')

            if len(self.players) == 1:
                self.server.sendto(pickle.dumps((1, 1, self.max_number, self.players[0][1])), self.players[0])
                continue
            elif len(self.players) == 2 and self.send_num:
                self.server.sendto(pickle.dumps((1, 2, self.max_number, self.players[0][1])), self.players[0])
                self.server.sendto(pickle.dumps((2, 2, self.max_number, self.players[1][1])), self.players[1])
                self.send_num = False
                continue

            # Обработка ожидания первым игроком второго, чтобы приложение корректно работало:
            if len(self.players) == 2 and self.message == "get_data":
                continue
            elif len(self.players) == 2:
                self.play()

        self.server.close()


if __name__ == '__main__':
    server = Server('192.168.0.108', 5001, 100, 5)
    server.main()
