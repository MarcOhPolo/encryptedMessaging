import socket
import threading
from EventBus import EventBus
from codes import *
from p2p_session import P2PSession


greeting_msg = ("Hi there, welcome to the MS encrypted messaging service! :D")


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 12345

    client_socket.connect((host, port))

    listen_thread = threading.Thread(target=listening_thread, args=(client_socket,),daemon=True)
    listen_thread.start()

    print(greeting_msg)
    name_registration(client_socket)

    client_interface_thread = threading.Thread(target=cmd, args=(client_socket,))
    client_interface_thread.start()


def name_registration(client_socket):
    name = input("Enter your name: ")
    name_submission = EventBus.message_builder(NAME_OPCODE,name)
    client_socket.sendall(name_submission)
    data = EventBus.get_from_queue(RESPONSE_NAME_OPCODE)
    print(f"{data}")


def request_userlist(client_socket, args=None):
    # Request user list from server
    # Now uses the EventBus to get the response from the listening thread instead of blocking recv
    client_socket.sendall(REQUEST_USER_LIST_OPCODE.encode('utf-8'))
    return EventBus.get_from_queue(RESPONSE_USER_LIST_OPCODE)


def request_connection(client_socket,args=None):
    target = select_target_user(client_socket)
    client_socket.sendall(CONNECT_TO_SERVER_MEDIATED_OPCODE.encode('utf-8')+target.encode('utf-8'))
    data = EventBus.get_from_queue(CONSENT_REQUEST_P2P_OPCODE)
    print(data)


def choose_target(client_socket, args=None):
    target = select_target_user(client_socket)
    return target


def select_target_user(client_socket):
    display_userlist(client_socket)
    while True:
        target = input("Select a user to connect to (enter name): ")
        if search_userlist(client_socket, target):
            print(f"Selected user: {target}")
            break
    return target

def search_userlist(client_socket, target):
    userlist = request_userlist(client_socket)
    return target in userlist["values"].values()

def display_userlist(client_socket, args=None):
    event_payload = request_userlist(client_socket)
    print(f"""User List:\n
{event_payload["formatted"]}""")
    return event_payload


def listening_thread(client_socket):
    with client_socket:
        while True:
            data = client_socket.recv(1024)
            if data:
                EventBus.publish(data)


def request_counter(client_socket, args=None):
    request_count = EventBus._queues[CONSENT_REQUEST_P2P_OPCODE].qsize()
    print(f"Connection requests: {request_count}")
    if request_count > 0:
        for _ in range(request_count):
            name = EventBus.get_from_queue(CONSENT_REQUEST_P2P_OPCODE)
            print(f"Connection request from: {name}")
        print(f"To respond, use the 'p2p' command with the name, then accept, ignore to deny")


def p2p_connection_handler(client_socket, args=None):
    try:
        argc = len(args)
        target = ""

        # p2p command with no target specified, displays user list, then input target
        if argc == 0:
            target = choose_target(client_socket)
        # p2p command with target specified
        if argc == 1:
            target = args[0]
            if not search_userlist(client_socket, target):
                print(f"User {target} not found")
                return 
        # Request has been accepted
        if argc == 2:
            p2p_consent(client_socket, args)
            target_address = EventBus.get_from_queue(
                RESPONSE_CLIENT_ADDRESS_OPCODE
            )
            if not target_address:
                print("Failed to retrieve target address.")
                return

            p2p_session_open(target_address)
            return
        # Only runs past this point if it's a request and not acceptance
        p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        p2p_socket.bind(("0.0.0.0", 0))
        request_payload = [target, client_socket.getsockname()[0], p2p_socket.getsockname()[1]]
        request = EventBus.message_builder(CLIENT_REQUEST_P2P_OPCODE, request_payload)
        client_socket.sendall(request)

    except (OSError, RuntimeError) as e:
        print(f"P2P error: {e}")



def p2p_consent(client_socket, args=None):
    
    if search_userlist(client_socket, args[0]):
        #Needs to change to send p2p session socket information
        message = EventBus.message_builder(CONSENT_TO_P2P,args)
        client_socket.sendall(message)
    else:
        print(f"{args[0]} is not a valid user, please input a connected user (see userlist)")


def p2p_session_open(peer_name, p2p_socket=None):
    if not p2p_socket:
        p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return P2PSession(p2p_socket, peer_name)



COMMANDS = {
    "userlist": display_userlist,
    "p2p": p2p_connection_handler,
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