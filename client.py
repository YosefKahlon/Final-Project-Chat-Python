# Python program to implement client side of chat room.

import socket
import sys
import threading
import tkinter
import tkinter.scrolledtext
from time import sleep
from tkinter import LEFT, simpledialog, HORIZONTAL
from tkinter.ttk import Progressbar
from turtle import left

PORT = 50011
STATE = 0
PORT_UDP = 50012
PKT_SIZE = 500
HOST = '127.0.0.1'


class Client:

    def __init__(self, port):

        msg = tkinter.Tk()
        msg.withdraw()
        self.port = PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = simpledialog.askstring("IP", "Pleas input IP", parent=msg)
        global HOST
        HOST = host
        self.host = str(host)
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

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win, height=7)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(padx=20, pady=5)

        self.msg_label = tkinter.Label(self.win, height=1, text="Message:", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, width=50, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=5, pady=5)
        self.send_button.place(x=5, y=200)

        self.list_button = tkinter.Button(self.win, text="Who is connected?", command=self.list)
        self.list_button.config(font=("Arial", 12))
        self.list_button.pack(padx=10, pady=5)
        self.list_button.place(x=5, y=240)

        self.private_label = tkinter.Label(self.win, text="send to:", bg="lightgray")
        self.private_label.config(font=("Arial", 12))
        self.private_label.pack(side=LEFT, padx=10, pady=5)

        self.input_private_area = tkinter.Text(self.win, height=1, width=20, padx=5, pady=5)
        self.input_private_area.pack(side=LEFT, padx=10, pady=5)

        self.private_button = tkinter.Button(self.win, text="private", command=self.private)
        self.private_button.config(font=("Arial", 12))
        self.private_button.pack(side=LEFT, padx=20, pady=5)

        self.server_files_button = tkinter.Button(self.win, text="show server files", command=self.server_files)
        self.server_files_button.config(font=("Arial", 12))
        self.server_files_button.pack(padx=30, pady=5)
        self.server_files_button.place(x=600, y=200)

        self.download_button = tkinter.Button(self.win, text="download", command=self.download)
        self.download_button.config(font=("Arial", 12))
        self.download_button.pack(padx=10, pady=5)
        self.download_button.place(x=600, y=240)

        self.input_download_area = tkinter.Text(self.win, height=1, width=20, padx=5, pady=5)
        self.input_download_area.pack(padx=20, pady=5)
        self.input_download_area.place(x=560, y=280)

        self.download_button = tkinter.Button(self.win, text="stop", command=self.stop_down)
        self.download_button.config(font=("Arial", 12))
        self.download_button.pack(padx=10, pady=5)

        self.download_button = tkinter.Button(self.win, text="pause", command=self.pause_down)
        self.download_button.config(font=("Arial", 12))
        self.download_button.pack(padx=10, pady=5)

        self.download_button = tkinter.Button(self.win, text="continue", command=self.continue_down())
        self.download_button.config(font=("Arial", 12))
        self.download_button.pack(padx=10, pady=5)

        self.progress_bar = Progressbar(self.win, orient=HORIZONTAL)
        self.progress_bar.pack(padx=10, pady=5)

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

        file = self.input_download_area.get('1.0', 'end')
        print(file + "----------")
        udp_sock = threading.Thread(target=self.handle_down, args=(file,))
        udp_sock.start()
        self.input_download_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def handle_down(self, filename):
        self.progress_bar['value'] = 0
        # at the begining of the download reset to play mode
        global STATE
        global PORT_UDP
        STATE = 1

        UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        filename = filename.replace("\n", "")
        print(filename + "---------------\n")
        file_r = open("transfered_" + filename, 'w+')
        packet_counter = 0
        accumulated_length = 0
        UDP_socket.bind((HOST, PORT_UDP))
        while True:
            print("waiting for reception ...")
            # if the pause button was pushed
            while STATE == 0:
                sleep(1)
            # if the stop button was pushed
            if STATE == 2:
                break
            try:
                data, server = UDP_socket.recvfrom(2048)
                print(data)
            except:
                print("connection doesn't succeed -> try again ")
                continue

            data = data.decode('utf-8')
            splited_data = data.split('~')
            print(splited_data)
            total_length = int(splited_data[1])
            sequence_data = splited_data[0]
            print(f"packet number {sequence_data} was received  ")
            if int(sequence_data) == packet_counter:
                packet_counter += 1
                new_data_part = splited_data[3]
                file_r.write(new_data_part)
                accumulated_length += int(splited_data[2])
                print(f"{(accumulated_length / total_length) * 100}% completed ")
                self.progress_bar['value'] += (int(splited_data[2]) * 100 / (total_length))
                print(f"part {sequence_data} was added to the file ")
                ACK = sequence_data
                UDP_socket.sendto(str(ACK).encode('utf-8'), server)
            else:
                print("wrong packet ! return request ")
                UDP_socket.sendto(str(packet_counter).encode('utf-8'), server)
                continue
            print(splited_data[2] + "--------------------")
            if int(splited_data[2]) < PKT_SIZE:
                print("here")
                UDP_socket.sendto("FIN".encode('utf-8'), server)
                break

        print("end of transfert -> closing socket ...")
        file_re = file_r.read()
        bytearr = bytearray(file_re, "utf8")
        file_r.close()
        UDP_socket.close()
        print("closeeeeeeeee")
        self.text_area.config(state='normal')
        self.text_area.insert('end', f"the last byte is {bytearr[-1:]}\n")
        self.text_area.yview('end')
        self.text_area.config(state='disabled')

    # send command to server to pause the download
    def pause_down(self):
        global STATE
        STATE = 0

    # send command to server to continue the download
    def continue_down(self):
        global STATE
        STATE = 1

    # send command to server to stop the download
    def stop_down(self):
        global STATE
        STATE = 2

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
