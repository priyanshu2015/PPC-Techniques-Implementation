from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util import number
import numpy as np

class Millionaire:
    def __init__(self, num_million, max_million=10, num_bits=1024):
        self.key = RSA.generate(2048)
        self.million = num_million
        self.max_million = max_million
        self.num_bits = num_bits
        self.x = None

    def get_pub_key_pem(self):
        return self.key.publickey().exportKey('PEM')

    def get_ciphertext(self, peer_key_pem):
        """
        Encrypts a random value with the peer's public key.
        """
        peer_pubKey = RSA.importKey(peer_key_pem)
        cipher_rsa = PKCS1_OAEP.new(peer_pubKey)
        self.x = number.getRandomNBitInteger(self.num_bits)
        x_bytes = self.x.to_bytes((self.x.bit_length() + 7) // 8, byteorder='big')

        return cipher_rsa.encrypt(x_bytes)

    def get_batch_z(self, ciphertext):
        """
        Creates a batch of z values based on the given ciphertext.
        """
        y_u = []
        for i in range(self.max_million):
            adjusted_bytes = ciphertext
            cipher_rsa = PKCS1_OAEP.new(self.key)
            try:
                decrypted_bytes = cipher_rsa.decrypt(adjusted_bytes)
                decrypted_value = int.from_bytes(decrypted_bytes, byteorder='big')
                y_u.append(decrypted_value)
            except ValueError:
                continue

        # Generate a prime p with a maximum iteration limit
        max_iterations = 100
        p = None
        for _ in range(max_iterations):
            p = number.getPrime(self.num_bits // 2)
            z_u = [y % p for y in y_u]

            row = np.array(z_u).reshape((1, len(z_u)))
            col = np.transpose(row)
            diff = np.abs(row - col)
            diff = diff + np.eye(len(z_u)) * 3
            if np.all(diff >= 2):
                break
        if p is None:
            # If unable to find a suitable prime, use a default prime
            p = number.getPrime(self.num_bits // 2)
            z_u = [y % p for y in y_u]

        # Adjust the batch z values
        final_z_u = [(z + 1) % p if i >= self.million else z for i, z in enumerate(z_u)]

        return p, final_z_u

    def peer_is_richer(self, p, batch_z):
        """
        Determines if the peer is richer based on the provided p and batch_z.
        """
        if self.million >= len(batch_z):
            return False
        box = batch_z[self.million]
        return self.x % p == box

if __name__ == '__main__':
    Alice = Millionaire(8)
    Bob = Millionaire(10)

    # Get Alice's public key
    Alice_pubKey = Alice.get_pub_key_pem()

    # Bob generates ciphertext based on Alice's public key
    Bob_ciphertext = Bob.get_ciphertext(Alice_pubKey)

    # Alice computes the batch z values using Bob's ciphertext
    Alice_p, Alice_batch_z = Alice.get_batch_z(Bob_ciphertext)

    # Bob checks if Alice is richer
    result = Bob.peer_is_richer(Alice_p, Alice_batch_z)

    print("Is Alice richer?", result)
