import socket
from game import Game
import pickle


class Server:

    def __init__(self, address: str, port: int, max_number: int):
        self.address = address
        self.port = port
        self.max_number = max_number
        self.game = Game()
        self.players = []
        self.number = None
        self.guess = None
        self.send_num = True

    def check_client_on_existence(self, client_addr):
        """The function checks if the player is in the list of players. If the player is new, then he is added to the
        list and information this is displayed in the server console."""

        if client_addr not in self.players:
            self.players.append(client_addr)
            print(self.players)

    def create_server(self):
        """The function creates a server and starts waiting for users to connect."""

        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.address, self.port))
        print(f'Server with address "{self.address}" and port "{self.port}" is running and waiting for connecting')

    def play(self):
        """The function that runs the game logic. We get the hidden number and update the attributes of the game (number
        attempts, and also pass the guessed number to the game) and send a notification to the second player that the
        number is guessed the first player. While the attempt to guess is not equal to the guessed number, we ask it
        from the second player. If the second the player guessed the number, we notify the players about this and
        change their places (1 becomes 2, and 2 becomes 1) and we notify you about it. Then the game is repeated."""

        while True:
            self.number = pickle.loads(self.server.recv(2048))
            self.game.reset_attributes(self.number)
            self.server.sendto(pickle.dumps('True'), self.players[1])

            while not self.number == self.guess and self.game.attempts > 0:
                self.guess = pickle.loads(self.server.recv(2048))
                check_on_correctness = pickle.dumps(self.game.guess(self.guess))
                self.server.sendto(check_on_correctness, self.players[0])
                self.server.sendto(check_on_correctness, self.players[1])

            self.players[0], self.players[1] = self.players[1], self.players[0]
            print(self.players)
            self.server.sendto(pickle.dumps((1, 2,  self.max_number)), self.players[0])
            self.server.sendto(pickle.dumps((2, 2,  self.max_number)), self.players[1])

    def main(self):
        """The main method of the server side of the application. A server is created, then in a loop we start receiving
        messages from players and check if they are on the list. Next, we look at how many players are connected. If
        one, then send him the number of players and his number, and then wait for the second player. When the second
        player connects, send to both players their number and the number of players in the game, after which the game
        begins."""

        self.create_server()
        while True:
            self.message, self.client_addr = self.server.recvfrom(2048)
            self.check_client_on_existence(self.client_addr)

            self.client_id = self.client_addr[1]
            if pickle.loads(self.message) == '__join_server':
                print(f'Client{self.client_id} has joined the chat!')

            if len(self.players) == 1:
                self.server.sendto(pickle.dumps((1, 1, self.max_number)), self.players[0])
                continue
            elif len(self.players) == 2 and self.send_num:
                self.server.sendto(pickle.dumps((1, 2, self.max_number)), self.players[0])
                self.server.sendto(pickle.dumps((2, 2, self.max_number)), self.players[1])
                self.send_num = False
                continue

            # Обработка ожидания первым игроком второго, чтобы приложение корректно работало:
            if len(self.players) == 2 and self.message == "get_data":
                continue
            elif len(self.players) == 2:
                self.play()

        self.server.close()


if __name__ == '__main__':
    server = Server('', 5001, 120)
    server.main()
