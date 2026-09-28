import rclpy
import numpy as np

from rclpy.node import Node
from rclpy.qos import ReliabilityPolicy, QoSProfile
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

# Adicione os imports necessários:
# from std_msgs.msg import String
# from robcomp_interfaces.msg import GameStatus


class BaseControlNode(Node):

    def __init__(self):
        super().__init__('node_name_here')

        self.robot_state = 'inicio'

        self.state_machine = {
            'inicio': self.inicio,
            'andar': self.andar,
            'esperar': self.esperar,
            'girar_direita': self.girar_direita,
            'girar_esquerda': self.girar_esquerda,
            'finalizar': self.finalizar,
            'done': self.done
        }

        self.estados_clientes = []

        # Inicialização das variáveis
        self.twist = Twist()

        self.frente = float('inf')
        self.direita = float('inf')
        self.esquerda = float('inf')

        self.parede_frente = False
        self.giro_terminou = False
        self.mensagem_inicial_enviada = False

        # QoS dos sensores
        qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT
        )

        # Subscribers
        self.laser_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            qos
        )

        # Adicione o subscriber de comunicação:
        #
        # self.comunicacao_sub = self.create_subscription(
        #     TipoDaMensagem,
        #     '/nome_do_topico',
        #     self.comunicacao_callback,
        #     10
        # )

        # Publishers
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Adicione o publisher de comunicação:
        #
        # self.comunicacao_pub = self.create_publisher(
        #     TipoDaMensagem,
        #     '/nome_do_topico',
        #     10
        # )

        # Timer
        self.timer = self.create_timer(
            0.1,
            self.control
        )

    # ---------------------------------------------------------
    # CALLBACKS
    # ---------------------------------------------------------

    def laser_callback(self, msg):
        # Atualize aqui as distâncias:
        #
        # self.frente = ...
        # self.direita = ...
        # self.esquerda = ...

        # Exemplo:
        # self.parede_frente = self.frente < 0.5

        pass

    def comunicacao_callback(self, msg):
        # Receba e processe aqui as mensagens.
        #
        # A callback pode alterar self.robot_state,
        # mas não deve publicar em /cmd_vel.

        pass

    # ---------------------------------------------------------
    # ESTADOS
    # ---------------------------------------------------------

    def inicio(self):
        if not self.mensagem_inicial_enviada:
            # Monte e publique aqui a mensagem inicial:
            #
            # mensagem = TipoDaMensagem()
            # mensagem.status = 'READY'
            # mensagem.player_name = 'Julia Mendes Huber'
            # self.comunicacao_pub.publish(mensagem)

            self.mensagem_inicial_enviada = True

        self.twist = Twist()
        self.robot_state = 'andar'

    def andar(self):
        if self.parede_frente:
            self.twist = Twist()
            self.robot_state = 'esperar'

        else:
            self.twist.linear.x = 0.2
            self.twist.angular.z = 0.0

    def esperar(self):
        self.twist = Twist()

        # Uma callback pode alterar o próximo estado:
        #
        # self.robot_state = 'girar_direita'
        # self.robot_state = 'girar_esquerda'
        # self.robot_state = 'andar'
        # self.robot_state = 'finalizar'

    def girar_direita(self):
        if self.giro_terminou:
            self.twist = Twist()
            self.giro_terminou = False
            self.robot_state = 'andar'

        else:
            self.twist.linear.x = 0.0
            self.twist.angular.z = -0.5

    def girar_esquerda(self):
        if self.giro_terminou:
            self.twist = Twist()
            self.giro_terminou = False
            self.robot_state = 'andar'

        else:
            self.twist.linear.x = 0.0
            self.twist.angular.z = 0.5

    def finalizar(self):
        self.twist = Twist()
        self.robot_state = 'done'

    def done(self):
        self.twist = Twist()

    # ---------------------------------------------------------
    # NÃO ALTERAR
    # ---------------------------------------------------------

    def control(self):
        print(f'Estado Atual: {self.robot_state}')
        self.state_machine[self.robot_state]()

        if self.robot_state not in self.estados_clientes:
            self.cmd_vel_pub.publish(self.twist)



def main(args=None):
    rclpy.init(args=args) # Inicia o ROS2

    ros_node = JogadorSimon() # Cria o nó

    while not ros_node.robot_state == 'done':
        rclpy.spin_once(ros_node)

    ros_node.destroy_node() # Destroi o nó
    rclpy.shutdown() # Encerra o ROS2


if __name__ == '__main__':
    main()