import math
import cv2
import numpy as np
import rclpy

from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from std_msgs.msg import String, Int32
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan, Image
from cv_bridge import CvBridge


# Escolha qual exemplo deseja executar.
#
# Opções:
#
# 'instrucao_movimento'
# 'laser_movimento'
# 'odom_movimento'
# 'imagem_quantidade'
EXEMPLO = 'instrucao_movimento'


# Coloque False se não quiser abrir a janela da imagem.
MOSTRAR_IMAGEM = True


# ============================================================
# RECEBER INSTRUÇÃO E MOVIMENTAR O ROBÔ
# ============================================================
#
# USE QUANDO O PROFESSOR PEDIR:
#
# - receber uma instrução de outro nó;
# - receber uma instrução produzida por um agente;
# - transformar palavras em movimentos;
# - movimentar o robô dependendo da mensagem recebida;
# - fazer o robô executar "frente", "trás", "direita" ou "parar".
#
# COMO FUNCIONA:
#
# O subscriber recebe uma String pelo tópico /instrucao.
#
# A callback salva o texto em self.instrucao.
#
# A função control verifica o texto recebido.
#
# O publisher envia uma mensagem Twist para /cmd_vel.
#
# FLUXO:
#
# /instrucao
#      ↓
# instrucao_callback
#      ↓
# self.instrucao
#      ↓
# control
#      ↓
# /cmd_vel
#
# O QUE VOCÊ PODE PRECISAR TROCAR:
#
# - o tópico de entrada '/instrucao';
# - o tipo String;
# - o campo msg.data;
# - os textos das instruções;
# - as velocidades;
# - o tópico de saída '/cmd_vel'.


class InstrucaoMovimento(Node):

    def __init__(self):

        super().__init__('instrucao_movimento')

        # Começa sem nenhuma instrução.
        self.instrucao = ''

        # SUBSCRIBER:
        # recebe as instruções.
        self.instrucao_sub = self.create_subscription(
            String,
            '/instrucao',
            self.instrucao_callback,
            10
        )

        # PUBLISHER:
        # envia velocidade para o robô.
        self.vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Executa control dez vezes por segundo.
        self.timer = self.create_timer(
            0.1,
            self.control
        )

    def instrucao_callback(self, msg: String):

        # String guarda o texto no campo data.
        #
        # lower transforma o texto em letras minúsculas.
        # Assim, "FRENTE" e "frente" serão tratados igualmente.
        self.instrucao = msg.data.lower()

        self.get_logger().info(
            f'Instrução recebida: {self.instrucao}'
        )

    def control(self):

        # Cria uma mensagem com todas as velocidades zeradas.
        #
        # Se nenhuma condição for atendida,
        # o robô continuará parado.
        velocidade = Twist()

        if self.instrucao == 'frente':

            velocidade.linear.x = 0.2

        elif self.instrucao == 'tras':

            velocidade.linear.x = -0.2

        elif self.instrucao == 'esquerda':

            velocidade.angular.z = 0.3

        elif self.instrucao == 'direita':

            velocidade.angular.z = -0.3

        elif self.instrucao == 'parar':

            # Twist vazio significa velocidade zero.
            pass

        else:

            # Instrução vazia ou desconhecida:
            # mantém o robô parado.
            pass

        self.vel_pub.publish(velocidade)


# ============================================================
# RECEBER LASER E MOVIMENTAR O ROBÔ
# ============================================================
#
# USE QUANDO O PROFESSOR PEDIR:
#
# - andar sem bater;
# - detectar um obstáculo e desviar;
# - parar antes de um obstáculo;
# - escolher o lado mais livre;
# - usar o Laser para controlar o movimento.
#
# COMO FUNCIONA:
#
# O subscriber recebe LaserScan pelo tópico /scan.
#
# A callback calcula:
#
# - distância da frente;
# - distância da esquerda;
# - distância da direita.
#
# A função control toma a decisão.
#
# O publisher envia Twist para /cmd_vel.
#
# FLUXO:
#
# /scan
#      ↓
# laser_callback
#      ↓
# frente, esquerda e direita
#      ↓
# control
#      ↓
# /cmd_vel
#
# O QUE VOCÊ PODE PRECISAR TROCAR:
#
# - a abertura analisada;
# - a distância mínima segura;
# - a velocidade para frente;
# - a velocidade de giro;
# - a regra usada para escolher o lado.


class LaserMovimento(Node):

    def __init__(self):

        super().__init__('laser_movimento')

        # Quantos graus serão analisados ao redor
        # de cada direção.
        self.abertura = 10

        # Distância mínima permitida na frente.
        self.distancia_seguranca = 0.5

        # As distâncias começam como infinito porque
        # ainda não recebemos o Laser.
        self.frente = float('inf')
        self.esquerda = float('inf')
        self.direita = float('inf')

        self.recebeu_laser = False

        # SUBSCRIBER:
        # recebe as medições do Laser.
        self.laser_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.BEST_EFFORT
            )
        )

        # PUBLISHER:
        # envia velocidades para o robô.
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

        # Converte para array NumPy.
        valores = np.array(
            medicoes,
            dtype=float
        )

        # No robô real, zero pode significar
        # que o sensor não conseguiu medir.
        valores[valores == 0] = np.inf

        # Remove valores NaN.
        valores = valores[~np.isnan(valores)]

        if len(valores) == 0:
            return float('inf')

        return float(np.min(valores))

    def laser_callback(self, msg: LaserScan):

        laser = np.array(
            msg.ranges,
            dtype=float
        )

        laser[laser == 0] = np.inf

        abertura = self.abertura

        # O índice zero representa a frente.
        #
        # A frente fica dividida entre o começo
        # e o final da lista.
        leituras_frente = np.concatenate(
            (
                laser[:abertura],
                laser[-abertura:]
            )
        )

        # Aproximadamente 90 graus:
        # lado esquerdo.
        leituras_esquerda = laser[
            90 - abertura:
            90 + abertura
        ]

        # Aproximadamente 270 graus:
        # lado direito.
        leituras_direita = laser[
            270 - abertura:
            270 + abertura
        ]

        self.frente = self.menor_distancia(
            leituras_frente
        )

        self.esquerda = self.menor_distancia(
            leituras_esquerda
        )

        self.direita = self.menor_distancia(
            leituras_direita
        )

        self.recebeu_laser = True

    def control(self):

        velocidade = Twist()

        # Antes de receber o Laser, publica velocidade zero.
        if not self.recebeu_laser:
            self.vel_pub.publish(velocidade)
            return

        # Se a frente estiver livre, anda.
        if self.frente >= self.distancia_seguranca:

            velocidade.linear.x = 0.2

            self.get_logger().info(
                f'Frente livre: {self.frente:.2f} m'
            )

        # Se encontrou obstáculo e a esquerda
        # está mais livre, gira para a esquerda.
        elif self.esquerda > self.direita:

            velocidade.angular.z = 0.3

            self.get_logger().info(
                'Obstáculo: girando para a esquerda'
            )

        # Se a direita estiver mais livre,
        # gira para a direita.
        else:

            velocidade.angular.z = -0.3

            self.get_logger().info(
                'Obstáculo: girando para a direita'
            )

        self.vel_pub.publish(velocidade)


# ============================================================
# RECEBER ODOM E MOVIMENTAR O ROBÔ
# ============================================================
#
# USE QUANDO O PROFESSOR PEDIR:
#
# - andar uma distância específica;
# - parar depois de percorrer determinada distância;
# - chegar a uma coordenada;
# - usar a posição para controlar o robô;
# - executar um movimento e verificar o resultado pelo Odom.
#
# COMO FUNCIONA:
#
# O subscriber recebe Odometry pelo tópico /odom.
#
# A callback salva a posição atual do robô.
#
# A distância é calculada usando a posição inicial
# e a posição atual.
#
# A função control manda o robô andar enquanto
# a distância for menor que o objetivo.
#
# Quando atingir a distância, publica Twist vazio
# e o robô para.
#
# FLUXO:
#
# /odom
#      ↓
# odom_callback
#      ↓
# posição e distância
#      ↓
# control
#      ↓
# /cmd_vel
#
# O QUE VOCÊ PODE PRECISAR TROCAR:
#
# - a distância desejada;
# - a velocidade;
# - o tópico do Odom;
# - a condição usada para parar;
# - usar X ou Y no lugar da distância total.


class OdomMovimento(Node):

    def __init__(self):

        super().__init__('odom_movimento')

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.x_inicial = None
        self.y_inicial = None

        self.distancia_percorrida = 0.0

        # Na prova, troque pela distância pedida.
        self.distancia_objetivo = 1.0

        self.recebeu_odom = False
        self.finalizado = False

        # SUBSCRIBER:
        # recebe a posição do robô.
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.RELIABLE
            )
        )

        # PUBLISHER:
        # manda velocidade para o robô.
        self.vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.timer = self.create_timer(
            0.1,
            self.control
        )

    def quaternion_para_yaw(self, orientation):

        x = orientation.x
        y = orientation.y
        z = orientation.z
        w = orientation.w

        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)

        return math.atan2(
            siny_cosp,
            cosy_cosp
        )

    def odom_callback(self, msg: Odometry):

        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        orientation = msg.pose.pose.orientation

        self.yaw = self.quaternion_para_yaw(
            orientation
        )

        # Guarda a posição inicial somente
        # na primeira mensagem recebida.
        if not self.recebeu_odom:

            self.x_inicial = self.x
            self.y_inicial = self.y

            self.recebeu_odom = True

        # Calcula a distância entre o ponto inicial
        # e a posição atual.
        diferenca_x = self.x - self.x_inicial
        diferenca_y = self.y - self.y_inicial

        self.distancia_percorrida = math.sqrt(
            diferenca_x ** 2 +
            diferenca_y ** 2
        )

    def control(self):

        velocidade = Twist()

        # Não anda antes de receber a posição inicial.
        if not self.recebeu_odom:
            self.vel_pub.publish(velocidade)
            return

        # Se ainda não chegou ao objetivo,
        # anda para frente.
        if (
            self.distancia_percorrida
            < self.distancia_objetivo
        ):

            velocidade.linear.x = 0.2

            self.get_logger().info(
                f'Distância: '
                f'{self.distancia_percorrida:.2f} m'
            )

        # Quando chegar, mantém velocidade zero.
        else:

            if not self.finalizado:
                self.get_logger().info(
                    'Distância alcançada. Robô parado.'
                )

                self.finalizado = True

        self.vel_pub.publish(velocidade)

        # OUTRO EXEMPLO:
        #
        # Se o professor pedir para parar em X = 2,
        # substitua a condição anterior por:
        #
        # if self.x < 2.0:
        #     velocidade.linear.x = 0.2
        # else:
        #     velocidade.linear.x = 0.0


# ============================================================
# RECEBER IMAGEM E PUBLICAR QUANTIDADE DE OBJETOS
# ============================================================
#
# USE QUANDO O PROFESSOR PEDIR:
#
# - receber uma imagem;
# - identificar objetos;
# - contar objetos;
# - calcular a área dos objetos;
# - publicar a quantidade encontrada;
# - transformar o resultado da visão em uma mensagem ROS.
#
# COMO FUNCIONA:
#
# O subscriber recebe Image da câmera.
#
# CvBridge transforma a mensagem em imagem OpenCV.
#
# O código cria uma máscara para a cor vermelha.
#
# Os contornos são encontrados.
#
# Os objetos com área maior que 100 são contados.
#
# O publisher envia a quantidade no tópico:
#
# /quantidade_objetos
#
# FLUXO:
#
# /camera/image_raw
#      ↓
# imagem_callback
#      ↓
# segmentação e contagem
#      ↓
# mensagem Int32
#      ↓
# /quantidade_objetos
#
# O QUE VOCÊ PODE PRECISAR TROCAR:
#
# - o tópico da câmera;
# - a cor procurada;
# - os limites inferior e superior do HSV;
# - a área mínima;
# - o tópico onde a quantidade será publicada;
# - o tipo da informação publicada.


class ImagemQuantidade(Node):

    def __init__(self):

        super().__init__('imagem_quantidade')

        # Converte ROS Image para OpenCV e vice-versa.
        self.bridge = CvBridge()

        # SUBSCRIBER:
        # recebe a imagem da câmera.
        self.imagem_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.imagem_callback,
            QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.BEST_EFFORT
            )
        )

        # PUBLISHER:
        # publica a quantidade de objetos.
        self.quantidade_pub = self.create_publisher(
            Int32,
            '/quantidade_objetos',
            10
        )

    def imagem_callback(self, msg: Image):

        # Converte a mensagem para imagem OpenCV.
        imagem = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8'
        )

        # Converte a imagem de BGR para HSV.
        imagem_hsv = cv2.cvtColor(
            imagem,
            cv2.COLOR_BGR2HSV
        )

        # Limites usados para encontrar objetos vermelhos.
        #
        # O vermelho aparece em duas regiões do HSV.
        vermelho_baixo_1 = np.array(
            [0, 100, 100]
        )

        vermelho_alto_1 = np.array(
            [10, 255, 255]
        )

        vermelho_baixo_2 = np.array(
            [170, 100, 100]
        )

        vermelho_alto_2 = np.array(
            [179, 255, 255]
        )

        mascara_1 = cv2.inRange(
            imagem_hsv,
            vermelho_baixo_1,
            vermelho_alto_1
        )

        mascara_2 = cv2.inRange(
            imagem_hsv,
            vermelho_baixo_2,
            vermelho_alto_2
        )

        mascara = cv2.bitwise_or(
            mascara_1,
            mascara_2
        )

        # Encontra os contornos.
        contornos, _ = cv2.findContours(
            mascara,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        quantidade = 0

        for contorno in contornos:

            area = cv2.contourArea(contorno)

            # Ignora manchas pequenas.
            if area > 100:

                quantidade += 1

                x, y, largura, altura = cv2.boundingRect(
                    contorno
                )

                # Desenha uma caixa ao redor do objeto.
                cv2.rectangle(
                    imagem,
                    (x, y),
                    (x + largura, y + altura),
                    (0, 255, 0),
                    2
                )

                # Mostra a área daquele objeto.
                cv2.putText(
                    imagem,
                    f'Area: {area:.0f}',
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

        # Cria a mensagem com a quantidade encontrada.
        quantidade_msg = Int32()

        quantidade_msg.data = quantidade

        # Publica a quantidade.
        self.quantidade_pub.publish(
            quantidade_msg
        )

        self.get_logger().info(
            f'Quantidade publicada: {quantidade}'
        )

        # Escreve a quantidade na imagem.
        cv2.putText(
            imagem,
            f'Quantidade: {quantidade}',
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        if MOSTRAR_IMAGEM:

            cv2.imshow(
                'Objetos encontrados',
                imagem
            )

            cv2.imshow(
                'Mascara',
                mascara
            )

            cv2.waitKey(1)


def main(args=None):

    # Inicia a ROS 2.
    rclpy.init(args=args)

    # Relaciona cada exemplo com sua classe.
    exemplos = {
        'instrucao_movimento': InstrucaoMovimento,
        'laser_movimento': LaserMovimento,
        'odom_movimento': OdomMovimento,
        'imagem_quantidade': ImagemQuantidade
    }

    if EXEMPLO not in exemplos:
        raise ValueError(
            f'Exemplo inválido: {EXEMPLO}'
        )

    # Cria somente o exemplo escolhido.
    node = exemplos[EXEMPLO]()

    # Mantém subscribers, publishers e timers funcionando.
    rclpy.spin(node)

    # Fecha possíveis janelas do OpenCV.
    cv2.destroyAllWindows()

    # Encerra o nó.
    node.destroy_node()

    # Encerra a ROS 2.
    rclpy.shutdown()


if __name__ == '__main__':
    main()