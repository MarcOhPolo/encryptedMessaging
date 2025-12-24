import socket
from queue import Queue
import threading

class P2PSession:

    def __init__(self, socket, peer_name, peer_address):
        self.socket = socket
        self.peer_name = peer_name
        self.peer_address = peer_address
        self.inbox = Queue()
        self.active = True

        P2PSession.p2p_bootstrap(self,socket,peer_address)

    def p2p_listener(session):
        while session.active:
            data = session.socket.recv(4096)
            if data:
                session.inbox.put(data.decode("utf-8"))
            while not session.inbox.empty():
                print(f"{session.peer_name}: {session.inbox.get()}")

    def p2p_connect(socket,peer_address):
        socket.connect(peer_address)

    def p2p_chat_ui(session):

        print(f"\n--- Chat with {session.peer_name} ---")
        print("Type '/exit' to leave\n")

        while session.active:

            msg = input("")
            if msg == "/exit":
                session.active = False
                session.socket.close()
                break

            session.socket.sendall(msg.encode("utf-8"))

    def p2p_bootstrap(self,socket,peer_address):
        P2PSession.p2p_connect(socket,peer_address)
        listen_thread = threading.Thread(target=P2PSession.p2p_listener, args=(self,),daemon=True)
        listen_thread.start()
        P2PSession.p2p_chat_ui(self)