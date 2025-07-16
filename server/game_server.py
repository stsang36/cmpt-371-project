import socket
import json
import os
import uuid
from _thread import start_new_thread
import threading

RECV_SIZE = 1024
SOCKET_TIMEOUT = 1

clients = [] # SHARED RESOURCE - MUST BE UNLOCKED AND LOCKED WHEN USING!
client_lock = threading.Lock()

class client:
    def __init__(self, new_uuid, conn, ip, port):
        self.id = new_uuid
        self.conn = conn
        self.ip = ip
        self.port = port

    def __str__(self):
        return f"Client connected: {self.ip}:{self.port} ID: {self.id}"
    
    def send(self, data):
        if isinstance(data, str):
            data = data.encode()
        self.conn.sendall(data)
    
    def receive(self):
        return self.conn.recv(RECV_SIZE).decode()
    
    def close(self):
        self.conn.close()

        with client_lock:
            clients.remove(self)
        print(f"Client disconnected: {self.ip}:{self.port}")
        

# TODO: This function needs to handle any updates sent from the client.
def handle_client(client, conn):
    try:
        while True:
            data = client.receive()
            print(data)

            client.send("back at you!")

    except Exception as e:
        print(f"Client Error: {e}")
    finally:
        client.close()
        print(f"There is now {conn.get_active()} active connections.")

    pass

def update_thread(client_list):
    # This thread would send all clients about game updates. 
    pass


class server_connection:
    def __init__(self, socket, ip, port):
        self.socket = socket
        self.recv_size = RECV_SIZE
        self.ip = ip
        self.port = port

        with client_lock:
            self.clients = clients

    def get_active(self):
        clients_len = 0

        with client_lock:
            clients_len = len(clients)
            
        return clients_len
    
    def __str__(self):
        return f"Listening at: {self.ip}:{self.port}, with {self.get_active()} active connections."
    
    def accept_clients(self):
        while True:
            if not self.socket:
                raise ConnectionError("Socket is not initialized.")
            
            try: 
                self.socket.settimeout(SOCKET_TIMEOUT)
                client_c, client_addr = self.socket.accept()
            except socket.timeout:
                continue
            except socket.error as e:
                print(f"Socket Error: {e}")
                raise ConnectionError(f"Failed to accept: {self.ip}:{self.port}.")
            client_id = uuid.uuid4()
            c = client(client_id,client_c, client_addr[0], client_addr[1])
            with client_lock:
                self.clients.append(c)
            
            print(f"New Client: {c}")
            start_new_thread(handle_client, (c, self, ) )
            print(f"There is now {self.get_active()} active connections.")

        return 
    
    def update_clients(self):
        #TODO: Implement a function that sends updates via a different threads that monitor game changes. 
        # Im not sure if we need a queue for this, or handle client will send changes immediately and do it for us. 
        pass
    
    
    def close(self):
        self.socket.close()

# Load the configuration from config.json
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"'config.json' not found at {config_path}.")
    
    with open(config_path, 'r') as file:
        return json.load(file)
    

# Initiate a connection using the server IP and port from config.json. Opens A TCP socket and returns the socket object.
def init_host():
    config = load_config()
    ip = config["host_ip"]
    port = config["host_port"]

    s = None

    if not ip or not port:
        raise ValueError("Missing host_ip or host_port in config.json")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((ip, port))
        s.listen() 
        
    except socket.error as e:
        print(e)
        if s:
            s.close()
        raise ConnectionError(f"Failed to host on {ip}:{port}.")
    
    connection = server_connection(s, ip, port)
    return connection

