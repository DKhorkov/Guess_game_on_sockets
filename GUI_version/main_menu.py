import tkinter
from tkinter import ttk

from configs import START_WINDOW_HEIGHT, START_WINDOW_TITLE, START_WINDOW_WIDTH


class MainMenu:

    def __init__(self):
        """Создаем стартовый ГУИ, добавляем ему название и размеры."""
        self.start_window = tkinter.Tk()
        self.start_window.title(START_WINDOW_TITLE)
        self.start_window.geometry(f'{START_WINDOW_WIDTH}x{START_WINDOW_HEIGHT}')
        self.__create_tabs()
        self.__fill_server_tab()

    def __create_tabs(self):
        """Создаем вкладки для сервера и клиента, чтобы развивать в дальнейшем."""
        self.tabs_panel = ttk.Notebook(self.start_window)
        self.server = ttk.Frame(self.tabs_panel)
        self.client = ttk.Frame(self.tabs_panel)
        self.tabs_panel.add(self.server, text='Server')
        self.tabs_panel.add(self.client, text='Client')
        self.tabs_panel.pack(expand=1, fill='both')

    def __fill_server_tab(self):
        """Создает текстовые аннотации и поля для заполнения адреса и порта сервера, который необходимо создать. Также
        создает кнопку, которая создает соединение."""
        self.server_address_label = tkinter.Label(self.server, text='Enter sever address (example: 192.168.0.108): ')
        self.server_port_label = tkinter.Label(self.server, text='Enter sever port (example: 5000): ')
        self.server_address_label.place(x=0, y=20, height=40)
        self.server_port_label.place(x=0, y=80, height=40)

        self.server_address_entry = tkinter.Entry(self.server, width=40)
        self.server_port_entry = tkinter.Entry(self.server, width=40)
        self.server_address_entry.place(x=350, y=20, height=40)
        self.server_port_entry.place(x=350, y=80, height=40)

        self.create_server_button = tkinter.Button(self.server, text='Create server', width=17,
                                                   command=self.__create_server)
        self.create_server_button.place(x=430, y=140)

    def __create_server(self):
        pass

    def start(self):
        tkinter.mainloop()


if __name__ == '__main__':
    main_menu = MainMenu()
    main_menu.start()
