# Python program to implement server side of chat room.
import json
import socket
import select
import sys
import threading

HOST = '127.0.0.1'
PORT = 8070

## tcp
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []
nicknames = []

# udp
server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_udp.bind((HOST, PORT))


file_list = []

# broacast -- send to all
def broacast(message):
    for client in clients:
        client.send(message)


def private_message(send_to, message, client1):
    sender_index = clients.index(client1)
    send_to_index = -1
    # serching the correct client in clients to send him the messege
    for client in clients:
        nickname = nicknames[clients.index(client)]

        if nickname == send_to:
            send_to_index = 0
            str = message.replace('-#', '')

            str2 = "private to: " + str
            client.send(str2.encode('utf-8'))
            client1.send(str2.encode('utf-8'))
    if send_to_index == -1:
        clients[sender_index].send("not connected or worng name".encode('utf-8'))


def show_online(index):
    title = "The connected users are:\n"

    names = ""
    for name in nicknames:
        title = title + name + "  \n"
    clients[index].send(title.encode('utf-8'))

####todo##########
def show_server_file():
    title = "Server File List \n"

    names = ""
    for name in file_list:
        title = title + name + "  \n"
    clients[index].send(title.encode('utf-8'))


# handle
def handle(client):
    while True:
        try:
            index = clients.index(client)
            # nickname =nicknames[index]
            message = client.recv(1024).decode('utf-8')
            print(type(message))

            if message == "-#list":
                show_online(index)

            if '-#private' in message:

                message2 = message.replace("-#private", "")

                for name in nicknames:
                    temp_name = '-#' + name
                    if temp_name in message2:
                        send_to = name
                        private_message(send_to, message2, client)

            if '-#everyone' in message:
                message2 = message.replace("-#everyone", "")
                print(f"{nicknames[clients.index(client)]}")
                broacast(message2.encode('utf-8'))
                
            if message == "-#file_list":
                show_server_file()    

        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)

            break


def handle2(client):
    while True:
        print("waiting...")
        try:
            index = clients.index(client)
            # nickname =nicknames[index]
            message = client.recv(1024).decode('utf-8')
            print(type(message))

            if message == "CONN_REQ":  # Establish connection
                clients.append(client)

                server_udp.sendto("ACK".encode('utf-8'), client)  # Send ACK to confirm connection
                print("connection established with " + client.nickname)





        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)

            break


# receive
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
        client.send("Connected to the server".encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

        client_udp, addresss = server_udp.accept()
        print(f"connected with {str(addresss)}!")

        client_udp.send("NICK".encode('utf-8'))
        nickname = client_udp.recv(1024).decode('utf-8')
        print(nickname)
        thread_udp = threading.Thread(target=handle2, args=(client_udp,))
        thread_udp.start()


print("server running......")
receive()
