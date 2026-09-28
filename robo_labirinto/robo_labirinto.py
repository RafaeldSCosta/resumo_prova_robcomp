#!/usr/bin/env python3

import math

import rclpy

from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String


# =============================================================
# VELOCIDADES
# =============================================================

VELOCIDADE_LINEAR = 0.18
VELOCIDADE_ANGULAR = 0.55


# =============================================================
# DISTÂNCIAS DO LASER
# =============================================================

# Se a frente ficar abaixo desse valor, não pode continuar andando.
DISTANCIA_FRONTAL_SEGURA = 0.55

# Acima desse valor, consideramos que existe passagem à direita.
ABERTURA_DIREITA = 0.90

# Distância que tentamos manter da parede direita.
DISTANCIA_PAREDE_DIREITA = 0.45

# Correção utilizada para acompanhar a parede.
GANHO_PAREDE = 0.80

# Limite da correção angular durante o movimento.
CORRECAO_ANGULAR_MAXIMA = 0.35


# =============================================================
# ROTAÇÃO
# =============================================================

# Erro angular aceito para finalizar uma curva.
TOLERANCIA_ANGULAR = math.radians(3)


# =============================================================
# DETECÇÃO DA SAÍDA
# =============================================================

# Consideramos uma região aberta quando as três direções superam
# esta distância.
DISTANCIA_REGIAO_ABERTA = 2.0

# Quantidade de execuções consecutivas em região aberta.
#
# Com timer de 0.1 segundo:
# 20 execuções correspondem aproximadamente a 2 segundos.
CICLOS_PARA_CONFIRMAR_SAIDA = 20


class RoboLabirinto(Node):
    """
    USE QUANDO O PROFESSOR PEDIR:

    - sair de um labirinto;
    - navegar sem colidir;
    - utilizar Laser e Odom;
    - seguir uma parede;
    - implementar máquina de estados;
    - publicar start e stop.

    Estratégia:
        regra da mão direita.
    """

    def __init__(self):
        super().__init__('robo_labirinto_node')

        # ---------------------------------------------------------
        # MÁQUINA DE ESTADOS
        # ---------------------------------------------------------

        self.robot_state = 'navegar'

        self.state_machine = {
            'navegar': self.navegar,
            'girar': self.girar,
            'parar': self.parar,
        }

        self.twist = Twist()

        # ---------------------------------------------------------
        # LASER
        # ---------------------------------------------------------

        self.laser_recebido = False

        self.distancia_frente = float('inf')
        self.distancia_direita = float('inf')
        self.distancia_esquerda = float('inf')

        # ---------------------------------------------------------
        # ODOM
        # ---------------------------------------------------------

        self.odom_recebida = False

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        # Ângulo que desejamos atingir durante uma curva.
        self.yaw_objetivo = 0.0

        # ---------------------------------------------------------
        # CONTROLE DA SAÍDA
        # ---------------------------------------------------------

        self.ciclos_regiao_aberta = 0
        self.finalizado = False

        # Evita repetir mensagens no tópico de status.
        self.status_pendente = 'START: procurando a saída'
        self.watcher_pendente = 'start'

        self.avisou_espera = False

        # ---------------------------------------------------------
        # PUBLISHERS
        # ---------------------------------------------------------

        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.status_pub = self.create_publisher(
            String,
            '/status_labirinto',
            10
        )

        # Mantido porque provas anteriores utilizaram /watcher
        # para receber start e stop.
        self.watcher_pub = self.create_publisher(
            String,
            '/watcher',
            10
        )

        # ---------------------------------------------------------
        # SUBSCRIBERS
        # ---------------------------------------------------------

        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.receber_laser,
            10
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.receber_odom,
            10
        )

        # ---------------------------------------------------------
        # TIMER
        # ---------------------------------------------------------

        self.timer = self.create_timer(
            0.1,
            self.control
        )

        self.get_logger().info('Robô labirinto iniciado.')

    # =============================================================
    # LASER
    # =============================================================

    def receber_laser(self, msg):
        """
        Divide o laser em três regiões.
        """

        self.distancia_frente = self.menor_distancia_setor(
            msg,
            angulo_central=0.0,
            abertura_graus=30
        )

        self.distancia_direita = self.menor_distancia_setor(
            msg,
            angulo_central=-math.pi / 2,
            abertura_graus=40
        )

        self.distancia_esquerda = self.menor_distancia_setor(
            msg,
            angulo_central=math.pi / 2,
            abertura_graus=40
        )

        self.laser_recebido = True
        self.avisou_espera = False

    def menor_distancia_setor(
        self,
        msg,
        angulo_central,
        abertura_graus
    ):
        """
        Retorna a menor distância dentro de um setor do laser.
        """

        meia_abertura = math.radians(
            abertura_graus / 2
        )

        distancias = []

        for indice, distancia in enumerate(msg.ranges):
            angulo = (
                msg.angle_min
                + indice * msg.angle_increment
            )

            diferenca = self.ajustar_angulo(
                angulo - angulo_central
            )

            if abs(diferenca) <= meia_abertura:
                if math.isnan(distancia):
                    continue

                if math.isinf(distancia):
                    distancia = msg.range_max

                if distancia >= msg.range_min:
                    distancias.append(distancia)

        if not distancias:
            return msg.range_max

        return min(distancias)

    # =============================================================
    # ODOM
    # =============================================================

    def receber_odom(self, msg):
        """
        Atualiza posição e ângulo do robô.
        """

        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        orientacao = msg.pose.pose.orientation

        # Converte quaternion para yaw.
        seno_yaw = 2.0 * (
            orientacao.w * orientacao.z
            + orientacao.x * orientacao.y
        )

        cosseno_yaw = 1.0 - 2.0 * (
            orientacao.y ** 2
            + orientacao.z ** 2
        )

        self.yaw = math.atan2(
            seno_yaw,
            cosseno_yaw
        )

        self.odom_recebida = True
        self.avisou_espera = False

    # =============================================================
    # FUNÇÕES AUXILIARES
    # =============================================================

    def ajustar_angulo(self, angulo):
        """
        Mantém um ângulo no intervalo entre -pi e pi.
        """

        return math.atan2(
            math.sin(angulo),
            math.cos(angulo)
        )

    def sensores_prontos(self):
        """
        O robô somente pode andar depois de receber Laser e Odom.
        """

        if self.laser_recebido and self.odom_recebida:
            return True

        self.twist = Twist()

        if not self.avisou_espera:
            self.status_pendente = (
                'WAITING: aguardando Laser e Odom'
            )

            self.avisou_espera = True

        return False

    def limitar(self, valor, minimo, maximo):
        """
        Limita um valor entre mínimo e máximo.
        """

        return max(
            minimo,
            min(valor, maximo)
        )

    # =============================================================
    # DETECÇÃO DA SAÍDA
    # =============================================================

    def verificar_saida(self):
        """
        Solução coringa:

        considera saída quando frente, esquerda e direita permanecem
        abertas por vários ciclos.

        SE A PROVA FORNECER UMA COORDENADA:

        substitua o conteúdo desta função por algo como:

            if self.x > 5.0:
                return True

        ou:

            if self.x < -3.0 and self.y > 2.0:
                return True
        """

        regiao_aberta = (
            self.distancia_frente > DISTANCIA_REGIAO_ABERTA
            and self.distancia_direita > DISTANCIA_REGIAO_ABERTA
            and self.distancia_esquerda > DISTANCIA_REGIAO_ABERTA
        )

        if regiao_aberta:
            self.ciclos_regiao_aberta += 1
        else:
            self.ciclos_regiao_aberta = 0

        return (
            self.ciclos_regiao_aberta
            >= CICLOS_PARA_CONFIRMAR_SAIDA
        )

    # =============================================================
    # INICIAR CURVA
    # =============================================================

    def iniciar_giro(self, graus, motivo):
        """
        Inicia uma rotação medida pela Odom.

        graus positivo:
            esquerda / anti-horário.

        graus negativo:
            direita / horário.
        """

        rotacao = math.radians(graus)

        self.yaw_objetivo = self.ajustar_angulo(
            self.yaw + rotacao
        )

        self.robot_state = 'girar'

        self.status_pendente = (
            f'IN_PROGRESS: {motivo}'
        )

        # Já executa o giro nesta chamada.
        self.girar()

    # =============================================================
    # ESTADO NAVEGAR
    # =============================================================

    def navegar(self):
        """
        Executa a regra da mão direita.
        """

        self.twist = Twist()

        if not self.sensores_prontos():
            return

        # Primeiro verifica se saiu do labirinto.
        if self.verificar_saida():
            self.finalizado = True
            self.robot_state = 'parar'

            self.status_pendente = (
                f'DONE: saída encontrada em '
                f'x={self.x:.2f}, y={self.y:.2f}'
            )

            self.watcher_pendente = 'stop'

            self.parar()
            return

        frente_bloqueada = (
            self.distancia_frente
            < DISTANCIA_FRONTAL_SEGURA
        )

        direita_aberta = (
            self.distancia_direita
            > ABERTURA_DIREITA
        )

        esquerda_aberta = (
            self.distancia_esquerda
            > DISTANCIA_FRONTAL_SEGURA
        )

        # Prioridade 1:
        # se existe passagem à direita e a frente permite fazer a curva.
        if direita_aberta and not frente_bloqueada:
            self.iniciar_giro(
                -90,
                'passagem à direita'
            )
            return

        # Prioridade 2:
        # frente bloqueada, mas esquerda livre.
        if frente_bloqueada and esquerda_aberta:
            self.iniciar_giro(
                90,
                'obstáculo frontal, girando à esquerda'
            )
            return

        # Prioridade 3:
        # beco sem saída.
        if frente_bloqueada and not esquerda_aberta:
            self.iniciar_giro(
                180,
                'beco sem saída, dando meia-volta'
            )
            return

        # Caso normal: andar seguindo a parede direita.
        erro_parede = (
            DISTANCIA_PAREDE_DIREITA
            - self.distancia_direita
        )

        correcao = GANHO_PAREDE * erro_parede

        correcao = self.limitar(
            correcao,
            -CORRECAO_ANGULAR_MAXIMA,
            CORRECAO_ANGULAR_MAXIMA
        )

        self.twist.linear.x = VELOCIDADE_LINEAR
        self.twist.angular.z = correcao

    # =============================================================
    # ESTADO GIRAR
    # =============================================================

    def girar(self):
        """
        Gira até atingir o yaw objetivo.
        """

        self.twist = Twist()

        if not self.odom_recebida:
            return

        erro = self.ajustar_angulo(
            self.yaw_objetivo - self.yaw
        )

        # Terminou a curva.
        if abs(erro) <= TOLERANCIA_ANGULAR:
            self.robot_state = 'navegar'
            self.status_pendente = 'IN_PROGRESS: curva concluída'

            # Para por um ciclo antes de voltar a andar.
            self.twist = Twist()
            return

        # Erro positivo: gira para a esquerda.
        if erro > 0:
            self.twist.angular.z = VELOCIDADE_ANGULAR

        # Erro negativo: gira para a direita.
        else:
            self.twist.angular.z = -VELOCIDADE_ANGULAR

    # =============================================================
    # ESTADO PARAR
    # =============================================================

    def parar(self):
        """
        Zera todas as velocidades.
        """

        self.twist = Twist()

    # =============================================================
    # STATUS
    # =============================================================

    def publicar_mensagens_pendentes(self):
        """
        Publica status e watcher sem repetir infinitamente.
        """

        if self.status_pendente is not None:
            msg_status = String()
            msg_status.data = self.status_pendente

            self.status_pub.publish(msg_status)

            self.get_logger().info(msg_status.data)

            self.status_pendente = None

        if self.watcher_pendente is not None:
            msg_watcher = String()
            msg_watcher.data = self.watcher_pendente

            self.watcher_pub.publish(msg_watcher)

            self.get_logger().info(
                f'Watcher: {msg_watcher.data}'
            )

            self.watcher_pendente = None

    # =============================================================
    # CONTROL
    # =============================================================

    def control(self):
        """
        Executa o estado atual.

        Esta é a única função que publica em /cmd_vel.
        """

        funcao_estado = self.state_machine[
            self.robot_state
        ]

        funcao_estado()

        self.cmd_vel_pub.publish(
            self.twist
        )

        self.publicar_mensagens_pendentes()

    def parar_antes_de_fechar(self):
        """
        Para o robô ao fechar o programa.
        """

        self.robot_state = 'parar'
        self.status_pendente = None
        self.watcher_pendente = None

        self.control()


def main(args=None):
    rclpy.init(args=args)

    node = RoboLabirinto()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        node.get_logger().info(
            'Encerrando o robô labirinto...'
        )

    finally:
        node.parar_antes_de_fechar()
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()