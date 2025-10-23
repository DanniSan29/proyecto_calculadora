"""
Prueba de Medias (Z) para U(0,1)
Z = (mean - 0.5) * sqrt(12n)
"""
from typing import Dict, Any
import numpy as np
from math import sqrt
from scipy.stats import norm

def prueba_medias(u: list, alpha: float=0.05) -> Dict[str, Any]:
    u = np.asarray(u, dtype=float)
    n = len(u)
    if n < 2:
        raise ValueError("Se requieren al menos 2 valores.")
    mean = float(np.mean(u))
    z = (mean - 0.5) * (12*n)**0.5
    zcrit = norm.ppf(1 - alpha/2.0)
    p_value = 2*(1 - norm.cdf(abs(z)))
    pasa = abs(z) <= zcrit
    return {"n": n, "media_muestral": mean, "z": z, "z_critico": zcrit, "alpha": alpha, "p_value": p_value, "pasa": bool(pasa)}
