# Python program to implement server side of chat room.
import json
import socket
import time

import select
import sys
import threading

# HOST = '127.0.0.1'
# PORT = 50011
#
# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.bind((HOST, PORT))


# connection data
PORT = 50011

UDP_port = 50012

try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP SOCKET
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    host_ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP SOCKET

    host_ip.connect(("8.8.8.8", 80))
    HOST = host_ip.getsockname()[0]
    print(HOST)
except:
    HOST = "127.0.0.1"
    print(HOST)
server.bind((HOST, PORT))
server.listen()

""" clients about to join the server"""
clients = []
nicknames = []
server_files = ["barak.png", "yossi.txt", "gal.txt", "final.pdf"]

""" broacast: Send a message to all clients connected to the server """


def broacast(message):
    for client in clients:
        client.send(message)


""" Send a message to a specific client on the server"""


def private_message(send_to, message, client1):
    sender_index = clients.index(client1)
    sender_nickname = nicknames[clients.index(client1)]

    # searching the correct client in clients to send him the messege
    for client in clients:
        nickname = nicknames[clients.index(client)]

        if nickname == send_to:
            str = message.replace('-#', '')
            str2 = "private to: " + str
            client.send(str2.encode('utf-8'))

            if sender_nickname != nickname:
                client1.send(str2.encode('utf-8'))


""" List of online clients on the server """


def show_online(index):
    title = "---The connected users are:---\n"

    names = ""
    for name in nicknames:
        title = title + name + "  \n"
    title = title + "--- end users list --- \n"
    clients[index].send(title.encode('utf-8'))


""" List of ready-to-download files """


def show_server_files(index):
    title = "---The files are: ---\n"
    names = ""
    for file in server_files:
        title = title + file + "  \n"

    title = title + "--- end files list ---\n"
    clients[index].send(title.encode('utf-8'))


"""
 UDP SERVER using GO-BACK-N
 in this method the server sends the necessary file for the client
 Overly reliable - udp
 
  about GO BACK N : 
  sliding window protocol , 
  the sender send multi of packet before the receiver send him back the acknowledge .
  if the sender does not receive ACK  at the right time, all the 
  packets will be send again .
  
  
 :param : client on the server   
 :param : file the client ask 
 :exception : error with file  
 """


def download(client, file_name):
    pakt_size = 500

    print("-------------SOCKET UDP IS READY------------------")
    packet_counter = 0
    packet_lost = 0
    address = (client.getsockname()[0], UDP_port)
    start_time = time.time()

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP SOCKET

    try:
        with open(file_name, 'r') as fileToSend:
            total_data = fileToSend.read()

    except FileNotFoundError:
        print("file is not found !!")
        print("closing the socket.")
        udp_socket.close()

    except:
        print("Error while trying open the file !!")
        print("closing the socket.")
        udp_socket.close()

    curr_status = 0

    file_size = total_data.__len__()

    # sending all the packets
    while curr_status < int((file_size / pakt_size) + 1):
        packet_counter += 1

        # open clock
        second_time = time.time()

        N = 5  # sliding window size

        # send all the packets in the window
        # go back N
        for i in range(N):
            curr_packet = total_data[(curr_status + i) * pakt_size: (curr_status + i) * pakt_size + pakt_size]

            packet_data = curr_packet
            sequence_num = curr_status + i
            packet_size = len(curr_packet)

            send_packet = f"{str(sequence_num)}~{str(file_size)}~{str(packet_size)}~{packet_data}"

            udp_socket.sendto(send_packet.encode('utf-8'), address)
            print(f"packet number {curr_status + i} was sent ")

        second_time = time.time() - second_time
        curr_ackn = curr_status
        num_of_ack = curr_status + N - 1

        # we check if we got acknowledge for every packet we send
        while curr_ackn < num_of_ack:

            third_time = time.time()
            try:
                ACK, address = udp_socket.recvfrom(1024)
            except:
                print("No message was entered")
                continue
            # to much acknowledge or time to send the pkt was too long than expected
            # so we lost a packet
            if ((int(ACK.decode('utf-8')) > curr_ackn) or (time.time() - third_time) > second_time):
                packet_lost += 1
                for i in range(curr_ackn, curr_status + N):
                    curr_packet = total_data[(curr_ackn + i) * pakt_size: (curr_ackn + i) * pakt_size + pakt_size]
                    packet_data = curr_packet
                    packet_size = len(curr_packet)
                    sequence_num = curr_ackn + i
                    send_packet = f"{str(sequence_num)}~{str(len(total_data))}~{str(packet_size)}~{packet_data}"
                    udp_socket.sendto(send_packet.encode('utf-8'), address)
                    print("packet number", curr_ackn + i, " was re-sent ")


            # the packets of the window size have been shipped
            elif ACK.decode('utf-8') == str(curr_ackn):
                curr_ackn += 1
                print("packet number", curr_ackn - 1, "was received by the client ")

            # all the packet have been shipped
            elif ACK.decode('utf-8') == "FIN":
                print("send all  message ---->  FIN")
                break
        curr_status = curr_ackn
    print("------------------------------------------------------------------------------------------")
    print("send packet  ---> ", packet_counter)
    print("packet lost  --->", packet_lost)
    print("time --->", (time.time() - start_time))

    print("------------- SOCKET IS CLOSE ------------------")

    udp_socket.close()


"""
    @:param client on the server 
    In this function we handle the client's request
    by making the endless loop the server "listen" to 
    to every client request for example download file, online client list ...
    
    Now if for some reason there is an error with 
    the connection to this client, 
    we remove it and its nickname, 
    close the connection and broadcast that this client has left the chat.

"""


def handle(client):
    while True:
        try:
            index = clients.index(client)
            nickname = nicknames[index]
            message = client.recv(1024).decode('utf-8')

            if message == "you bitch!!":
                show_server_files(index)
            if message == "-#list":
                show_online(index)

            if 'download_server_file' in message:

                bool = True
                for file in server_files:
                    if file in message:
                        bool = False
                        udp_sock = threading.Thread(target=download, args=(client, file))
                        udp_sock.start()
                if bool:
                    message2 = "The file is not exists or the name is incorrect\n"
                    client.send(message2.encode('utf-8'))

            if '-#private' in message:

                message2 = message.replace("-#private", "")
                send_to_index = True
                for name in nicknames:
                    temp_name = '-#' + name
                    if temp_name in message2:
                        send_to_index = False
                        send_to = name
                        private_message(send_to, message2, client)
                if send_to_index:
                    message2 = "The user is not connected or the name is incorrect\n"
                    client.send(message2.encode('utf-8'))

            if '-#everyone' in message:
                message2 = message.replace("-#everyone", "")
                print(f"{nicknames[clients.index(client)]}")
                broacast(message2.encode('utf-8'))

        except:
            message = "The user " + nickname + " has left the chat\n"

            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            broacast(message.encode('utf-8'))
            break


"""
    in this function we accept new connection from clients ,
    Once a client is connected it sends the string ‘NICK’ to it, 
    which will tell the client that its nickname is requested.
    
    and now we can append the client to the online client in the server.
    after that we start new trade that run handle function for this particular  client .
    
    Notice that we are always encoding and decoding the messages here. 
    The reason for this is that we can only send bytes and not strings.
    So we always need to encode messages, when we send them and decode them, when we receive them.
"""


def receive():
    while True:
        client, address = server.accept()
        print(f"connected with {str(address)}!")

        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        print(nickname)

        nicknames.append(nickname)

        clients.append(client)

        print(f"Nickname of the client is {nickname}")
        broacast(f"{nickname} connected to the server!\n".encode('utf-8'))
        client.send("Connected to the server \n".encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("server running......")
receive()

"""
we got a lot of information from 
https://www.neuralnine.com/tcp-chat-in-python/
"""
