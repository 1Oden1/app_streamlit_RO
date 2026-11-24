# Programmation linéaire — Approche graphique & PuLP

Application Streamlit : approche graphique (2 variables) et résolution d'un PL avec PuLP.

## Structure
| Fichier | Rôle |
|---|---|
| `app.py` | Point d'entrée : saisie du problème (objectif, contraintes, options) |
| `onglets.py` | Affichage des onglets « Approche graphique » et « Résolution PuLP » |
| `solveur.py` | Construction et résolution du modèle avec PuLP |
| `graphique.py` | Calculs graphiques : région réalisable, sommets, optimum |
| `dessin.py` | Tracé matplotlib (droites, région, iso-Z, optimum) |
| `outils.py` | Constantes et fonctions utilitaires |

## Lancer en local
```bash
pip install -r requirements.txt
streamlit run app.py
```
