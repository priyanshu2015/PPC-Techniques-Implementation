from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Util import number
from Crypto.Cipher import PKCS1_OAEP
import numpy as np

# doesnt work


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
        This function generates a random x, encrypts it with the peer's public key,
        and returns the encrypted result minus the millionaire's amount.
        """
        peer_pubKey = RSA.importKey(peer_key_pem)
        cipher_rsa = PKCS1_OAEP.new(peer_pubKey)
        self.x = number.getRandomNBitInteger(self.num_bits)
        x_bytes = self.x.to_bytes((self.x.bit_length() + 7) // 8, byteorder='big')

        # Encrypt x_bytes with the peer's public key
        k = cipher_rsa.encrypt(x_bytes)

        # Return the integer form of ciphertext minus the millionaire's value
        return int.from_bytes(k, byteorder='big') - self.million

    def get_batch_z(self, ciphertext):
        """
        This function creates a batch of z values based on the given ciphertext
        and returns the prime p and final batch of z values.
        """
        y_u = []
        for i in range(self.max_million):
            adjusted_ciphertext = ciphertext + i
            adjusted_bytes = adjusted_ciphertext.to_bytes((adjusted_ciphertext.bit_length() + 7) // 8, byteorder='big')

            # Decrypt using the private key
            cipher_rsa = PKCS1_OAEP.new(self.key)
            try:
                decrypted_bytes = cipher_rsa.decrypt(adjusted_bytes)
            except ValueError:
                # Incorrect decryption typically results in ValueError when padding is wrong
                continue

            decrypted_value = int.from_bytes(decrypted_bytes, byteorder='big')
            y_u.append(decrypted_value)

        # Generate prime p
        while True:
            p = number.getPrime(self.num_bits // 2)
            z_u = [y % p for y in y_u]

            row = np.array(z_u).reshape((1, len(z_u)))
            col = np.transpose(row)
            diff = np.abs(row - col)
            diff = diff + np.eye(len(z_u)) * 3  # Prevent 0 in the diagonal
            if np.all(diff >= 2):
                break

        # Adjust the batch z values
        final_z_u = []
        for i, z in enumerate(z_u):
            if i >= self.million:
                z = (z + 1) % p
            final_z_u.append(z)

        return p, final_z_u

    def peer_is_richer(self, p, batch_z):
        """
        Determines if the peer is richer based on the provided p and batch_z.
        """
        box = batch_z[self.million]
        # peer is richer
        return self.x % p == box


if __name__ == '__main__':
    Alice = Millionaire(8)
    Bob = Millionaire(5)

    # Get Alice's public key
    Alice_pubKey = Alice.get_pub_key_pem()

    # Bob generates ciphertext based on Alice's public key
    Bob_ciphertext = Bob.get_ciphertext(Alice_pubKey)

    # Alice computes the batch z values using Bob's ciphertext
    Alice_p, Alice_batch_z = Alice.get_batch_z(Bob_ciphertext)

    # Bob checks if Alice is richer
    result = Bob.peer_is_richer(Alice_p, Alice_batch_z)

    print("Is Alice richer?", result)
