import numpy as np
import rclpy

from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


# Escolha o exemplo:
#
# 'mostrar'
# 'detectar_obstaculo'
# 'parar_antes_de_bater'
# 'desviar'
EXEMPLO = 'mostrar'


class UsarLaser(Node):

    # ============================================================
    # USANDO LASER
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - medir a distância até um obstáculo;
    # - verificar se a frente está livre;
    # - descobrir as distâncias dos lados;
    # - parar antes de bater;
    # - escolher o lado mais livre;
    # - desviar de um obstáculo.
    #
    # O Laser recebe informações pelo tópico:
    #
    # /scan
    #
    # A mensagem recebida é:
    #
    # sensor_msgs/msg/LaserScan
    #
    # As distâncias ficam em:
    #
    # msg.ranges
    #
    # No Laser da disciplina:
    #
    # índice 0: frente;
    # índice 90: esquerda;
    # índice 180: trás;
    # índice 270: direita.

    def __init__(self):

        super().__init__('usar_laser')

        # Quantidade de graus analisados para cada
        # lado da direção central.
        #
        # Abertura 10 significa que serão analisados
        # aproximadamente 20 graus em cada direção.
        self.abertura = 10

        # Distância usada para considerar que existe
        # um obstáculo próximo.
        #
        # Troque conforme o enunciado.
        self.distancia_seguranca = 0.5

        self.frente = float('inf')
        self.esquerda = float('inf')
        self.direita = float('inf')
        self.tras = float('inf')

        self.recebeu_laser = False

        # Recebe as medições do Laser.
        self.laser_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.BEST_EFFORT
            )
        )

        # Envia velocidade para o robô.
        self.vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.timer = self.create_timer(
            0.1,
            self.control
        )

    def menor_distancia(self, medicoes):

        # Converte as medições para array NumPy.
        valores = np.array(
            medicoes,
            dtype=float
        )

        # Zero pode significar que o sensor não
        # conseguiu fazer a leitura.
        valores[valores == 0] = np.inf

        # Remove possíveis valores NaN.
        valores = valores[~np.isnan(valores)]

        if len(valores) == 0:
            return float('inf')

        # Usamos o menor valor porque ele representa
        # o obstáculo mais próximo naquela direção.
        return float(np.min(valores))

    def laser_callback(self, msg: LaserScan):

        # Copia todas as distâncias recebidas.
        laser = np.array(
            msg.ranges,
            dtype=float
        )

        laser[laser == 0] = np.inf

        abertura = self.abertura

        # A frente fica dividida entre o começo
        # e o final da lista.
        leituras_frente = np.concatenate(
            (
                laser[:abertura],
                laser[-abertura:]
            )
        )

        leituras_esquerda = laser[
            90 - abertura:
            90 + abertura
        ]

        leituras_tras = laser[
            180 - abertura:
            180 + abertura
        ]

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

        self.tras = self.menor_distancia(
            leituras_tras
        )

        self.recebeu_laser = True

    def andar(self, velocidade=0.2):

        msg = Twist()
        msg.linear.x = velocidade

        self.vel_pub.publish(msg)

    def girar(self, velocidade=0.3):

        msg = Twist()
        msg.angular.z = velocidade

        self.vel_pub.publish(msg)

    def parar(self):

        msg = Twist()

        self.vel_pub.publish(msg)

    def mostrar_laser(self):

        # Use quando o professor pedir apenas para acessar
        # ou mostrar as leituras do Laser.

        print(f'Frente: {self.frente:.2f} m')
        print(f'Esquerda: {self.esquerda:.2f} m')
        print(f'Direita: {self.direita:.2f} m')
        print(f'Trás: {self.tras:.2f} m')
        print()

    def detectar_obstaculo(self):

        # Use quando o professor pedir apenas para verificar
        # se existe algo próximo da frente do robô.

        if self.frente < self.distancia_seguranca:

            print(
                f'Obstáculo detectado a '
                f'{self.frente:.2f} m'
            )

        else:

            print(
                f'Frente livre: {self.frente:.2f} m'
            )

    def parar_antes_de_bater(self):

        # Use quando o professor pedir:
        #
        # "Ande para frente e pare antes do obstáculo."

        if self.frente >= self.distancia_seguranca:

            self.andar(0.2)

            print(
                f'Andando. Obstáculo a '
                f'{self.frente:.2f} m'
            )

        else:

            self.parar()

            print(
                f'Parado. Obstáculo a '
                f'{self.frente:.2f} m'
            )

    def desviar(self):

        # Use quando o professor pedir:
        #
        # "Ande para frente e desvie dos obstáculos."

        # Caminho livre:
        # continua andando.
        if self.frente >= self.distancia_seguranca:

            self.andar(0.2)

            print('Andando para frente')

        # Obstáculo na frente e esquerda mais livre:
        # gira para a esquerda.
        elif self.esquerda > self.direita:

            self.girar(0.3)

            print('Girando para a esquerda')

        # Obstáculo na frente e direita mais livre:
        # gira para a direita.
        else:

            self.girar(-0.3)

            print('Girando para a direita')

    def control(self):

        # Não movimenta o robô antes de receber
        # a primeira mensagem do Laser.
        if not self.recebeu_laser:
            self.parar()
            return

        exemplos = {
            'mostrar': self.mostrar_laser,
            'detectar_obstaculo': self.detectar_obstaculo,
            'parar_antes_de_bater': self.parar_antes_de_bater,
            'desviar': self.desviar
        }

        if EXEMPLO not in exemplos:
            self.parar()

            raise ValueError(
                f'Exemplo inválido: {EXEMPLO}'
            )

        exemplos[EXEMPLO]()


def main(args=None):

    rclpy.init(args=args)

    node = UsarLaser()

    rclpy.spin(node)

    # Garante que o robô pare ao encerrar.
    node.parar()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

#self.abertura = 10
#self.distancia_seguranca = 0.5