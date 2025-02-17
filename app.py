
import sys

from config import Config
from messages import OutboundMessage
from nodes import Node


def set_initial_config():
    """xxx"""

    Config.set_node_id()
    Config.set_test_config()  # Tests only
    Config.set_inbound_port()
    Config.set_outbound_port()
    print(f'\nInbound Port: {Config.INBOUND_PORT}')
    print(f'Outbound Port: {Config.OUTBOUND_PORT}\n')
    print(f'NODE_ID: {Config.NODE_ID}\n')


def show_search_menu():
    """xxx"""

    print("1. Search for nodes over the LAN")
    print("2. Search for nodes over the internet")
    print("3. Search for nodes over both the LAN and the internet")
    print("4. Exit")


def show_recipient_menu():
    """xxx"""

    print("1. Search for nodes over the LAN")
    print("2. Search for nodes over the internet")
    print("3. Search for nodes over both the LAN and the internet")
    print("4. Exit")
    

def run():
    """Starts the application"""

    set_initial_config()

    node = Node()
    node.search(lan=True)
    node.start_server()
    node.get_messages()
    conn = node.accept_connections()

    while True:

        msg = input("> ")

        if msg.lower() == '/exit':
            print('Bye!\n')
            sys.exit()
        elif msg.lower() == '/nodes':
            print(f'\nNodes: {node.peers}\n')
            continue
        elif msg.lower() == '/bye':
            node.end_conversation()
            continue

        # Complement the user message if they are already in a conversation
        if node.get_talking_to():
            msg = f'@{node.get_talking_to()} {msg}'

        # Instantiate the OutboundMessage class
        m = OutboundMessage(msg)
        if not m.is_valid:
            continue
        
        recipient_id = m.get_data().get('to')
        conn = node.peers.get(recipient_id)

        # Print the messages
        if recipient_id != node.get_talking_to() and node.get_talking_to() is not None:
            m.end_conversation()
        elif node.get_talking_to() is None:
            m.print_new()
            node.set_talking_to(recipient_id)
        elif recipient_id == node.get_talking_to():
            m.print_reply()

        # If the peer is directly connected to this node send directly to it
        if conn:
            m.send(conn)
        
        # If the peer is not directly connected to this node, forward to all connected peers
        elif not conn:
            for node_id, conn in node.peers.items():
                m.send(conn)




if __name__ == '__main__':
    run()
