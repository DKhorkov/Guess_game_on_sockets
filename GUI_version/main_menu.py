import tkinter
from tkinter import ttk
from tkinter import messagebox as msg
from subprocess import Popen, PIPE, STDOUT

from configs import START_WINDOW_HEIGHT, START_WINDOW_TITLE, START_WINDOW_WIDTH, ATTEMPTS, MAX_NUMBER_TO_CONCEIVE


class MainMenu:

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
        max_num = self.server_max_num_entry.get()
        attempts = self.server_attempts_entry.get()
        try:
            if addr == '' or port == '':
                return msg.showerror('Server creation error!', 'Invalid IP address and/or port! Please, try again!')
            if max_num != '' and attempts != '':
                server_start_command = f'python server.py --ip_address={addr} --port={port} --max_number={max_num} ' \
                                       f'--attempts={attempts}'
            elif max_num != '':
                server_start_command = f'python server.py --ip_address={addr} --port={port} --max_number={max_num}'
            elif attempts != '':
                server_start_command = f'python server.py --ip_address={addr} --port={port} --attempts={attempts}'
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

    def __connect_to_server(self):
        """Функция пытается подключиться к серверу с полученными аргументами. Если подключение успешно, создается новое
        окно ГУИ с игрой. Если происходит ошибка, то выводится уведомление в отдельном мини-окне."""
        addr = self.client_address_entry.get()
        port = self.client_port_entry.get()
        try:
            if addr == '' or port == '':
                return msg.showerror('Connection error!', 'Invalid IP address and/or port! Please, try again!')
            client_connection_command = f'python client.py --ip_address={addr} --port={port}'
            data = Popen(client_connection_command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
            popen_out = data.stdout.readline().decode('utf-8')
            if 'Traceback' in popen_out:
                return msg.showerror('Connection error!', 'Something went wrong. Please, try again and check, if '
                                                          'all data was entered correctly!')
            self.connection_to_server_string.set(f'Connected to server with IP {addr} and port {port}.')
        except Exception as e:
            msg.showerror('Connection error!', str(e))

    def start(self):
        tkinter.mainloop()


if __name__ == '__main__':
    main_menu = MainMenu()
    main_menu.start()
