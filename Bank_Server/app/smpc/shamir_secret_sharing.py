import random
from random import SystemRandom
from functools import reduce
from operator import mul

"""
This file contains the implementation of Shamir's Secret Sharing algorithm.
Based on research from: https://www.mdpi.com/1424-8220/22/1/331
"""

# Function to compute modular inverse
def mod_inverse(a, p):
    """
    Compute the modular inverse of a under modulus p using Fermat's Little Theorem.
    This function returns a^(-1) mod p.
    """
    return pow(a, p - 2, p)

# Function to perform Lagrange interpolation to reconstruct the secret
def lagrange_interpolate(x, x_s, y_s, p):
    """
    Perform Lagrange interpolation at a given x to reconstruct the secret.

    Parameters:
    x (int): The x-value to evaluate the polynomial at (typically 0 for reconstruction).
    x_s (list of int): List of x-values from shares.
    y_s (list of int): List of y-values from shares.
    p (int): Prime modulus for the field.

    Returns:
    int: The interpolated value at x.
    """
    k = len(x_s)
    assert k == len(y_s), "Mismatched share lengths"
    total = 0
    for i in range(k):
        xi, yi = x_s[i], y_s[i]
        # Compute the Lagrange basis polynomial for the i-th share
        prod = yi
        for j in range(k):
            if i != j:
                xj = x_s[j]
                # Compute (x - xj) / (xi - xj) under modulus p
                prod = prod * (x - xj) * mod_inverse(xi - xj, p) % p
        total = (total + prod) % p
    return total

# Function to split a secret into shares
def split_secret(secret, n, k, p=2 ** 127 - 1):
    """
    Split a secret into n shares using a polynomial of degree (k-1).

    Parameters:
    secret (int): The secret to be shared.
    n (int): Number of shares to create.
    k (int): Minimum number of shares required to reconstruct the secret.
    p (int): Prime number for modulus (default is 2**127 - 1).

    Returns:
    list of tuples: Each tuple contains (x, y) where y is the polynomial evaluated at x.
    """
    assert 1 <= k <= n, "k must be <= n"

    # Generate random coefficients for the polynomial
    coefficients = [secret] + [SystemRandom().randint(0, p - 1) for _ in range(k - 1)]
    print(f"Coefficients: {coefficients}")

    # Compute shares (x, y) where y = f(x) = sum(c_i * x^i)
    shares = []
    for i in range(1, n + 1):
        x = i
        y = sum(coefficients[j] * (x ** j) % p for j in range(k)) % p
        shares.append((x, y))

    return shares

# Function to reconstruct the secret from shares
def reconstruct_secret(shares, p=2 ** 127 - 1):
    """
    Reconstruct the secret from shares using Lagrange interpolation.

    Parameters:
    shares (list of tuples): List of (x, y) tuples representing the shares.
    p (int): Prime number for modulus (default is 2**127 - 1).

    Returns:
    int: The reconstructed secret.
    """
    x_s, y_s = zip(*shares)
    print(f"Shares: {shares}")
    print(f"x_s: {x_s}")
    print(f"y_s: {y_s}")
    return lagrange_interpolate(0, x_s, y_s, p)
