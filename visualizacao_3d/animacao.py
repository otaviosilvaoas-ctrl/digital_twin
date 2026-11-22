import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def animar_pendulo(t, X, guia=0.60, comprimento=0.36):

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.set_xlim(-guia/2 - 0.1, guia/2 + 0.1)
    ax.set_ylim(-comprimento - 0.1, comprimento + 0.15)
    
    ax.set_aspect('equal')
    ax.grid()

    ax.set_title("Simulação do Pêndulo Invertido")

    ax.set_xlabel("Posição [m]")
    ax.set_ylabel("Altura [m]")

    # Guia
    ax.plot(
        [-guia/2, guia/2],
        [0, 0],
        'k',
        linewidth=4
    )

    # Elementos gráficos
    carrinho, = ax.plot([], [], 's', markersize=15)
    haste, = ax.plot([], [], 'o-', linewidth=3)

    texto = ax.text(0.02, 0.95, '', transform=ax.transAxes)

    def atualizar(i):

        x = X[i, 0]
        theta = X[i, 1]

        # Posição do carrinho
        carrinho.set_data([x], [0])

        # Posição da extremidade do pêndulo
        xp = x + comprimento*np.sin(theta)
        yp = -comprimento*np.cos(theta)

        haste.set_data([x, xp], [0, yp])

        texto.set_text(
            f"Tempo: {t[i]:.2f} s\n"
            f"Ângulo: {np.degrees(theta):.2f}°\n"
            f"Posição: {x:.3f} m"
        )

        return carrinho, haste, texto

    animacao = FuncAnimation(
        fig,
        atualizar,
        frames=len(t),
        interval=20,
        blit=True
    )

    plt.show()

    return animacao