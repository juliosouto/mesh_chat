
from functools import wraps
import socket
import struct
import threading

import hashlib


def run_on_thread(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        threading.Thread(target=func, args=(self, *args,), kwargs=kwargs, daemon=True).start()
    return wrapper


# Função para converter IP para inteiro
def ip_to_int(ip):
    return struct.unpack("!I", socket.inet_aton(ip))[0]


# Função para converter inteiro para IP
def int_to_ip(n):
    return socket.inet_ntoa(struct.pack("!I", n))


def str_to_hash(node_id: str) -> str:
    """
    Generates a idempotent SHA-256 hash from the node_id.

    :param node_id: The Node ID to be hashed.
    :type node_id: str

    :return: The hash of the Node ID.
    :rtype: str
    """

    if not type(node_id) is str:
        raise TypeError("The argument <node_id> must be str")
    return hashlib.sha256(node_id.encode()).hexdigest()

