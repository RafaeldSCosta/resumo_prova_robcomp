import math
import numpy as np
import rclpy

from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import String


# Escolha qual código coringa será executado.
#
# Opções:
# 'basico'
# 'odom'
# 'laser'
# 'movimento'
# 'instrucoes'
# 'laser_movimento'
MODELO = 'basico'


# ============================================================
# NÓ BÁSICO
# ============================================================
#
# Use quando o professor pedir apenas para criar um nó ROS
# ou quando você quiser começar uma questão do zero.
#
# O que normalmente será substituído:
#
# 'no_basico':
# nome do nó.
#
# 0.5:
# intervalo de tempo entre cada execução do control.
#
# control:
# função onde será colocada a lógica da questão.


class NoBasico(Node):

    def __init__(self):

        # Como a classe herda de Node, precisamos inicializar Node.
        #
        # Essa linha permite utilizar publishers, subscribers,
        # timers e as outras ferramentas da ROS.
        super().__init__('no_basico')

        # Crie aqui as variáveis necessárias para a questão.
        self.contador = 0

        # Chama self.control a cada 0.5 segundo.
        #
        # Se quiser executar mais rapidamente, diminua 0.5.
        # Por exemplo: 0.1 executa dez vezes por segundo.
        self.timer = self.create_timer(
            0.5,
            self.control
        )

    def control(self):

        # Coloque aqui o que o nó precisa fazer repetidamente.
        self.contador += 1

        self.get_logger().info(
            f'Nó funcionando: {self.contador}'
        )


# ============================================================
# NÓ USANDO ODOM
# ============================================================
#
# Use quando o professor pedir:
#
# - posição do robô;
# - coordenada X ou Y;
# - orientação do robô;
# - verificar se chegou a uma posição;
# - calcular quanto o robô andou.
#
# Antes de programar, você pode conferir:
#
# ros2 topic info /odom
# ros2 interface show nav_msgs/msg/Odometry
#
# O que substituir:
#
# '/odom':
# troque se o professor fornecer outro nome de tópico.
#
# Odometry:
# troque se o tópico utilizar outro tipo de mensagem.
#
# msg.pose.pose.position.x:
# troque pelo campo que você precisa acessar.


class NoOdom(Node):

    def __init__(self):

        super().__init__('no_odom')

        # Valores atuais recebidos do Odom.
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        # Valores do ponto onde o programa começou.
        self.x_inicial = None
        self.y_inicial = None

        # Evita utilizar valores antes da primeira mensagem.
        self.recebeu_odom = False

        # Sempre que chegar uma mensagem em /odom,
        # a ROS executará self.odom_callback.
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.RELIABLE
            )
        )

        # O control utilizará os valores salvos pela callback.
        self.timer = self.create_timer(
            0.1,
            self.control
        )

    def odom_callback(self, msg: Odometry):

        # A posição do robô está nestes campos.
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        # A orientação chega como quaternion.
        orientation = msg.pose.pose.orientation

        # Para um robô andando no chão, queremos principalmente
        # o yaw, que representa a rotação ao redor do eixo Z.
        self.yaw = self.quaternion_para_yaw(orientation)

        # Guarda a posição inicial somente na primeira mensagem.
        if not self.recebeu_odom:
            self.x_inicial = self.x
            self.y_inicial = self.y
            self.recebeu_odom = True

    def quaternion_para_yaw(self, orientation):

        # Não precisa decorar essa conversão.
        # Copie esta função quando precisar descobrir o yaw.

        x = orientation.x
        y = orientation.y
        z = orientation.z
        w = orientation.w

        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)

        return math.atan2(siny_cosp, cosy_cosp)

    def control(self):

        # Não usa os dados antes de receber a primeira mensagem.
        if not self.recebeu_odom:
            return

        yaw_graus = math.degrees(self.yaw)

        print(f'X: {self.x:.2f} m')
        print(f'Y: {self.y:.2f} m')
        print(f'Yaw: {yaw_graus:.2f} graus')

        # EXEMPLO 1:
        # Se pedirem para verificar se chegou em X = 2.

        if self.x >= 2.0:
            print('O robô chegou em X = 2')

        # EXEMPLO 2:
        # Se pedirem para calcular a distância desde o início.

        diferenca_x = self.x - self.x_inicial
        diferenca_y = self.y - self.y_inicial

        distancia = math.sqrt(
            diferenca_x ** 2 +
            diferenca_y ** 2
        )

        print(f'Distância desde o início: {distancia:.2f} m')

        # EXEMPLO 3:
        # Se pedirem para verificar se andou pelo menos 1 metro.

        if distancia >= 1.0:
            print('O robô andou pelo menos 1 metro')


# ============================================================
# NÓ USANDO LASER
# ============================================================
#
# Use quando o professor pedir:
#
# - detectar obstáculos;
# - medir a distância da frente;
# - comparar esquerda e direita;
# - escolher o caminho mais livre.
#
# Antes de programar, você pode conferir:
#
# ros2 topic info /scan
# ros2 interface show sensor_msgs/msg/LaserScan
#
# No Laser utilizado na disciplina:
#
# índice 0: frente;
# índice 90: esquerda;
# índice 180: trás;
# índice 270: direita.
#
# O que substituir:
#
# '/scan':
# nome do tópico.
#
# LaserScan:
# tipo da mensagem.
#
# self.abertura:
# quantidade de leituras consideradas em cada direção.
#
# 0.5:
# distância utilizada para considerar que existe obstáculo.


class NoLaser(Node):

    def __init__(self):

        super().__init__('no_laser')

        # Quantos graus ao redor de uma direção serão analisados.
        #
        # Com abertura 10, a frente considera aproximadamente
        # 10 graus para cada lado do índice zero.
        self.abertura = 10

        # Começam como infinito porque o Laser ainda não enviou
        # nenhuma medição.
        self.frente = float('inf')
        self.esquerda = float('inf')
        self.direita = float('inf')
        self.tras = float('inf')

        self.recebeu_laser = False

        # BEST_EFFORT é o padrão utilizado para receber o Laser.
        self.laser_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.BEST_EFFORT
            )
        )

        self.timer = self.create_timer(
            0.1,
            self.control
        )

    def menor_distancia(self, medicoes):

        # Transforma as medições em um array NumPy.
        valores = np.array(medicoes, dtype=float)

        # Remove NaN e valores inválidos.
        valores = valores[np.isfinite(valores)]

        # Se não existir nenhuma leitura válida, considera
        # que não há obstáculo dentro do alcance.
        if len(valores) == 0:
            return float('inf')

        return float(np.min(valores))

    def laser_callback(self, msg: LaserScan):

        # msg.ranges é a lista com todas as distâncias medidas.
        laser = np.array(msg.ranges, dtype=float)

        abertura = self.abertura

        # A frente fica na divisão entre o começo e o final
        # da lista. Por isso, juntamos os dois pedaços.
        leituras_frente = np.concatenate(
            (
                laser[:abertura],
                laser[-abertura:]
            )
        )

        # A esquerda fica ao redor do índice 90.
        leituras_esquerda = laser[
            90 - abertura:
            90 + abertura
        ]

        # A parte de trás fica ao redor do índice 180.
        leituras_tras = laser[
            180 - abertura:
            180 + abertura
        ]

        # A direita fica ao redor do índice 270.
        leituras_direita = laser[
            270 - abertura:
            270 + abertura
        ]

        # Guarda a menor distância encontrada em cada região.
        self.frente = self.menor_distancia(leituras_frente)
        self.esquerda = self.menor_distancia(leituras_esquerda)
        self.direita = self.menor_distancia(leituras_direita)
        self.tras = self.menor_distancia(leituras_tras)

        self.recebeu_laser = True

    def control(self):

        if not self.recebeu_laser:
            return

        print(f'Frente: {self.frente:.2f} m')
        print(f'Esquerda: {self.esquerda:.2f} m')
        print(f'Direita: {self.direita:.2f} m')
        print(f'Trás: {self.tras:.2f} m')

        # EXEMPLO 1:
        # Se pedirem para detectar obstáculo na frente.

        if self.frente < 0.5:
            print('Existe um obstáculo na frente')

        # EXEMPLO 2:
        # Se pedirem para descobrir qual lado está mais livre.

        if self.esquerda > self.direita:
            print('A esquerda está mais livre')

        elif self.direita > self.esquerda:
            print('A direita está mais livre')

        else:
            print('Os dois lados possuem a mesma distância')


# ============================================================
# NÓ CONTROLANDO O ROBÔ
# ============================================================
#
# Use quando o professor pedir:
#
# - andar para frente;
# - andar para trás;
# - girar;
# - parar;
# - publicar uma velocidade.
#
# O robô recebe velocidade pelo tópico /cmd_vel.
# O tipo da mensagem é geometry_msgs/msg/Twist.
#
# O que substituir:
#
# '/cmd_vel':
# tópico onde a velocidade será publicada.
#
# 0.2:
# velocidade linear do robô.
#
# 0.3:
# velocidade angular do robô.


class NoMovimento(Node):

    def __init__(self):

        super().__init__('no_movimento')

        # Publisher que manda velocidades para o robô.
        self.vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.timer = self.create_timer(
            0.1,
            self.control
        )

    def andar(self, velocidade=0.2):

        msg = Twist()

        # Valor positivo: anda para frente.
        # Valor negativo: anda para trás.
        msg.linear.x = velocidade

        self.vel_pub.publish(msg)

    def girar(self, velocidade=0.3):

        msg = Twist()

        # Valor positivo: gira para a esquerda.
        # Valor negativo: gira para a direita.
        msg.angular.z = velocidade

        self.vel_pub.publish(msg)

    def parar(self):

        # Uma mensagem Twist vazia possui todas as
        # velocidades iguais a zero.
        msg = Twist()

        self.vel_pub.publish(msg)

    def control(self):

        # EXEMPLO 1: andar para frente.
        self.andar(0.2)

        # EXEMPLO 2: andar para trás.
        # Comente o exemplo anterior e descomente este:
        #
        # self.andar(-0.2)

        # EXEMPLO 3: girar para a esquerda.
        #
        # self.girar(0.3)

        # EXEMPLO 4: girar para a direita.
        #
        # self.girar(-0.3)

        # EXEMPLO 5: parar.
        #
        # self.parar()


# ============================================================
# NÓ RECEBENDO INSTRUÇÕES
# ============================================================
#
# Use quando existir um nó ou agente enviando comandos como:
#
# frente
# tras
# esquerda
# direita
# parar
#
# Neste exemplo, o tópico /instrucao carrega uma String.
#
# O que substituir:
#
# '/instrucao':
# troque pelo tópico informado pelo professor.
#
# String:
# troque pelo tipo descoberto com ros2 topic info.
#
# msg.data:
# troque pelo campo mostrado em ros2 interface show.


class NoInstrucoes(Node):

    def __init__(self):

        super().__init__('no_instrucoes')

        # Guarda a última instrução recebida.
        self.instrucao = ''

        # Recebe as instruções.
        self.instrucao_sub = self.create_subscription(
            String,
            '/instrucao',
            self.instrucao_callback,
            10
        )

        # Publica a velocidade para o robô.
        self.vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.timer = self.create_timer(
            0.1,
            self.control
        )

    def instrucao_callback(self, msg: String):

        # Em uma mensagem String, o texto fica em msg.data.
        self.instrucao = msg.data.lower()

        print(f'Instrução recebida: {self.instrucao}')

    def andar(self, velocidade):

        msg = Twist()
        msg.linear.x = velocidade
        self.vel_pub.publish(msg)

    def girar(self, velocidade):

        msg = Twist()
        msg.angular.z = velocidade
        self.vel_pub.publish(msg)

    def parar(self):

        msg = Twist()
        self.vel_pub.publish(msg)

    def control(self):

        # Troque os textos abaixo pelos comandos que o
        # professor ou o agente utilizar.

        if self.instrucao == 'frente':
            self.andar(0.2)

        elif self.instrucao == 'tras':
            self.andar(-0.2)

        elif self.instrucao == 'esquerda':
            self.girar(0.3)

        elif self.instrucao == 'direita':
            self.girar(-0.3)

        elif self.instrucao == 'parar':
            self.parar()


# ============================================================
# NÓ USANDO LASER E MOVIMENTO
# ============================================================
#
# Use quando o professor pedir algo como:
#
# "Ande para frente e desvie dos obstáculos."
#
# Este nó é um exemplo completo de integração:
#
# subscriber recebe o Laser;
# callback salva as distâncias;
# control toma uma decisão;
# publisher manda velocidade para o robô.
#
# O que substituir:
#
# 0.5:
# distância mínima aceita.
#
# 0.2:
# velocidade para frente.
#
# 0.3 e -0.3:
# velocidades de giro.


class NoLaserMovimento(Node):

    def __init__(self):

        super().__init__('no_laser_movimento')

        self.abertura = 10

        self.frente = float('inf')
        self.esquerda = float('inf')
        self.direita = float('inf')

        self.recebeu_laser = False

        # Subscriber que recebe o Laser.
        self.laser_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.BEST_EFFORT
            )
        )

        # Publisher que movimenta o robô.
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

        valores = np.array(medicoes, dtype=float)
        valores = valores[np.isfinite(valores)]

        if len(valores) == 0:
            return float('inf')

        return float(np.min(valores))

    def laser_callback(self, msg: LaserScan):

        laser = np.array(msg.ranges, dtype=float)
        abertura = self.abertura

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

        leituras_direita = laser[
            270 - abertura:
            270 + abertura
        ]

        self.frente = self.menor_distancia(leituras_frente)
        self.esquerda = self.menor_distancia(leituras_esquerda)
        self.direita = self.menor_distancia(leituras_direita)

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

    def control(self):

        if not self.recebeu_laser:
            self.parar()
            return

        # Se a frente estiver livre, anda.
        if self.frente >= 0.5:
            self.andar(0.2)

        # Se existe obstáculo, escolhe o lado mais livre.
        elif self.esquerda > self.direita:
            self.girar(0.3)

        else:
            self.girar(-0.3)


def main(args=None):

    rclpy.init(args=args)

    # Cada opção seleciona um código coringa diferente.
    modelos = {
        'basico': NoBasico,
        'odom': NoOdom,
        'laser': NoLaser,
        'movimento': NoMovimento,
        'instrucoes': NoInstrucoes,
        'laser_movimento': NoLaserMovimento
    }

    # Procura no dicionário a classe correspondente ao
    # texto escolhido em MODELO e cria o nó.
    node = modelos[MODELO]()

    rclpy.spin(node)

    # Ao finalizar, publica velocidade zero caso o modelo
    # possua a função parar.
    if hasattr(node, 'parar'):
        node.parar()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()