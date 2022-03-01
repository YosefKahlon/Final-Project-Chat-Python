# Python program to implement client side of chat room.

import socket
import sys
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import LEFT, simpledialog
from turtle import left




PORT = 50011



class Client:

    def __init__(self, port):

        msg = tkinter.Tk()
        msg.withdraw()
        self.port=PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = simpledialog.askstring("IP", "Pleas input IP", parent=msg)
        print(host)
        self.host=str(host)
        self.sock.connect((self.host, port))




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

        self.chat_label = tkinter.Label(self.win, text="Chat: " + self.nickname, bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win,height=7)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(padx=20, pady=5)

        self.msg_label = tkinter.Label(self.win, height=1,text="Message:", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win,width=50, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=5, pady=5)
        self.send_button.place(x=5,y=200)

        self.list_button = tkinter.Button(self.win, text="Who is connected?", command=self.list)
        self.list_button.config(font=("Arial", 12))
        self.list_button.pack( padx=10, pady=5)
        self.list_button.place(x=5,y=240)

        self.private_label = tkinter.Label(self.win, text="send to:", bg="lightgray")
        self.private_label.config(font=("Arial", 12))
        self.private_label.pack(side=LEFT,padx=10, pady=5)


        self.input_private_area = tkinter.Text(self.win, height=1, width=20, padx=5, pady=5)
        self.input_private_area.pack(side=LEFT,padx=10, pady=5)

        self.private_button = tkinter.Button(self.win, text="private", command=self.private)
        self.private_button.config(font=("Arial", 12))
        self.private_button.pack(side=LEFT,padx=20, pady=5)

        self.server_files_button = tkinter.Button(self.win, text="show server files", command=self.server_files)
        self.server_files_button.config(font=("Arial", 12))
        self.server_files_button.pack( padx=30, pady=5)
        self.server_files_button.place(x=600,y=200)


        self.download_button = tkinter.Button(self.win, text="download", command=self.download)
        self.download_button.config(font=("Arial", 12))
        self.download_button.pack(padx=10, pady=5)
        self.download_button.place(x=600,y=240)


        self.input_download_area = tkinter.Text(self.win, height=1, width=20, padx=5, pady=5)
        self.input_download_area.pack(padx=20, pady=5)
        self.input_download_area.place(x=560,y=280)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    def write(self):

        message = f"-#everyone {self.nickname}: {self.input_area.get('1.0', 'end')}"

        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def list(self):
        message = "-#list"
        self.sock.send(message.encode('utf-8'))

    def private(self):
        if self.input_private_area.get('1.0', 'end') != "":
            message = f"-#private -#{self.input_private_area.get('1.0', 'end')}-# {self.nickname}: {self.input_area.get('1.0', 'end')}"
            print("private message" + message)
            self.sock.send(message.encode('utf-8'))

        self.input_area.delete('1.0', 'end')

    def server_files(self):
        message = "you bitch!!"
        self.sock.send(message.encode('utf-8'))

    def download(self):
        message = f"download_server_file+{self.input_download_area.get('1.0', 'end')}"
        self.sock.send(message.encode('utf-8'))
        self.input_download_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)
    # def udp(self):
    #
    #     server_udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #     server_udp.bind((self.host,self.port))
    #
    #     addr = (self.host,self.port)
    #     buf=1024
    #
    #     f = open("yossi.txt",'wb')
    #
    #     data,addr = server_udp.recvfrom(buf)
    #     try:
    #         while(data):
    #             f.write(data)
    #             server_udp.settimeout(2)
    #             data,addr = server_udp.recvfrom(buf)
    #     except socket.timeout:
    #         f.close()
    #         server_udp.close()
    #         print ("File Donwloaded")

    def recevie(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')

                if message == 'NICK':
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


client = Client(PORT)
