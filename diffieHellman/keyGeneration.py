"""
Performs the Diffie-Hellman key exchange algorithm.

Steps:
1. Agree on a large prime number `p` and a primitive root modulo `p` (generator) `g`.
2. Each party generates a private key: a random integer less than `p`.
3. Each party computes their public key as `A = g^a mod p` or `B = g^b mod p`.
4. Exchange public keys between the parties.
5. Each party computes the shared secret using the other party's public key and their own private key:
    - Shared secret = (other_public_key)^(own_private_key) mod p
6. The resulting shared secret can be used as a symmetric key for further communication.

Comments:
- Ensure that the prime `p` and generator `g` are agreed upon securely.
- Private keys must remain confidential.
- Public keys can be exchanged over an insecure channel.
- The security of the exchange relies on the difficulty of the discrete logarithm problem.
"""

import random
from sympy import isprime, primerange
from sympy.ntheory import primitive_root
from math import gcd
import os
import base64
import hashlib

def generate_large_prime(bits=512):
    """Generate a large prime number with the specified bit length."""
    while True:
        num = random.getrandbits(bits)
        if isprime(num):
            return num

def generate_private_key(p):
    """Generate a private key that is a random integer less than p."""
    while True:
        private_key = random.randint(2, p - 2)
        if gcd(private_key, p - 1) == 1:  # Ensure private key is coprime to p-1
            return private_key