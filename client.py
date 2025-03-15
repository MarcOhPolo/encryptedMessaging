import socket
import pickle
from socketServer import codes


greeting_msg = ("Hi there, welcome to the MS Diffie Hellam Protocol simulator! :D")


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 12345
    client_socket.connect((host, port))
    print(greeting_msg)
    message = codes.NAME_OPCODE + input("Enter your name: ")
    client_socket.sendall(message.encode('utf-8'))
    data = client_socket.recv(1024)
    response = data.decode('utf-8')

    print(f"Server response: {response}")
    while True:
        client_request_userlist(client_socket)


def request_userlist_and_display(client_socket):
    client_socket.sendall(codes.USER_LIST_OPCODE.encode('utf-8'))
    data = client_socket.recv(1024)
    i=1
    for str in pickle.loads(data).values():
        print(f"{i}: {str}")
        i+=1


def request_connection(client_socket):
    client_socket.sendall(codes.CONNECT_TO_OPCODE.encode('utf-8'))
    data = client_socket.recv(1024)
    print(data.decode('utf-8'))


def client_request_userlist(client_socket):
    request = input("""Input your command:
                    Generate userlist command - U
                    Connect to a user - C""")
    request = request.lower()
    match request:
        case "U":
            request_userlist_and_display(client_socket)
        case "C":
            request_connection(client_socket)
        case _:
            print("Select a valid commant please")
            client_request_userlist(client_socket)

 
def choose_connection(client_socket):
    data = input("Please select a user to message from the list (type their name)")
    client_socket.sendall((codes.CONNECT_TO_OPCODE+data).encode('utf-8'))
    

if __name__ == "__main__":
    main()