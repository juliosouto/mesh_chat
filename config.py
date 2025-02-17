
import random
import socket
import uuid

from utils import str_to_hash


class Config:
    """Global configuration"""

    NODE_ID: str = None
    DEBUG: bool = True
    HOST: str = '0.0.0.0'
    PORT_RANGE: tuple = (54000, 54011) #(54000, 54101)
    SEARCH_INTERNET_IP_RANGE: tuple = ('189.18.143.140', '189.18.143.155')  # 189.18.143.149
    WAIT_BETWEEN_SEARCHES: int = 5
    INBOUND_PORT: int = None
    OUTBOUND_PORT: int = None
    MAX_PEERS_PER_NODE: int = 10
    HELLO_MSG: str = 'Hello Peer, you are connected!'
    MSG_MAX_LENGTH: int = 565

    # For tests
    USE_RANDOM_NODE_ID = True  # Useful when running 2 or more instances on the same machine


    @classmethod
    def set_node_id(cls):
        """xxx"""

        cls.NODE_ID = str_to_hash(str(uuid.getnode()))


    @classmethod
    def set_test_config(cls):
        """xxx"""

        if cls.USE_RANDOM_NODE_ID is True:
            cls.NODE_ID = str_to_hash(str(random.randint(1000000, 9000000)))


    @classmethod
    def set_inbound_port(cls):
        """Host port (for accepting connections and receiving messages)"""

        for port in range(*cls.PORT_RANGE):
            if cls.is_port_free(port):
                cls.INBOUND_PORT = port
                break
        else:
            raise ValueError(f'There is no port available in the range <{cls.PORT_RANGE}>')
    

    @classmethod
    def set_outbound_port(cls):
        """Client port (for sending messages)"""

        cls.OUTBOUND_PORT = random.randint(60000, 61000)
        return

        for port in range(*cls.PORT_RANGE):
            if port == cls.INBOUND_PORT:
                continue
            if cls.is_port_free(port):
                cls.OUTBOUND_PORT = port
                break


    @classmethod
    def is_port_free(cls, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((cls.HOST, port))
                return True
            except socket.error:
                return False
