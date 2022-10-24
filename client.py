import select
import socket
import struct
import time


class ClientSocket:
    def __init__(self, server_ip: str, server_port: int):
        self.server_ip = server_ip
        self.server_port = server_port
        self.disconnect_message = "!DISCONNECT"
        self.socket = self.connect_to_server()
        self.socket.setblocking(False)

    def connect_to_server(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server_ip, self.server_port))

        return client_socket

    def receive_all(self, bytes):
        # Helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < bytes:
            packet = self.socket.recv(bytes - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def recv_msg(self):
        try:
            # Read message length and unpack it into an integer
            raw_msglen = self.receive_all(4)
            if not raw_msglen:
                return None
            msglen = struct.unpack(">I", raw_msglen)[0]
            # Read the message data
            data = self.receive_all(msglen)
            if data is not None:
                return data.decode()
            return data
        except:
            return None

    def get_last_msg_from_buffer(self):
        msg = None
        while True:
            new_msg = self.recv_msg()
            if new_msg is None:
                break
            msg = new_msg

        return msg

    def run(self):
        msg = None
        inputs = [self.socket]
        readable, _, _ = select.select(inputs, [], inputs, 2)
        for _ in readable:
            msg = self.get_last_msg_from_buffer()
        return msg


server_ip = socket.gethostbyname(socket.gethostname())
server_port = 5051
client = ClientSocket(server_ip=server_ip, server_port=server_port)

connected = True
while connected:
    msg = client.run()
    print(msg)
    if msg == client.disconnect_message:
        print("[DISCONNECTED FROM SERVER]")
        connected = False
    time.sleep(0.5)
