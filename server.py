import socket
import pickle
import threading
import simplejson as json


class codes:
    OPCODE_PREFIX = "op"

    # Define opcodes
    # First digit, direction of communication, 0 = client to server (recieved), 1 = server to client (sent)
    # Second digit, type of encoder/decoder, 0 default(utf-8), 1= pickle object
    # Third digit, subject of communication, 001 = name registration, 002 = user list, 003 = connect to server mediated, 004 = connect to p2p, 005 = client request p2p

    POSITION_OF_DATA_FLOW = -3  # Position of data flow digit in opcode
    POSITION_OF_ENCODING_TYPE = -2  # Position of encoding digit in opcode
    POSITION_OF_SUBJECT = -1  # Position of subject digit in opcode

    NAME_OPCODE = OPCODE_PREFIX+"001"
    RESPONSE_USER_LIST_OPCODE = OPCODE_PREFIX+"112"
    CONNECT_TO_SERVER_MEDIATED_OPCODE = OPCODE_PREFIX+"003"
    CONNECT_TO_P2P_OPCODE = OPCODE_PREFIX+"004"
    CLIENT_REQUEST_P2P_OPCODE = OPCODE_PREFIX+"005"
    RESPONSE_ENCRYPTION_METHODS_OPCODE = OPCODE_PREFIX+"116"
    RESPONSE_NAME_OPCODE = OPCODE_PREFIX+"101"
    REQUEST_USER_LIST_OPCODE = OPCODE_PREFIX+"002"
    RESPONSE_CLIENT_ADDRESS_OPCODE = OPCODE_PREFIX+"124"

    opcode_length = len(NAME_OPCODE)  # All opcodes are the same length



ENCRYPTION_METHODS = {1:"DIFFIE HELLMAN"}
#ENCRYPTION_METHODS = {
#    1: {
#        "name": "Diffie Hellman",
#        "encrypt": diffie_hellman_encrypt,
#        "decrypt": diffie_hellman_decrypt
#    },
#    2: {
#        "name": "RSA",
#        "encrypt": rsa_encrypt,
#        "decrypt": rsa_decrypt
#    },
#    3: {
#        "name": "AES",
#        "encrypt": aes_encrypt,
#        "decrypt": aes_decrypt
#    }
#}

#BUG:   when server's thread for handling a specific client the user stays on the userlist. This is because
#       userlist drops are run on the same thread the server uses to handle client connection
# Solutions:
#1 - Make userlist updates run on the main thread of server - then each child 
# thread can share that userlist using locks. Then the server can look at active threads/connections
# and decide to pop from dictionary if connection or thread has crashed


user_list = {}


def handle_client(client_socket, client_address):
    with client_socket:
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break  # client closed the connection

            except ConnectionResetError:
                print("Connection was ended by the client.")
                break

            except TimeoutError:
                print("Socket operation timed out.")
                break

            except Exception as e:
                print(f"Unexpected socket error: {e}")
                break

            handle_requests(client_socket, client_address, data)

    if client_address in user_list:
        user_list.pop(client_address, None)


def find_recipient(client_socket, recipient_name):
    recipient_address = next(
    (addr for addr, name in user_list.items() if name == recipient_name),
    None)

    if recipient_address is not None:
        return recipient_address

    client_socket.sendall(("Recipient not found. Please try again.").encode('utf-8'))
    return None


def handOff_connection(client_socket, client_address, recipient_name):
    recipient_address = find_recipient(client_socket, recipient_name=recipient_name) 
    packet = json.dumps({
            "address": {
            "ip": recipient_address[0],
            "port": recipient_address[1]}
            })
    client_socket.sendto(codes.RESPONSE_CLIENT_ADDRESS_OPCODE.encode('utf-8')+packet.encode('utf-8'),recipient_address)


def prompt_encryption_selection(client_socket, opcode, target):
    client_socket.sendall(codes.RESPONSE_ENCRYPTION_METHODS_OPCODE.encode('utf-8')+pickle.dumps(ENCRYPTION_METHODS))
    data = client_socket.recv(1024)
    try:
        enc_method = ENCRYPTION_METHODS[data]
        while True:
            middle_man_messages(client_socket, target, enc_method)
    except:
        client_socket.sendall(("No such method try again").encode('utf-8'))
    def middle_man_messages(client_socket, target, enc_method):
        message = client_socket.recv(1024)
        target_address = find_recipient(client_socket, target)
        pass  # Placeholder for message handling logic


def handle_requests(client_socket, client_address, data):

    request = data.decode('utf-8')
    opcode = request[:codes.opcode_length]

    try:
        request_content = request[codes.opcode_length:]
    except:
        print("Message with no content, only opcode")

    match opcode:

        case codes.NAME_OPCODE:

            print(f"Received name: {request_content}")
            response = "Server received your name: " + request_content
            user_list[client_address] = request_content
            client_socket.sendall(response.encode('utf-8'))

        case codes.REQUEST_USER_LIST_OPCODE:
            print(f"Server received request from: {user_list[client_address]}. Sending list...")
            client_socket.sendall(codes.RESPONSE_USER_LIST_OPCODE.encode("utf-8") + pickle.dumps(user_list))
        case codes.CONNECT_TO_SERVER_MEDIATED_OPCODE:
            print(f"Server received connection request from: {user_list[client_address]}. Prompting for encryption method...")
            prompt_encryption_selection(client_socket, opcode, request_content)
        case codes.CONNECT_TO_P2P_OPCODE:
            print(f"Server received p2p connection request from: {user_list[client_address]}. Initiating handoff...")
            handOff_connection(client_socket, client_address, request_content)
        case _:
            print(f"Check opcode: {opcode}")


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