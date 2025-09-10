"""
Generador de Productos Medios (Mid-Product)
"""
from typing import Tuple, List

def _middle_digits_of_product(a: int, b: int, d: int) -> int:
    s = str(a*b).zfill(2*d)
    start = (len(s)-d)//2
    return int(s[start:start+d])

def productos_medios(semilla1: int, semilla2: int, n: int, d: int=None) -> Tuple[List[int], List[float]]:
    if semilla1 <= 0 or semilla2 <= 0:
        raise ValueError("Las semillas deben ser enteros positivos.")
    if d is None:
        d = len(str(semilla1))
    if len(str(semilla1)) != d or len(str(semilla2)) != d:
        raise ValueError("Ambas semillas deben tener exactamente d dígitos.")
    m = 10**d
    xs = [semilla1, semilla2]
    while len(xs) < n:
        next_x = _middle_digits_of_product(xs[-2], xs[-1], d)
        xs.append(next_x)
    us = [x/m for x in xs[:n]]
    return xs[:n], us
