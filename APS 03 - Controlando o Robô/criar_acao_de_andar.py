import rclpy

from rclpy.node import Node
from geometry_msgs.msg import Twist


# Distância utilizada se este arquivo for executado sozinho.
#
# Positivo:
# anda para frente.
#
# Negativo:
# anda para trás.
DISTANCIA_TESTE = 1.0


class Andar(Node):

    # ============================================================
    # AÇÃO DE ANDAR
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - criar uma ação para o robô;
    # - andar determinada distância;
    # - criar uma tarefa com início, meio e fim;
    # - criar uma ação que possa ser chamada por outro código;
    # - controlar o movimento usando tempo e velocidade.
    #
    # COMO FUNCIONA:
    #
    # A distância é calculada por:
    #
    # distância = velocidade × tempo
    #
    # Portanto:
    #
    # tempo = distância / velocidade
    #
    # Exemplo:
    #
    # Para andar 1 metro com velocidade 0.2 m/s:
    #
    # tempo = 1 / 0.2
    # tempo = 5 segundos
    #
    # ESTADOS:
    #
    # done:
    # ação parada, esperando alguém chamar reset().
    #
    # andar:
    # envia velocidade para o robô.
    #
    # stop:
    # zera a velocidade e finaliza a ação.

    def __init__(self):

        super().__init__('andar_node')

        # O timer começa desligado.
        #
        # Ele será criado quando reset() iniciar a ação.
        self.timer = None

        # A ação começa como finalizada.
        self.robot_state = 'done'

        # Relaciona cada estado com sua função.
        self.state_machine = {
            'andar': self.andar,
            'stop': self.stop,
            'done': self.done
        }

        # Velocidade padrão do robô.
        #
        # Na prova, troque se o enunciado pedir
        # outra velocidade.
        self.velocidade = 0.2

        # Variáveis preenchidas quando reset for chamado.
        self.distancia = 0.0
        self.tempo_necessario = 0.0
        self.tempo_inicial = None
        self.tempo_decorrido = 0.0

        # Guarda a velocidade que será publicada.
        self.twist = Twist()

        # Publisher que controla o robô.
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

    def reset(self, distancia):

        # reset inicia ou reinicia a ação.
        #
        # O código que quiser fazer o robô andar chama:
        #
        # self.acao_andar.reset(2.0)
        #
        # Isso significa:
        # andar 2 metros.

        self.twist = Twist()

        self.distancia = distancia

        # Calcula quanto tempo o robô precisa andar.
        #
        # Usamos abs para o tempo sempre ficar positivo.
        self.tempo_necessario = (
            abs(self.distancia) / self.velocidade
        )

        # Guarda o horário em que a ação começou.
        self.tempo_inicial = self.get_clock().now()

        self.tempo_decorrido = 0.0

        # Inicia a ação no estado andar.
        self.robot_state = 'andar'

        # Cria o timer somente se ele ainda não existir.
        if self.timer is None:

            self.timer = self.create_timer(
                0.1,
                self.control
            )

        print(
            f'\nIniciando ação: andar '
            f'{self.distancia:.2f} m'
        )

        print(
            f'Tempo necessário: '
            f'{self.tempo_necessario:.2f} s'
        )

    def andar(self):

        # Distância positiva:
        # anda para frente.
        if self.distancia >= 0:
            self.twist.linear.x = self.velocidade

        # Distância negativa:
        # anda para trás.
        else:
            self.twist.linear.x = -self.velocidade

        # Pega o horário atual.
        tempo_atual = self.get_clock().now()

        # Subtrair dois horários gera uma duração.
        duracao = tempo_atual - self.tempo_inicial

        # Converte nanossegundos para segundos.
        self.tempo_decorrido = (
            duracao.nanoseconds / 1_000_000_000
        )

        print(
            f'Tempo: {self.tempo_decorrido:.2f} / '
            f'{self.tempo_necessario:.2f} s'
        )

        # Quando o tempo necessário acabar,
        # muda para o estado stop.
        if (
            self.tempo_decorrido
            >= self.tempo_necessario
        ):
            self.twist.linear.x = 0.0
            self.robot_state = 'stop'

    def stop(self):

        # Zera todas as velocidades.
        self.twist = Twist()

        print('Parando o robô')

        # Cancela o timer da ação.
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None

        # Indica que a ação terminou.
        self.robot_state = 'done'

    def done(self):

        # Mantém a velocidade zerada enquanto
        # a ação não for iniciada novamente.
        self.twist = Twist()

    def control(self):

        print(
            f'Estado da ação: {self.robot_state}'
        )

        # Executa a função correspondente ao estado atual.
        self.state_machine[self.robot_state]()

        # Apenas control publica no /cmd_vel.
        #
        # Isso evita que diferentes funções publiquem
        # velocidades conflitantes.
        self.cmd_vel_pub.publish(self.twist)


def main(args=None):

    rclpy.init(args=args)

    node = Andar()

    # Inicia a ação com a distância definida no começo.
    node.reset(DISTANCIA_TESTE)

    # Continua processando a ação enquanto ela
    # não estiver finalizada.
    while (
        rclpy.ok()
        and node.robot_state != 'done'
    ):
        rclpy.spin_once(node)

    # Garante uma última publicação com velocidade zero.
    node.control()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()