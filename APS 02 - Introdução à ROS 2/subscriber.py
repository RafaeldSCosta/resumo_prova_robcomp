import math
import cv2
import numpy as np
import rclpy

from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from std_msgs.msg import String, Bool, Int32, Float64
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan, Image
from cv_bridge import CvBridge


# Escolha qual subscriber deseja executar.
#
# Opções:
#
# 'string'
# 'dados'
# 'twist'
# 'odom'
# 'laser'
# 'imagem'
EXEMPLO = 'string'


# Coloque False se não quiser abrir a janela da câmera.
MOSTRAR_IMAGEM = True


# ============================================================
# SUBSCRIBER DE STRING
# ============================================================
#
# USE QUANDO O PROFESSOR PEDIR:
#
# - receber uma palavra ou frase;
# - receber uma instrução de outro nó;
# - receber comandos como "frente", "direita" ou "parar";
# - receber o nome de um objeto;
# - receber uma resposta produzida por um agente;
# - executar uma ação dependendo do texto recebido.
#
# PARA QUE SERVE:
#
# Este subscriber recebe textos publicados em um tópico.
#
# Sempre que uma nova mensagem chegar, a ROS executará
# automaticamente a função instrucao_callback.
#
# DE ONDE RECEBE:
#
# Neste exemplo, recebe do tópico:
#
# /instrucao
#
# ONDE ESTÁ A INFORMAÇÃO:
#
# Em mensagens String, o texto fica em:
#
# msg.data
#
# O QUE VOCÊ PODE PRECISAR TROCAR:
#
# - o tópico '/instrucao';
# - o tipo String;
# - o nome da callback;
# - os textos utilizados nas condições;
# - as ações executadas para cada instrução.


class SubscriberString(Node):

    def __init__(self):

        super().__init__('subscriber_string')

        # Guarda a última instrução recebida.
        self.instrucao = ''

        # Cria o subscriber.
        #
        # String:
        # tipo da mensagem recebida.
        #
        # '/instrucao':
        # tópico que será acompanhado.
        #
        # self.instrucao_callback:
        # função executada quando uma mensagem chegar.
        #
        # 10:
        # tamanho da fila de mensagens.
        self.subscription = self.create_subscription(
            String,
            '/instrucao',
            self.instrucao_callback,
            10
        )

    def instrucao_callback(self, msg: String):

        # Pega o texto recebido.
        self.instrucao = msg.data.lower()

        self.get_logger().info(
            f'Instrução recebida: {self.instrucao}'
        )

        # EXEMPLO PRÁTICO:
        # escolhe uma ação dependendo do texto recebido.

        if self.instrucao == 'frente':
            print('O robô deve andar para frente')

        elif self.instrucao == 'tras':
            print('O robô deve andar para trás')

        elif self.instrucao == 'esquerda':
            print('O robô deve girar para a esquerda')

        elif self.instrucao == 'direita':
            print('O robô deve girar para a direita')

        elif self.instrucao == 'parar':
            print('O robô deve parar')

        else:
            print('Instrução desconhecida')


# ============================================================
# SUBSCRIBER DE BOOL, INT32 E FLOAT64
# ============================================================
#
# USE QUANDO O PROFESSOR PEDIR:
#
# - receber se uma tarefa terminou;
# - receber uma condição verdadeira ou falsa;
# - receber uma quantidade de objetos;
# - receber uma contagem;
# - receber uma distância;
# - receber uma área;
# - receber qualquer número inteiro ou decimal.
#
# PARA QUE SERVE:
#
# Este subscriber recebe valores simples publicados
# por outros nós.
#
# Bool:
# recebe True ou False.
#
# Int32:
# recebe um número inteiro.
#
# Float64:
# recebe um número decimal.
#
# DE ONDE RECEBE:
#
# Neste exemplo:
#
# Bool recebe de /tarefa_finalizada.
# Int32 recebe de /quantidade_objetos.
# Float64 recebe de /distancia_objeto.
#
# ONDE ESTÁ A INFORMAÇÃO:
#
# Nos três tipos, o valor fica em:
#
# msg.data
#
# O QUE VOCÊ PODE PRECISAR TROCAR:
#
# - o tipo da mensagem;
# - o nome do tópico;
# - o nome da callback;
# - a condição que utiliza o valor recebido.


class SubscriberDados(Node):

    def __init__(self):

        super().__init__('subscriber_dados')

        self.finalizado = False
        self.quantidade = 0
        self.distancia = 0.0

        # Recebe True ou False.
        self.bool_sub = self.create_subscription(
            Bool,
            '/tarefa_finalizada',
            self.bool_callback,
            10
        )

        # Recebe números inteiros.
        self.int_sub = self.create_subscription(
            Int32,
            '/quantidade_objetos',
            self.int_callback,
            10
        )

        # Recebe números decimais.
        self.float_sub = self.create_subscription(
            Float64,
            '/distancia_objeto',
            self.float_callback,
            10
        )

    def bool_callback(self, msg: Bool):

        self.finalizado = msg.data

        if self.finalizado:
            print('A tarefa terminou')

        else:
            print('A tarefa ainda está acontecendo')

    def int_callback(self, msg: Int32):

        self.quantidade = msg.data

        print(
            f'Quantidade recebida: {self.quantidade}'
        )

        # Exemplo:
        # verificar se encontrou pelo menos cinco objetos.
        if self.quantidade >= 5:
            print('Foram encontrados pelo menos 5 objetos')

    def float_callback(self, msg: Float64):

        self.distancia = msg.data

        print(
            f'Distância recebida: {self.distancia:.2f} m'
        )

        # Exemplo:
        # verificar se o objeto está próximo.
        if self.distancia < 0.5:
            print('O objeto está próximo')


# ============================================================
# SUBSCRIBER DE TWIST
# ============================================================
#
# USE QUANDO O PROFESSOR PEDIR:
#
# - receber uma velocidade;
# - acompanhar os comandos enviados ao robô;
# - descobrir se o robô está andando ou girando;
# - monitorar o tópico /cmd_vel;
# - salvar ou analisar o movimento comandado.
#
# PARA QUE SERVE:
#
# Este subscriber recebe comandos de velocidade.
#
# Ele não movimenta o robô.
#
# Ele apenas observa as mensagens que algum publisher
# está enviando para o tópico.
#
# DE ONDE RECEBE:
#
# Normalmente, recebe do tópico:
#
# /cmd_vel
#
# ONDE ESTÁ A INFORMAÇÃO:
#
# Velocidade linear:
#
# msg.linear.x
#
# Velocidade angular:
#
# msg.angular.z
#
# O QUE VOCÊ PODE PRECISAR TROCAR:
#
# - o tópico;
# - as velocidades analisadas;
# - as condições usadas para identificar o movimento.


class SubscriberTwist(Node):

    def __init__(self):

        super().__init__('subscriber_twist')

        self.velocidade_linear = 0.0
        self.velocidade_angular = 0.0

        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.velocidade_callback,
            10
        )

    def velocidade_callback(self, msg: Twist):

        self.velocidade_linear = msg.linear.x
        self.velocidade_angular = msg.angular.z

        print(
            f'Linear: {self.velocidade_linear:.2f} | '
            f'Angular: {self.velocidade_angular:.2f}'
        )

        # Verifica se o robô está parado.
        if (
            self.velocidade_linear == 0.0
            and self.velocidade_angular == 0.0
        ):
            print('O robô está parado')

        # Verifica se está andando para frente.
        elif (
            self.velocidade_linear > 0.0
            and self.velocidade_angular == 0.0
        ):
            print('O robô está andando para frente')

        # Verifica se está andando para trás.
        elif (
            self.velocidade_linear < 0.0
            and self.velocidade_angular == 0.0
        ):
            print('O robô está andando para trás')

        # Verifica se está girando para a esquerda.
        elif self.velocidade_angular > 0.0:
            print('O robô está girando para a esquerda')

        # Verifica se está girando para a direita.
        elif self.velocidade_angular < 0.0:
            print('O robô está girando para a direita')


# ============================================================
# SUBSCRIBER DE ODOMETRY
# ============================================================
#
# USE QUANDO O PROFESSOR PEDIR:
#
# - descobrir a posição atual do robô;
# - acessar as coordenadas X e Y;
# - descobrir para onde o robô está virado;
# - calcular quanto o robô andou;
# - verificar se o robô chegou a uma posição;
# - verificar se o robô girou determinado ângulo.
#
# PARA QUE SERVE:
#
# Este subscriber recebe a estimativa da posição,
# da orientação e da velocidade do robô.
#
# O simulador atualiza essas informações enquanto
# o robô se movimenta.
#
# DE ONDE RECEBE:
#
# Normalmente, recebe do tópico:
#
# /odom
#
# O tipo da mensagem é:
#
# nav_msgs/msg/Odometry
#
# ONDE ESTÁ A INFORMAÇÃO:
#
# Posição:
#
# msg.pose.pose.position.x
# msg.pose.pose.position.y
#
# Orientação:
#
# msg.pose.pose.orientation
#
# Velocidade:
#
# msg.twist.twist.linear.x
# msg.twist.twist.angular.z
#
# O QUE VOCÊ PODE PRECISAR TROCAR:
#
# - o tópico;
# - a coordenada analisada;
# - a posição desejada;
# - a distância que o robô deve percorrer;
# - o ângulo que o robô deve atingir.


class SubscriberOdom(Node):

    def __init__(self):

        super().__init__('subscriber_odom')

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.x_inicial = None
        self.y_inicial = None

        self.recebeu_odom = False

        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.RELIABLE
            )
        )

    def quaternion_para_yaw(self, orientation):

        # Converte a orientação de quaternion para yaw.
        #
        # Não precisa decorar essa fórmula.
        # Use este bloco sempre que precisar do ângulo do robô.

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

        # Pega a posição atual.
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        # Pega a orientação em quaternion.
        orientation = msg.pose.pose.orientation

        # Converte a orientação para yaw.
        self.yaw = self.quaternion_para_yaw(
            orientation
        )

        # Guarda a posição inicial apenas uma vez.
        if not self.recebeu_odom:
            self.x_inicial = self.x
            self.y_inicial = self.y
            self.recebeu_odom = True

        # Converte o ângulo para graus.
        yaw_graus = math.degrees(self.yaw)

        print(f'X: {self.x:.2f} m')
        print(f'Y: {self.y:.2f} m')
        print(f'Yaw: {yaw_graus:.2f} graus')

        # Calcula a distância entre a posição inicial
        # e a posição atual.
        diferenca_x = self.x - self.x_inicial
        diferenca_y = self.y - self.y_inicial

        distancia = math.sqrt(
            diferenca_x ** 2 +
            diferenca_y ** 2
        )

        print(
            f'Distância percorrida: {distancia:.2f} m'
        )

        # EXEMPLO:
        # verificar se chegou em X = 2.
        if self.x >= 2.0:
            print('O robô chegou em X = 2')

        # EXEMPLO:
        # verificar se percorreu 1 metro.
        if distancia >= 1.0:
            print('O robô percorreu pelo menos 1 metro')


# ============================================================
# SUBSCRIBER DE LASERSCAN
# ============================================================
#
# USE QUANDO O PROFESSOR PEDIR:
#
# - detectar um obstáculo;
# - descobrir a distância da frente;
# - descobrir as distâncias dos lados;
# - comparar esquerda e direita;
# - escolher o caminho mais livre;
# - impedir o robô de bater;
# - desviar de um objeto.
#
# PARA QUE SERVE:
#
# Este subscriber recebe as distâncias medidas pelo
# sensor Laser ao redor do robô.
#
# DE ONDE RECEBE:
#
# Normalmente, recebe do tópico:
#
# /scan
#
# O tipo da mensagem é:
#
# sensor_msgs/msg/LaserScan
#
# ONDE ESTÁ A INFORMAÇÃO:
#
# As distâncias ficam em:
#
# msg.ranges
#
# No Laser da disciplina:
#
# índice 0: frente;
# índice 90: esquerda;
# índice 180: trás;
# índice 270: direita.
#
# O QUE VOCÊ PODE PRECISAR TROCAR:
#
# - o tópico;
# - a abertura usada em cada direção;
# - a distância mínima considerada segura;
# - as direções analisadas;
# - as condições usadas para detectar obstáculos.


class SubscriberLaser(Node):

    def __init__(self):

        super().__init__('subscriber_laser')

        # Quantidade de graus para cada lado da direção central.
        self.abertura = 10

        self.frente = float('inf')
        self.esquerda = float('inf')
        self.direita = float('inf')
        self.tras = float('inf')

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.BEST_EFFORT
            )
        )

    def menor_distancia(self, medicoes):

        # Transforma as medições em array.
        valores = np.array(
            medicoes,
            dtype=float
        )

        # No robô real, zero pode significar que o sensor
        # não conseguiu fazer a leitura.
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

        # Troca zero por infinito.
        laser[laser == 0] = np.inf

        abertura = self.abertura

        # A frente fica dividida entre o começo
        # e o final da lista.
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

        leituras_tras = laser[
            180 - abertura:
            180 + abertura
        ]

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

        self.tras = self.menor_distancia(
            leituras_tras
        )

        print(f'Frente: {self.frente:.2f} m')
        print(f'Esquerda: {self.esquerda:.2f} m')
        print(f'Direita: {self.direita:.2f} m')
        print(f'Trás: {self.tras:.2f} m')

        # EXEMPLO:
        # detectar obstáculo a menos de 50 centímetros.
        if self.frente < 0.5:
            print('Existe um obstáculo na frente')

        else:
            print('A frente está livre')

        # EXEMPLO:
        # escolher o lado mais livre.
        if self.esquerda > self.direita:
            print('A esquerda está mais livre')

        elif self.direita > self.esquerda:
            print('A direita está mais livre')

        else:
            print('Os dois lados possuem a mesma distância')


# ============================================================
# SUBSCRIBER DE IMAGE
# ============================================================
#
# USE QUANDO O PROFESSOR PEDIR:
#
# - receber a imagem da câmera;
# - converter uma imagem ROS para OpenCV;
# - identificar objetos de determinada cor;
# - contar a quantidade de objetos;
# - calcular a área de objetos;
# - encontrar contornos;
# - desenhar caixas nos objetos encontrados.
#
# PARA QUE SERVE:
#
# Este subscriber recebe imagens publicadas pela câmera.
#
# CvBridge transforma a mensagem ROS em uma imagem
# que pode ser processada pelo OpenCV.
#
# DE ONDE RECEBE:
#
# Neste exemplo, recebe do tópico:
#
# /camera/image_raw
#
# O tópico da câmera pode ser diferente na prova.
# Confira o nome fornecido pelo professor.
#
# ONDE ESTÁ A INFORMAÇÃO:
#
# A mensagem completa chega como Image.
#
# Para trabalhar com OpenCV, fazemos:
#
# imagem = self.bridge.imgmsg_to_cv2(
#     msg,
#     desired_encoding='bgr8'
# )
#
# O QUE VOCÊ PODE PRECISAR TROCAR:
#
# - o tópico da câmera;
# - a codificação da imagem;
# - os limites da cor;
# - a área mínima dos objetos;
# - o processamento feito depois da conversão.


class SubscriberImagem(Node):

    def __init__(self):

        super().__init__('subscriber_imagem')

        # Faz a conversão entre ROS Image e OpenCV.
        self.bridge = CvBridge()

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.imagem_callback,
            QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.BEST_EFFORT
            )
        )

    def imagem_callback(self, msg: Image):

        # Converte a mensagem ROS para uma imagem OpenCV.
        imagem = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8'
        )

        # Converte BGR para HSV.
        #
        # HSV normalmente facilita a segmentação por cor.
        imagem_hsv = cv2.cvtColor(
            imagem,
            cv2.COLOR_BGR2HSV
        )

        # Exemplo:
        # segmentação de objetos vermelhos.
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

        # Junta as duas máscaras do vermelho.
        mascara = cv2.bitwise_or(
            mascara_1,
            mascara_2
        )

        # Encontra os contornos dos objetos segmentados.
        contornos, _ = cv2.findContours(
            mascara,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        quantidade = 0

        for contorno in contornos:

            area = cv2.contourArea(contorno)

            # Ignora manchas muito pequenas.
            #
            # Na prova, ajuste este valor conforme
            # o tamanho dos objetos da imagem.
            if area > 100:

                quantidade += 1

                # Cria uma caixa ao redor do objeto.
                x, y, largura, altura = cv2.boundingRect(
                    contorno
                )

                cv2.rectangle(
                    imagem,
                    (x, y),
                    (x + largura, y + altura),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    imagem,
                    f'Area: {area:.0f}',
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

        print(
            f'Quantidade de objetos vermelhos: {quantidade}'
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

        # Abre uma janela para mostrar o resultado.
        if MOSTRAR_IMAGEM:
            cv2.imshow(
                'Imagem recebida',
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

    # Relaciona cada nome com uma classe de subscriber.
    exemplos = {
        'string': SubscriberString,
        'dados': SubscriberDados,
        'twist': SubscriberTwist,
        'odom': SubscriberOdom,
        'laser': SubscriberLaser,
        'imagem': SubscriberImagem
    }

    # Verifica se a opção escolhida existe.
    if EXEMPLO not in exemplos:
        raise ValueError(
            f'Exemplo inválido: {EXEMPLO}'
        )

    # Cria somente o subscriber escolhido.
    node = exemplos[EXEMPLO]()

    # Mantém o nó recebendo mensagens.
    rclpy.spin(node)

    # Fecha as janelas do OpenCV.
    cv2.destroyAllWindows()

    # Encerra o nó.
    node.destroy_node()

    # Encerra a ROS 2.
    rclpy.shutdown()


if __name__ == '__main__':
    main()