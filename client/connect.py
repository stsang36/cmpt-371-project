import socket
import json
import os
import threading
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import shared.packet as packet
from typing import Optional

RECV_SIZE = 1024

class client_connection:
    '''
    Client connection class requires the following:
        - ID
        - socket object
        - Client IP
        - Client Port
    Methods:
        Printing the object itself will display the IP:PORT and ID.
        .send(data) will encode and send the data from the parameter to the server in the socket object.
        .receive() will decode and return the data to the caller.
        .close() will close the client connection.
        .start_receiving(recv_handler) will start a thread to listen for incoming data and call the provided handler.
        .set_id(new_id) will set the ID of the client connection.
        .get_id() will return the ID of the client connection.
    '''


    def __init__(self, socket, ip, port):
        self.id = None
        self.socket = socket
        self.recv_size = RECV_SIZE
        self.ip = ip
        self.port = port
        self.player_slot = None
        self.player_list: dict[str, dict[str, object]] = {
        '1': {'player': None, 'uuid': None},
        '2': {'player': None, 'uuid': None},
        '3': {'player': None, 'uuid': None},
        '4': {'player': None, 'uuid': None},
        }

        self.player_list_lock = threading.Lock()



    def __str__(self):
        return f"Client Connected to server at {self.ip}:{self.port}"

    def send(self, data, STATUS: packet.Status):
        
        packet_data = packet.serialize(data, STATUS)
        self.socket.sendall(packet_data + b'\n')  

    def receive(self):

        buff = b''
        while True:
            d = self.socket.recv(self.recv_size)

            if not d:
                raise ConnectionError("Connection closed.")
            buff += d
            if b'\n' in buff:
                full_data, buff = buff.split(b'\n', 1)
                return full_data
            
            if len(buff) >= self.recv_size:
                return buff
    
    def start_recieving(self, recv_handler):
        '''
        This function will start a thread and listen for any new data to be recieved.
        Takes in a handler that requires a client_connection object.
        '''
        print("Reciever Started...")
        t = threading.Thread(target=recv_handler, args=(self, ), daemon=True)
        t.start()
    
    def close(self):
        with self.player_list_lock:
            self.socket.close()

    def set_id(self, new_id):
        self.id = new_id
        print(f"Client ID set to: {self.id}")
    
    def get_id(self):
        return self.id
    
    def set_player_slot(self, slot):
        '''
        Set the player slot for this client.
        This is used to identify which player this client is controlling.
        '''
        self.player_slot = slot
        print(f"Player slot set to: {self.player_slot}")

def load_config():
    '''
    Load the configuration from config.json in the same directory as this file.

    We might change it so that ip and port are passed as arguments to the init_connection function.
    '''

    config_path = os.path.join(os.path.dirname(__file__), 'config.json')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"'config.json' not found at {config_path}.")
    
    with open(config_path, 'r') as file:
        return json.load(file)
    

def init_connection():
    '''
    Initiate a connection using the server IP and port from config.json. Opens A TCP socket and returns the socket object.
    '''
    config = load_config()
    ip = config["server_ip"]
    port = config["server_port"]

    s = None

    if not ip or not port:
        raise ValueError("Missing IP and PORT in config.json")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.connect((ip, port))
    except socket.error as e:
        print(e)
        if s:
            s.close()
        raise ConnectionError(f"Failed to connect to {ip}:{port}. Is the server running or blocked by firewall?")
    
    connection = client_connection(s, ip, port)
    return connection
