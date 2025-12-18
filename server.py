import socket
import pickle
import threading
from EventBus import EventBus
from EventBus import codes

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

#---- SERVER STATE DICTIONARIES -----#

# These dictionaries collectively represent the server’s authoritative runtime state.
# They store client identity, active connections, and transient P2P handshake state, and are
# updated only in response to network events (never polled or waited on).

# client_address -> username
user_list = {}

# client_address -> socket
clients = {}

# request_id -> {from, to}
# Tracks pending P2P connection requests; entries are resolved via incoming responses and removed.
pending_p2p_requests = {}


#---- CLIENT HANDLERS -----#
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
    if client_address in clients:
        clients.pop(client_address, None)


def find_recipient_address(recipient_name):

    recipient_address = next(
    (addr for addr, name in user_list.items() if name == recipient_name),
    None)

    if recipient_address is not None:
        return recipient_address
    return None

def find_recipient_name(recipient_address):

    recipient_name = user_list.get(recipient_address, None)

    if recipient_name is not None:
        return recipient_name
    return None

def find_recipient_socket(recipient_name=None, recipient_address=None):
    if recipient_address:
        return clients[recipient_address]
    if recipient_name:
        recipient_address = find_recipient_address(recipient_name)
        return clients[recipient_address]


#---- P2P Functions ----#
def create_P2P_request(client_socket, recipient_name):

    recipient_address = find_recipient_address(recipient_name=recipient_name) 
    consent_request_p2p_connection(client_socket, recipient_name)
    message = EventBus.message_builder(codes.RESPONSE_CLIENT_ADDRESS_OPCODE, recipient_address)
    client_socket.sendall(message)


def consent_request_p2p_connection(client_socket, target):
    target_address = find_recipient_address(target)
    message = EventBus.message_builder(codes.CONSENT_REQUEST_P2P_OPCODE, find_recipient_name(client_socket.getpeername()))
    clients[target_address].sendall(message)
    print(f"Sent consent request to {target} at {target_address}.")


def consent_recieved_p2p_connection(client_socket, target_name, response):
    response = response.decode('utf-8')
    match response.lower():
        case "y":
            target_socket = find_recipient_socket(recipient_name=target_name)
            client_a_message = EventBus.message_builder(codes.RESPONSE_CLIENT_ADDRESS_OPCODE, client_socket.getpeername())
            client_b_message = EventBus.message_builder(codes.RESPONSE_CLIENT_ADDRESS_OPCODE, find_recipient_address(target_name))
            client_socket.sendall(client_b_message)
            target_socket.sendall(client_a_message)
        case "n":
            print("P2P request rejected")
        case _:
            print("Invalid response recieved")


def prompt_encryption_selection(client_socket, opcode, target):

    message = EventBus.message_builder(codes.RESPONSE_ENCRYPTION_METHODS_OPCODE, pickle.dumps(ENCRYPTION_METHODS))
    client_socket.sendall(message)
    data = client_socket.recv(1024)
    try:
        enc_method = ENCRYPTION_METHODS[data]
        while True:
            middle_man_messages(client_socket, target, enc_method)
    except:
        EventBus.message_builder(codes.FILLER_OPCODE,"No such method try again")
    def middle_man_messages(client_socket, target, enc_method):
        message = client_socket.recv(1024)
        target_address = find_recipient_address(target)
        pass  # Placeholder for message handling logic


#---- OPCODE HANDLERS -----#
def handle_requests(client_socket, client_address, data):
    opcode,request_content = EventBus.parse_event(data, return_opcode=True)

    handler = OPCODE_HANDLERS.get(opcode)

    if handler is None:
        print(f"Unknown opcode: {opcode}")
        return

    handler(client_socket, client_address, request_content)


def handle_name(client_socket, client_address, content):
    print(f"Received name: {content}")
    user_list[client_address] = content
    response = EventBus.message_builder(codes.RESPONSE_NAME_OPCODE,f"Server received your name: {content}")
    client_socket.sendall(response)


def handle_user_list_request(client_socket, client_address, _):

    username = user_list.get(client_address, "UNKNOWN")
    print(f"Server received request from: {username}. Sending list...")

    payload = EventBus.message_builder(codes.RESPONSE_USER_LIST_OPCODE, user_list)
    client_socket.sendall(payload)


def handle_mediated_connection(client_socket, client_address, content):

    prompt_encryption_selection(client_socket, codes.CONNECT_TO_SERVER_MEDIATED_OPCODE, content)


def handle_p2p_connection(client_socket, client_address, content):

    print(
        f"Server received p2p connection request from: "
        f"{user_list.get(client_address, 'UNKNOWN')}. Initiating handoff..."
    )
    create_P2P_request(client_socket, content)


OPCODE_HANDLERS = {
    #All opcodes' first digit should be 0 as this reflects the client -> server data flow
    codes.NAME_OPCODE: handle_name,
    codes.REQUEST_USER_LIST_OPCODE: handle_user_list_request,
    codes.CONNECT_TO_SERVER_MEDIATED_OPCODE: handle_mediated_connection,
    codes.CLIENT_REQUEST_P2P_OPCODE: handle_p2p_connection,
    codes.CONSENT_REQUEST_P2P_OPCODE: consent_recieved_p2p_connection,
}


#---- SERVER MAIN LOOP -----#
def main():
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 12345
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")
    while True:
        client_socket, client_address = server_socket.accept()
        clients[client_address] = client_socket
        print(f"Accepted connection from {client_address}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address,))
        client_handler.start()


if __name__ == "__main__":
    main()