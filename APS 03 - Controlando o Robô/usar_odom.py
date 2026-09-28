import math
import rclpy

from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist


# Escolha o exemplo:
#
# 'mostrar'
# 'andar_distancia'
# 'chegar_em_x'
# 'girar_angulo'
EXEMPLO = 'mostrar'


class UsarOdom(Node):

    # ============================================================
    # USANDO ODOM
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - descobrir a posição do robô;
    # - acessar as coordenadas X e Y;
    # - descobrir para onde o robô está virado;
    # - andar uma distância específica;
    # - chegar em uma coordenada;
    # - girar uma quantidade de graus.
    #
    # O Odom recebe informações pelo tópico:
    #
    # /odom
    #
    # A mensagem recebida é:
    #
    # nav_msgs/msg/Odometry
    #
    # Principais campos:
    #
    # msg.pose.pose.position.x
    # msg.pose.pose.position.y
    # msg.pose.pose.orientation

    def __init__(self):

        super().__init__('usar_odom')

        # Posição e orientação atuais.
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        # Posição e orientação do início da tarefa.
        self.x_inicial = None
        self.y_inicial = None
        self.yaw_inicial = None

        self.recebeu_odom = False
        self.finalizado = False

        # Valores dos exemplos.
        #
        # Troque de acordo com o enunciado.
        self.distancia_objetivo = 1.0
        self.x_objetivo = 2.0
        self.angulo_objetivo = 90.0

        # Recebe a posição e a orientação.
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.RELIABLE
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

    def odom_callback(self, msg: Odometry):

        # Pega a posição atual.
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        # A orientação chega como quaternion.
        orientation = msg.pose.pose.orientation

        # Converte o quaternion para yaw.
        self.yaw = self.quaternion_para_yaw(
            orientation
        )

        # Guarda os valores iniciais somente uma vez.
        if not self.recebeu_odom:

            self.x_inicial = self.x
            self.y_inicial = self.y
            self.yaw_inicial = self.yaw

            self.recebeu_odom = True

    def quaternion_para_yaw(self, orientation):

        # Esta função transforma o quaternion recebido
        # pelo Odom no ângulo yaw.
        #
        # O yaw indica para onde o robô está virado.

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

    def calcular_distancia(self):

        # Calcula a distância em linha reta entre
        # a posição inicial e a posição atual.

        diferenca_x = self.x - self.x_inicial
        diferenca_y = self.y - self.y_inicial

        return math.sqrt(
            diferenca_x ** 2 +
            diferenca_y ** 2
        )

    def calcular_angulo_girado(self):

        # Calcula quanto o robô girou desde o início.
        diferenca = self.yaw - self.yaw_inicial

        # Mantém o ângulo entre -pi e pi.
        #
        # Isso evita erros quando o yaw passa
        # de 180 graus para -180 graus.
        diferenca = math.atan2(
            math.sin(diferenca),
            math.cos(diferenca)
        )

        return math.degrees(diferenca)

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

    def mostrar_odom(self):

        # Use este exemplo quando o professor pedir
        # apenas para mostrar ou acessar os valores do Odom.

        yaw_graus = math.degrees(self.yaw)
        distancia = self.calcular_distancia()

        print(f'Posição X: {self.x:.2f} m')
        print(f'Posição Y: {self.y:.2f} m')
        print(f'Yaw: {yaw_graus:.2f} graus')
        print(f'Distância: {distancia:.2f} m')
        print()

    def andar_distancia(self):

        # Use quando o professor pedir:
        #
        # "Ande uma determinada distância e pare."
        #
        # Troque self.distancia_objetivo no __init__.

        distancia = self.calcular_distancia()

        print(
            f'Distância: {distancia:.2f} / '
            f'{self.distancia_objetivo:.2f} m'
        )

        if distancia < self.distancia_objetivo:
            self.andar(0.2)

        else:
            self.parar()

            if not self.finalizado:
                print('Distância alcançada')
                self.finalizado = True

    def chegar_em_x(self):

        # Use quando o professor pedir:
        #
        # "Faça o robô chegar em determinada coordenada X."
        #
        # Troque self.x_objetivo no __init__.

        print(
            f'X atual: {self.x:.2f} | '
            f'X desejado: {self.x_objetivo:.2f}'
        )

        # Se o objetivo estiver à frente no eixo X.
        if self.x < self.x_objetivo:
            self.andar(0.2)

        else:
            self.parar()

            if not self.finalizado:
                print('Coordenada X alcançada')
                self.finalizado = True

    def girar_angulo(self):

        # Use quando o professor pedir:
        #
        # "Gire determinada quantidade de graus."
        #
        # Positivo:
        # gira para a esquerda.
        #
        # Negativo:
        # gira para a direita.

        angulo_girado = self.calcular_angulo_girado()

        print(
            f'Ângulo: {angulo_girado:.2f} / '
            f'{self.angulo_objetivo:.2f} graus'
        )

        # Se o objetivo for positivo, gira para a esquerda.
        if self.angulo_objetivo > 0:

            if angulo_girado < self.angulo_objetivo:
                self.girar(0.3)

            else:
                self.parar()
                self.finalizado = True

        # Se o objetivo for negativo, gira para a direita.
        else:

            if angulo_girado > self.angulo_objetivo:
                self.girar(-0.3)

            else:
                self.parar()
                self.finalizado = True

        if self.finalizado:
            print('Ângulo alcançado')

    def control(self):

        # Não movimenta o robô antes de receber
        # a primeira mensagem do Odom.
        if not self.recebeu_odom:
            self.parar()
            return

        exemplos = {
            'mostrar': self.mostrar_odom,
            'andar_distancia': self.andar_distancia,
            'chegar_em_x': self.chegar_em_x,
            'girar_angulo': self.girar_angulo
        }

        if EXEMPLO not in exemplos:
            self.parar()

            raise ValueError(
                f'Exemplo inválido: {EXEMPLO}'
            )

        exemplos[EXEMPLO]()


def main(args=None):

    rclpy.init(args=args)

    node = UsarOdom()

    rclpy.spin(node)

    # Garante que o robô pare ao encerrar.
    node.parar()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

# Para adaptar na prova, os valores principais ficam aqui:
# self.distancia_objetivo = 1.0
# self.x_objetivo = 2.0
# self.angulo_objetivo = 90.0