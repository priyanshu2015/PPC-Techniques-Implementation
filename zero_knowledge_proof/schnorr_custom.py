import random
from Crypto.Util.number import getPrime

# Parameters for Schnorr protocol
p = getPrime(512)  # Large prime number
g = 2  # Generator

# Step 1: Registration
class Server:
    def __init__(self):
        self.public_keys = {}  # Dictionary to store public keys of users

    def register_user(self, username, public_key):
        """Registers a user by storing their public key."""
        self.public_keys[username] = public_key
        print(f"User {username} registered with public key: {public_key}")

    def get_public_key(self, username):
        """Returns the public key of the registered user."""
        return self.public_keys.get(username, None)

    def generate_challenge(self):
        """Generates a random challenge."""
        return random.randint(1, p-1)


class User:
    def __init__(self, username):
        self.username = username
        self.private_key = None
        self.public_key = None

    def generate_keys(self):
        """Generates a private-public key pair for the user."""
        self.private_key = random.randint(1, p-1)  # Private key
        self.public_key = pow(g, self.private_key, p)  # Public key y = g^x mod p
        return self.public_key

    def commit(self):
        """User generates a random value and computes the commitment t."""
        self.r = random.randint(1, p-1)  # Random value r
        self.t = pow(g, self.r, p)  # Commitment t = g^r mod p
        return self.t

    def compute_response(self, c):
        """User computes the response s = r + c * x mod (p-1)."""
        self.s = (self.r + c * self.private_key) % (p-1)
        return self.s


# Step 2: Login Protocol
def login(server, user):
    """User tries to log in to the server using Schnorr protocol."""
    public_key = server.get_public_key(user.username)
    if public_key is None:
        print(f"User {user.username} not registered.")
        return False

    # Prover (User) Commitment Phase
    t = user.commit()  # User generates a commitment t = g^r mod p
    print(f"User {user.username} commitment (t): {t}")

    # Verifier (Server) generates challenge
    c = server.generate_challenge()
    print(f"Server generated challenge (c): {c}")

    # Prover (User) computes response
    s = user.compute_response(c)
    print(f"User {user.username} response (s): {s}")

    # Verifier (Server) checks if g^s == t * public_key^c mod p
    left_hand_side = pow(g, s, p)
    right_hand_side = (t * pow(public_key, c, p)) % p
    print(f"g^s mod p: {left_hand_side}")
    print(f"t * public_key^c mod p: {right_hand_side}")

    if left_hand_side == right_hand_side:
        print("Login successful.")
        return True
    else:
        print("Login failed.")
        return False


# Simulation of Registration and Login Process
# -------------------------------------------------

# Server setup
server = Server()

# User registration
user1 = User("user1")
public_key1 = user1.generate_keys()
server.register_user(user1.username, public_key1)

# Login attempt
login_success = login(server, user1)
