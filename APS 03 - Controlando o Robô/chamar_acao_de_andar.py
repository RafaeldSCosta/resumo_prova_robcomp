import rclpy

from rclpy.node import Node
from geometry_msgs.msg import Twist

# Este import considera que os dois arquivos estão
# dentro do pacote prova_ai.
#
# Se o pacote tiver outro nome, troque prova_ai.
from prova_ai.criar_acao_de_andar import Andar


class ChamarAcaoDeAndar(Node):

    # ============================================================
    # CHAMANDO A AÇÃO DE ANDAR
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - utilizar a ação de andar;
    # - iniciar uma ação criada em outro arquivo;
    # - criar um nó principal que gerencia ações;
    # - executar uma ação e esperar até ela terminar;
    # - passar uma distância para a ação.
    #
    # COMO FUNCIONA:
    #
    # Este código cria um objeto da classe Andar.
    #
    # Depois chama:
    #
    # self.acao_andar.reset(distancia)
    #
    # Enquanto a ação está funcionando, este código
    # executa spin_once no nó da ação.
    #
    # Quando a ação chega ao estado done,
    # este controlador continua para o próximo estado.
    #
    # IMPORTANTE:
    #
    # Durante o estado chamar_andar, somente a ação
    # publica velocidade no /cmd_vel.
    #
    # O controlador não pode publicar ao mesmo tempo,
    # pois os comandos poderiam entrar em conflito.

    def __init__(self):

        super().__init__('chamar_acao_de_andar')

        # Cria o nó responsável pela ação.
        self.acao_andar = Andar()

        # Distância que será enviada para a ação.
        #
        # Troque pelo valor pedido no enunciado.
        self.distancia_desejada = 1.0

        # Estado inicial do controlador.
        self.robot_state = 'chamar_andar'

        self.state_machine = {
            'chamar_andar': self.chamar_andar,
            'outra_tarefa': self.outra_tarefa,
            'done': self.done
        }

        # Estados nos quais outro nó controla o robô.
        #
        # Enquanto estiver em chamar_andar,
        # a classe Andar possui o controle do /cmd_vel.
        self.estados_controlados_por_acao = [
            'chamar_andar'
        ]

        self.twist = Twist()

        # Este publisher será utilizado somente quando
        # o controlador estiver fora da ação.
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.timer = self.create_timer(
            0.1,
            self.control
        )

    def chamar_andar(self):

        # Se a ação está em done, ela ainda não começou
        # ou já terminou.
        #
        # Como o controlador ainda está neste estado,
        # significa que precisamos iniciá-la.
        if self.acao_andar.robot_state == 'done':

            print('\nIniciando a ação de andar')

            # Processa possíveis callbacks pendentes.
            rclpy.spin_once(
                self.acao_andar,
                timeout_sec=0.0
            )

            # Inicia a ação e informa a distância.
            self.acao_andar.reset(
                self.distancia_desejada
            )

        # Permite que o timer e as funções da ação
        # sejam executados.
        rclpy.spin_once(
            self.acao_andar,
            timeout_sec=0.0
        )

        # Depois do spin_once, verificamos novamente.
        #
        # Se chegou em done, a ação terminou.
        if self.acao_andar.robot_state == 'done':

            # Garante que a velocidade seja zerada.
            self.acao_andar.control()

            print('Ação de andar finalizada')

            # Depois de andar, vai para outra tarefa.
            self.robot_state = 'outra_tarefa'

    def outra_tarefa(self):

        # EXEMPLO:
        #
        # Depois que a ação terminar, o controlador
        # pode executar qualquer outra coisa.
        #
        # Na prova, substitua pelo próximo comportamento.
        print('Executando a próxima tarefa')

        # Neste exemplo, apenas finalizamos.
        self.robot_state = 'done'

    def done(self):

        # Mantém o robô parado.
        self.twist = Twist()

    def control(self):

        print(
            f'Estado do controlador: {self.robot_state}'
        )

        # Executa o estado atual.
        self.state_machine[self.robot_state]()

        # O controlador só publica se a ação não estiver
        # controlando o robô.
        if (
            self.robot_state
            not in self.estados_controlados_por_acao
        ):
            self.cmd_vel_pub.publish(self.twist)


def main(args=None):

    rclpy.init(args=args)

    node = ChamarAcaoDeAndar()

    while (
        rclpy.ok()
        and node.robot_state != 'done'
    ):
        rclpy.spin_once(node)

    # Publica velocidade zero antes de encerrar.
    node.control()

    node.acao_andar.destroy_node()
    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()