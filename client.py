import socket
import threading
from EventBus import EventBus
from server import codes
import sys
import time


greeting_msg = ("Hi there, welcome to the MS encrypted messaging service! :D")


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 12345

    client_socket.connect((host, port))
    print(greeting_msg)

    name_registration(client_socket)

    client_interface_thread = threading.Thread(target=cmd, args=(client_socket,))
    client_interface_thread.start()
    while True:
        listen_thread = threading.Thread(target=listening_thread, args=(client_socket,))
        listen_thread.start()

def name_registration(client_socket):
    name = codes.NAME_OPCODE + input("Enter your name: ")
    client_socket.sendall(name.encode('utf-8'))
    data = client_socket.recv(1024).decode('utf-8')
    print(f"{data}")


def request_userlist(client_socket):
    # Request user list from server
    # Now uses the EventBus to get the response from the listening thread instead of blocking recv
    client_socket.sendall(codes.REQUEST_USER_LIST_OPCODE.encode('utf-8'))

def request_connection(client_socket):
    request_userlist(client_socket)
    target = input ("Select a user to connect to through the server (enter name, press enter to continue)")
    client_socket.sendall(codes.CONNECT_TO_SERVER_MEDIATED_OPCODE.encode('utf-8')+target.encode('utf-8'))
    data = EventBus.get()
    print(data)

def choose_connection(client_socket):
    target = select_target_user(client_socket)
    client_socket.sendall(codes.CONNECT_TO_P2P_OPCODE.encode('utf-8')+target.encode('utf-8'))
    #WHEN THE SERVER RESPONDS WITH THE ADDRESS OF THE OTHER CLIENT
    #LAUNCH P2P CONNECTION HERE ON A NEW THREAD
    print(EventBus.get())

def select_target_user(client_socket):
    request_userlist(client_socket)
    data = input("Please select a user to message from the list (type their name): ")
    return data

def display_userlist(event_payload):
    print(f"""
----------------------- 
User list:
{event_payload}-----------------------
""")

def listening_thread(client_socket):
    while True:
        data = client_socket.recv(1024)
        if data:
            EventBus.publish(data)


def request_counter(connection_requests=[]):
    print(f"Connection requests: {len(connection_requests)}")


COMMANDS = {
    "userlist": request_userlist,
}


def cmd(client_socket):
    print("Command terminal ready. Type 'help' or 'quit'.")

    while True:
        raw = input("> ").strip()
        if not raw:
            continue

        if raw == "quit":
            print("Goodbye.")
            break

        parts = raw.split()
        name, args = parts[0], parts[1:]

        if name in COMMANDS:
            result = COMMANDS[name](args)
            print(result)
        else:
            print(f"Unknown command: {name}")

if __name__ == "__main__":
    main()