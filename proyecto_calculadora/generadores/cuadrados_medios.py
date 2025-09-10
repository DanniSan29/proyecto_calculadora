"""
Generador de Cuadrados Medios (Mid-Square)
"""
from typing import Tuple, List

def _middle_digits(num: int, d: int) -> int:
    s = str(num*num).zfill(2*d)
    start = (len(s)-d)//2
    return int(s[start:start+d])

def cuadrados_medios(semilla: int, n: int, d: int=None) -> Tuple[List[int], List[float]]:
    if semilla <= 0:
        raise ValueError("La semilla debe ser un entero positivo.")
    if d is None:
        d = len(str(semilla))
    if len(str(semilla)) != d:
        raise ValueError("La semilla debe tener exactamente d dígitos.")
    m = 10**d
    xs = [semilla]
    for _ in range(n-1):
        next_x = _middle_digits(xs[-1], d)
        xs.append(next_x)
    us = [x/m for x in xs]
    return xs, us
