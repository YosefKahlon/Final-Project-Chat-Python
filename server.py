# Python program to implement server side of chat room.
import json
import socket
import select
import sys
import threading

HOST = '127.0.0.1'
PORT = 8070

server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((HOST,PORT))

server.listen()

clients=[]
nicknames=[]

#broacast
def broacast(message):
    for client in clients:
        client.send(message)


def private_message(sent_to,message,client1):
    sender_index =clients.index(client1)
    send_to_index=-1
    for client in clients:
        if client.nickname==sent_to:
            send_to_index=clients.index(client)
    if sender_index==-1:
        clients[sender_index].send(("not connected or worng name").encode('utf-8'))
    if sender_index>-1:
        clients[send_to_index].send(message.encode('utf-8'))


def show_online(index):
    title="The connected users are:\n"

    names = ""
    for name in nicknames:
        title = title+name+"  \n"
    clients[index].send(title.encode('utf-8'))

#handle
def handle(client):
    while True:
        try:

            index =clients.index(client)
            # nickname =nicknames[index]
            message = client.recv(1024).decode('utf-8')
            print(message)




            if message== "-#list":
                show_online(index)

            if '-#private' in message:
                message.replace("-#private","")
                for name in nicknames:
                    if '-#'+name+'-#' in message:
                        send_to=name
                private_message(send_to,message,client)


            if '-#everyone' in message:
                message.replace("-#everyone","")

                print("server: "+message)
                print(f"{nicknames[clients.index(client)]}")
                broacast(message.encode('utf-8'))
            

        except:
            index =clients.index(client)
            clients.remove(client)
            client.close()
            nickname =nicknames[index]
            nicknames.remove(nickname)

            break
#receive
def receive():
    while True:
        client,address=server.accept()
        print(f"connected with {str(address)}!")

        client.send("NICK".encode('utf-8'))
        nickname= client.recv(1024).decode('utf-8')
        print(nickname)

        nicknames.append(nickname)

        clients.append(client)
        

        print(f"Nickname of the client is {nickname}")
        broacast(f"{nickname} connected to the server!\n".encode('utf-8'))
        client.send("Connected to the server".encode('utf-8'))

        thread = threading.Thread(target= handle,args=(client,))
        thread.start()



print("server running......")
receive()

