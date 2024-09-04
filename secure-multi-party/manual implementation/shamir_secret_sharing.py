import random
from random import SystemRandom
from functools import reduce
from operator import mul


# Function to perform modular inverse
def mod_inverse(a, p):
    return pow(a, p - 2, p)


# Function to perform Lagrange interpolation at x=0 to reconstruct the secret
def lagrange_interpolate(x, x_s, y_s, p):
    k = len(x_s)
    assert k == len(y_s), "Mismatched share lengths"
    total = 0
    for i in range(k):
        xi, yi = x_s[i], y_s[i]
        # Calculate the Lagrange basis polynomial for this point
        prod = yi
        for j in range(k):
            if i != j:
                xj = x_s[j]
                # Multiply by the fraction (x - xj) / (xi - xj) under the prime modulus p
                prod = prod * (x - xj) * mod_inverse(xi - xj, p) % p
        total = (total + prod) % p
    return total


# Function to split a secret into shares
def split_secret(secret, n, k, p=2 ** 127 - 1):
    # secret: The secret to share
    # n: Number of shares to create
    # k: Minimum number of shares to reconstruct the secret
    # p: Prime number for modulus
    assert 1 <= k <= n, "k must be <= n"

    # Randomly generate coefficients for the polynomial
    coefficients = [secret] + [SystemRandom().randint(0, p - 1) for _ in range(k - 1)]

    # Generate the shares (x, y) pairs where y = f(x) = sum(c_i * x^i)
    shares = []
    for i in range(1, n + 1):
        x = i
        y = sum(coefficients[j] * (x ** j) % p for j in range(k)) % p
        shares.append((x, y))

    return shares


# Function to reconstruct the secret from shares
def reconstruct_secret(shares, p=2 ** 127 - 1):
    x_s, y_s = zip(*shares)
    return lagrange_interpolate(0, x_s, y_s, p)


# Example usage
if __name__ == "__main__":
    # The secret we want to share (e.g., 12345)
    secret = 111233216424745047463126641208267665733

    # Number of shares to create
    num_shares = 6

    # Minimum number of shares needed to reconstruct the secret
    threshold = 4

    # Split the secret into shares
    shares = split_secret(secret, num_shares, threshold)
    print(f"Shares: {shares}")

    # Select any 3 shares and try to reconstruct the secret
    subset_of_shares = random.sample(shares, k=threshold)
    #subset_of_shares = shares[:threshold]
    recovered_secret = reconstruct_secret(subset_of_shares)
    assert recovered_secret == secret, "Secret recovery failed"
    print(f"Reconstructed secret: {recovered_secret}")
