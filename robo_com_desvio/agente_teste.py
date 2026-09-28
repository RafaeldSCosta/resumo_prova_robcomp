#!/usr/bin/env python3

import rclpy

from rclpy.node import Node
from std_msgs.msg import String


class AgenteTeste(Node):
    """
    Simula o agente do professor.

    O agente envia comandos ao robô e recebe os status publicados.

    Na prova, este arquivo pode ser substituído pelo agente já existente
    no simulador.
    """

    def __init__(self):
        super().__init__('agente_teste_desvio_node')

        # ---------------------------------------------------------
        # COMANDOS DE TESTE
        # ---------------------------------------------------------

        # Altere esta lista para testar outros comportamentos.
        self.comandos = [
            'frente',
            'parar',
            'direita',
            'parar',
            'frente',
            'parar',
            'esquerda',
            'parar',
            'tras',
            'parar',
        ]

        self.indice = 0

        # Tempo entre os comandos.
        self.intervalo = 4.0

        # ---------------------------------------------------------
        # PUBLISHER E SUBSCRIBER
        # ---------------------------------------------------------

        self.comando_pub = self.create_publisher(
            String,
            '/comando_robo',
            10
        )

        self.status_sub = self.create_subscription(
            String,
            '/status_robo',
            self.receber_status,
            10
        )

        self.timer = self.create_timer(
            self.intervalo,
            self.enviar_proximo_comando
        )

        self.get_logger().info('Agente de teste iniciado.')

    def enviar_proximo_comando(self):
        """
        Publica os comandos da lista, um de cada vez.
        """

        if self.indice >= len(self.comandos):
            self.timer.cancel()

            self.get_logger().info(
                'Sequência de comandos finalizada.'
            )
            return

        comando = self.comandos[self.indice]

        msg = String()
        msg.data = comando

        self.comando_pub.publish(msg)

        self.get_logger().info(
            f'Comando enviado: "{comando}"'
        )

        self.indice += 1

    def receber_status(self, msg):
        """
        Exibe as respostas enviadas pelo robô.
        """

        self.get_logger().info(
            f'Resposta do robô: "{msg.data}"'
        )


def main(args=None):
    rclpy.init(args=args)

    node = AgenteTeste()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        node.get_logger().info('Encerrando o agente...')

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()