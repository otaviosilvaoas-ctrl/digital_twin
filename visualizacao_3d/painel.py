import tkinter as tk
import numpy as np
import parametros as p
import controle
import main


from planta import PlantaFalsa
from gemeo_digital import GemeoDigital
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk

PASSOS_ANIMACAO = 3     # redesenha o pêndulo a cada 3 passos (30 ms)
PASSOS_GRAFICOS = 10    # redesenha os gráficos a cada 10 passos (100 ms)
PASSOS_MAX_CENTRALIZAR = 500    # limite de 5 s, para nunca ficar preso


class PainelGemeo:

    def __init__(self, janela):

        self.janela = janela

        self.janela.title("Gêmeo Digital - Pêndulo Invertido")
        self.janela.geometry("1200x800")
        self.janela.minsize(1000, 650)

        self.criar_interface()

        # Preparação da simulação
        self.preparar_simulacao()

    # ======================================================
    # PREPARAÇÃO DA SIMULAÇÃO
    # ======================================================

    def preparar_simulacao(self):

        # Inicializa a simulação definida no main.py
        self.K, self.N, self.planta, self.gemeo = main.criar_simulacao()

        # Índice da simulação
        self.indice = 0

        # Dados para os gráficos
        self.tempo_dados = []
        self.posicao_dados = []
        self.angulo_dados = []
        self.controle_dados = []

        # Estados iniciais
        self.X_planta = [self.planta.ler()]
        self.X_gemeo = [self.gemeo.ler()]

        # Estado da execução
        self.simulacao_ativa = False
        self.simulacao_pausada = False
        self.controlador_ativo = False
        self.centralizando = False
        self.id_after = None

        self.atualizar_botoes()

    def criar_interface(self):

        # ==================================================
        # PAINEL LATERAL ESQUERDO
        # ==================================================

        self.painel_esquerdo = ttk.Frame(
            self.janela,
            padding=15
        )

        self.painel_esquerdo.pack(
            side="left",
            fill="y"
        )

        titulo = ttk.Label(
            self.painel_esquerdo,
            text="PAINEL DE CONTROLE",
            font=("Arial", 14, "bold")
        )

        titulo.pack(pady=15)

        self.status_simulacao = ttk.Label(
            self.painel_esquerdo,
            text="Simulação: Parada",
            font=("Arial", 11)
        )

        self.status_simulacao.pack(pady=10)

        self.botao_iniciar = ttk.Button(
            self.painel_esquerdo,
            text="Iniciar",
            command=self.iniciar
        )

        self.botao_iniciar.pack(fill="x", pady=5)

        self.botao_pausar = ttk.Button(
            self.painel_esquerdo,
            text="Pausar",
            command=self.pausar
        )

        self.botao_pausar.pack(fill="x", pady=5)

        self.botao_reiniciar = ttk.Button(
            self.painel_esquerdo,
            text="Reiniciar",
            command=self.reiniciar
        )

        self.botao_reiniciar.pack(fill="x", pady=5)

        ttk.Separator(
            self.painel_esquerdo,
            orient="horizontal"
        ).pack(fill="x", pady=20)

        titulo_controlador = ttk.Label(
            self.painel_esquerdo,
            text="CONTROLADOR",
            font=("Arial", 12, "bold")
        )

        titulo_controlador.pack(pady=10)

        self.status_controlador = ttk.Label(
            self.painel_esquerdo,
            text="Desativado"
        )

        self.status_controlador.pack(pady=5)

        self.botao_controlador = ttk.Button(
            self.painel_esquerdo,
            text="Ativar controlador",
            command=self.alternar_controlador
        )

        self.botao_controlador.pack(fill="x", pady=5)

        # ==================================================
        # ÁREA PRINCIPAL
        # ==================================================

        self.area_principal = ttk.Frame(
            self.janela,
            padding=10
        )

        self.area_principal.pack(
            side="right",
            fill="both",
            expand=True
        )

        titulo_principal = ttk.Label(
            self.area_principal,
            text="GÊMEO DIGITAL",
            font=("Arial", 18, "bold")
        )

        titulo_principal.pack(pady=10)

        # ==================================================
        # ÁREA DE VISUALIZAÇÃO
        # ==================================================

        self.area_visualizacao = ttk.LabelFrame(
            self.area_principal,
            text="Área de visualização da planta virtual",
            padding=10
        )

        self.area_visualizacao.pack(
            fill="both",
            expand=True
        )

        # ==================================================
        # ÁREA DA ANIMAÇÃO DO PÊNDULO
        # ==================================================

        self.figura_animacao = Figure(
            figsize=(8, 4),
            dpi=100
        )

        self.ax_animacao = self.figura_animacao.add_subplot(111)

        self.ax_animacao.set_title("Animação do pêndulo invertido")
        self.ax_animacao.set_xlabel("Posição (m)")
        self.ax_animacao.set_ylabel("Altura (m)")
        self.ax_animacao.grid(True)
        self.ax_animacao.set_aspect("equal")

        self.canvas_animacao = FigureCanvasTkAgg(
            self.figura_animacao,
            master=self.area_visualizacao
        )

        self.canvas_animacao.draw()

        self.canvas_animacao.get_tk_widget().pack(
            fill="both",
            expand=True
        )


        # ==================================================
        # ELEMENTOS GRÁFICOS DO PÊNDULO
        # ==================================================

        self.comprimento = 0.36
        self.guia = 0.60

        # Limites da visualização
        self.ax_animacao.set_xlim(-0.45, 0.45)
        self.ax_animacao.set_ylim(-0.50, 0.50)

        # Trilho do carrinho
        self.ax_animacao.plot(
            [-self.guia / 2, self.guia / 2],
            [0, 0],
            linewidth=4,
            color="black"
        )

        # Carrinho
        self.carrinho, = self.ax_animacao.plot(
            [0], [0],
            "s",
            markersize=15
        )

        # Haste do pêndulo
        self.haste, = self.ax_animacao.plot(
            [0, 0],
            [0, -self.comprimento],
            "o-",
            linewidth=3,
            markersize=7
        )

        # ==================================================
        # ÁREA DOS GRÁFICOS
        # ==================================================

        self.area_graficos = ttk.Frame(
            self.area_principal
        )

        self.area_graficos.pack(
            fill="x",
            pady=10
        )

        self.criar_graficos()




        # ==================================================
        # POSIÇÃO INICIAL DA ANIMAÇÃO
        # ==================================================

        self.atualizar_animacao(0.0, 0.0)





    # ======================================================
    # ATUALIZAÇÃO DA ANIMAÇÃO
    # ======================================================

    def atualizar_animacao(self, posicao, angulo):

        # Posição horizontal do carrinho
        x = posicao

        # Coordenadas da ponta do pêndulo
        xp = x + self.comprimento * np.sin(angulo)
        yp = -self.comprimento * np.cos(angulo)

        # Atualização do carrinho
        self.carrinho.set_data([x], [0])

        # Atualização da haste
        self.haste.set_data(
            [x, xp],
            [0, yp]
        )

        # Atualização da tela
        self.canvas_animacao.draw_idle()

    # ======================================================
    # CRIAÇÃO DOS GRÁFICOS
    # ======================================================
    # ======================================================
    # EXECUÇÃO DA SIMULAÇÃO
    # ======================================================
    def executar_simulacao(self):

        if not self.simulacao_ativa:
            return

        if self.indice >= self.N:
            self.simulacao_ativa = False
            self.id_after = None
            self.status_simulacao.config(text="Simulação: Finalizada")
            self.atualizar_botoes()
            return

        x_planta, x_gemeo, u = main.executar_passo(
            self.planta,
            self.gemeo,
            self.K,
            self.controlador_ativo
        )

        tempo = (self.indice + 1) * p.TS

        self.tempo_dados.append(tempo)
        self.posicao_dados.append(x_planta[0])
        self.angulo_dados.append(np.degrees(x_planta[1]))
        self.controle_dados.append(u)

        self.X_planta.append(x_planta)
        self.X_gemeo.append(x_gemeo)

        if self.indice % PASSOS_ANIMACAO == 0:
            self.atualizar_animacao(x_planta[0], x_planta[1])

        if self.indice % PASSOS_GRAFICOS == 0:
            self.atualizar_graficos()

        self.indice += 1

        self.id_after = self.janela.after(10, self.executar_simulacao)

    # ======================================================
    # ATUALIZAÇÃO DOS GRÁFICOS
    # ======================================================

    def atualizar_graficos(self):

        self.linha_posicao.set_data(self.tempo_dados, self.posicao_dados)
        self.linha_angulo.set_data(self.tempo_dados, self.angulo_dados)
        self.linha_controle.set_data(self.tempo_dados, self.controle_dados)

        for eixo in (self.ax_posicao, self.ax_angulo, self.ax_controle):
            eixo.relim()
            eixo.autoscale_view(scalex=False)   # só o eixo y se ajusta

        self.canvas.draw_idle()

    # ======================================================
    # CRIAÇÃO DOS GRÁFICOS
    # ======================================================

    def criar_graficos(self):

        self.figura = Figure(
            figsize=(10, 3.5),
            dpi=100
        )

        # Gráfico 1: posição
        self.ax_posicao = self.figura.add_subplot(131)
        self.ax_posicao.set_title("Posição do carrinho")
        self.ax_posicao.set_xlabel("Tempo (s)")
        self.ax_posicao.set_ylabel("Posição (m)")
        self.ax_posicao.grid(True)

        self.linha_posicao, = self.ax_posicao.plot(
            [], []
        )

        # Gráfico 2: ângulo
        self.ax_angulo = self.figura.add_subplot(132)

        self.ax_angulo.set_title("Ângulo do pêndulo")
        self.ax_angulo.set_xlabel("Tempo (s)")
        self.ax_angulo.set_ylabel("Ângulo (graus)")
        self.ax_angulo.grid(True)

        self.linha_angulo, = self.ax_angulo.plot(
            [], []
        )

        # Gráfico 3: controle
        self.ax_controle = self.figura.add_subplot(133)

        self.ax_controle.set_title("Sinal de controle")
        self.ax_controle.set_xlabel("Tempo (s)")
        self.ax_controle.set_ylabel("Tensão (V)")
        self.ax_controle.grid(True)

        self.linha_controle, = self.ax_controle.plot(
            [], []
        )

        for eixo in (self.ax_posicao, self.ax_angulo, self.ax_controle):
            eixo.set_xlim(0, p.TF)

        self.figura.tight_layout()

        self.canvas = FigureCanvasTkAgg(
            self.figura,
            master=self.area_graficos
        )

        self.canvas.draw()

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )



    def atualizar_botoes(self):

        ocupado = self.centralizando
        ativa = self.simulacao_ativa
        terminou = self.indice >= self.N
        self.botao_iniciar.config(state="disabled" if (ativa or terminou or ocupado) else "normal")
        self.botao_pausar.config(state="normal" if (ativa and not ocupado) else "disabled")
        self.botao_reiniciar.config(state="disabled" if ocupado else "normal")
        self.botao_controlador.config(state="disabled" if ocupado else "normal")

    # ======================================================
    # AÇÕES DOS BOTÕES
    # ======================================================

    def iniciar(self):
        if self.simulacao_ativa or self.indice >= self.N:
            return
        self.simulacao_ativa = True
        self.simulacao_pausada = False
        self.status_simulacao.config(text="Simulação: Em execução")
        self.atualizar_botoes()
        self.id_after = self.janela.after(10, self.executar_simulacao)

    def pausar(self):
        if not self.simulacao_ativa:
            return
        self.simulacao_ativa = False
        self.simulacao_pausada = True
        if self.id_after is not None:
            self.janela.after_cancel(self.id_after)
            self.id_after = None
        self.status_simulacao.config(text="Simulação: Pausada")
        self.atualizar_botoes()

    def reiniciar(self):
        # Para a execução em andamento
        self.simulacao_ativa = False
        if self.id_after is not None:
            self.janela.after_cancel(self.id_after)
            self.id_after = None

        # Controlador desligado durante o retorno
        self.controlador_ativo = False
        self.status_controlador.config(text="Desativado")
        self.botao_controlador.config(text="Ativar controlador")

        # Inicia o retorno do carro ao centro
        self.centralizando = True
        self.passos_centralizar = 0
        self.status_simulacao.config(text="Simulação: Centralizando o carro...")
        self.atualizar_botoes()
        self.id_after = self.janela.after(10, self.centralizar_carro)

    def centralizar_carro(self):
        x_planta, x_gemeo, u = main.executar_passo_centralizar(self.planta, self.gemeo)
        self.passos_centralizar += 1

        if self.passos_centralizar % PASSOS_ANIMACAO == 0:
            self.atualizar_animacao(x_planta[0], x_planta[1])

        centralizado = abs(x_planta[0]) < 0.005 and abs(x_planta[2]) < 0.01
        estourou = self.passos_centralizar >= PASSOS_MAX_CENTRALIZAR

        if centralizado or estourou:
            self.finalizar_reinicio()
            return

        self.id_after = self.janela.after(10, self.centralizar_carro)

    def finalizar_reinicio(self):
        # Planta e gêmeo voltam ao estado inicial, índice zero, listas limpas
        self.preparar_simulacao()

        self.linha_posicao.set_data([], [])
        self.linha_angulo.set_data([], [])
        self.linha_controle.set_data([], [])
        self.canvas.draw_idle()

        self.atualizar_animacao(main.X0[0], main.X0[1])
        self.status_simulacao.config(text="Simulação: Parada (carro centralizado)")

    def alternar_controlador(self):
        self.controlador_ativo = not self.controlador_ativo
        if self.controlador_ativo:
            self.status_controlador.config(text="Ativado")
            self.botao_controlador.config(text="Desativar controlador")
        else:
            self.status_controlador.config(text="Desativado")
            self.botao_controlador.config(text="Ativar controlador")


# ==========================================================
# EXECUÇÃO
# ==========================================================

if __name__ == "__main__":

    janela = tk.Tk()

    painel = PainelGemeo(janela)

    janela.mainloop()