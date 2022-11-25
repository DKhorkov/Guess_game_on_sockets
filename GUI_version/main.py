import pickle
import socket
import sys
import tkinter
from tkinter import ttk, END
from tkinter import messagebox as msg
from subprocess import Popen, PIPE, STDOUT

from configs import START_WINDOW_HEIGHT, START_WINDOW_TITLE, START_WINDOW_WIDTH, ATTEMPTS, MAX_NUMBER_TO_CONCEIVE, \
    GAME_WINDOW_TITLE, GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT, CONNECTION_TO_SERVER_TIMEOUT, TABS, PARAGRAPHS


class Main:

    def __init__(self):
        """Создаем стартовый ГУИ, добавляем ему название и размеры."""

        self.start_window = tkinter.Tk()
        self.start_window.title(START_WINDOW_TITLE)
        self.start_window.geometry(f'{START_WINDOW_WIDTH}x{START_WINDOW_HEIGHT}')
        self.__create_tabs()
        self.__fill_server_tab()
        self.__fill_client_tab()
        self.__create_server_label()
        self.__connection_to_server_label()

        self.client_process = None
        self.notification = None
        self.number_to_guess = None
        self.num_after_check = None
        self.score = None
        self.last_message = None

    def __game_window(self):
        self.game_window = tkinter.Tk()
        self.game_window.title(GAME_WINDOW_TITLE)
        self.game_window.geometry(f'{GAME_WINDOW_WIDTH}x{GAME_WINDOW_HEIGHT}')
        self.user_input = tkinter.StringVar()
        self.log = tkinter.Text(self.game_window)
        self.msg = tkinter.Entry(self.game_window, textvariable=self.user_input)
        self.msg.pack(side='bottom', fill='x', expand=1, ipady=20)
        self.log.pack(side='top', fill='both', expand=1)
        self.send_message_button = tkinter.Button(self.game_window, text='Send', width=17,
                                                  command=self.__send_message)
        self.send_message_button.pack(side='bottom')

    def __send_message(self):
        self.user_input.set(self.msg.get())
        self.msg.delete(0, END)

    def __check_input(self, user_input: str) -> int or str:
        """This method checks the user's input for the validity of the data format: only integers in valid in
        range from zero to the maximum number, specified when the server was created."""

        if user_input.lower() == 'exit':
            return 'exit'
        if not user_input.isdecimal():
            self.log.insert(0.0, '\nError. You need to input a number! Please, try again!\n')
            return None
        if not 0 <= int(user_input) <= self.max_number:
            self.log.insert(0.0, f'\nError. You need to input a number between 0 and {self.max_number} inclusively! '
                                 f'Please, try again!\n')
            return None
        return int(user_input)

    def __user_input_loop(self):
        if self.user_input.get() != '':
            self.log.insert(0.0, 'You: ' + self.user_input.get() + '\n\n')
            self.number_to_guess = self.__check_input(self.user_input.get())
            self.num_after_check = self.number_to_guess
            self.user_input.set('')
        self.game_window.after(1000, self.__user_input_loop)

    # def sendproc(self, event):
    #     self.log.insert(0.0, self.user_input.get() + ':' + '\n')
    #     self.user_input.set('')

    def __create_server_label(self):
        self.create_server_string = tkinter.StringVar()
        self.create_server_label = tkinter.Label(self.server, textvariable=self.create_server_string)
        self.create_server_label.place(x=200, y=280, width=400, height=50)

    def __connection_to_server_label(self):
        self.connection_to_server_string = tkinter.StringVar()
        self.connection_to_server_label = tkinter.Label(self.client, textvariable=self.connection_to_server_string)
        self.connection_to_server_label.place(x=200, y=180, width=400, height=50)

    def __create_tabs(self):
        """Создаем вкладки для сервера и клиента, чтобы развивать в дальнейшем."""

        self.tabs_panel = ttk.Notebook(self.start_window)
        self.server = ttk.Frame(self.tabs_panel)
        self.client = ttk.Frame(self.tabs_panel)
        self.tabs_panel.add(self.server, text='Server')
        self.tabs_panel.add(self.client, text='Client')
        self.tabs_panel.pack(expand=1, fill='both')  # необходимы оба параметра для корректного создания вкладок

    def __fill_server_tab(self):
        """Создает текстовые аннотации и поля для заполнения адреса и порта сервера, который необходимо создать. Также
        создает кнопку, которая создает соединение."""

        self.server_address_label = tkinter.Label(self.server, text='Enter sever address (example: 192.168.0.108): ')
        self.server_port_label = tkinter.Label(self.server, text='Enter sever port (example: 5000): ')
        self.server_max_num_label = tkinter.Label(self.server, text=f'Enter max number to conceive '
                                                                    f'(default: {MAX_NUMBER_TO_CONCEIVE}): ')
        self.server_attempts_label = tkinter.Label(self.server, text=f'Enter number of attempts to guess the conceived '
                                                                     f'num (default: {ATTEMPTS}): ')
        self.server_address_label.place(x=0, y=20, height=40)
        self.server_port_label.place(x=0, y=80, height=40)
        self.server_max_num_label.place(x=0, y=140, height=40)
        self.server_attempts_label.place(x=0, y=200, height=40)

        self.server_address_entry = tkinter.Entry(self.server, width=40)
        self.server_port_entry = tkinter.Entry(self.server, width=40)
        self.server_max_num_entry = tkinter.Entry(self.server, width=40)
        self.server_attempts_entry = tkinter.Entry(self.server, width=40)

        self.server_address_entry.place(x=500, y=20, height=40)
        self.server_port_entry.place(x=500, y=80, height=40)
        self.server_max_num_entry.place(x=500, y=140, height=40)
        self.server_attempts_entry.place(x=500, y=200, height=40)

        self.create_server_button = tkinter.Button(self.server, text='Create server', width=17,
                                                   command=self.__create_server)
        self.create_server_button.place(x=580, y=250)

    def __fill_client_tab(self):
        """Создает текстовые аннотации и поля для заполнения адреса и порта сервера, к которому будет подключаться
        клиент. Также создает кнопку, которая создает соединение."""

        self.client_address_label = tkinter.Label(self.client, text='Enter sever address to connect to '
                                                                    '(example: 192.168.0.108): ')
        self.client_port_label = tkinter.Label(self.client, text='Enter sever port to connect to(example: 5000): ')
        self.client_address_label.place(x=0, y=20, height=40)
        self.client_port_label.place(x=0, y=80, height=40)

        self.client_address_entry = tkinter.Entry(self.client, width=40)
        self.client_port_entry = tkinter.Entry(self.client, width=40)

        self.client_address_entry.place(x=500, y=20, height=40)
        self.client_port_entry.place(x=500, y=80, height=40)

        self.client_connection_button = tkinter.Button(self.client, text='Connect to server', width=17,
                                                       command=self.__connect_to_server)
        self.client_connection_button.place(x=580, y=150)

    def __create_server(self):
        """Функция пытается создать сервер с полученными аргументами. Если сервер запускается, выводится лейбл
        с уведомлением юзера об этом. Если происходит ошибка, то выводится уведомление в отдельном мини-окне."""
        addr = self.server_address_entry.get()
        port = self.server_port_entry.get()
        self.max_num = self.server_max_num_entry.get()
        self.attempts = self.server_attempts_entry.get()
        try:
            if addr == '' or port == '':
                return msg.showerror('Server creation error!', 'Invalid IP address and/or port! Please, try again!')
            if self.max_num != '' and self.attempts != '':
                server_start_command = f'python server.py --ip_address={addr} --port={port} ' \
                                       f'--max_number={self.max_num} --attempts={self.attempts}'
            elif self.max_num != '':
                server_start_command = f'python server.py --ip_address={addr} --port={port} --max_number={self.max_num}'
            elif self.attempts != '':
                server_start_command = f'python server.py --ip_address={addr} --port={port} --attempts={self.attempts}'
            else:
                server_start_command = f'python server.py --ip_address={addr} --port={port}'
            data = Popen(server_start_command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
            popen_out = data.stdout.readline().decode('utf-8')
            if 'Traceback' in popen_out:
                return msg.showerror('Server creation error!', 'Something went wrong. Please, try again and check, if '
                                                               'all data was entered correctly!')
            self.create_server_string.set(f'Created server with IP {addr} and port {port}.')
        except Exception as e:
            msg.showerror('Server creation error!', str(e))
        else:
            # self.__game_window()
            self.__connect_to_server(addr, port)
            # self.msg.bind('<Return>', self.sendproc)
            # self.game_window.after(1000, self.__user_input_loop)

    def __print_score(self):
        """Function, which prints current score in console."""

        opponent_id = [key for key in self.score.keys() if key != self.player_id][0]
        self.log.insert(0.0, f'{PARAGRAPHS + TABS}Current score:\n'
                             f'{TABS}You: {self.score[self.player_id]}\n'
                             f'{TABS}Opponent: {self.score[opponent_id]}{PARAGRAPHS}')
        self.log.insert(0.0, f"\nNow u'r player {self.player_number}!{PARAGRAPHS}")

    def __connect_to_server(self, addr: str = None, port: str = None):
        """Функция пытается подключиться к серверу с полученными аргументами. Если подключение успешно, создается новое
        окно ГУИ с игрой. Если происходит ошибка, то выводится уведомление в отдельном мини-окне."""
        self.__game_window()
        if addr is None or port is None:
            addr = self.client_address_entry.get()
            port = self.client_port_entry.get()
        try:
            if addr == '' or port == '':
                return msg.showerror('Connection error!', 'Invalid IP address and/or port! Please, try again!')
            try:
                self.client_app = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.client_app.settimeout(CONNECTION_TO_SERVER_TIMEOUT)
                self.client_app.connect((addr, int(port)))
                self.client_app.send(pickle.dumps('__join_server'))
                self.player_number, self.number_of_players, self.max_number, self.player_id = \
                    pickle.loads(self.client_app.recv(2048))
                self.game_window.after(1000, self.__main_client)
            except:
                return msg.showerror('Connection error!', 'Something went wrong. Please, try again and check, if '
                                                          'all data was entered correctly!')
            else:
                self.connection_to_server_string.set(f'Connected to server with IP {addr} and port {port}.')
        except Exception as e:
            msg.showerror('Connection error!', str(e))

    def __p1_cycle(self):
        """Loop for the first player. The first player conceives a number and sends it to the server. Then the first
        player waits for the second player trying to guess the number. If second player guesses the number, the first
        player will get a positive response from the server -> change places with the second player. If the answer is
        negative, the first player waits for the next attempt from the second player."""
        try:
            data = 'Waiting for second player to guess the number...\n\n'
            if data != self.last_message:
                self.log.insert(0.0, data)
                self.last_message = data
            message = pickle.loads(self.client_app.recv(2048))
            if message == 'exit':
                data = 'Second player left the game! You won! See you soon!\n\n'
                if data != self.last_message:
                    self.log.insert(0.0, data)
                    self.last_message = data
                return
            if message[0] == 'True':
                if message[1] >= 0 and self.num_after_check == message[3]:
                    data = f'\n\nAnother player guessed the num in {5 - message[1]} attempts. U lost...\n\n'
                    if data != self.last_message:
                        self.log.insert(0.0, data)
                        self.last_message = data
                else:
                    data = f"U won! Second player didn't guess the correct num. He thought, " \
                           f"it was {message[3]}.\n\n"
                    if data != self.last_message:
                        self.log.insert(0.0, data)
                        self.last_message = data
                self.player_number, self.number_of_players, self.max_number, self.score = \
                    pickle.loads(self.client_app.recv(2048))
                self.__print_score()
                return
            data = f"Second player didn't guess the correct num. He thought, it was {message[3]} and now  " \
                   f"has {message[1]} attempts!\n\n"
            if data != self.last_message:
                self.log.insert(0.0, data)
                self.last_message = data
        except BlockingIOError:
            self.game_window.after(1000, self.__p1_cycle)
            return
        self.game_window.after(1000, self.__p1_cycle)

    def __main_client(self):
        """The main function of the client side. Connects to the server and sends a start message. Next gets player
        number and number of players in the game. If we are the only player, send a request to update information
        about the players on the server. If there are two players, the game starts."""
        self.client_app.setblocking(False)
        try:
            if self.player_number == 1 and self.number_of_players == 2:
                data = f'Enter an integer number between 0 and {self.max_number} inclusively, which second player ' \
                       f'should guess or enter "exit" to end the game:\n\n'
                self.game_window.after(1000, self.__user_input_loop)
                if self.number_to_guess is not None:
                    self.client_app.send(pickle.dumps(self.number_to_guess))
                    if self.number_to_guess == 'exit':
                        self.log.insert(0.0, 'Thanks for the game! See you soon!\n\n')
                        self.number_to_guess = None
                        # self.game_window.after(1000, self.__p1_cycle)
                    else:
                        self.number_to_guess = None
                        self.game_window.after(1000, self.__p1_cycle)

            elif self.player_number == 2 and self.number_of_players == 2:
                data = 'Waiting for first player to choose the number...\n\n'
                # num = pickle.loads(self.client.recv(2048))
                # if num == 'exit':
                #     print('\n\U0001F6AA First player left the game! See you soon! \U0001F596 \n')
                #     sys.exit()
                # self.number_chosen = bool(num)
                # print('\n\U0001F3AF Number was chosen! Now, try to guess it! \U0001F3AF ')
                # self.p2_cycle()

            else:
                data = 'Waiting for second player...\n\n'
                self.client_app.send(pickle.dumps('get_data'))
                # if self.notification is None or self.notification != data:
                #     self.notification = data
                #     self.log.insert(0.0, self.notification)
                self.player_number, self.number_of_players, self.max_number, self.player_id = \
                    pickle.loads(self.client_app.recv(2048))
            if self.notification is None or self.notification != data:
                self.notification = data
                self.log.insert(0.0, self.notification)
        except BlockingIOError:
            self.game_window.after(1000, self.__main_client)
            return
        self.game_window.after(1000, self.__main_client)

    def start(self):
        tkinter.mainloop()


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

        self.connect_to_server()
        self.client.send(pickle.dumps('__join_server'))
        self.player_number, self.number_of_players, self.max_number, self.player_id = \
            pickle.loads(self.client.recv(2048))

    def connect_to_server(self, addr, port):
        """A function that establishes a connection to the server. If there is no connection in fixed time, exit
        connection."""

        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.settimeout(CONNECTION_TO_SERVER_TIMEOUT)
        self.client.connect((addr, port))
        self.client.send(pickle.dumps('__join_server'))
        self.player_number, self.number_of_players, self.max_number, self.player_id = \
            pickle.loads(self.client.recv(2048))

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
            guess = self.check_input(input(f'\U0001F3F9 Guess the num between 0 and {self.max_number} or enter "exit" '
                                           f'to end the game: '))
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

    def main(self, window, chat_logger, notification, func_to_log_input, user_input):
        """The main function of the client side. Connects to the server and sends a start message. Next gets player
        number and number of players in the game. If we are the only player, send a request to update information
        about the players on the server. If there are two players, the game starts."""
        self.client.setblocking(False)
        # while True:
        try:
            if self.player_number == 1 and self.number_of_players == 2:
                data = f'Enter an integer number between 0 and {self.max_number} inclusively, which second player should' \
                       f' guess or enter "exit" to end the game:\n\n'
                window.after(1000, func_to_log_input)
                if user_input is not None:
                    print(user_input)
                    user_input = None
                    print(user_input)
                # self.client.send(pickle.dumps(self.number_to_guess))
                # if self.number_to_guess == 'exit':
                #     print('\n\U0001F596 Thanks for the game! See you soon! \U0001F596 \n')
                #     sys.exit()
                # self.p1_cycle()

            elif self.player_number == 2 and self.number_of_players == 2:
                data = '\Waiting for first player to choose the number...\n\n'
                # num = pickle.loads(self.client.recv(2048))
                # if num == 'exit':
                #     print('\n\U0001F6AA First player left the game! See you soon! \U0001F596 \n')
                #     sys.exit()
                # self.number_chosen = bool(num)
                # print('\n\U0001F3AF Number was chosen! Now, try to guess it! \U0001F3AF ')
                # self.p2_cycle()

            else:
                data = 'Waiting for second player...\n\n'
                self.client.send(pickle.dumps('get_data'))
                # sleep(5)
                if notification is None or notification != data:
                    notification = data
                    chat_logger.insert(0.0, notification)
                self.player_number, self.number_of_players, self.max_number, self.player_id = \
                    pickle.loads(self.client.recv(2048))
            if notification is None or notification != data:
                notification = data
                chat_logger.insert(0.0, notification)
        except BlockingIOError:
            window.after(1000, self.main, window, chat_logger, notification, func_to_log_input, user_input)
            return
        window.after(1000, self.main, window, chat_logger, notification, func_to_log_input, user_input)


if __name__ == '__main__':
    main = Main()
    main.start()
