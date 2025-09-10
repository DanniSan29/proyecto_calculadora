"""
Generador Multiplicador Constante

"""
from typing import Tuple, List

def _middle_digits(num: int, d: int) -> int:
    s = str(num).zfill(2*d)
    start = (len(s)-d)//2
    return int(s[start:start+d])

def multiplicador_constante(semilla: int, c: int, n: int, d: int=None) -> Tuple[List[int], List[float]]:
    if semilla <= 0 or c <= 0:
        raise ValueError("Semilla y multiplicador deben ser enteros positivos.")
    if d is None:
        d = len(str(semilla))
    if len(str(semilla)) != d:
        raise ValueError("La semilla debe tener exactamente d dígitos.")
    m = 10**d
    xs = [semilla]
    for _ in range(n-1):
        prod = c * xs[-1]
        next_x = _middle_digits(prod, d)
        xs.append(next_x)
    us = [x/m for x in xs]
    return xs, us
