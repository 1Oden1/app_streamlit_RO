"""Constantes et fonctions utilitaires communes."""
import numpy as np

EPS = 1e-9
TOL = 1e-6
SIGNES = ["≤", "≥", "="]
INDICES = "₁₂₃₄₅₆₇₈₉"


def nom(i):
    """Nom affiché de la variable i (0-indexé) : x₁, x₂, …"""
    return "x" + (INDICES[i] if i < 9 else str(i + 1))


def lettre(k):
    """Nom d'un sommet : A, B, C, …"""
    return chr(65 + k % 26)


def expression(coefs):
    """Formate une expression linéaire : 3x₁ + 5x₂ − x₃."""
    termes = []
    for i, v in enumerate(coefs):
        if abs(v) < EPS:
            continue
        mag = abs(v)
        coef = "" if abs(mag - 1) < EPS else f"{mag:g}"
        termes.append(("−" if v < 0 else "+", f"{coef}{nom(i)}"))
    if not termes:
        return "0"
    s = ("−" if termes[0][0] == "−" else "") + termes[0][1]
    for sg, t in termes[1:]:
        s += f" {sg} {t}"
    return s


def respecte(a, signe, b, p):
    """Vrai si le point p vérifie la contrainte a·p (signe) b."""
    v = float(np.dot(a, p))
    tol = TOL * (1 + abs(b))
    if signe == "≤":
        return v <= b + tol
    if signe == "≥":
        return v >= b - tol
    return abs(v - b) <= tol
