
import base64
from collections import defaultdict
import json
import socket
import sys

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

from config import Config


class Message:
    def __init__(self, msg: bytes):
        self.msg = msg


    def print_new(self):
        """
        _summary_
        """

        print('\n\n================= NEW =================\n\n')
        print(f"{self.data.get('from')[-5:]}: {self.data.get('body')}")


    def print_reply(self):
        """
        _summary_
        """

        pass


    def end_conversation(self):
        """
        _summary_
        """

        print('\n\n================= END =================\n\n')


class Handshake:
    def __init__(self, data: dict, conn: socket.socket):
        """
        _summary_

        :param data: _description_
        :type data: dict
        """

        self.fields = ['hello', 'host_id', 'pk', 'mode']
        self.data = data
        self.conn = conn
        self.serialized_data = None
        self.is_valid = False
        self.validate()
    
    
    def validate(self) -> bool:
        """_summary_

        :raises ValueError: _description_
        :raises TypeError: _description_
        :return: _description_
        :rtype: bool
        """

        if (len(self.data.keys())) != len(self.fields):
            raise ValueError(f"The fields quantity ({len(self.fields)}) do not match. Please check.")
        for field in self.fields:
            if not self.data.get(field):
                raise ValueError(f"The field <{field}> is missing. Please check.")
        
        # Compare the hello message
        if self.data.get('hello') != Config.HELLO_MSG:
            return
        
        # Success
        self.is_valid = True
    

    def request(self):
        """_summary_
        """

        self.serialize()
        self.send()
    

    def accept(self) -> dict:
        """_summary_
        """

        self.data['pk'] = base64.b64decode(self.data['pk'])
        return self.data


    
    def serialize(self):
        """_summary_
        """

        self.serialized_data = self.data.copy()
        self.serialized_data['pk'] = base64.b64encode(self.serialized_data['pk'].encode()).decode()
        self.serialized_data = json.dumps(self.serialized_data)
    

    def send(self):
        """_summary_

        :raises ValueError: _description_
        :raises TypeError: _description_
        :return: _description_
        :rtype: _type_
        """

        try:
            self.conn.sendall(self.serialized_data.encode())
        except socket.error as e:
            print(f"Error while handshaking: {e}")
            raise


class InboundMessage(Message):
    def __init__(self, msg: bytes, peers: dict, host_id_origin: str):
        super().__init__(msg)
        self.queue = defaultdict(list)
        self.data: dict = None
        self.is_valid = False
        self.peers = peers
        self.host_id_origin = host_id_origin
    

    def get(self):
        pass


    def read(self):
        """
        _summary_
        """
        
        self.parse()
        self.decrypt()

        if not self.validate():
            return
    

    def parse(self):
        """
        _summary_
        """

        try:
            self.data = json.loads(self.msg.decode())
        except json.JSONDecodeError as e:
            raise ValueError(f'Could not parse the JSON: {str(e)}')


    def decrypt(self):
        """
        _summary_
        """

        try:
            self.data['from'] = Config.PRIVATE_KEY.decrypt(
                base64.b64decode(self.data.get('from')),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            ).decode()

            self.data['body'] = Config.PRIVATE_KEY.decrypt(
                base64.b64decode(self.data.get('body')),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            ).decode()
        except:
            return
    
        
    def is_mine(self):
        """
        _summary_
        """

        return self.data.get('to') == Config.NODE_ID

    
    def validate(self) -> bool | None:
        """
        _summary_
        """

        if not self.data:
            return
        if not self.data.get('from'):
            return
        if not self.data.get('to'):
            return
        if not self.data.get('body'):
            return
        
        # Success
        self.is_valid = True
        
        # TODO: Validate the min and max size of each value for each key
        # TODO: Do not forward the message if it contains invalid data
        
        # Forward the message if its recipient ins't this node
        if not self.is_mine():
            self.forward()
            return
        
        return True
    

    def forward(self):
        """
        _summary_
        """

        for node_id in self.peers:
            if node_id == self.host_id_origin:
                continue
            print(f'*** forwarding message: {self.msg}')
            conn = self.peers.get(node_id).get('conn')
            try:
                conn.sendall(self.msg)
                print(f'*** ok\n')
            except socket.error as e:
                print(f"Error while handshaking: {e}")
                raise


    def get_from(self):
        """
        _summary_
        """

        return self.data.get('from')
    

    def get_to(self):
        """
        _summary_
        """

        return self.data.get('to')
    

    def get_body(self):
        """
        _summary_
        """

        return self.data.get('body')
    

    def print_reply(self):
        """
        _summary_
        """

        print('')
        sys.stdout.write("\033[F")  # Move the cursor to the previous line
        sys.stdout.write("\033[K")  # Erases the current line
        print(f"{self.data.get('from')[-5:]}: {self.data.get('body')}")


class OutboundMessage(Message):
    def __init__(self, msg: str, peers: dict=None, talking_to: str=None):
        self.is_valid = False
        self.recipient_id = None
        self.message = None
        self.data = None
        self.encrypted_data = None
        self.serialized_data = None
        self.peers = peers
        self.talking_to = talking_to
        self.pk = None
        if not self.validate(msg):
            return
        super().__init__(msg)
        self.queue = defaultdict(list)
    
    
    def validate(self, msg: str):
        """
        _summary_
        """

        length = len(msg)
        
        if length == 0 and self.talking_to:
            return

        # Check the regular messages requisites
        if length < 67:  # At least '@' + <node_id> + ' ' + <letter>
            print('\nYou cannot send empty messages. Use the following example for the first message:')
            print('@20930d3366acdaf6f60ee5a41fee2c6455d7afe282cf0b5b115f4be37af4400d Hi there!\n')
            return
        elif length > Config.MSG_MAX_LENGTH:
            print('\nYou cannot send messages with more than 500 characters.')
            print('Please try again.\n')
            return
        elif msg[0] != '@':
            print('\nYou must mention the recipient (node ID) preceded by "@". Example for the first message:')
            print('@20930d3366acdaf6f60ee5a41fee2c6455d7afe282cf0b5b115f4be37af4400d Hi there!\n')
            return
        
        self.is_valid = True
        self.recipient_id = msg[1:65]  # TODO: Must validate the node_id
        self.message = msg[65:].strip()
        
        self.build()
        self.set_pk()
        self.encrypt()
        self.serialize()

        return True
    

    def print_new(self):
        """
        _summary_
        """

        print('\n\n================= NEW =================\n\n')
        print(f'You: {self.data.get('body')}')
    

    def print_reply(self):
        """
        _summary_
        """
        
        print('')
        sys.stdout.write("\033[F")  # Move the cursor to the previous line
        sys.stdout.write("\033[K")  # Erases the current line
        sys.stdout.write("\033[F")  # Move the cursor to the previous line
        sys.stdout.write("\033[K")  # Erases the current line
        print(f'You: {self.data.get('body')}')


    def set_pk(self):
        """
        _summary_
        """

        for node_id in self.peers:
            pk = self.peers.get(self.recipient_id).get('pk')
        if not isinstance(pk, str):
            raise TypeError("The <pk> argument must of type <str>.")
        self.pk = pk


    def build_handshake(self):
        """
        _summary_
        """

        self.data = {
            "message": self.msg,
            "host_id": Config.NODE_ID,
        }

    
    def build_handshake_pk(self):
        """
        _summary_
        """

        self.data = {
            "pk": self.msg,
            "host_id": Config.NODE_ID,
        }


    def build(self):
        """
        _summary_
        """

        self.data = {
            'from': Config.NODE_ID,
            'to': self.recipient_id,
            'body': self.message
        }
    

    def encrypt(self):
        """
        _summary_
        """
        
        public_key = serialization.load_pem_public_key(self.pk.encode())

        self.encrypted_data = self.data.copy()
        self.encrypted_data['from'] = public_key.encrypt(
            self.data.get('from').encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        self.encrypted_data['body'] = public_key.encrypt(
            self.data.get('body').encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        self.encrypted_data['from'] = base64.b64encode(self.encrypted_data['from']).decode()
        self.encrypted_data['body'] = base64.b64encode(self.encrypted_data['body']).decode()


    def serialize(self):
        """
        _summary_
        """

        self.serialized_data = json.dumps(self.encrypted_data)


    def send(self, conn: socket.socket):
        """
        Sends a message to one or more connected peer(s).

        :param conn: _description_
        :type conn: socket.socket
        """

        if not self.is_valid:
            return
        try:
            conn.sendall(self.serialized_data.encode())
        except socket.error as e:
            pass
    

    def get_data(self) -> dict:
        """
        _summary_
        """
        
        return self.data

