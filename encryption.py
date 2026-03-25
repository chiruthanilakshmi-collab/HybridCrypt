from Crypto.PublicKey import ElGamal
from Crypto.Random import get_random_bytes
from Crypto import Random
from Crypto.Util.number import GCD
import numpy as np

def logistic_map(x0, r, n):
    sequence = []
    x = x0
    for _ in range(n):
        x = r * x * (1 - x)
        sequence.append(int((x * 255)) % 256)  # Normalize
    return sequence

def hybrid_encrypt(filepath):
    with open(filepath, "rb") as f:
        data = f.read()

    # Step 1: Chaos encryption
    chaos_key = logistic_map(0.7, 3.99, len(data))
    chaos_encrypted = bytes([b ^ k for b, k in zip(data, chaos_key)])

    # Step 2: ElGamal encryption
    key = ElGamal.generate(2048, Random.new().read)
    plaintext_int = int.from_bytes(chaos_encrypted, byteorder='big')
    while GCD(plaintext_int, key.p) != 1:
        plaintext_int = int.from_bytes(get_random_bytes(len(chaos_encrypted)), byteorder='big')
    
    k = Random.new().read(int(2048 / 8))
    ciphertext = key.encrypt(plaintext_int, int.from_bytes(k, 'big'))

    return str(ciphertext).encode()
