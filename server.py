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
PKT_SIZE = 500
PORT_UDP = 50012

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
server_files = ["barak.png", "yossi.txt", "gal.txt"]

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


# TODO WITH BIG EXPLINE
"""
 UDP SERVER 
 
 """


def download(client, file_name):
    # message = "need to know how to download " + file_name + "\n"
    # for file in server_files:
    #     if file == file_name:
    #         client.send(message.encode('utf-8'))
    N = 5
    print("UDP socket starting...")
    counter_packet = 0
    packet_lost = 0
    address = (client.getsockname()[0], PORT_UDP)
    start = time.time()
    packet_sq_n = 0
    packet_data = 0
    packet_length = 0
    packet_file = 0

    UDP_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        path = f'{file_name}'
        with open(path, 'rb') as fileToSend:
            # fileToSend = open(path, 'rb')
            total_data = fileToSend.read()
            print(total_data)
        # fileToSend.close()
    except:
        print("an error occur during the reading of the file")
        UDP_sock.close()
    curr_state = 0

    # while the last packet was sent
    while curr_state < int((len(total_data) / PKT_SIZE) + 1):
        print(f"{curr_state} <-> {int((len(total_data) / PKT_SIZE) + 1)}")
        counter_packet += 1

        # create a repere time for our timeout
        max_time = time.time()

        # send all the packets in the window
        for i in range(N):
            curr_packet = total_data[(curr_state + i) * PKT_SIZE: (curr_state + i) * PKT_SIZE + PKT_SIZE]
            packet_data = curr_packet
            packet_length = len(curr_packet)
            packet_sq_n = curr_state + i
            packet_to_send = f"{str(packet_sq_n)}~{str(len(total_data))}~{str(packet_length)}~{packet_data}"
            print(packet_to_send)

            UDP_sock.sendto(packet_to_send.encode('utf-8'), address)
            print(f"packet number {curr_state + i} was sent ")
        max_time = time.time() - max_time
        curr_ACK = curr_state
        # while all the ack of the window was not received
        while curr_ACK < curr_state + N - 1:
            # start timeout
            start_time = time.time()
            try:
                ACK, addresst = UDP_sock.recvfrom(200)
            except:
                print("no message incoming")
                continue
            # another that the last parcel of the file was delivered
            if ACK.decode('utf-8') == "FIN":
                print("FIN")
                break
            # if we get the ack of the good packet
            elif ACK.decode('utf-8') == str(curr_ACK):
                curr_ACK += 1
                print(f"packet number {curr_ACK - 1} was received by the client ")
            # if we get an unwanted packet or the timeout passed
            elif ((int(ACK.decode('utf-8')) > curr_ACK) or (time.time() - start_time) > max_time):
                packet_lost += 1
                last_ack = curr_ACK
                # resend the rest of the window that wasn't already received by the client
                for i in range(curr_ACK, curr_state + N):
                    curr_packet = total_data[(curr_ACK + i) * PKT_SIZE: (curr_ACK + i) * PKT_SIZE + PKT_SIZE]
                    packet_data = curr_packet
                    packet_length = len(curr_packet)
                    packet_sq_n = curr_ACK + i
                    packet_to_send = f"{str(packet_sq_n)}~{str(len(total_data))}~{str(packet_length)}~{packet_data}"
                    print(packet_to_send.encode())
                    UDP_sock.sendto(packet_to_send.encode('utf-8'), address)
                    print(f"packet number {curr_ACK + i} was re-sent ")
        curr_state = curr_ACK

    print(
        f"summary :\n \t packet loss : {packet_lost} \n \t total of packet sent : {counter_packet} \n \t length of original packet/500 : {len(total_data) / PKT_SIZE} \n \t time elapsed : {str(time.time() - start)} seconds ")
    UDP_sock.close()


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
