# Python program to implement server side of chat room.
import json
import socket
import select
import sys
import threading

HOST = '127.0.0.1'
PORT = 8070

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []
nicknames = []


# broacast
def broacast(message):
    for client in clients:
        client.send(message)


# handle
def handle(client):
    while True:
        try:
            index = clients.index(client)
            # nickname =nicknames[index]
            message = client.recv(1024).decode('utf-8')

            if message == "list":

                title = "The connected users are:\n"
                # title=str(title)+"\n"
                # clients[index].send(title.encode('utf-8'))
               # print(str(nicknames))
                names = ""

                for name in nicknames:
                    title = title + name + "    \n"
                    #print(name)
                clients[index].send(title.encode('utf-8'))
            # if message == "private":
            #     pass
            # else:
            #     print(f"{nicknames[clients.index(client)]}")
            #     broacast(message.encode('utf-8'))


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


print("server running......")
receive()
