
import os

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


class Rsa:
    def __init__(self):
        self.__private_key = None
        self.__serialized_private_key = None
        self.__public_key = None
        self.__serialized_public_key = None
        self.BASE_DIR = os.path.dirname(__file__)
    

    def __set_private_key(self, private_key: rsa.RSAPrivateKey):
        """
        _summary_
        """

        if not isinstance(private_key, rsa.RSAPrivateKey):
            raise TypeError('The private key must be of type <rsa.RSAPrivateKey>')
        self.__private_key = private_key


    def __set_public_key(self, public_key: rsa.RSAPublicKey):
        """
        _summary_
        """

        if not isinstance(public_key, rsa.RSAPublicKey):
            raise TypeError('The private key must be of type <rsa.RSAPublicKey>')
        self.__public_key = public_key


    def get_private_key(self):
        """
        _summary_
        """
        
        return self.__private_key
    

    def get_public_key(self):
        """
        _summary_
        """
        
        return self.__public_key
    

    def get_serialized_private_key(self):
        """
        _summary_
        """
        
        return self.__serialized_private_key


    def get_serialized_public_key(self):
        """
        _summary_
        """

        return self.__serialized_public_key

    
    def generate_keys(self):
        """
        Generates the RSA private and public keys
        if they don't exist yet. The keys are replaced
        every time the app is started.
        """

        self.__generate_private_key()
        self.__generate_public_key()
        self.__serialize_private_key()
        self.__serialize_public_key()
    

    def __generate_private_key(self):
        """
        Generates a RSA private key.
        """

        private_key = rsa.generate_private_key(
            public_exponent=65537,  # Valor padrão para RSA
            key_size=2048,           # Tamanho da chave (2048 ou 4096 bits)
        )
        self.__set_private_key(private_key)
    

    def __generate_public_key(self):
        """
        Generates a RSA public key.
        """
    
        public_key = self.get_private_key().public_key()
        self.__set_public_key(public_key)


    def __serialize_private_key(self):
        """
        Serializes the private key for storage and/or transmission. 
        """

        private_pem = self.get_private_key().private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()  # Ou use uma senha para criptografar
        )
        self.__serialized_private_key = private_pem
        with open(os.path.join(self.BASE_DIR, 'secrets/private_key.pem'), 'wb') as f:
            f.write(private_pem)
    

    def __serialize_public_key(self):
        """
        Serializes the public key for storage and/or transmission. 
        """

        public_pem = self.get_public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.__serialized_public_key = public_pem
        with open(os.path.join(self.BASE_DIR, 'secrets/public_key.pem'), 'wb') as f:
            f.write(public_pem)
