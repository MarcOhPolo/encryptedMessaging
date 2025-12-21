import socket
from queue import Queue

class P2PSession:

    def __init__(self, socket, peer):
        self.socket = socket
        self.peer_name = peer
        self.inbox = Queue()
        self.active = True

        P2PSession.p2p_chat_ui(self)

    def p2p_listener(session):

        while session.active:
            data = session.socket.recv(4096)
            if not data:
                break
            session.inbox.put(data.decode("utf-8"))

    def p2p_chat_ui(session):

        print(f"\n--- Chat with {session.peer_name} ---")
        print("Type '/exit' to leave\n")

        while session.active:
            while not session.inbox.empty():
                print(f"{session.peer_name}: {session.inbox.get()}")

            msg = input("> ")
            if msg == "/exit":
                session.active = False
                session.socket.close()
                break

            session.socket.sendall(msg.encode("utf-8"))
