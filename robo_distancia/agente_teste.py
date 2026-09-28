#!/usr/bin/env python3

import rclpy

from rclpy.node import Node
from std_msgs.msg import Float64
from std_msgs.msg import String


class AgenteTeste(Node):
    """
    Simula o agente do professor.

    Envia uma distância e espera o robô publicar DONE antes de
    enviar a próxima.

    Isso é melhor do que utilizar um intervalo fixo, porque movimentos
    maiores levam mais tempo para terminar.
    """

    def __init__(self):
        super().__init__('agente_teste_distancia_node')

        # ---------------------------------------------------------
        # DISTÂNCIAS DE TESTE
        # ---------------------------------------------------------

        # Positivo = frente.
        # Negativo = trás.
        self.distancias = [
            1.0,
            -0.5,
            0.75,
        ]

        self.indice = 0

        # Indica se existe um movimento em andamento.
        self.aguardando_resultado = False

        # ---------------------------------------------------------
        # PUBLISHER
        # ---------------------------------------------------------

        self.distancia_pub = self.create_publisher(
            Float64,
            '/distancia_desejada',
            10
        )

        # ---------------------------------------------------------
        # SUBSCRIBER
        # ---------------------------------------------------------

        self.status_sub = self.create_subscription(
            String,
            '/status_distancia',
            self.receber_status,
            10
        )

        # Verifica periodicamente se pode mandar o próximo objetivo.
        self.timer = self.create_timer(
            2.0,
            self.verificar_proximo_objetivo
        )

        self.get_logger().info('Agente de teste iniciado.')

    def verificar_proximo_objetivo(self):
        """
        Envia a próxima distância somente quando o robô não estiver
        executando a anterior.
        """

        if self.aguardando_resultado:
            return

        if self.indice >= len(self.distancias):
            self.timer.cancel()

            self.get_logger().info(
                'Todos os objetivos foram concluídos.'
            )
            return

        distancia = self.distancias[self.indice]

        msg = Float64()
        msg.data = distancia

        self.distancia_pub.publish(msg)

        self.get_logger().info(
            f'Distância enviada: {distancia:.3f} m'
        )

        self.indice += 1
        self.aguardando_resultado = True

    def receber_status(self, msg):
        """
        Recebe READY, IN_PROGRESS, DONE ou ERROR.
        """

        status = msg.data

        self.get_logger().info(
            f'Resposta do robô: "{status}"'
        )

        # Quando o robô terminar ou encontrar um erro,
        # permite o envio do próximo objetivo.
        if status.startswith('DONE'):
            self.aguardando_resultado = False

        elif status.startswith('ERROR'):
            self.aguardando_resultado = False


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