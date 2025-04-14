from logging import Logger
from typing import Any, Optional, Self
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


logger = Logger(__name__)
KEY_DIR = "/keys"
os.makedirs(KEY_DIR, exist_ok=True)


class CertFile:
    def __init__(self, username: Optional[str] = None):
        self.username = username
        self.public_key: Any
        self.private_key: Any

    def set_username(self, username: str) -> Self:
        self.username = username

        return self

    def get_username(self):
        return self.username

    def read(self, key_name: str) -> Any:
        path = self.__make_path(key_name)
        if not os.path.exists(path):
            self.write()

        with open(path, "rb") as f:
            return f.read()

    def write(self):
        private_pem, public_pem = self.__make_keys().__make_pems()

        self.__save_to_disk(self.__make_path("private"), private_pem)
        self.__save_to_disk(self.__make_path("public"), public_pem)

    # TODO remove certFile while logout
    def remove(self):
        private_path = self.__make_path("private")
        if os.path.exists(private_path):
            os.remove(private_path)

        public_path = self.__make_path("public")
        if os.path.exists(public_path):
            os.remove(public_path)

    def __make_pems(self):
        # Serialize private key sang PEM
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Serialize public key sang PEM
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return private_pem, public_pem

    def __make_keys(self) -> Self:
        self.private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )

        self.public_key = self.private_key.public_key()

        return self

    def __make_path(self, key_name: str):
        return os.path.join(KEY_DIR, f"{self.username}_{key_name}.pem")

    def __save_to_disk(self, path: str, pem: bytes):
        if os.path.exists(path):
            return

        with open(path, "wb") as f:
            f.write(pem)
