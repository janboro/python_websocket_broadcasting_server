import logging
import os
import socket
import struct
import threading
import time


class ServerSocket:
    def __init__(self, host_ip: str, port: int):
        self.host_ip = host_ip
        self.port = port
        self.disconnect_message = "!DISCONNECT"
        self.clients = []
        self.socket = self.setup_server()
        self.orderbook_thread = threading.Thread(target=self.accept_connections).start()

    def setup_server(self) -> socket.socket:
        logging.info("Setting up server...")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host_ip, self.port))
        server_socket.listen()
        logging.info("Server setup successful on %s:%s", self.host_ip, self.port)

        return server_socket

    def broadcast_message(self, message):
        message = struct.pack(">I", len(message)) + message.encode()
        if len(self.clients) > 0:
            for client in self.clients:
                client[0].sendall(message)

    def accept_connections(self):
        while True:
            conn, addr = self.socket.accept()
            if addr not in self.clients:
                self.clients.append([conn, addr])
            logging.info("[ACTIVE CONNECTIONS]: %s", len(self.clients))

    def close_all_connections(self):
        self.broadcast_message(message=self.disconnect_message)
        time.sleep(5)  # waiting that all clients are disconnected in order to not block the port


host_ip = socket.gethostbyname(socket.gethostname())
port = 5051
server = ServerSocket(host_ip=host_ip, port=port)

i = 0
running = True
while running:
    msg = f"{i} Hello"
    server.broadcast_message(msg)
    time.sleep(0.1)
    i += 1
    if i == 50:
        server.close_all_connections()
        logging.info("closed")
        running = False
os._exit(1)  # closing the main thread
