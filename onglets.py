"""Affichage Streamlit des deux onglets de résultats."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pulp
import streamlit as st

from graphique import fenetre, optimum_graphique, points_entiers, sommets
from outils import TOL, lettre, nom
from solveur import STATUTS, code_python
from dessin import tracer


def onglet_graphique(c, A, signes, b, sens, entier, positif):
    if len(c) != 2:
        st.info("L'approche graphique n'est possible qu'avec **2 variables**. "
                "Réglez le nombre de variables à 2 dans la barre latérale, "
                "ou consultez l'onglet PuLP.")
        return

    lo, hi = fenetre(A, b, positif)
    pts = sommets(A, signes, b, positif, lo, hi)
    entiers = points_entiers(A, signes, b, positif, lo, hi) if entier else None
    opt, msg, ex_aequo = optimum_graphique(c, pts, sens, entier, entiers)

    g1, g2 = st.columns([3, 2])
    with g1:
        fig = tracer(A, signes, b, c, pts, lo, hi, opt, entiers)
        st.pyplot(fig)
        plt.close(fig)
    with g2:
        st.markdown("**Méthode des sommets**")
        reels = [p for p, art in pts if not art]
        if reels:
            st.dataframe(pd.DataFrame({
                "Sommet": [lettre(k) for k in range(len(reels))],
                "x₁": [round(p[0], 4) for p in reels],
                "x₂": [round(p[1], 4) for p in reels],
                "Z": [round(float(np.dot(c, p)), 4) for p in reels],
            }), hide_index=True, width="stretch")
        if msg:
            st.warning(msg)
        elif opt is not None:
            st.success(f"Optimum graphique : x₁ = {opt[0]:g}, x₂ = {opt[1]:g}, "
                       f"**Z* = {float(np.dot(c, opt)):g}**")
            if len(ex_aequo) > 1:
                noms = ", ".join(lettre(k) for k in ex_aequo)
                st.info(f"Solutions optimales multiples : tout le segment "
                        f"entre les sommets {noms}.")
        if entier and entiers is None:
            st.warning("Zone trop grande pour énumérer les points entiers ; "
                       "voir la solution PuLP.")
        st.caption("La région verte est l'ensemble des solutions réalisables. "
                   "La droite pointillée est la droite d'iso-Z passant par "
                   "l'optimum ; la flèche rouge indique le sens où Z s'améliore.")


def onglet_pulp(prob, xvars, c, A, signes, b, sens, entier, positif):
    statut = pulp.LpStatus[prob.status]
    texte = STATUTS.get(statut, statut)
    if statut != "Optimal":
        st.error(f"Statut : {texte}")
    else:
        st.success(f"Statut : {texte}")
        k1, k2 = st.columns(2)
        k1.metric("Valeur optimale Z*", f"{pulp.value(prob.objective):g}")
        k2.metric("Solveur", "CBC (via PuLP)")
        _tableau_variables(xvars, entier)
        _tableau_contraintes(prob, xvars, A, signes, b, entier)

    with st.expander("Modèle généré par PuLP"):
        st.code(str(prob), language=None)
    with st.expander("Code Python équivalent"):
        st.code(code_python(c, A, signes, b, sens, entier, positif), language="python")


def _tableau_variables(xvars, entier):
    st.markdown("**Variables**")
    st.dataframe(pd.DataFrame({
        "Variable": [nom(i) for i in range(len(xvars))],
        "Valeur": [round(v.varValue, 6) for v in xvars],
        "Coût réduit": [None if entier or v.dj is None else round(v.dj, 6)
                        for v in xvars],
    }), hide_index=True, width="stretch")


def _tableau_contraintes(prob, xvars, A, signes, b, entier):
    st.markdown("**Contraintes**")
    valeurs = [v.varValue for v in xvars]
    lignes = []
    for j, (nom_c, cons) in enumerate(prob.constraints.items()):
        lhs = float(np.dot(A[j], valeurs))
        ecart = b[j] - lhs if signes[j] == "≤" else lhs - b[j]
        lignes.append({
            "Contrainte": nom_c,
            "Valeur du membre gauche": round(lhs, 6),
            "Signe": signes[j],
            "b": b[j],
            "Écart": round(ecart, 6),
            "Saturée": "oui" if abs(ecart) <= TOL * (1 + abs(b[j])) else "non",
            "Prix dual (prix fictif)": None if entier or cons.pi is None
            else round(cons.pi, 6),
        })
    st.dataframe(pd.DataFrame(lignes), hide_index=True, width="stretch")
    if entier:
        st.caption("Prix duals et coûts réduits non définis pour un problème en nombres entiers.")
