"""Calculs de l'approche graphique (2 variables) : région, sommets, optimum."""
import itertools

import numpy as np

from outils import EPS, TOL, respecte


def fenetre(A, b, positif):
    """Taille de la zone de tracé, assez grande pour contenir tous les sommets."""
    vals = []
    for a, bb in zip(A, b):
        for k in range(2):
            if abs(a[k]) > EPS:
                vals.append(abs(bb / a[k]))
    for (a1, b1), (a2, b2) in itertools.combinations(zip(A, b), 2):
        M = np.array([a1, a2])
        if abs(np.linalg.det(M)) > EPS:
            vals.extend(np.abs(np.linalg.solve(M, [b1, b2])))
    L = max(vals) if vals else 10.0
    L = max(L, 1.0) * 1.25
    return (0.0 if positif else -L), L


def sommets(A, signes, b, positif, lo, hi):
    """Sommets de la région réalisable (découpée par la fenêtre de tracé).

    Retourne une liste (point, artificiel) ; « artificiel » = le sommet est
    créé par le bord de la fenêtre, signe que la région est non bornée.
    """
    reelles = [(np.asarray(a, float), s, float(bb)) for a, s, bb in zip(A, signes, b)]
    if positif:
        reelles += [(np.array([1.0, 0.0]), "≥", 0.0), (np.array([0.0, 1.0]), "≥", 0.0)]
    cadre = [(np.array([1.0, 0.0]), "≤", hi), (np.array([0.0, 1.0]), "≤", hi)]
    if not positif:
        cadre += [(np.array([1.0, 0.0]), "≥", lo), (np.array([0.0, 1.0]), "≥", lo)]
    toutes = reelles + cadre

    pts = []
    for (a1, _, b1), (a2, _, b2) in itertools.combinations(toutes, 2):
        M = np.array([a1, a2])
        if abs(np.linalg.det(M)) < EPS:
            continue
        p = np.linalg.solve(M, [b1, b2])
        if all(respecte(a, s, bb, p) for a, s, bb in toutes):
            art = any(abs(np.dot(a, p) - bb) <= TOL * (1 + abs(bb)) for a, _, bb in cadre)
            if not any(np.allclose(p, q, atol=1e-6) for q, _ in pts):
                pts.append((p, art))
    if pts:
        centre = np.mean([p for p, _ in pts], axis=0)
        pts.sort(key=lambda t: np.arctan2(t[0][1] - centre[1], t[0][0] - centre[0]))
    return pts


def points_entiers(A, signes, b, positif, lo, hi):
    """Points à coordonnées entières réalisables (None si la zone est trop grande)."""
    a, z = int(np.floor(lo)), int(np.ceil(hi))
    if (z - a) > 60:
        return None
    return [
        np.array([i, j], float)
        for i in range(a, z + 1)
        for j in range(a, z + 1)
        if all(respecte(r, s, bb, (i, j)) for r, s, bb in zip(A, signes, b))
        and (not positif or (i >= 0 and j >= 0))
    ]


def optimum_graphique(c, pts, sens, entier, entiers):
    """Méthode des sommets (ou des points entiers en PLNE).

    Retourne (optimum, message d'erreur, indices des sommets ex aequo).
    """
    signe = 1 if sens == "Maximiser" else -1
    if entier:
        if not entiers:
            return None, "Aucun point entier réalisable dans la zone tracée.", []
        best = max(entiers, key=lambda p: signe * np.dot(c, p))
        return best, None, []
    if not pts:
        return None, "Région réalisable vide : le problème est irréalisable.", []
    reels = [p for p, art in pts if not art]
    vals_reels = [signe * np.dot(c, p) for p in reels]
    vals_tous = [signe * np.dot(c, p) for p, _ in pts]
    if not reels or max(vals_tous) > max(vals_reels) + TOL * (1 + abs(max(vals_reels))):
        return None, ("La région est non bornée dans la direction d'amélioration "
                      "de Z : le problème est non borné."), []
    zbest = max(vals_reels)
    idx = [k for k, v in enumerate(vals_reels) if abs(v - zbest) <= TOL * (1 + abs(zbest))]
    return reels[idx[0]], None, idx
