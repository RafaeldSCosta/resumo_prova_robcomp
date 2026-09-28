import math
import numpy as np
import rclpy

from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


# Escolha o comportamento que será executado.
#
# 'monitorar'
# 'andar_distancia_seguro'
# 'desviar_obstaculos'
# 'missao_completa'
EXEMPLO = 'missao_completa'


class ControlarRobo(Node):

    # ============================================================
    # CONTROLANDO O ROBÔ COM ODOM E LASER
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - movimentar o robô usando mais de um sensor;
    # - andar uma distância sem bater;
    # - parar se encontrar um obstáculo;
    # - desviar dos obstáculos;
    # - cumprir uma missão usando posição e Laser;
    # - integrar subscriber e publisher.
    #
    # COMO FUNCIONA:
    #
    # Odom informa:
    #
    # - posição X;
    # - posição Y;
    # - orientação;
    # - distância percorrida.
    #
    # Laser informa:
    #
    # - distância da frente;
    # - distância da esquerda;
    # - distância da direita.
    #
    # Twist envia:
    #
    # - velocidade linear;
    # - velocidade angular.
    #
    # FLUXO:
    #
    # /odom ──→ posição e distância ──┐
    #                                 ├──→ control ──→ /cmd_vel
    # /scan ──→ obstáculos ──────────┘

    def __init__(self):

        super().__init__('controlar_robo')

        # ----------------------------
        # Informações do Odom
        # ----------------------------

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.x_inicial = None
        self.y_inicial = None

        self.distancia_percorrida = 0.0

        self.recebeu_odom = False

        # ----------------------------
        # Informações do Laser
        # ----------------------------

        self.abertura = 10

        self.frente = float('inf')
        self.esquerda = float('inf')
        self.direita = float('inf')

        self.recebeu_laser = False

        # ----------------------------
        # Valores que você pode trocar
        # ----------------------------

        # Distância que o robô deve percorrer.
        self.distancia_objetivo = 2.0

        # Distância mínima permitida de um obstáculo.
        self.distancia_seguranca = 0.5

        # Velocidades utilizadas.
        self.velocidade_linear = 0.2
        self.velocidade_angular = 0.3

        # Estado usado na missão completa.
        self.estado = 'andar'

        self.finalizado = False

        # ----------------------------
        # Subscriber do Odom
        # ----------------------------

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.RELIABLE
            )
        )

        # ----------------------------
        # Subscriber do Laser
        # ----------------------------

        self.laser_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.BEST_EFFORT
            )
        )

        # ----------------------------
        # Publisher de velocidade
        # ----------------------------

        self.vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Executa control dez vezes por segundo.
        self.timer = self.create_timer(
            0.1,
            self.control
        )

    # ============================================================
    # RECEBENDO ODOM
    # ============================================================

    def odom_callback(self, msg: Odometry):

        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        orientation = msg.pose.pose.orientation

        self.yaw = self.quaternion_para_yaw(
            orientation
        )

        # Guarda a posição inicial somente uma vez.
        if not self.recebeu_odom:

            self.x_inicial = self.x
            self.y_inicial = self.y

            self.recebeu_odom = True

        # Calcula a distância entre a posição inicial
        # e a posição atual.
        diferenca_x = self.x - self.x_inicial
        diferenca_y = self.y - self.y_inicial

        self.distancia_percorrida = math.sqrt(
            diferenca_x ** 2 +
            diferenca_y ** 2
        )

    def quaternion_para_yaw(self, orientation):

        x = orientation.x
        y = orientation.y
        z = orientation.z
        w = orientation.w

        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)

        return math.atan2(
            siny_cosp,
            cosy_cosp
        )

    # ============================================================
    # RECEBENDO LASER
    # ============================================================

    def menor_distancia(self, medicoes):

        valores = np.array(
            medicoes,
            dtype=float
        )

        # Zero pode representar uma leitura inválida.
        valores[valores == 0] = np.inf

        # Remove valores NaN.
        valores = valores[~np.isnan(valores)]

        if len(valores) == 0:
            return float('inf')

        return float(np.min(valores))

    def laser_callback(self, msg: LaserScan):

        laser = np.array(
            msg.ranges,
            dtype=float
        )

        laser[laser == 0] = np.inf

        abertura = self.abertura

        # Frente: índices próximos de zero.
        leituras_frente = np.concatenate(
            (
                laser[:abertura],
                laser[-abertura:]
            )
        )

        # Esquerda: índices próximos de 90.
        leituras_esquerda = laser[
            90 - abertura:
            90 + abertura
        ]

        # Direita: índices próximos de 270.
        leituras_direita = laser[
            270 - abertura:
            270 + abertura
        ]

        self.frente = self.menor_distancia(
            leituras_frente
        )

        self.esquerda = self.menor_distancia(
            leituras_esquerda
        )

        self.direita = self.menor_distancia(
            leituras_direita
        )

        self.recebeu_laser = True

    # ============================================================
    # AÇÕES BÁSICAS
    # ============================================================

    def andar(self, velocidade=None):

        # Se nenhuma velocidade for informada,
        # usa o valor definido no __init__.
        if velocidade is None:
            velocidade = self.velocidade_linear

        msg = Twist()
        msg.linear.x = velocidade

        self.vel_pub.publish(msg)

    def girar(self, velocidade=None):

        if velocidade is None:
            velocidade = self.velocidade_angular

        msg = Twist()
        msg.angular.z = velocidade

        self.vel_pub.publish(msg)

    def parar(self):

        msg = Twist()

        self.vel_pub.publish(msg)

    # ============================================================
    # EXEMPLO 1 — MONITORAR ODOM E LASER
    # ============================================================

    def monitorar(self):

        # Use quando quiser apenas conferir se os dois
        # sensores estão funcionando.

        yaw_graus = math.degrees(self.yaw)

        print(
            f'Posição: ({self.x:.2f}, {self.y:.2f})'
        )

        print(
            f'Yaw: {yaw_graus:.2f} graus'
        )

        print(
            f'Distância percorrida: '
            f'{self.distancia_percorrida:.2f} m'
        )

        print(
            f'Laser — frente: {self.frente:.2f} | '
            f'esquerda: {self.esquerda:.2f} | '
            f'direita: {self.direita:.2f}'
        )

        print()

    # ============================================================
    # EXEMPLO 2 — ANDAR UMA DISTÂNCIA COM SEGURANÇA
    # ============================================================

    def andar_distancia_seguro(self):

        # USE QUANDO O PROFESSOR PEDIR:
        #
        # "Ande uma determinada distância, mas pare
        # se encontrar um obstáculo."

        # Primeiro verifica se já chegou à distância.
        if (
            self.distancia_percorrida
            >= self.distancia_objetivo
        ):

            self.parar()

            if not self.finalizado:
                print('Distância objetivo alcançada')
                self.finalizado = True

            return

        # Se ainda não chegou, verifica o Laser.
        if self.frente < self.distancia_seguranca:

            self.parar()

            print(
                f'Obstáculo detectado a '
                f'{self.frente:.2f} m'
            )

        else:

            self.andar()

            print(
                f'Andando: '
                f'{self.distancia_percorrida:.2f} / '
                f'{self.distancia_objetivo:.2f} m'
            )

    # ============================================================
    # EXEMPLO 3 — DESVIAR CONTINUAMENTE
    # ============================================================

    def desviar_obstaculos(self):

        # USE QUANDO O PROFESSOR PEDIR:
        #
        # "Faça o robô andar e desviar dos obstáculos."
        #
        # Neste exemplo, o robô não possui um destino.
        # Ele continuará andando pelo ambiente.

        if self.frente >= self.distancia_seguranca:

            self.andar()

            print('Frente livre: andando')

        elif self.esquerda > self.direita:

            self.girar(self.velocidade_angular)

            print('Obstáculo: girando para a esquerda')

        else:

            self.girar(-self.velocidade_angular)

            print('Obstáculo: girando para a direita')

    # ============================================================
    # EXEMPLO 4 — MISSÃO COMPLETA
    # ============================================================

    def missao_completa(self):

        # USE QUANDO O PROFESSOR PEDIR ALGO COMO:
        #
        # "Faça o robô andar pelo ambiente, desviar dos
        # obstáculos e parar depois de percorrer uma distância."
        #
        # Odom:
        # verifica a distância percorrida.
        #
        # Laser:
        # encontra obstáculos e escolhe o lado mais livre.
        #
        # Twist:
        # movimenta o robô.

        # A distância possui prioridade.
        #
        # Quando alcançar o objetivo, a missão termina.
        if (
            self.distancia_percorrida
            >= self.distancia_objetivo
        ):

            self.estado = 'parar'

        # Executa o comportamento correspondente
        # ao estado atual.
        if self.estado == 'andar':

            # Se encontrou obstáculo, decide para onde girar.
            if self.frente < self.distancia_seguranca:

                if self.esquerda > self.direita:
                    self.estado = 'girar_esquerda'

                else:
                    self.estado = 'girar_direita'

            else:

                self.andar()

                print(
                    f'Andando: '
                    f'{self.distancia_percorrida:.2f} / '
                    f'{self.distancia_objetivo:.2f} m'
                )

        elif self.estado == 'girar_esquerda':

            # Continua girando até a frente ficar livre.
            if self.frente < self.distancia_seguranca:

                self.girar(self.velocidade_angular)

                print('Girando para a esquerda')

            else:

                self.parar()
                self.estado = 'andar'

        elif self.estado == 'girar_direita':

            if self.frente < self.distancia_seguranca:

                self.girar(-self.velocidade_angular)

                print('Girando para a direita')

            else:

                self.parar()
                self.estado = 'andar'

        elif self.estado == 'parar':

            self.parar()

            if not self.finalizado:

                print('Missão finalizada')
                self.finalizado = True

    # ============================================================
    # CONTROL
    # ============================================================

    def control(self):

        # Só começa depois de receber os dois sensores.
        if not self.recebeu_odom or not self.recebeu_laser:
            self.parar()
            return

        exemplos = {
            'monitorar': self.monitorar,
            'andar_distancia_seguro': self.andar_distancia_seguro,
            'desviar_obstaculos': self.desviar_obstaculos,
            'missao_completa': self.missao_completa
        }

        if EXEMPLO not in exemplos:
            self.parar()

            raise ValueError(
                f'Exemplo inválido: {EXEMPLO}'
            )

        exemplos[EXEMPLO]()


def main(args=None):

    rclpy.init(args=args)

    node = ControlarRobo()

    rclpy.spin(node)

    # Garante que o robô pare ao encerrar.
    node.parar()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()


#self.distancia_objetivo = 2.0
#self.distancia_seguranca = 0.5
#self.velocidade_linear = 0.2
#self.velocidade_angular = 0.3

#EXEMPLO = 'missao_completa'