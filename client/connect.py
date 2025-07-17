import socket
import json
import os

RECV_SIZE = 1024


# perhaps we need to make the client multithreaded to get and send game updates to the server. 
def send_thread(data):
    pass

def recv_thread(data):
    pass


class client_connection:
    def __init__(self, socket, ip, port):
        self.socket = socket
        self.recv_size = RECV_SIZE
        self.ip = ip
        self.port = port

    def __str__(self):
        return f"Client Connected to server at {self.ip}:{self.port}"

    def send(self, data):
        if isinstance(data, str):
            data = data.encode()
        self.socket.sendall(data)

    def receive(self):
        return self.socket.recv(self.recv_size).decode()
    
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
def init_connection():
    config = load_config()
    ip = config["server_ip"]
    port = config["server_port"]

    s = None

    if not ip or not port:
        raise ValueError("Missing IP and PORT in config.json")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
    except socket.error as e:
        print(e)
        if s:
            s.close()
        raise ConnectionError(f"Failed to connect to {ip}:{port}. Is the server running or blocked by firewall?")
    
    connection = client_connection(s, ip, port)
    return connection
    # return connection