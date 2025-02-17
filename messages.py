
from collections import defaultdict
import json
import socket
import sys

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

        print('')
        sys.stdout.write("\033[F")  # Move the cursor to the previous line
        sys.stdout.write("\033[K")  # Erases the current line
        print(f"{self.data.get('from')[-5:]}: {self.data.get('body')}")


    def end_conversation(self):
        """
        _summary_
        """

        print('\n\n================= END =================\n\n')


class InboundMessage(Message):
    def __init__(self, msg: bytes):
        super().__init__(msg)
        self.queue = defaultdict(list)
        self.data: dict = None
    

    def get(self):
        pass


    def decrypt(self):
        """
        _summary_
        """

        pass


    def encrypt(self):
        """
        _summary_
        """

        pass


    def parse(self):
        """
        _summary_
        """

        try:
            self.data = json.loads(self.msg.decode())
        except json.JSONDecodeError as e:
            raise ValueError(f'Could not parse the JSON: {str(e)}')
    
        
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
        
        # TODO: Validate the min and max size of each value for each key
        # TODO: Do not forward the message if it contains invalid data
        
        # Forward the message if its recipient ins't this node
        if not self.is_mine():
            self.encrypt()
            self.forward()
            return
        
        return True
    

    def forward(self):
        """
        _summary_
        """

        pass


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


class OutboundMessage(Message):
    def __init__(self, msg: str):
        self.is_valid = False
        self.recipient_id = None
        self.message = None
        self.data = None
        self.serialized_data = None
        if not self.validate(msg):
            return
        super().__init__(msg)
        self.queue = defaultdict(list)
    
    
    def validate(self, msg: str):
        """
        _summary_
        """

        length = len(msg)
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
        print(f'You: {self.data.get('body')}')


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

        pass
    

    def serialize(self):
        """
        _summary_
        """

        self.serialized_data = json.dumps(self.data)


    def send(self, conn: socket.socket):
        """
        Sends a message to one or more connected peer(s).

        :param conn: _description_
        :type conn: socket.socket
        """

        try:
            conn.sendall(self.serialized_data.encode())
        except socket.error as e:
            pass
    
    def get_data(self) -> dict:
        """
        _summary_
        """
        
        return self.data

