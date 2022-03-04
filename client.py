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

PORT = 50011  ## need to random
STATE = 0
PORT_UDP = 50012
PKT_SIZE = 500
HOST = '127.0.0.1'


class Client:
    """
    The first steps of the client are to choose a nickname and to connect to our server.

    Instead of binding the data and listening, we are connecting to an existing server.


    Now, a client needs to have two threads that are running at the same time.
     The first one will constantly receive data from the server
     and the second one will send our own messages to the server.
     So we will need two functions here.
    """

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



    """ 
    create chat window (buttons,  text area..)
    """
    def gui_loop(self):

        self.win = tkinter.Tk()
        self.win.configure(bg="light blue")
        self.win.geometry("900x500")

        self.chat_label = tkinter.Label(self.win, text="Chat: " + self.nickname, bg="light blue")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        # Scrolled Text option
        self.text_area = tkinter.scrolledtext.ScrolledText(self.win, height=7)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(padx=20, pady=5)

        self.msg_label = tkinter.Label(self.win, height=1, text="Message:", bg="light blue")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, width=50, height=3)
        self.input_area.pack(padx=20, pady=5)

        # click to send
        self.send_button = tkinter.Button(self.win, text="Send", command=self.write, height=1, width=10)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=5, pady=5)
        self.send_button.place(x=400, y=280)

        # list of all online
        self.list_button = tkinter.Button(self.win, text="Who is connected?", command=self.list)
        self.list_button.config(font=("Arial", 12))
        self.list_button.pack(padx=10, pady=5)
        self.list_button.place(x=100, y=420)

        # ----------------------------private ------------------------------------------------------

        self.private_label = tkinter.Label(self.win, text="send to:", bg="light blue")
        self.private_label.config(font=("Arial", 12))
        self.private_label.pack(side=LEFT, padx=10, pady=5)

        self.input_private_area = tkinter.Text(self.win, height=1, width=20, padx=5, pady=5)
        self.input_private_area.pack(side=LEFT, padx=10, pady=5)

        self.private_button = tkinter.Button(self.win, text="private", command=self.private)
        self.private_button.config(font=("Arial", 12))
        self.private_button.pack(side=LEFT, padx=20, pady=5)

        # ----------------------- show server files---------------------------------------------
        self.server_files_button = tkinter.Button(self.win, text="show server files", command=self.server_files)
        self.server_files_button.config(font=("Arial", 12))
        self.server_files_button.pack(padx=30, pady=5)
        self.server_files_button.place(x=380, y=367)

        # ----------------------- download server files---------------------------------------------
        self.download_button = tkinter.Button(self.win, text="download", command=self.download)
        self.download_button.config(font=("Arial", 12))
        self.download_button.pack(padx=10, pady=5)
        self.download_button.place(x=730, y=367)

        self.input_download_area = tkinter.Text(self.win, height=1, width=20, padx=5, pady=5)
        self.input_download_area.pack(padx=20, pady=5)
        self.input_download_area.place(x=530, y=367)

        # stop download button
        self.stop_button = tkinter.Button(self.win, text="stop", command=self.stop_down)
        self.stop_button.config(font=("Arial", 12))
        self.stop_button.pack(padx=10, pady=5)
        self.stop_button.place(x=520, y=420)

        # pause download button
        self.pause_button = tkinter.Button(self.win, text="pause", command=self.pause_down)
        self.pause_button.config(font=("Arial", 12))
        self.pause_button.pack(padx=10, pady=5)
        self.pause_button.place(x=580, y=420)

        # progress bar
        self.progress_bar = Progressbar(self.win, orient=HORIZONTAL, length=100, mode='determinate')
        self.progress_bar.pack(padx=10, pady=5)
        self.progress_bar.place(x=660, y=420)

        self.gui_done = True
        # 192.168.1.31
        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()


    """
    The writing function
    runs in an endless loop which is always waiting for an 
    input from the user. Once it gets some, it combines it with the nickname and sends it to the server. 
    """
    def write(self):
        message = f"-#everyone {self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')


    """A request list from the server of all connected"""
    def list(self):
        message = "-#list"
        self.sock.send(message.encode('utf-8'))

    def private(self):
        if self.input_private_area.get('1.0', 'end') != "":
            message = f"-#private -#{self.input_private_area.get('1.0', 'end')}-# {self.nickname}: {self.input_area.get('1.0', 'end')}"
            print("private message" + message)
            self.sock.send(message.encode('utf-8'))

        self.input_area.delete('1.0', 'end')
    """ A request list from the server of all the server files """
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

    ##todo change stuff and add our explosion
    def handle_down(self, filename):
        self.progress_bar['value'] = 0
        # at the begining of the download reset to play mode
        global STATE
        global PORT_UDP
        STATE = 1

        UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        filename = filename.replace("\n", "")
        print(filename + "---------------\n")
        # file_r = open("transferred_" + filename, 'w+')
        with open("transferred_" + filename, 'w') as file_r:
            packet_counter = 0
            accumulated_length = 0
            UDP_socket.bind((HOST, PORT_UDP))
            while True:
                print("waiting for reception ...")
                # if the pause button was pushed
                while STATE % 2 == 0:
                    sleep(1)
                # if the stop button was pushed

                if STATE == 2:
                    break
                try:
                    data, server = UDP_socket.recvfrom(2048)
                    data = data.decode('utf-8')
                    print("data--------------------------------------------------> ", data)
                except:
                    print("connection doesn't succeed -> try again ")
                    continue

                # data = data.decode('utf-8')
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
        # file_r.close()
        UDP_socket.close()
        print("closeeeeeeeee")
        self.text_area.config(state='normal')
        self.text_area.insert('end', f"the last byte is {bytearr[-1:]}\n")
        self.text_area.yview('end')
        self.text_area.config(state='disabled')

    """pause and continue download"""

    def pause_down(self):
        global STATE
        STATE += 1

    """stop the download and close the udp socket"""

    def stop_down(self):
        global STATE
        STATE = 2


    """"
    in this function we constantly tries to receive messages and to print them onto the screen.
    
    :exception : In case there is some error, we close the connection and break the loop 
    """
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
