"""Programmation linéaire : approche graphique + résolution avec PuLP.

Lancer en local :  streamlit run app.py
"""
import numpy as np
import pandas as pd
import streamlit as st

from onglets import onglet_graphique, onglet_pulp
from outils import SIGNES, expression, nom
from solveur import resoudre_pulp

st.set_page_config(page_title="Programmation linéaire", page_icon="📈", layout="wide")
st.title("📈 Programmation linéaire")
st.caption("Approche graphique (2 variables) et résolution avec la librairie PuLP")

# ---- Paramètres -----------------------------------------------------------
with st.sidebar:
    st.header("Paramètres")
    sens = st.radio("Objectif", ["Maximiser", "Minimiser"], horizontal=True)
    n = int(st.number_input("Nombre de variables", 2, 10, 2))
    m = int(st.number_input("Nombre de contraintes", 1, 15, 3))
    positif = st.checkbox("Contraintes de non-négativité (xᵢ ≥ 0)", value=True)
    entier = st.checkbox("Variables entières (PLNE)")
    st.divider()
    st.caption("Exemple par défaut (2 var., 3 contraintes) : "
               "max Z = 3x₁ + 5x₂, x₁ ≤ 4, 2x₂ ≤ 12, 3x₁ + 2x₂ ≤ 18.")

# ---- Fonction objectif ----------------------------------------------------
st.subheader("Fonction objectif")
cols = st.columns(n)
c_defaut = [3.0, 5.0]
c = np.array([
    cols[i].number_input(f"Coefficient de {nom(i)}",
                         value=c_defaut[i] if i < 2 else 1.0, key=f"c{i}")
    for i in range(n)
])
st.markdown(f"**{'max' if sens == 'Maximiser' else 'min'} Z = {expression(c)}**")

# ---- Contraintes ----------------------------------------------------------
st.subheader("Contraintes")
if n == 2 and m == 3:
    df0 = pd.DataFrame({"x1": [1.0, 0.0, 3.0], "x2": [0.0, 2.0, 2.0],
                        "Signe": ["≤"] * 3, "b": [4.0, 12.0, 18.0]})
else:
    df0 = pd.DataFrame({**{f"x{i + 1}": [1.0] * m for i in range(n)},
                        "Signe": ["≤"] * m, "b": [10.0] * m})
df0.index = [f"C{j + 1}" for j in range(m)]

df = st.data_editor(
    df0,
    key=f"contraintes_{n}_{m}",
    width="stretch",
    column_config={
        **{f"x{i + 1}": st.column_config.NumberColumn(nom(i), format="%g")
           for i in range(n)},
        "Signe": st.column_config.SelectboxColumn("Signe", options=SIGNES, required=True),
        "b": st.column_config.NumberColumn("Second membre b", format="%g"),
    },
)
A = df[[f"x{i + 1}" for i in range(n)]].fillna(0).astype(float).to_numpy()
signes = df["Signe"].fillna("≤").tolist()
b = df["b"].fillna(0).astype(float).to_numpy()

with st.expander("Modèle mathématique"):
    lignes = [f"{'max' if sens == 'Maximiser' else 'min'} Z = {expression(c)}", "s.c."]
    lignes += [f"  {expression(a)} {s} {bb:g}" for a, s, bb in zip(A, signes, b)]
    variables = ", ".join(nom(i) for i in range(n))
    if positif:
        lignes.append(f"  {variables} ≥ 0")
    if entier:
        lignes.append(f"  {variables} entiers")
    st.code("\n".join(lignes), language=None)

# ---- Résultats ------------------------------------------------------------
prob, xvars = resoudre_pulp(c, A, signes, b, sens, entier, positif)
tab_graph, tab_pulp = st.tabs(["🖼️ Approche graphique", "🧮 Résolution PuLP"])
with tab_graph:
    onglet_graphique(c, A, signes, b, sens, entier, positif)
with tab_pulp:
    onglet_pulp(prob, xvars, c, A, signes, b, sens, entier, positif)
