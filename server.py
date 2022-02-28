# Python program to implement server side of chat room.
import json
import socket
import select
import sys
import threading

HOST = '127.0.0.1'
PORT = 50011

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

# try:
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     file_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     file_socket.connect(("8.8.8.8", 80))
#     IP = file_socket.getsockname()[0]
# except:
#     IP="127.0.0.1"
#

server.listen()

clients = []
nicknames = []
server_files = ["yossi.txt", "gal.txt"]


server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_udp.accept()



# broacast -- send to all
def broacast(message):
    for client in clients:
        client.send(message)


def private_message(send_to, message, client1):
    sender_index = clients.index(client1)
    sender_nickname = nicknames[clients.index(client1)]
    # serching the correct client in clients to send him the messege
    for client in clients:
        nickname = nicknames[clients.index(client)]

        if nickname == send_to:
            str = message.replace('-#', '')
            str2 = "private to: " + str
            client.send(str2.encode('utf-8'))

            if sender_nickname != nickname:
                client1.send(str2.encode('utf-8'))


def show_online(index):
    title = "---The connected users are:---\n"

    names = ""
    for name in nicknames:
        title = title + name + "  \n"
    title = title + "--- end users list --- \n"
    clients[index].send(title.encode('utf-8'))


def show_server_files(index):
    title = "---The files are: ---\n"

    names = ""
    for file in server_files:
        title = title + file + "  \n"
    title = title + "--- end files list ---\n"
    clients[index].send(title.encode('utf-8'))


def download(index, file_name):
    message = "need to know how to download " + file_name + "\n"
    for file in server_files:
        if file == file_name:
            clients[index].send(message.encode('utf-8'))
            try:
                with open(file_name) as  f:
                     server_udp.sendto(f,IP)





# handle
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
                thread_udp = threading.Thread(target=handle2, args=(client,message,))
                thread_udp.start()
                bool = True
                for file in server_files:
                    if file in message:
                        bool = False
                        download(index, file)
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


# def udp_senf_file(index):
#     pass


server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_udp.bind((HOST, 5001))


# receive


def handle2(client,message):
    print("---sam--------"+message+"---ack------")



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

        thread = threading.Thread(target=handle, args=(client, ))
        thread.start()






print("server running......")
receive()
