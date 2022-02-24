# Python program to implement client side of chat room.

import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import LEFT, simpledialog
from turtle import left

HOST = '127.0.0.1'
PORT = 8070


class Client:

    def __init__(self, host, port):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        msg = tkinter.Tk()
        msg.withdraw()

        self.nickname = simpledialog.askstring("Nickname ", "Pleas choosa a nickname", parent=msg)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.recevie)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(padx=20, pady=5)

        self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(side=LEFT, padx=5, pady=5)

        self.list_button = tkinter.Button(self.win, text="Who is connected?", command=self.list)
        self.list_button.config(font=("Arial", 12))
        self.list_button.pack(side=LEFT, padx=20, pady=5)

        self.private_button = tkinter.Button(self.win, text="private", command=self.private)
        self.private_button.config(font=("Arial", 12))
        self.private_button.pack(side=LEFT, padx=30, pady=5)
        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    def write(self):

        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def list(self):
        message = "list"
        self.sock.send(message.encode('utf-8'))


    def private(self):
        # message="private"
        #
        # self.sock.send(message.encode('utf-8'))
        pass

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def recevie(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                print(f"message {message} finish")
                if message == 'NICK':
                    self.sock.send(self.nickname.encode('utf-8'))
                if message == "list":
                    self.sock.send(self.nickname.encode('utf-8'))
                if message == "private":
                    self.sock.send(self.nickname.encode('utf-8'))

                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')

            except ConnectionError:
                break
            except:
                print("Error")
                self.sock.close()
                break


client = Client(HOST, PORT)
