"""Résolution du PL avec la librairie PuLP."""
import pulp

STATUTS = {
    "Optimal": "Solution optimale trouvée",
    "Infeasible": "Problème irréalisable (aucune solution)",
    "Unbounded": "Problème non borné",
    "Not Solved": "Non résolu",
    "Undefined": "Indéterminé (souvent : irréalisable ou non borné)",
}
OPERATEURS = {"≤": "<=", "≥": ">=", "=": "=="}


def resoudre_pulp(c, A, signes, b, sens, entier, positif):
    """Construit et résout le modèle. Retourne (problème, variables)."""
    n = len(c)
    prob = pulp.LpProblem(
        "PL", pulp.LpMaximize if sens == "Maximiser" else pulp.LpMinimize
    )
    cat = pulp.LpInteger if entier else pulp.LpContinuous
    x = [
        pulp.LpVariable(f"x{i + 1}", lowBound=0 if positif else None, cat=cat)
        for i in range(n)
    ]
    prob += pulp.lpSum(c[i] * x[i] for i in range(n)), "Z"
    for j, (a, s, bb) in enumerate(zip(A, signes, b)):
        lhs = pulp.lpSum(a[i] * x[i] for i in range(n))
        if s == "≤":
            prob += lhs <= bb, f"C{j + 1}"
        elif s == "≥":
            prob += lhs >= bb, f"C{j + 1}"
        else:
            prob += lhs == bb, f"C{j + 1}"
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    return prob, x


def code_python(c, A, signes, b, sens, entier, positif):
    """Génère le script PuLP équivalent au problème saisi."""
    n, m = len(c), len(b)
    objectif = "LpMaximize" if sens == "Maximiser" else "LpMinimize"
    lb = "0" if positif else "None"
    cat = "pulp.LpInteger" if entier else "pulp.LpContinuous"
    code = ["import pulp", "", f"prob = pulp.LpProblem('PL', pulp.{objectif})"]
    code += [f"x{i + 1} = pulp.LpVariable('x{i + 1}', lowBound={lb}, cat={cat})"
             for i in range(n)]
    code.append(f"prob += {' + '.join(f'{c[i]:g}*x{i + 1}' for i in range(n))}, 'Z'")
    for j in range(m):
        lhs = " + ".join(f"{A[j][i]:g}*x{i + 1}" for i in range(n))
        code.append(f"prob += {lhs} {OPERATEURS[signes[j]]} {b[j]:g}, 'C{j + 1}'")
    code += [
        "",
        "prob.solve(pulp.PULP_CBC_CMD(msg=False))",
        "print(pulp.LpStatus[prob.status], pulp.value(prob.objective))",
        "for v in prob.variables():",
        "    print(v.name, '=', v.varValue)",
    ]
    return "\n".join(code)
