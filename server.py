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
packet_size = 500
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
server_files = ["ex.txt", "yossi.txt", "gal.txt", "final.pdf"]

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
    print("------------------UDP socket is open----------------")

    packet_lost = 0
    address = (client.getsockname()[0], UDP_port)
    open_clock = time.time()  # how long will it take

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Open the file requested by the client
    try:
        with open(file_name, 'r') as file:

            file_read = file.read()


    except Exception:
        print("Error while trying reading the file ! ")
        print("------closing the socket ---- ")
        udp_socket.close()

    state = 0
    counter = 0
    last_packet = int((len(file_read) / packet_size) + 1)

    # while the last packet was sent
    while state < last_packet:

        counter += 1
        end = time.time()
        N = 5
        # send the packets in the slide window
        # N is length of the window
        for i in range(N):
            curr_packet = file_read[(state + i) * packet_size: (state + i) * packet_size + packet_size]

            seq_num = state + i
            packet_len = len(curr_packet)
            packet_data = curr_packet


            send_packet = f"{str(seq_num)}#{str(len(file_read))}#{str(packet_len)}#{packet_data}"

            # send each packet to the client address
            send_p = send_packet.encode('utf-8')
            udp_socket.sendto(send_p, address)

            packet_num = state + i
            print("send packet --->", packet_num)

        end = time.time() - end
        curr_ack = state

        # got  the ack message for each packet
        while curr_ack < state + N - 1:


            start = time.time()
            try:
                (ACK, addresst) = udp_socket.recvfrom(200)
            except:
                continue

            message = ACK.decode('utf-8')

            # Received the ACK message for the current package
            if message == str(curr_ack):
                curr_ack += 1


                # all the packets arrived
            elif message == "FIN":
                print("----------FIN-------------")
                break



            # more ACK than expected
            # the packet arrived but time was running out
            elif ((int(message) > curr_ack) or (time.time() - start) > end):
                packet_lost += 1

                # resend the window again with the problem
                for i in range(curr_ack, state + N):
                    curr_packet = file_read[(curr_ack + i) * packet_size: (curr_ack + i) * packet_size + packet_size]
                    packet_data = curr_packet
                    packet_len = len(curr_packet)
                    seq_num = curr_ack + i
                    send_packet = f"{str(seq_num)}#{str(len(file_read))}#{str(packet_len)}#{packet_data}"

                    udp_socket.sendto(send_packet.encode('utf-8'), address)

        state = curr_ack
        print("---------------------------")
        print("send packet ---->", counter)
        print("packet loss ---->", packet_lost)
        print("the time ---->", time.time() - open_clock)
        print("---------------------------")

    print("------closing the socket ---- ")

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
