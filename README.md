
# MeshChat

This is an Open Source project for a console-based text communication service using a Mesh architecture. The goal is to enable efficient and decentralized message exchange between nodes, all through the terminal.

## Project Status
The project is currently under development and is not yet fully finished. Some features may be in the testing phase or still missing.

As of now, the application was manually tested on MacOS Sequoia, using Python 3.13.1. By running two instances of the application using two distinct terminal windows, they can automatically connect to each other.

## Current Features
- Real-time node search over the LAN.
- Real-time communication between nodes.
- Send and receive messages via the console.
- Decentralized Mesh-based architecture, where each node can directly communicate with others without the need for central servers.
- Automatic connection between nodes.

## Roadmap
- Flow control over the terminal.
- Add more docstrings and useful comments.
- Automated unit and integration tests.
- Real-time node search over the internet.
- Auto-forwarding of messages (routing).
- Messages encryption using asymmetric cryptography.
- Messages queues.
- SQLite for persistence.
- Support for Docker.
- Etc.

## How to Use

1. Clone the repository:
   ```bash
   git clone https://github.com/juliosouto/mesh_chat.git

2. Navigate to the project directory:
    ```bash
    cd mesh_chat

3. Create and activate a virtual environment:
    ```bash
    python3.13 -m venv .venv
    source .venv/bin/activate

4. Run the application:
    ```bash
    python app.py

5. Look for the NODE_ID printed to the console. It looks like:
    ```bash
    NODE_ID: 6593209927e8abbe55ed344a79589ef6a551b1806319bb0bc8b44a429736af82

6. To start a conversation with the node identified by the previous node ID, go to the other terminal window (the other node) and type:
    ```bash
    @6593209927e8abbe55ed344a79589ef6a551b1806319bb0bc8b44a429736af82 Hi there

7. You should see the message on both terminal windows. Something like:

    TERMINAL 1
    ```bash


    ================= NEW =================


    You: Hi there
    6af82: Whats up
    > 
    ```

    TERMINAL 2
    ```bash


    ================= NEW =================


    3f092: Hi there
    You: Whats up
    > 
    ```

8. To end a conversation:
    ```bash
    /bye

9. To see the connected nodes:
    ```bash
    /nodes

10. To exit the application:
    ```bash
    /exit

