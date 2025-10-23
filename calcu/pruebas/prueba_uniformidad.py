"""
Prueba de Uniformidad (Chi-cuadrado de bondad de ajuste)
"""
from typing import Dict, Any, Tuple
import numpy as np
from scipy.stats import chi2

def tabla_frecuencias(u: list, k: int):
    u = np.asarray(u, dtype=float)
    counts, edges = np.histogram(u, bins=k, range=(0.0,1.0))
    return counts.tolist(), edges.tolist()

def prueba_uniformidad(u: list, k: int=None, alpha: float=0.05) -> Dict[str, Any]:
    n = len(u)
    if n < 2:
        raise ValueError("Se requieren al menos 2 valores.")
    if k is None:
        k = max(5, int(n**0.5))
    counts, edges = tabla_frecuencias(u, k)
    ei = n / k
    x2 = float(((np.array(counts) - ei)**2 / ei).sum())
    gl = k - 1
    chi2_crit = chi2.ppf(1 - alpha, gl)
    p_value = 1 - chi2.cdf(x2, gl)
    pasa = x2 <= chi2_crit
    return {"n": n, "k": k, "frecuencias": counts, "intervalos": edges, "esperado_por_intervalo": ei, "x2": x2, "gl": gl, "chi2_critico": chi2_crit, "alpha": alpha, "p_value": p_value, "pasa": bool(pasa)}
