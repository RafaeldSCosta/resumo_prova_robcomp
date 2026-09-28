#!/usr/bin/env python3

import math

import rclpy

from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Float64
from std_msgs.msg import String


# =============================================================
# CONFIGURAÇÕES
# =============================================================

# Velocidade usada durante a maior parte do movimento.
VELOCIDADE_NORMAL = 0.20

# Velocidade usada quando o robô está próximo do objetivo.
VELOCIDADE_APROXIMACAO = 0.08

# Quando faltar menos que este valor, o robô reduz a velocidade.
DISTANCIA_PARA_REDUZIR = 0.15

# Erro de distância aceito para considerar que terminou.
TOLERANCIA = 0.03


class RoboDistancia(Node):
    """
    USE QUANDO O PROFESSOR PEDIR:

    - receber uma distância por tópico;
    - andar para frente ou para trás;
    - medir o deslocamento usando Odom;
    - parar quando atingir a distância;
    - avisar outro nó quando terminar.

    Mensagem positiva:
        anda para frente.

    Mensagem negativa:
        anda para trás.
    """

    def __init__(self):
        # Inicializa a classe Node.
        super().__init__('robo_distancia_node')

        # ---------------------------------------------------------
        # ESTADO DO ROBÔ
        # ---------------------------------------------------------

        # O robô começa parado.
        self.robot_state = 'parar'

        # Twist que será publicado em /cmd_vel.
        self.twist = Twist()

        # Máquina de estados.
        self.state_machine = {
            'andar_distancia': self.andar_distancia,
            'parar': self.parar,
        }

        # ---------------------------------------------------------
        # DADOS DA ODOM
        # ---------------------------------------------------------

        # Indica se uma mensagem de Odom já chegou.
        self.odom_recebida = False

        # Posição atual do robô.
        self.x_atual = 0.0
        self.y_atual = 0.0

        # Posição em que o movimento começou.
        self.x_inicial = 0.0
        self.y_inicial = 0.0

        # ---------------------------------------------------------
        # DADOS DO OBJETIVO
        # ---------------------------------------------------------

        # Distância recebida pelo tópico, mantendo o sinal.
        self.distancia_com_sinal = 0.0

        # Distância que realmente precisa ser percorrida.
        self.distancia_objetivo = 0.0

        # Distância calculada desde o começo do movimento.
        self.distancia_percorrida = 0.0

        # Direção do movimento:
        # 1.0  = frente
        # -1.0 = trás
        self.direcao = 1.0

        # Se uma distância chegar antes da Odom, ela fica guardada aqui.
        self.distancia_pendente = None

        # Status que ainda precisa ser publicado.
        self.status_pendente = 'READY'

        # ---------------------------------------------------------
        # PUBLISHERS
        # ---------------------------------------------------------

        # Publica a velocidade do robô.
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Publica READY, IN_PROGRESS, DONE ou ERROR.
        self.status_pub = self.create_publisher(
            String,
            '/status_distancia',
            10
        )

        # ---------------------------------------------------------
        # SUBSCRIBERS
        # ---------------------------------------------------------

        # Recebe a distância desejada.
        #
        # Se o professor usar uma mensagem personalizada:
        # 1. troque Float64 pelo tipo correto;
        # 2. troque o nome do tópico;
        # 3. substitua msg.data pelo campo correto.
        self.distancia_sub = self.create_subscription(
            Float64,
            '/distancia_desejada',
            self.receber_distancia,
            10
        )

        # Recebe a posição do robô.
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.receber_odom,
            10
        )

        # ---------------------------------------------------------
        # TIMER
        # ---------------------------------------------------------

        # Chama control dez vezes por segundo.
        self.timer = self.create_timer(0.1, self.control)

        self.get_logger().info('Robô de distância iniciado.')
        self.get_logger().info(
            'Esperando uma distância em /distancia_desejada.'
        )

    # =============================================================
    # CALLBACK DA ODOM
    # =============================================================

    def receber_odom(self, msg):
        """
        Atualiza a posição X e Y do robô.

        Na mensagem Odometry, a posição fica em:

        msg.pose.pose.position.x
        msg.pose.pose.position.y
        """

        self.x_atual = msg.pose.pose.position.x
        self.y_atual = msg.pose.pose.position.y

        primeira_odom = not self.odom_recebida
        self.odom_recebida = True

        if primeira_odom:
            self.get_logger().info('Primeira Odom recebida.')

        # Se uma distância chegou antes da primeira Odom,
        # começamos o movimento agora.
        if self.distancia_pendente is not None:
            distancia = self.distancia_pendente
            self.distancia_pendente = None

            self.iniciar_movimento(distancia)

    # =============================================================
    # CALLBACK DA DISTÂNCIA
    # =============================================================

    def receber_distancia(self, msg):
        """
        Recebe a distância enviada pelo agente.

        Para Float64, o número fica em msg.data.
        """

        # Se a mensagem personalizada tiver um campo distancia:
        # distancia = float(msg.distancia)
        distancia = float(msg.data)

        self.get_logger().info(
            f'Distância recebida: {distancia:.3f} m'
        )

        # Não podemos salvar a posição inicial antes de receber Odom.
        if not self.odom_recebida:
            self.distancia_pendente = distancia
            self.robot_state = 'parar'

            self.status_pendente = (
                'WAITING: distância recebida, aguardando Odom'
            )

            self.get_logger().warning(
                'Aguardando a primeira mensagem de /odom.'
            )
            return

        self.iniciar_movimento(distancia)

    # =============================================================
    # INICIAR MOVIMENTO
    # =============================================================

    def iniciar_movimento(self, distancia):
        """
        Prepara todas as variáveis para um novo movimento.

        Se chegar uma nova distância enquanto o robô estiver andando,
        o objetivo anterior é cancelado e o novo começa da posição atual.
        """

        self.distancia_com_sinal = distancia
        self.distancia_objetivo = abs(distancia)

        # Salva a posição atual como início.
        self.x_inicial = self.x_atual
        self.y_inicial = self.y_atual

        self.distancia_percorrida = 0.0

        # Distância negativa significa andar para trás.
        if distancia < 0:
            self.direcao = -1.0
        else:
            self.direcao = 1.0

        # Se a distância for praticamente zero, não precisa andar.
        if self.distancia_objetivo <= TOLERANCIA:
            self.robot_state = 'parar'
            self.status_pendente = 'DONE: distância igual a zero'
            return

        self.robot_state = 'andar_distancia'

        self.status_pendente = (
            f'IN_PROGRESS: objetivo = {distancia:.3f} m'
        )

        self.get_logger().info(
            f'Iniciando movimento de {distancia:.3f} m.'
        )

    # =============================================================
    # CALCULAR DISTÂNCIA
    # =============================================================

    def calcular_distancia_percorrida(self):
        """
        Calcula a distância entre a posição inicial e a posição atual.

        Fórmula:
            sqrt(delta_x² + delta_y²)
        """

        delta_x = self.x_atual - self.x_inicial
        delta_y = self.y_atual - self.y_inicial

        return math.sqrt(delta_x ** 2 + delta_y ** 2)

    # =============================================================
    # ESTADOS
    # =============================================================

    def andar_distancia(self):
        """
        Anda até atingir a distância solicitada.
        """

        self.twist = Twist()

        # Segurança: não movimenta sem Odom.
        if not self.odom_recebida:
            self.robot_state = 'parar'
            self.status_pendente = 'ERROR: Odom indisponível'
            return

        self.distancia_percorrida = (
            self.calcular_distancia_percorrida()
        )

        distancia_restante = (
            self.distancia_objetivo
            - self.distancia_percorrida
        )

        # Se chegou suficientemente perto, finaliza.
        if distancia_restante <= TOLERANCIA:
            self.robot_state = 'parar'

            self.status_pendente = (
                f'DONE: percorreu '
                f'{self.distancia_percorrida:.3f} m'
            )

            self.get_logger().info(
                f'Objetivo concluído. Percorrido: '
                f'{self.distancia_percorrida:.3f} m'
            )

            # Zera a velocidade nesta mesma execução.
            self.parar()
            return

        # Diminui a velocidade quando está próximo do objetivo.
        if distancia_restante <= DISTANCIA_PARA_REDUZIR:
            velocidade = VELOCIDADE_APROXIMACAO
        else:
            velocidade = VELOCIDADE_NORMAL

        # A direção é positiva para frente e negativa para trás.
        self.twist.linear.x = self.direcao * velocidade
        self.twist.angular.z = 0.0

    def parar(self):
        """
        Zera todas as velocidades.
        """

        self.twist = Twist()

    # =============================================================
    # STATUS
    # =============================================================

    def publicar_status_pendente(self):
        """
        Publica cada mudança de status somente uma vez.
        """

        if self.status_pendente is None:
            return

        msg = String()
        msg.data = self.status_pendente

        self.status_pub.publish(msg)

        self.get_logger().info(
            f'Status publicado: "{msg.data}"'
        )

        self.status_pendente = None

    # =============================================================
    # CONTROLE
    # =============================================================

    def control(self):
        """
        Executa o estado atual.

        Esta é a única função que publica em /cmd_vel.
        """

        funcao_do_estado = self.state_machine[self.robot_state]
        funcao_do_estado()

        self.cmd_vel_pub.publish(self.twist)

        self.publicar_status_pendente()

    def parar_antes_de_fechar(self):
        """
        Para o robô antes de encerrar.
        """

        self.robot_state = 'parar'
        self.status_pendente = None
        self.control()


def main(args=None):
    rclpy.init(args=args)

    node = RoboDistancia()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        node.get_logger().info('Encerrando o nó...')

    finally:
        node.parar_antes_de_fechar()
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()