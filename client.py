import socket
import pickle
import threading
from EventBus import EventBus
from server import codes

greeting_msg = ("Hi there, welcome to the MS encrypted messaging service! :D")

# can be expanded to support more opcodes as needed
# need 2 threads, one for showing user information, the other for the backend conversation with server


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 12345

    client_socket.connect((host, port))
    print(greeting_msg)

    name_registration(client_socket)

    client_interface_thread = threading.Thread(target=client_interface, args=(client_socket,))
    client_interface_thread.start()
    while True:
        listen_thread = threading.Thread(target=listening_thread, args=(client_socket,))
        listen_thread.start()


def name_registration(client_socket):
    message = codes.NAME_OPCODE + input("Enter your name: ")
    client_socket.sendall(message.encode('utf-8'))

    data = client_socket.recv(1024).decode('utf-8')

    print(f"{data}")


def request_userlist_and_display(client_socket):
    # Request user list from server
    # Now uses the EventBus to get the response from the listening thread instead of blocking recv
    client_socket.sendall(codes.REQUEST_USER_LIST_OPCODE.encode('utf-8'))
    data = EventBus.get()
    print(f"""
-----------------------
User list:
{data}-----------------------
""")

def request_connection(client_socket):
    request_userlist_and_display(client_socket)
    target = input ("Select a user to connect to through the server (enter name, press enter to continue)")
    client_socket.sendall(codes.CONNECT_TO_SERVER_MEDIATED_OPCODE.encode('utf-8')+target.encode('utf-8'))
    data = EventBus.get()
    print(data)


def handle_server_connection(client_socket):
    request = input("""Input your command:
                    Generate userlist command - U
                    Connect to a user through the server - S
                    Connect to a user directly (p2p) - D
                    Your command: """)
    request = request.upper()
    match request:
        case "U":
            request_userlist_and_display(client_socket)
            handle_server_connection(client_socket)
        case "S":
            request_connection(client_socket)
        case "D":
            choose_connection(client_socket)
        case _:
            print("Select a valid commant please")
            handle_server_connection(client_socket)

 
def choose_connection(client_socket):
    target = select_target_user(client_socket)
    client_socket.sendall(codes.CONNECT_TO_P2P_OPCODE.encode('utf-8')+target.encode('utf-8'))
    #WHEN THE SERVER RESPONDS WITH THE ADDRESS OF THE OTHER CLIENT
    #LAUNCH P2P CONNECTION HERE ON A NEW THREAD
    print(EventBus.get())


def client_interface(client_socket):
    #When server connection is established, handle interactions
    handle_server_connection(client_socket)

def select_target_user(client_socket):
    request_userlist_and_display(client_socket)
    data = input("Please select a user to message from the list (type their name): ")
    return data

def listening_thread(client_socket):
    while True:
        data = client_socket.recv(1024)
        if data:
            EventBus.publish(data)
    
if __name__ == "__main__":
    main()