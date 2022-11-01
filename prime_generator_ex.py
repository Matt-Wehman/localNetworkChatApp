import math
import random


def generate_primes(l, h):
    assert l >= 1
    assert h > l
    primes = []
    for x in range(l, h + 1):
        prime = True
        for y in range(2, x):
            if x % y == 0:
                prime = False
                break
        if prime:
            primes.append(x)
    return primes


primes = generate_primes(100, 254)

e = 17
p = random.choice(primes)
while math.gcd(p - 1, e) != 1:
    p = random.choice(primes)