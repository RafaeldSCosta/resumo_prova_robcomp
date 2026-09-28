#!/usr/bin/env python3

import rclpy

from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String


class RoboComandado(Node):
    """
    USE QUANDO O PROFESSOR PEDIR:

    - receber comandos enviados por outro nó;
    - fazer o robô obedecer instruções;
    - usar publisher e subscriber no mesmo programa;
    - publicar o estado do robô;
    - controlar o robô usando uma máquina de estados.

    Este exemplo usa String para os comandos e para o status.

    Na prova, verifique se o professor forneceu outro tipo de mensagem.
    Se forneceu, altere o import, o tipo do subscriber e os campos da mensagem.
    """

    def __init__(self):
        # Inicializa a classe Node e define o nome deste nó na ROS 2.
        super().__init__('robo_comandado_node')

        # ---------------------------------------------------------
        # VARIÁVEIS DE CONTROLE
        # ---------------------------------------------------------

        # Estado inicial: o robô começa parado.
        self.robot_state = 'parar'

        # Guarda o último comando recebido.
        self.ultimo_comando = 'parar'

        # Twist guarda a velocidade linear e angular do robô.
        self.twist = Twist()

        # Guarda uma mensagem de status que ainda precisa ser publicada.
        # Depois da publicação, esta variável volta a ser None.
        # Isso evita publicar READY ou DONE infinitamente.
        self.status_pendente = 'READY'

        # ---------------------------------------------------------
        # MÁQUINA DE ESTADOS
        # ---------------------------------------------------------

        # Cada texto corresponde a uma função.
        #
        # Não coloque parênteses depois das funções aqui.
        # Correto:   self.andar_frente
        # Incorreto: self.andar_frente()
        self.state_machine = {
            'andar_frente': self.andar_frente,
            'andar_tras': self.andar_tras,
            'girar_direita': self.girar_direita,
            'girar_esquerda': self.girar_esquerda,
            'parar': self.parar,
        }

        # ---------------------------------------------------------
        # DICIONÁRIO DE COMANDOS
        # ---------------------------------------------------------

        # O lado esquerdo é a mensagem que pode chegar pelo tópico.
        # O lado direito é o estado que será ativado.
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

        # Publica a velocidade que controla o robô.
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Publica mensagens para informar ao agente o estado do robô.
        self.status_pub = self.create_publisher(
            String,
            '/status_robo',
            10
        )

        # ---------------------------------------------------------
        # SUBSCRIBER
        # ---------------------------------------------------------

        # Recebe comandos enviados por outro agente.
        #
        # SE O PROFESSOR MUDAR:
        # 1. troque String pelo tipo correto;
        # 2. troque '/comando_robo' pelo tópico correto;
        # 3. altere msg.data dentro de receber_comando().
        self.comando_sub = self.create_subscription(
            String,
            '/comando_robo',
            self.receber_comando,
            10
        )

        # ---------------------------------------------------------
        # TIMER
        # ---------------------------------------------------------

        # Chama control a cada 0.1 segundo.
        # É control que publica em /cmd_vel.
        self.timer = self.create_timer(0.1, self.control)

        self.get_logger().info('Robô comandado iniciado.')
        self.get_logger().info('Esperando comandos em /comando_robo.')

    # =============================================================
    # CALLBACK DO SUBSCRIBER
    # =============================================================

    def receber_comando(self, msg):
        """
        Esta função é chamada automaticamente quando chega uma mensagem.

        Ela NÃO publica em /cmd_vel.

        A função somente:
        1. lê a mensagem;
        2. identifica o estado correspondente;
        3. troca robot_state;
        4. prepara uma resposta para o agente.
        """

        # Para String, o conteúdo fica em msg.data.
        #
        # Se a mensagem da prova tiver um campo chamado instrucao:
        # comando = msg.instrucao
        #
        # Se possuir um campo chamado comando:
        # comando = msg.comando
        comando = msg.data.strip().lower()

        self.get_logger().info(
            f'Comando recebido: "{comando}"'
        )

        # Verifica se o comando recebido existe no dicionário.
        if comando in self.comandos:
            # Descobre qual estado corresponde ao comando.
            novo_estado = self.comandos[comando]

            self.robot_state = novo_estado
            self.ultimo_comando = comando

            # O status será publicado uma vez no próximo control().
            if novo_estado == 'parar':
                self.status_pendente = 'DONE: robô parado'
            else:
                self.status_pendente = f'IN_PROGRESS: {comando}'

        else:
            # Comando desconhecido: o comportamento mais seguro é parar.
            self.robot_state = 'parar'
            self.ultimo_comando = comando
            self.status_pendente = f'ERROR: comando desconhecido: {comando}'

            self.get_logger().warning(
                f'Comando desconhecido: "{comando}". Robô será parado.'
            )

    # =============================================================
    # ESTADOS DO ROBÔ
    # =============================================================

    def andar_frente(self):
        """
        Faz o robô andar para frente.

        linear.x positivo = frente.
        """

        # Criar um Twist novo evita manter uma velocidade antiga.
        self.twist = Twist()

        # SE O PROFESSOR PEDIR OUTRA VELOCIDADE:
        # altere somente este valor.
        self.twist.linear.x = 0.2

        # Sem rotação.
        self.twist.angular.z = 0.0

    def andar_tras(self):
        """
        Faz o robô andar para trás.

        linear.x negativo = trás.
        """

        self.twist = Twist()

        # Velocidade negativa faz o robô recuar.
        self.twist.linear.x = -0.2
        self.twist.angular.z = 0.0

    def girar_direita(self):
        """
        Faz o robô girar para a direita.

        angular.z negativo = sentido horário.
        """

        self.twist = Twist()

        # Não anda para frente enquanto gira.
        self.twist.linear.x = 0.0

        # Valor negativo gira para a direita.
        self.twist.angular.z = -0.5

    def girar_esquerda(self):
        """
        Faz o robô girar para a esquerda.

        angular.z positivo = sentido anti-horário.
        """

        self.twist = Twist()

        self.twist.linear.x = 0.0

        # Valor positivo gira para a esquerda.
        self.twist.angular.z = 0.5

    def parar(self):
        """
        Zera todas as velocidades.

        Use Twist vazio para garantir que linear e angular sejam zero.
        """

        self.twist = Twist()

    # =============================================================
    # PUBLICAÇÃO DE STATUS
    # =============================================================

    def publicar_status_pendente(self):
        """
        Publica o status somente quando existe uma mensagem nova.

        Isso evita o problema de publicar READY, DONE ou ERROR
        dez vezes por segundo.
        """

        if self.status_pendente is None:
            return

        status_msg = String()
        status_msg.data = self.status_pendente

        self.status_pub.publish(status_msg)

        self.get_logger().info(
            f'Status publicado: "{status_msg.data}"'
        )

        # Apaga o status depois de publicar.
        self.status_pendente = None

    # =============================================================
    # CONTROLE PRINCIPAL
    # =============================================================

    def control(self):
        """
        Esta função é chamada pelo timer.

        Ela é a única função que publica em /cmd_vel.
        """

        # Procura a função correspondente ao estado atual e executa.
        funcao_do_estado = self.state_machine[self.robot_state]
        funcao_do_estado()

        # Publica a velocidade preparada pela função do estado.
        self.cmd_vel_pub.publish(self.twist)

        # Publica uma eventual resposta para o agente.
        self.publicar_status_pendente()

    def parar_antes_de_fechar(self):
        """
        Garante que o robô receba velocidade zero antes de fechar o nó.

        Chamamos control para manter a regra de que apenas control
        publica em /cmd_vel.
        """

        self.robot_state = 'parar'
        self.status_pendente = None
        self.control()


def main(args=None):
    # Inicializa a ROS 2.
    rclpy.init(args=args)

    # Cria o nó.
    node = RoboComandado()

    try:
        # Mantém o nó executando e processando callbacks e timers.
        rclpy.spin(node)

    except KeyboardInterrupt:
        # Permite fechar com Ctrl+C.
        node.get_logger().info('Encerrando o nó...')

    finally:
        # Para o robô antes de destruir o nó.
        node.parar_antes_de_fechar()

        # Destrói o nó.
        node.destroy_node()

        # Encerra a ROS 2.
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()