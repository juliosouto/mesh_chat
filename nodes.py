
import json
from queue import Queue
import socket
import sys
import time

from config import Config
from messages import InboundMessage, OutboundMessage, Message
from utils import run_on_thread, ip_to_int, int_to_ip, str_to_hash


class Node:
    """
    Implements the Singleton pattern to ensure only one instance of the class is created.

    This class represents a node in a network, responsible for managing server connections
    and maintaining a list of connected peers.

    Attributes:
        _instance (Node): The single instance of the class (Singleton).
        server_socket (socket): Server socket for accepting connections.
        peers (dict): Dict of <host_id> and connected nodes (peers).
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Controls the creation of class instances, ensuring only one is created (Singleton).

        :return: The single instance of the class.
        :rtype: Node
        """

        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the node instance, setting up the server socket and the list of peers.
        """

        self.server_socket = None
        self.peers = {}
        self.talking_to = None  # Current conversation with

    
    def start_server(self):
        """Start the server to accept connections"""

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((Config.HOST, Config.INBOUND_PORT))
        self.server_socket.listen(5)
        print(f"Server started on {Config.HOST}:{Config.INBOUND_PORT}")
    

    def register_peer(self, host_id: str, conn: socket.socket):
        """xxx"""

        self.peers[host_id] = conn

    
    @run_on_thread
    def accept_connections(self):
        """
        Host accept connections from other nodes
        """
        
        while True:
            if len(self.peers.keys()) >= Config.MAX_PEERS_PER_NODE:
                #print('Could not accept a new connection. Max Peers limit reached.')
                time.sleep(5)  # Wait time before trying again
                continue

            conn, addr = self.server_socket.accept()

            try:
                msg = conn.recv(1024)  # Reads up to 1024 bytes
                data = self.validate_peer(msg.decode())
                if not data:
                    continue
                
                # Avoid accepting connections from itself
                if data.get('host_id') == Config.NODE_ID:
                    continue

                self.register_peer(data.get('host_id'), conn)
                print(f"Connection received from {addr}\n")

                # Identify itself to the connected peer
                conn.sendall(self.identify_itself().encode())

            except:
                continue
    

    def identify_itself(self) -> str:
        """
        Identifies itself to the connected peer.

        :return: The serialized JSON containing the host details.
        :rtype: str
        """

        data = {
            "message": Config.HELLO_MSG,
            "host_id": Config.NODE_ID,
        }
        return json.dumps(data)


    def get_peer_list(self):
        """xxx"""

        pass


    @run_on_thread
    def search(self, lan: bool=False, internet: bool=False):
        """
        Search for peers continuously.
        
        :param lan: Search for other peer on your local network.
        :type lan: bool

        :param internet: Search for other peers over the internet.
        :type internet: bool
        """

        if lan is False and internet is False:
            raise ValueError("The search arguments `lan` and `internet` cannot be both False")
        
        if lan:
            print('Searching for nodes over the LAN...')
        if internet:
            print('Searching for nodes over the internet...')

        # Run the searches
        while True:
            
            # Make sure the MAX_PEERS_PER_NODE limit isn't exceeded
            if len(self.peers.keys()) >= Config.MAX_PEERS_PER_NODE:
                time.sleep(Config.WAIT_BETWEEN_SEARCHES)  # Wait n seconds before trying again
                continue
            
            # Run the searches
            if lan:
                self.search_lan()
            if internet:
                self.search_internet()
            
            return  # disable


    def search_lan(self, peer_ip: str='127.0.0.1', timeout: float=0.5) -> socket.socket | None:
        """
        Search for peers in the local network.

        :param peer_ip: The peer's IP address.
        :type peer_ip: str
        
        :param timeout: The timeout in seconds for the connection attempt.
        :type timeout: float

        :return: The connected socket or None if it fails.
        :rtype: socket.socket or None
        """

        qs = []
        for port in range(*Config.PORT_RANGE):
            
            # Avoid connecting to itself
            if port == Config.INBOUND_PORT:
                continue

            q = Queue()
            qs.append(q)

            self.check_peer_and_connect(peer_ip, port, q)
        
        # Get the results from the queues
        for q in qs:
            result = q.get()
            if not result:
                continue
            conn = result[1]
            if conn:
                self.register_peer(result[0], conn)
    

    def search_internet(self) -> socket.socket | None:
        """
        Search for available peers over the internet.
        The method uses one thread per IP address and port,
        so the search can be done faster.

        :return: The connected socket or None if it fails.
        :rtype: socket.socket or None
        """

        return

        # Iterating over the IP range
        start_int = ip_to_int(Config.SEARCH_INTERNET_IP_RANGE[0])
        end_int = ip_to_int(Config.SEARCH_INTERNET_IP_RANGE[1])

        qs = []
        for ip_int in range(start_int, end_int + 1):
            peer_ip = int_to_ip(ip_int)

            # Iterate over each port in range
            for port in range(*Config.PORT_RANGE):
                
                # Avoid connecting to itself
                # TODO
                # TODO: Verify the machine ID and port below
                # TODO
                if port == Config.INBOUND_PORT:
                    continue
                
                q = Queue()
                qs.append(q)
                
                # NOTE: Working
                self.check_peer_and_connect(peer_ip, port, q)

        # Get the results from the queues
        for q in qs:
            if not q:
                continue
            result = q.get()
            if not result:
                continue
            conn = result[1]
            self.register_peer(result[0], conn)
    

    @run_on_thread
    def check_peer_and_connect(self, peer_ip: str, port: int, q: Queue=None) -> tuple[str, socket.socket] | None:
        """
        Tries to connect to a node at a specific IP and port.
        
        :param peer_ip: The peer's IP address.
        :type peer_ip: str

        :param port: The peer's port.
        :type port: int

        :param q: The Queue object to return the values from the thread.
        :type q: Queue

        :return: A tuple containing the <host_id> and the connected socket or None if it fails.
        :rtype: tuple[str, socket.socket] or None
        """

        # Make sure the MAX_PEERS_PER_NODE limit isn't reached
        if len(self.peers.keys()) >= Config.MAX_PEERS_PER_NODE:
            return
        
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((peer_ip, port))
            conn.sendall(self.identify_itself().encode())  # Hello message to the host

            # Check if the host responds with a valid message
            for _ in range(100):
                
                host_msg = conn.recv(1024).decode()
                if not host_msg:
                    continue
                data = self.validate_peer(host_msg)
                if not data:
                    q.put(None)
                    return
                break
            
            # If the connection is successful
            print(f'Located node on {peer_ip} : {port}\n')
            q.put((data.get('host_id'), conn))
            return (data.get('host_id'), conn)
        
        except:
            conn.close()
            q.put(None)
            return
        

    def validate_peer(self, msg: str) -> dict:
        """
        Validates the peer by checking its welcome message.

        :param msg: The message sent by the host after a successful connection.
        :type msg: str

        :return: A dictionary / JSON containing the host identification and hello message.
        :rtype: dict
        """

        if not msg:
            return
        if type(msg) is not str:
            raise TypeError("The argument <msg> must be str")
        
        data = json.loads(msg)

        if data.get('message') != Config.HELLO_MSG:
            return
        if not data.get('host_id'):
            return
        if self.peers.get(data['host_id']):  # Already connected
            return
        
        return data


    @run_on_thread
    def get_messages(self):
        """
        Listen to new messages from the connected peers.

        :param conn: The active connection to the peer.
        :type conn: socket.socket
        """
        
        while True:
            # Avoid RuntimeError because of changes in the dict during the iteration
            host_ids = tuple(self.peers.keys())

            for host_id in host_ids:
                try:
                    msg = self.peers.get(host_id).recv(1024)
                    if not msg:
                        continue

                    # Instantiate a new InboundMessage
                    m = InboundMessage(msg)
                    m.decrypt()
                    m.parse()
                    is_valid = m.validate()

                    if not is_valid:
                        #del m  # FIXME: Will affect the queues
                        continue
                    
                    # If the user is not talking to anybody (first message)
                    if self.talking_to is None:
                        self.talking_to = m.get_from()
                        m.print_new()
                    
                    # The user is talking to the same node
                    elif self.talking_to == m.get_from():
                        m.print_reply()
                    
                    # TODO: else
                
                except:
                    pass
    

    def end_conversation(self):
        """xxx"""

        self.talking_to = None
        Message(b'').end_conversation()


    def disconnect(self):
        """Disconnect"""

        pass


    def get_talking_to(self):
        """
        _summary_
        """

        return self.talking_to


    def set_talking_to(self, talking_to: str):
        """
        _summary_

        :param talking_to: _description_
        :type talking_to: str
        """

        if not type(talking_to) is str:
            raise TypeError('The type of <talking_to> must be str.')
        self.talking_to = talking_to
    
