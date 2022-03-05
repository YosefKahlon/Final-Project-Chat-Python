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
packet_size = 500
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
        udp_sock = threading.Thread(target=self.download_over_reliable_udp, args=(file,))
        udp_sock.start()
        self.input_download_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    global state
    global UDP_port
    """
    in this function the client download the file from the server over reliable udp
    reliable udp - GO - BACK - N   
    """
    def download_over_reliable_udp(self, file_name):
        self.progress_bar['value'] = 0

        UDP_port = 50012
        STATE = 1

        UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        file_name = file_name.replace("\n", "")

        with open("file_after_download_" + file_name, 'w') as file:
            counter = 0

            UDP_socket.bind((HOST, UDP_port))

            while True:

                # if the pause button was pushed
                # 0 = pause , 1 = continue
                while STATE % 2 == 0:
                    sleep(1)

                # if the stop button was pushed
                if STATE == 2:
                    break
                try:
                    (data, server) = UDP_socket.recvfrom(1024)
                    data = data.decode('utf-8')

                except Exception:
                    print("Error ! ")
                    continue

                get_data = data.split('#')

                seq_num = get_data[0]
                file_size = int(get_data[1])
                packet_len = int(get_data[2])
                packet_data = get_data[3]
                more_left = 0

                # Have the right packages to start writing
                if int(seq_num) == counter:
                    counter += 1

                    # write  the packet data to the new file
                    file.write(packet_data)

                    more_left += packet_len

                    #  percentage of the download
                    percentage_left = (more_left / file_size) * 100
                    print(percentage_left, " %")

                    progress_val = (packet_len * 100) / file_size

                    self.progress_bar['value'] += progress_val

                    ack = seq_num
                    ACK = str(ack).encode('utf-8')
                    UDP_socket.sendto(ACK, server)


                # Wrong packet
                else:
                    num_of_packet = str(counter).encode('utf-8')
                    UDP_socket.sendto(num_of_packet, server)
                    continue

                if packet_len < packet_size:
                    print("------FIN----------")
                    fin = "FIN".encode('utf-8')
                    UDP_socket.sendto(fin, server)
                    break

            print("------ Download complete --------- ")

        UDP_socket.close()
        print("\n")
        print(" -------Closing the socket -----")

    """pause and continue download"""

    def pause_down(self):
        global state
        state += 1

    """stop the download and close the udp socket"""

    def stop_down(self):
        global state
        state = 2

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
