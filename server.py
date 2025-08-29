import socket
import pickle
import threading


class codes:
    OPCODE_PREFIX = "op"
    NAME_OPCODE = OPCODE_PREFIX+"001"
    USER_LIST_OPCODE = OPCODE_PREFIX+"002"
    CONNECT_TO_SERVER_MEDIATED_OPCODE = OPCODE_PREFIX+"003"
    CONNECT_TO_P2P_OPCODE = OPCODE_PREFIX+"004"


ENCRYPTION_METHODS = {1,"DIFFIE HELLMAN"}
opcode_length = len(codes.NAME_OPCODE)
user_list = {}


def handle_client(client_socket, client_address):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        handle_requests(client_socket,client_address,data)
    client_socket.close()
    if user_list[client_address]:
        user_list.pop(client_address)


def handle_connection(client_socket, client_address, recipient_name):
    try:
        recipient_address = user_list[recipient_name]
    except:
        print("User not found, sending new query")
        client_socket.sendall(("User not found try again").encode('utf-8'))
        return None
    #now prompt user1 (message requester) to select the encryption protocol

def handOff_connection(client_socket, client_address, recipient_name):
    


def prompt_encryption_selection(client_socket):
    client_socket.sendall(pickle.dumps(ENCRYPTION_METHODS))
    data = client_socket.recv(1024)
    try:
        enc_method = ENCRYPTION_METHODS[data]
    except:
        client_socket.sendall(("No such method try again").encode('utf-8'))
    

def handle_requests(client_socket, client_address, data):

    request = data.decode('utf-8')
    op_code = request[:opcode_length]

    try:
        request_content = request[opcode_length:]
    except:
        print("Message with no content, only opcode")

    match op_code:

        case codes.NAME_OPCODE:

            print(f"Received name: {request_content}")
            response = "Server received your name: " + request_content
            user_list[client_address] = request_content
            client_socket.sendall(response.encode('utf-8'))

        case codes.USER_LIST_OPCODE:
            print(f"Server received request from: {user_list[client_address]}. Sending list...")
            client_socket.sendall(pickle.dumps(user_list))
        case codes.CONNECT_TO_SERVER_MEDIATED_OPCODE:
            print(f"Server received connection request from: {user_list[client_address]}. Prompting for encryption method...")
            prompt_encryption_selection(client_socket)
        case codes.CONNECT_TO_P2P_OPCODE:
            print(f"Server received p2p connection request from: {user_list[client_address]}. Handing off to recipient...")
            handOff_connection(client_socket, client_address, request_content)
        case _:
            print(f"Check opcode: {op_code}")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 12345
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address,))
        client_handler.start()


if __name__ == "__main__":
    main()