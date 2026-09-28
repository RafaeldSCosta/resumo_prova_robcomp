#!/usr/bin/env python3

import math

import rclpy

from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String


# =============================================================
# CONFIGURAÇÕES PRINCIPAIS
# =============================================================

# Velocidade para andar para frente ou para trás.
VELOCIDADE_LINEAR = 0.20

# Velocidade usada nas rotações.
VELOCIDADE_ANGULAR = 0.50

# Se a frente estiver abaixo deste valor, começa o desvio.
DISTANCIA_SEGURA_FRENTE = 0.60

# Depois de começar a desviar, somente volta a andar quando a frente
# estiver acima deste valor.
DISTANCIA_LIBERAR_FRENTE = 0.85

# Distância mínima para permitir que o robô ande para trás.
DISTANCIA_SEGURA_TRASEIRA = 0.45


class RoboComDesvio(Node):
    """
    USE QUANDO O PROFESSOR PEDIR:

    - receber comandos de outro agente;
    - verificar o laser antes de obedecer;
    - evitar obstáculos;
    - escolher entre direita e esquerda;
    - publicar o estado do robô;
    - utilizar máquina de estados.

    Fluxo:

    comando -> subscriber -> escolha do estado -> consulta ao laser
    -> decisão -> publicação em /cmd_vel
    """

    def __init__(self):
        # Inicializa o Node e define o nome do nó.
        super().__init__('robo_com_desvio_node')

        # ---------------------------------------------------------
        # VARIÁVEIS DO ROBÔ
        # ---------------------------------------------------------

        # O robô começa parado.
        self.robot_state = 'parar'

        # Guarda o movimento que será publicado em /cmd_vel.
        self.twist = Twist()

        # Guarda o último comando recebido.
        self.ultimo_comando = 'parar'

        # Indica se alguma mensagem do laser já foi recebida.
        # Antes do primeiro laser, o robô permanece parado.
        self.laser_recebido = False

        # Evita publicar repetidamente que está esperando o laser.
        self.avisou_sem_laser = False

        # Distâncias iniciais.
        # float('inf') representa uma distância ainda desconhecida.
        self.distancia_frente = float('inf')
        self.distancia_esquerda = float('inf')
        self.distancia_direita = float('inf')
        self.distancia_tras = float('inf')

        # Status que será publicado uma única vez pelo control.
        self.status_pendente = 'READY'

        # ---------------------------------------------------------
        # MÁQUINA DE ESTADOS
        # ---------------------------------------------------------

        self.state_machine = {
            'andar_frente': self.andar_frente,
            'andar_tras': self.andar_tras,
            'girar_direita': self.girar_direita,
            'girar_esquerda': self.girar_esquerda,
            'desviar_direita': self.desviar_direita,
            'desviar_esquerda': self.desviar_esquerda,
            'parar': self.parar,
        }

        # Mensagem recebida -> estado correspondente.
        #
        # Se o professor usar outras palavras, altere este dicionário.
        self.comandos = {
            'frente': 'andar_frente',
            'andar': 'andar_frente',
            'avancar': 'andar_frente',
            'avançar': 'andar_frente',

            'tras': 'andar_tras',
            'trás': 'andar_tras',
            'voltar': 'andar_tras',
            'recuar': 'andar_tras',

            'direita': 'girar_direita',
            'girar direita': 'girar_direita',

            'esquerda': 'girar_esquerda',
            'girar esquerda': 'girar_esquerda',

            'parar': 'parar',
            'pare': 'parar',
            'stop': 'parar',
        }

        # ---------------------------------------------------------
        # PUBLISHERS
        # ---------------------------------------------------------

        # Publica a velocidade do robô.
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Publica respostas para o agente.
        self.status_pub = self.create_publisher(
            String,
            '/status_robo',
            10
        )

        # ---------------------------------------------------------
        # SUBSCRIBERS
        # ---------------------------------------------------------

        # Recebe comandos enviados pelo agente.
        self.comando_sub = self.create_subscription(
            String,
            '/comando_robo',
            self.receber_comando,
            10
        )

        # Recebe todas as medidas do laser.
        self.laser_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.receber_laser,
            10
        )

        # ---------------------------------------------------------
        # TIMER
        # ---------------------------------------------------------

        # Chama control dez vezes por segundo.
        self.timer = self.create_timer(0.1, self.control)

        self.get_logger().info('Robô com desvio iniciado.')
        self.get_logger().info('Esperando comandos e dados do laser.')

    # =============================================================
    # CALLBACK DO COMANDO
    # =============================================================

    def receber_comando(self, msg):
        """
        Recebe a instrução enviada pelo agente.

        Esta função não publica em /cmd_vel.
        Ela apenas escolhe o próximo estado.
        """

        # Para std_msgs/String, o texto fica em msg.data.
        #
        # Se a mensagem da prova possuir um campo chamado instrucao:
        # comando = msg.instrucao.strip().lower()
        comando = msg.data.strip().lower()

        self.get_logger().info(
            f'Comando recebido: "{comando}"'
        )

        if comando in self.comandos:
            novo_estado = self.comandos[comando]

            self.robot_state = novo_estado
            self.ultimo_comando = comando

            if novo_estado == 'parar':
                self.status_pendente = 'DONE: robô parado'
            else:
                self.status_pendente = f'IN_PROGRESS: {comando}'

        else:
            # Segurança: qualquer comando desconhecido para o robô.
            self.robot_state = 'parar'
            self.ultimo_comando = comando
            self.status_pendente = (
                f'ERROR: comando desconhecido: {comando}'
            )

            self.get_logger().warning(
                f'Comando desconhecido: "{comando}".'
            )

    # =============================================================
    # CALLBACK DO LASER
    # =============================================================

    def receber_laser(self, msg):
        """
        Recebe a mensagem LaserScan e separa quatro regiões:

        - frente;
        - esquerda;
        - direita;
        - traseira.

        Cada variável guarda a menor distância encontrada no setor.
        """

        self.distancia_frente = self.menor_distancia_setor(
            msg=msg,
            angulo_central=0.0,
            abertura_graus=30.0
        )

        self.distancia_esquerda = self.menor_distancia_setor(
            msg=msg,
            angulo_central=math.pi / 2,
            abertura_graus=50.0
        )

        self.distancia_direita = self.menor_distancia_setor(
            msg=msg,
            angulo_central=-math.pi / 2,
            abertura_graus=50.0
        )

        self.distancia_tras = self.menor_distancia_setor(
            msg=msg,
            angulo_central=math.pi,
            abertura_graus=30.0
        )

        self.laser_recebido = True
        self.avisou_sem_laser = False

    def menor_distancia_setor(
        self,
        msg,
        angulo_central,
        abertura_graus
    ):
        """
        Retorna a menor distância dentro de uma região do laser.

        Parâmetros:

        msg:
            Mensagem LaserScan completa.

        angulo_central:
            Direção central da região, em radianos.

            0       = frente
            pi/2    = esquerda
            -pi/2   = direita
            pi      = traseira

        abertura_graus:
            Largura total da região analisada.
        """

        meia_abertura = math.radians(abertura_graus / 2)

        distancias_validas = []

        for indice, distancia in enumerate(msg.ranges):
            # Calcula o ângulo correspondente àquela posição da lista.
            angulo = msg.angle_min + indice * msg.angle_increment

            # Calcula a diferença angular normalizada entre -pi e pi.
            diferenca = math.atan2(
                math.sin(angulo - angulo_central),
                math.cos(angulo - angulo_central)
            )

            # Verifica se o raio pertence ao setor desejado.
            if abs(diferenca) <= meia_abertura:
                # NaN não representa uma medida válida.
                if math.isnan(distancia):
                    continue

                # Alguns lasers usam infinito quando não existe obstáculo.
                if math.isinf(distancia):
                    distancia = msg.range_max

                # Descarta valores menores que o limite físico do sensor.
                if distancia >= msg.range_min:
                    distancias_validas.append(distancia)

        # Se nenhuma medida válida for encontrada, consideramos range_max.
        if not distancias_validas:
            return msg.range_max

        return min(distancias_validas)

    # =============================================================
    # FUNÇÕES AUXILIARES DE SEGURANÇA
    # =============================================================

    def pode_movimentar(self):
        """
        Verifica se o laser já enviou alguma mensagem.

        O robô não deve se movimentar usando distâncias desconhecidas.
        """

        if self.laser_recebido:
            return True

        self.twist = Twist()

        if not self.avisou_sem_laser:
            self.status_pendente = 'WAITING: aguardando o laser'
            self.avisou_sem_laser = True

        return False

    def escolher_lado_do_desvio(self):
        """
        Compara esquerda e direita e retorna o lado mais livre.
        """

        if self.distancia_esquerda >= self.distancia_direita:
            return 'desviar_esquerda'

        return 'desviar_direita'

    # =============================================================
    # ESTADOS DO ROBÔ
    # =============================================================

    def andar_frente(self):
        """
        Anda para frente somente se o caminho estiver livre.

        Se existir um obstáculo, escolhe o lado mais livre.
        """

        self.twist = Twist()

        if not self.pode_movimentar():
            return

        if self.distancia_frente >= DISTANCIA_SEGURA_FRENTE:
            # Caminho livre: anda normalmente.
            self.twist.linear.x = VELOCIDADE_LINEAR
            self.twist.angular.z = 0.0
            return

        # Existe um obstáculo à frente.
        lado_escolhido = self.escolher_lado_do_desvio()

        self.robot_state = lado_escolhido
        self.status_pendente = (
            f'DESVIANDO: obstáculo a '
            f'{self.distancia_frente:.2f} m'
        )

        # Executa imediatamente o novo estado para não esperar
        # a próxima chamada do timer.
        self.state_machine[self.robot_state]()

    def andar_tras(self):
        """
        Anda para trás somente se a região traseira estiver livre.
        """

        self.twist = Twist()

        if not self.pode_movimentar():
            return

        if self.distancia_tras >= DISTANCIA_SEGURA_TRASEIRA:
            self.twist.linear.x = -VELOCIDADE_LINEAR
            self.twist.angular.z = 0.0
            return

        # Obstáculo traseiro: interrompe o movimento.
        self.robot_state = 'parar'
        self.twist = Twist()

        self.status_pendente = (
            f'BLOCKED: obstáculo traseiro a '
            f'{self.distancia_tras:.2f} m'
        )

    def girar_direita(self):
        """
        Gira no sentido horário.

        Como linear.x é zero, o robô gira sem avançar.
        """

        self.twist = Twist()
        self.twist.linear.x = 0.0
        self.twist.angular.z = -VELOCIDADE_ANGULAR

    def girar_esquerda(self):
        """
        Gira no sentido anti-horário.
        """

        self.twist = Twist()
        self.twist.linear.x = 0.0
        self.twist.angular.z = VELOCIDADE_ANGULAR

    def desviar_direita(self):
        """
        Gira para a direita até a frente ficar livre.
        """

        self.twist = Twist()

        if not self.pode_movimentar():
            return

        # Quando a frente estiver suficientemente livre,
        # o robô volta ao estado andar_frente.
        if self.distancia_frente >= DISTANCIA_LIBERAR_FRENTE:
            self.robot_state = 'andar_frente'
            self.status_pendente = 'IN_PROGRESS: caminho liberado'

            # Já começa a andar nesta mesma chamada.
            self.andar_frente()
            return

        self.twist.linear.x = 0.0
        self.twist.angular.z = -VELOCIDADE_ANGULAR

    def desviar_esquerda(self):
        """
        Gira para a esquerda até a frente ficar livre.
        """

        self.twist = Twist()

        if not self.pode_movimentar():
            return

        if self.distancia_frente >= DISTANCIA_LIBERAR_FRENTE:
            self.robot_state = 'andar_frente'
            self.status_pendente = 'IN_PROGRESS: caminho liberado'

            self.andar_frente()
            return

        self.twist.linear.x = 0.0
        self.twist.angular.z = VELOCIDADE_ANGULAR

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
        Publica o status uma vez e depois limpa a variável.
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
    # CONTROLE PRINCIPAL
    # =============================================================

    def control(self):
        """
        Executa o estado atual e publica a velocidade.

        Esta é a única função que publica em /cmd_vel.
        """

        funcao_do_estado = self.state_machine[self.robot_state]
        funcao_do_estado()

        self.cmd_vel_pub.publish(self.twist)

        self.publicar_status_pendente()

    def parar_antes_de_fechar(self):
        """
        Para o robô antes de destruir o nó.
        """

        self.robot_state = 'parar'
        self.status_pendente = None
        self.control()


def main(args=None):
    rclpy.init(args=args)

    node = RoboComDesvio()

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