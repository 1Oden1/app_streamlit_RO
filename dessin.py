"""Dessin matplotlib de l'approche graphique."""
import matplotlib.pyplot as plt
import numpy as np

from outils import EPS, expression, lettre


def _droite(ax, a, bb, xs, **style):
    """Trace la droite a₁x₁ + a₂x₂ = b (verticale si a₂ = 0)."""
    if abs(a[1]) > EPS:
        ax.plot(xs, (bb - a[0] * xs) / a[1], **style)
    elif abs(a[0]) > EPS:
        ax.axvline(bb / a[0], **style)


def tracer(A, signes, b, c, pts, lo, hi, optimum, entiers):
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    xs = np.linspace(lo, hi, 400)
    couleurs = plt.cm.tab10.colors

    # Droites des contraintes
    for j, (a, s, bb) in enumerate(zip(A, signes, b)):
        _droite(ax, a, bb, xs, color=couleurs[j % 10], lw=1.8,
                label=f"C{j + 1} : {expression(a)} {s} {bb:g}")

    # Région réalisable et sommets
    if pts:
        P = np.array([p for p, _ in pts])
        if len(P) >= 3:
            ax.fill(P[:, 0], P[:, 1], color="tab:green", alpha=0.22,
                    label="Région réalisable")
        else:
            ax.plot(P[:, 0], P[:, 1], color="tab:green", lw=5, alpha=0.5,
                    label="Région réalisable")
        reels = [p for p, art in pts if not art]
        for k, p in enumerate(reels):
            ax.scatter(*p, color="black", zorder=5, s=25)
            ax.annotate(lettre(k), p, textcoords="offset points",
                        xytext=(6, 6), fontsize=10, weight="bold")

    # Points entiers (PLNE)
    if entiers:
        E = np.array(entiers)
        ax.scatter(E[:, 0], E[:, 1], s=10, color="gray", zorder=4,
                   label="Points entiers réalisables")

    # Droite d'iso-Z, optimum et gradient
    if optimum is not None and np.linalg.norm(c) > EPS:
        z = float(np.dot(c, optimum))
        _droite(ax, c, z, xs, color="k", ls="--", lw=1.4,
                label=f"Droite d'iso-Z : Z = {z:g}")
        ax.scatter(*optimum, marker="*", s=320, color="red", zorder=6,
                   label=f"Optimum ({optimum[0]:g} ; {optimum[1]:g})")
        d = np.asarray(c, float) / np.linalg.norm(c) * (hi - lo) * 0.12
        ax.annotate("", xy=optimum + d, xytext=optimum,
                    arrowprops=dict(arrowstyle="->", color="red", lw=1.6))

    ax.axhline(0, color="black", lw=0.8)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("x₁")
    ax.set_ylabel("x₂")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="upper right", framealpha=0.9)
    fig.tight_layout()
    return fig
