# Python program to implement client side of chat room.

import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import LEFT, simpledialog, ANCHOR
from turtle import left
from tkinter import Toplevel, Button, Tk, Menu

HOST = '127.0.0.1'
PORT = 8070


class Client:

    def __init__(self, host, port):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        self.msg = tkinter.Tk()
        self.msg.withdraw()

        self.nickname = simpledialog.askstring("Nickname ", "Pleas choosa a nickname", parent=self.msg)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.recevie)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat: " + self.nickname, bg="lightgray")
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

        self.win.geometry("200x250")
        lbl = tkinter.Label(self.win, text="online")
        listbox1 = tkinter.Listbox(self.win)
        #listbox1.place(x=445, y=0, width=130, height=320)
        lbl.pack()

        listbox1.pack()






        ####################################################333

        # self.menubar = Menu(self.win)
        # file = Menu(self.menubar, tearoff=0)
        # file = Menu(self.menubar, tearoff=0)
        # file.add_command(label="New")
        # file.add_command(label="Open")
        # file.add_command(label="Save")
        # file.add_command(label="Save as...")
        # file.add_command(label="Close")
        #
        # file.add_separator()
        #
        # file.add_command(label="Exit", command=self.win.quit)
        #
        # self.menubar.add_cascade(label="File", menu=file)
        # edit = Menu(self.menubar, tearoff=0)
        # edit.add_command(label="Undo")
        #
        # edit.add_separator()
        #
        # edit.add_command(label="Cut")
        # edit.add_command(label="Copy")
        # edit.add_command(label="Paste")
        # edit.add_command(label="Delete")
        # edit.add_command(label="Select All")
        #
        # self.menubar.add_cascade(label="Edit", menu=edit)
        # help = Menu(self.menubar, tearoff=0)
        # help.add_command(label="About")
        # self.menubar.add_cascade(label="Help", menu=help)
        #
        # self.win.config(menu=self.menubar)
        # #####################################################################################################33#################
        # self.win.geometry("900x1800")
        #
        # lbl = tkinter.Label(self.win, text="online")
        #
        # listbox = tkinter.Listbox(self.win)
        #
        #
        #
        #
        # # this button will delete the selected item from the list
        #
        # btn = Button(self.win, text="delete", command=lambda listbox=listbox: listbox.delete(ANCHOR))
        #
        # lbl.pack()
        #
        # listbox.pack()
        #
        # btn.pack()
        #####################################################################################################33

        # # online user list button
        # button1 = tkinter.Button(self.win, text='Online users', command=self.users)
        # button1.place(x=485, y=320, width=90, height=30)
        #
        # # Input Text box
        # a = tkinter.StringVar()
        # a.set('')
        # entry = tkinter.Entry(self.win, width=120, textvariable=a)
        # entry.place(x=5, y=350, width=570, height=40)
        ############333


        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    def users(self):
        global listbox1, ii
        if ii == 1:
            listbox1.place(x=445, y=0, width=130, height=320)
            ii = 0
        else:
            # 隱藏controller
            listbox1.place_forget()
            ii = 1

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
                print("leave")

                break
            except:
                print("Error")
                # message = f"{self.nickname}  leave the chet: {self.input_area.get('1.0', 'end')}"
                # self.sock.send(message.encode('utf-8'))
                # self.input_area.delete('1.0', 'end')
                self.sock.close()

                break


client = Client(HOST, PORT)
