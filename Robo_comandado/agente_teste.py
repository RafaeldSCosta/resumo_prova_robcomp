#!/usr/bin/env python3

import rclpy

from rclpy.node import Node
from std_msgs.msg import String


class AgenteTeste(Node):
    """
    Este nó simula o agente ou orquestrador do professor.

    Ele publica comandos em /comando_robo e recebe as respostas
    publicadas pelo robô em /status_robo.

    Na prova, provavelmente o simulador já terá um agente próprio.
    Portanto, este arquivo serve principalmente para testar o pacote.
    """

    def __init__(self):
        super().__init__('agente_teste_node')

        # ---------------------------------------------------------
        # CONFIGURAÇÃO DO TESTE
        # ---------------------------------------------------------

        # Comandos que serão enviados, na ordem.
        #
        # Você pode alterar esta lista para testar outros comandos.
        self.comandos = [
            'frente',
            'parar',
            'esquerda',
            'parar',
            'tras',
            'parar',
            'direita',
            'parar',
        ]

        # Posição atual na lista.
        self.indice = 0

        # Intervalo entre os comandos, em segundos.
        self.intervalo = 3.0

        # ---------------------------------------------------------
        # PUBLISHER
        # ---------------------------------------------------------

        # Envia comandos ao robô.
        self.comando_pub = self.create_publisher(
            String,
            '/comando_robo',
            10
        )

        # ---------------------------------------------------------
        # SUBSCRIBER
        # ---------------------------------------------------------

        # Recebe as respostas enviadas pelo robô.
        self.status_sub = self.create_subscription(
            String,
            '/status_robo',
            self.receber_status,
            10
        )

        # Chama enviar_proximo_comando a cada intervalo.
        self.timer = self.create_timer(
            self.intervalo,
            self.enviar_proximo_comando
        )

        self.get_logger().info('Agente de teste iniciado.')
        self.get_logger().info(
            f'Um comando será enviado a cada {self.intervalo} segundos.'
        )

    def enviar_proximo_comando(self):
        """
        Envia o próximo comando da lista.

        Quando todos os comandos forem enviados, cancela o timer
        para não repetir a sequência.
        """

        # Verifica se todos os comandos já foram enviados.
        if self.indice >= len(self.comandos):
            self.timer.cancel()

            self.get_logger().info(
                'Todos os comandos foram enviados.'
            )
            return

        # Pega o próximo texto da lista.
        comando_atual = self.comandos[self.indice]

        # Cria a mensagem String.
        msg = String()
        msg.data = comando_atual

        # Publica a mensagem.
        self.comando_pub.publish(msg)

        self.get_logger().info(
            f'Comando enviado: "{comando_atual}"'
        )

        # Prepara o índice do próximo comando.
        self.indice += 1

    def receber_status(self, msg):
        """
        É chamada quando o robô publica uma resposta.
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
        node.get_logger().info('Encerrando o agente de teste...')

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()