import socket
import json
import os, sys
import uuid
import threading
import game_track as gt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import shared.packet as packet

RECV_SIZE = 1024
SOCKET_TIMEOUT = 1

clients = [] # SHARED RESOURCE - MUST BE UNLOCKED AND LOCKED WHEN USING!
client_lock = threading.Lock()

class client:
    '''
    Client class requires the following:
        - ID
        - server_connection object
        - Client IP
        - Client Port

    Methods:
        Printing the object itself will display the IP:PORT and ID.
        .send(data) will encode and send the data from the paramater to the server in the server_connection object. 
        .recieve() will decode and return the data to the caller.
        .close() will close the client connection and remove itself from the clients list.

    '''
    def __init__(self, new_uuid, conn, ip, port):
        self.id = new_uuid
        self.conn = conn
        self.ip = ip
        self.port = port
        self.ready = False

    def __str__(self):
        return f"Client connected: {self.ip}:{self.port} ID: {self.id}"
    
    def send(self, data):
        '''.send(data) will encode and send the data from the paramater to the server in the server_connection object.'''
        
        if isinstance(data, str):
            data = data.encode()
        self.conn.sendall(data + b'\n')

    
    
    def receive(self) -> bytes:
        '''
        .receive() will decode and return the data to the caller.
        Returns a dictionary with the status and the data.
        '''
        buff = b''
        while True:
            d = self.conn.recv(RECV_SIZE)
            
            if not d:
                raise ConnectionError("Connection closed.")
            buff += d
            
            if b'\n' in buff:
                full_data, buff = buff.split(b'\n', 1)
                return full_data
            
            if len(buff) >= RECV_SIZE:
                return buff        
    
    def close(self):
        '''.close() will close the client connection and remove itself from the clients list.'''

        with client_lock:
            clients.remove(self)
            self.ready = False
            self.conn.close()

        print(f"Client disconnected: {self.ip}:{self.port} ID: {self.id}")

    def get_id(self) -> str:
        '''.get_id() will return the ID of the client connection.'''
        return self.id
    
    def ready_up(self):
        '''.ready_up() will set the client as ready after getting the initial info.'''
        with client_lock:
            self.ready = True
    
    def is_ready(self) -> bool:
        return self.ready
        

class server_connection:
    '''
    This class requires:
        - A socket when opened.
        - IP
        - Port
    
    Methods:
        .get_active(), returns active connections
        .accept_clients(client_handler), starts accepting new clients and have each one run client_handler() 
        .Printing the object would return the IP:PORT and active connections
        .close(), closes the socket of the server, disconnecting all clients.


    '''
    def __init__(self, socket, ip, port):
        self.socket = socket
        self.recv_size = RECV_SIZE
        self.ip = ip
        self.port = port
        self.clients = clients
        self.clients_lock = client_lock
        self.game_state = gt.Game_State()
        


    def get_active(self):
        '''Gets a the number of active clients.'''

        clients_len = 0

        with client_lock:
            clients_len = len(clients)
            
        return clients_len
    
    def __str__(self):
        return f"Listening at: {self.ip}:{self.port}, with {self.get_active()} active connections."
    
    
    def accept_clients(self, client_handler ):
        ''' .accept_clients() must recieve a handler which contains a server_connection object and a client object.'''
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
            t = threading.Thread(target=client_handler, args=(c, self, ), daemon=True)
            t.start()
            print(f"There is now {self.get_active()} active connections.")

        return 
    
    def update_clients(self, data=None):
        #TODO: Implement a function that sends updates via a different threads that monitor game changes. 
        # Im not sure if we need a queue for this, or handle client will send changes immediately and do it for us. 
            
        if not data:
            raise ValueError(f"No data to send to clients.")
        if not self.clients:
            raise Exception ("No clients connected to send data to.")
        

        with self.clients_lock:
            for aClient in self.clients:

                if aClient.is_ready():
                    try:
                        aClient.send(data)
                    except socket.error as e:
                        print(f"Error sending data to client {aClient.id}: {e}")
                        aClient.close()

    def send_player_list(self):
        ''' sends the player list to all clients. '''
        player_list = self.game_state.get_player_list()
        data = packet.serialize({
            "p1": player_list["p1"].id or "",
            "p2": player_list["p2"].id or "",
            "p3": player_list["p3"].id or "",
            "p4": player_list["p4"].id or ""
        }, packet.Status.PLAYER_LIST)

        try: 
            self.update_clients(data)
        except Exception as e:
            print(f"Error sending player list: {e}")
            return
        
        print(f"sent player list to all clients")

    def send_scoreboard(self):
        '''
        Sends the scoreboard to all clients.
        '''

        curr_scoreboard = self.game_state.get_scoreboard()

        if not curr_scoreboard:
            raise ValueError("GAME_STATE ERROR: No scoreboard to send.")
        
        data = packet.serialize({
            "upper_score": curr_scoreboard["upper_score"],
            "lower_score": curr_scoreboard["lower_score"]
        }, packet.Status.SCOREBOARD)

        try:
            self.update_clients(data)
        except Exception as e:
            print(f"Error sending scoreboard: {e}")
            return
        
        print(f"Sent scoreboard to all clients")


    def close(self):
        self.socket.close()

def load_config():
    '''Loads the configuration from the config.json file in the same directory as the file.'''

    config_path = os.path.join(os.path.dirname(__file__), 'config.json')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"'config.json' not found at {config_path}.")
    
    with open(config_path, 'r') as file:
        return json.load(file)
    

def init_host():
    '''
    Initiate a connection using the server IP and port load_config(). Opens A TCP socket and returns the socket object.
    Returns ValueError Exception when the configuration is not loaded correctly.
    Returns ConnectionError Exception if failed during open, bind, and listen stages.
    
    Returens a server_connection object on success.
    '''
    config = load_config()
    ip = config["host_ip"]
    port = config["host_port"]

    s = None

    if not ip or not port:
        raise ValueError("Missing host_ip or host_port in config.json")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.bind((ip, port))
        s.listen() 
        
    except socket.error as e:
        print(e)
        if s:
            s.close()
        raise ConnectionError(f"Failed to host on {ip}:{port}.")
    
    connection = server_connection(s, ip, port)
    return connection

