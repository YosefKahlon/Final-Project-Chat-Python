import socket
import threading

import tkinter

import tkinter.scrolledtext
from tkinter import simpledialog
from tkinter import  *
HOST = '127.0.0.1'
PORT = 9090


class Client:

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

        self.msg = tkinter.Tk()

        self.msg.withdraw()

        self.nickname = simpledialog.askstring("Login", " Please chose a nickname", parent=self.msg)

        self.gui_done = False

        self.runing = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Ariel", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disable')

        self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.msg_label.config(font=("Ariel", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        ##--------------send message---------------------

        self.send_botton = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_botton.config(font=("Ariel", 12))
        self.send_botton.pack(padx=20, pady=5)

        # ## send to
        # self.add = tkinter.Button(self.win, text="add", command=self.write)
        #
        # self.add.config(font=("Ariel", 12))
        # self.add.pack(padx=20, pady=5)
        # self.add.option_readfile()

        lb1 = Listbox(self.win)
        lb1.insert()

        self.gui_done = True




        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def write(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.socket.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.runing = False
        self.win.destroy()
        self.socket.close()
        exit(0)

    def receive(self):
        while self.runing:
            try:
                message = self.socket.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self.socket.send(self.nickname.encode('utf-8'))
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:

                print("ERROR")
                self.socket.close()
                break


client = Client(HOST, PORT)
