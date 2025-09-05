import socket
import pickle
import threading


class codes:
    OPCODE_PREFIX = "op"
    NAME_OPCODE = OPCODE_PREFIX+"001"
    USER_LIST_OPCODE = OPCODE_PREFIX+"002"
    CONNECT_TO_SERVER_MEDIATED_OPCODE = OPCODE_PREFIX+"003"
    CONNECT_TO_P2P_OPCODE = OPCODE_PREFIX+"004"
    CLIENT_REQUEST_P2P_OPCODE = OPCODE_PREFIX+"005"


ENCRYPTION_METHODS = {1,"DIFFIE HELLMAN"}
opcode_length = len(codes.NAME_OPCODE)
#BUG:   when server's thread for handling a specific client the user stays on the userlist. This is because
#       userlist drops are run on the same thread the server uses to handle client connection
# Solutions:
#1 - Make userlist updates run on the main thread of server - then each child 
# thread can share that userlist using locks. Then the server can look at active threads/connections
# and decide to pop from dictionary if connection or thread has crashed

user_list = {}


def handle_client(client_socket, client_address):
    while True:
        data = client_socket.recv(1024)
        # Fix this with an actual exception error (bad code bruh)
        if not data:
            break
        handle_requests(client_socket,client_address,data)
    client_socket.close()
    if user_list[client_address]:
        user_list.pop(client_address)


def handle_connection(client_socket, recipient_name):
    """
    Handles the process of finding the recipient's address from the user list.

    Parameters:
        client_socket (socket.socket): The socket object for the client.
        recipient_name (str): The name of the recipient to look up.

    Returns:
        recipient_address (tuple): The address of the recipient if found, otherwise None.

    Side Effects:
        If the recipient is not found, sends a message to the client indicating this.

    Exceptions:
        Raises KeyError if the recipient is not found in the user list.
        Handles KeyError by sending an error message to the client and returning None.
    """
    try:
        # Find the address of the recipient by their name
        recipient_address = next((addr for addr, name in user_list.items() if name == recipient_name), None)
        if recipient_address is not None:
            return recipient_address
        client_socket.sendall(("Recipient not found. Please try again.").encode('utf-8'))
    except KeyError:
        return None

def handOff_connection(client_socket, client_address, recipient_name):
        
        recipient_address = handle_connection(client_socket, recipient_name=recipient_name) 
        socket.socket.sendto(client_socket,codes.CLIENT_REQUEST_P2P_OPCODE.encode("utf-8"),recipient_address)


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
            print(f"Server received p2p connection request from: {user_list[client_address]}. Initiating handoff...")
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