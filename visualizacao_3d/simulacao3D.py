from vpython import *
import numpy as np
import parametros as p


class Simulacao3D:
    """Representação tridimensional do carrinho e do pêndulo."""

    def __init__(self):

        # Configuração da janela
        scene.title = "Gêmeo Digital - Pêndulo Invertido"
        scene.width = 1000
        scene.height = 650
        scene.background = color.white
        scene.center = vector(0, 0, 0)
        scene.forward = vector(0, -0.3, -1)

        # Dimensões visuais
        self.comprimento_trilho = p.guia
        self.comprimento_haste = 2 * p.l_pend

        # Trilho
        self.trilho = box(
            pos=vector(0, -0.14, 0),
            size=vector(self.comprimento_trilho, 0.04, 0.12),
            color=color.gray(0.5)
        )

        # Carrinho
        self.carrinho = box(
            pos=vector(0, 0, 0),
            size=vector(0.12, 0.10, 0.10),
            color=color.blue
        )

        # Rodas
        self.roda_esquerda = cylinder(
            pos=vector(-0.035, -0.075, 0.06),
            axis=vector(0, 0, -0.12),
            radius=0.035,
            color=color.black
        )

        self.roda_direita = cylinder(
            pos=vector(0.035, -0.075, 0.06),
            axis=vector(0, 0, -0.12),
            radius=0.035,
            color=color.black
        )

        # Articulação do pêndulo
        self.articulacao = sphere(
            pos=vector(0, 0.05, 0),
            radius=0.018,
            color=color.red
        )

        # Haste
        self.haste = cylinder(
            pos=self.articulacao.pos,
            axis=vector(0, -self.comprimento_haste, 0),
            radius=0.009,
            color=color.red
        )

        # Massa na extremidade da haste (representação visual)
        self.massa_pendulo = sphere(
            pos=self.haste.pos + self.haste.axis,
            radius=0.025,
            color=color.orange
        )

    def atualizar(self, estados):
        """
        Atualiza a representação 3D.

        estados = [posição, ângulo, velocidade, velocidade angular]
        """

        posicao = estados[0]
        theta = estados[1]

        # Atualiza o carrinho
        self.carrinho.pos.x = posicao

        # Atualiza as rodas
        self.roda_esquerda.pos.x = posicao - 0.035
        self.roda_direita.pos.x = posicao + 0.035

        # Atualiza a articulação
        self.articulacao.pos.x = posicao

        # Calcula a orientação da haste
        eixo_haste = vector(
            self.comprimento_haste * np.sin(theta),
            -self.comprimento_haste * np.cos(theta),
            0
        )

        self.haste.pos = self.articulacao.pos
        self.haste.axis = eixo_haste

        # Atualiza a massa na extremidade
        self.massa_pendulo.pos = self.haste.pos + self.haste.axis


# Teste isolado da visualização
if __name__ == "__main__":

    simulacao = Simulacao3D()

    t = 0

    while True:
        rate(100)

        # Movimento fictício apenas para testar a visualização
        posicao = 0.10 * np.sin(t)
        theta = np.pi + 0.15 * np.sin(2 * t)

        estados = [posicao, theta, 0, 0]

        simulacao.atualizar(estados)

        t += p.TS