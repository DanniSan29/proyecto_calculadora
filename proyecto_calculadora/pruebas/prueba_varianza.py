"""
Prueba de Varianza (Chi-cuadrado) para U(0,1)
X2 = (n-1)*S2 / (1/12)
"""
from typing import Dict, Any
import numpy as np
from scipy.stats import chi2

def prueba_varianza(u: list, alpha: float=0.05) -> Dict[str, Any]:
    u = np.asarray(u, dtype=float)
    n = len(u)
    if n < 2:
        raise ValueError("Se requieren al menos 2 valores.")
    s2 = float(np.var(u, ddof=1))
    sigma2 = 1.0/12.0
    gl = n - 1
    x2 = gl * s2 / sigma2
    chi2_inf = chi2.ppf(alpha/2.0, gl)
    chi2_sup = chi2.ppf(1 - alpha/2.0, gl)
    pasa = (chi2_inf <= x2 <= chi2_sup)
    p_left = chi2.cdf(x2, gl)
    p_value = 2*min(p_left, 1-p_left)
    return {"n": n, "var_muestral": s2, "x2": x2, "gl": gl, "chi2_inf": chi2_inf, "chi2_sup": chi2_sup, "alpha": alpha, "p_value": p_value, "pasa": bool(pasa)}
