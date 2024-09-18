import random
from random import SystemRandom
from functools import reduce
from operator import mul

"""
This file contains the implementation of Shamir's Secret Sharing algorithm.
"""

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
# p is defined as 2**127 − 1, which is a Mersenne prime
# The prime modulus ensures that all arithmetic operations (such as addition, multiplication, and division) happen within the bounds of a finite field, preventing overflow and ensuring that results are securely wrapped within this field.
def split_secret(secret, n, k, p=2 ** 127 - 1):
    # secret: The secret to share
    # n: Number of shares to create
    # k: Minimum number of shares to reconstruct the secret
    # p: Prime number for modulus
    assert 1 <= k <= n, "k must be <= n"

    # Randomly generate coefficients for the polynomial
    coefficients = [secret] + [SystemRandom().randint(0, p - 1) for _ in range(k - 1)]
    print(f"Coefficients: {coefficients}")

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
    print(f"shares: {shares}")
    print(f"x_s: {x_s}")
    print(f"y_s: {y_s}")
    return lagrange_interpolate(0, x_s, y_s, p)

