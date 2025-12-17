import socket
import threading
from EventBus import EventBus
from EventBus import codes


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
    listen_thread = threading.Thread(target=listening_thread, args=(client_socket,),daemon=True)
    listen_thread.start()


def name_registration(client_socket):
    name = codes.NAME_OPCODE + input("Enter your name: ")
    client_socket.sendall(name.encode('utf-8'))
    data = client_socket.recv(1024).decode('utf-8')
    print(f"{data}")


def request_userlist(client_socket, args=None):
    # Request user list from server
    # Now uses the EventBus to get the response from the listening thread instead of blocking recv
    client_socket.sendall(codes.REQUEST_USER_LIST_OPCODE.encode('utf-8'))
    return EventBus.get_from_queue(codes.RESPONSE_USER_LIST_OPCODE)


def request_connection(client_socket,args=None):
    target = select_target_user(client_socket)
    client_socket.sendall(codes.CONNECT_TO_SERVER_MEDIATED_OPCODE.encode('utf-8')+target.encode('utf-8'))
    data = EventBus.get_from_queue(codes.RESPONSE_CLIENT_ADDRESS_OPCODE)
    print(data)


def choose_connection(client_socket, args=None):
    target = select_target_user(client_socket)
    client_socket.sendall(codes.CONNECT_TO_P2P_OPCODE.encode('utf-8')+target.encode('utf-8'))
    # WHEN THE SERVER RESPONDS WITH THE ADDRESS OF THE OTHER CLIENT
    # LAUNCH P2P CONNECTION HERE ON A NEW THREAD
    # Returns JSON with all information neeeded to make a socket connection
    p2p_connection_handler(client_socket, EventBus.get_from_queue(codes.RESPONSE_CLIENT_ADDRESS_OPCODE))


def select_target_user(client_socket):
    userlist = display_userlist(client_socket)
    while True:
        target = input("Select a user to connect to directly (enter name): ")
        if target in userlist["values"].values():
            print(f"Selected user: {target}")
            break
    return target


def display_userlist(client_socket, args=None):
    event_payload = request_userlist(client_socket)
    print(f"""User List:\n
{event_payload["formatted"]}
    """)
    return event_payload


def listening_thread(client_socket):
    while True:
        data = client_socket.recv(1024)
        if data:
            EventBus.publish(data)


def request_counter(connection_requests=[]):
    print(f"Connection requests: {len(connection_requests)}")


def p2p_connection_handler(client_socket, address):
    print(f"Establishing P2P connection to {address}...")
    # p2p_connection_establish(address)
    print(f"P2P connection to {address} established.")


def p2p_connection_establish(address):
    p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p2p_socket.connect(address)
    print("P2P connection established.")


def p2p_consent_request_handler(client_socket, address):
    print(f"Requesting consent for P2P connection from {address}...")
    client_socket.sendall(codes.CONSENT_REQUEST_P2P_OPCODE.encode('utf-8'))


def p2p_connection_consent_handler(client_socket, address):
    print(f"Received P2P connection request from {address}.")


COMMANDS = {
    "userlist": display_userlist,
    "p2p": choose_connection,
    "server-mediated": request_connection,
    "requests": request_counter,
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
            COMMANDS[name](client_socket, args)
        else:
            print(f"Unknown command: {name}")


if __name__ == "__main__":
    main()