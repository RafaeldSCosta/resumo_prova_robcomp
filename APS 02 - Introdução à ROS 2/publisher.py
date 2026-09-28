import math
import cv2
import numpy as np
import rclpy

from rclpy.node import Node

from std_msgs.msg import String, Bool, Int32, Float64
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan, Image
from cv_bridge import CvBridge


# Escolha qual exemplo deseja executar.
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


# ============================================================
# PUBLISHER DE STRING
# ============================================================
#
# USE QUANDO O PROFESSOR PEDIR:
#
# - publicar uma palavra ou uma frase;
# - enviar uma instrução para outro nó;
# - enviar comandos como "frente", "direita" ou "parar";
# - publicar o nome de um objeto identificado;
# - informar estados como "procurando" ou "finalizado";
# - mandar uma resposta produzida pelo agente.
#
# PARA QUE SERVE:
#
# Este publisher envia textos para um tópico da ROS.
#
# Qualquer nó inscrito nesse tópico poderá receber o texto.
#
# Exemplo:
#
# Este publisher envia "frente" no tópico /instrucao.
# Outro nó recebe "frente" e manda o robô andar.
#
# PARA ONDE ENVIA:
#
# Neste exemplo, envia para:
#
# /instrucao
#
# ONDE COLOCA A INFORMAÇÃO:
#
# Mensagens String guardam o texto em:
#
# msg.data
#
# O QUE VOCÊ PODE PRECISAR TROCAR:
#
# - o tópico '/instrucao';
# - o texto colocado em msg.data;
# - as condições que escolhem qual texto publicar.


class PublisherString(Node):

    def __init__(self):

        # Como a classe herda de Node, precisamos iniciar
        # a parte correspondente à ROS 2.
        super().__init__('publisher_string')

        # Cria o publisher.
        #
        # String:
        # tipo da mensagem que será publicada.
        #
        # '/instrucao':
        # tópico onde a mensagem será publicada.
        #
        # 10:
        # tamanho da fila de mensagens.
        self.publisher = self.create_publisher(
            String,
            '/instrucao',
            10
        )

        # Exemplo prático:
        # sequência de instruções que serão publicadas.
        #
        # Na prova, troque os textos pelas instruções
        # pedidas no enunciado.
        self.instrucoes = [
            'frente',
            'esquerda',
            'frente',
            'direita',
            'parar'
        ]

        self.indice = 0

        # Chama self.publicar a cada 1 segundo.
        self.timer = self.create_timer(
            1.0,
            self.publicar
        )

    def publicar(self):

        # Cria uma mensagem do tipo String.
        msg = String()

        # Pega a próxima instrução da lista.
        msg.data = self.instrucoes[self.indice]

        # Publica a mensagem no tópico /instrucao.
        self.publisher.publish(msg)

        self.get_logger().info(
            f'Instrução publicada: {msg.data}'
        )

        # Passa para a próxima instrução.
        self.indice += 1

        # Quando chegar ao final da lista,
        # volta para a primeira instrução.
        if self.indice >= len(self.instrucoes):
            self.indice = 0


# ============================================================
# PUBLISHER DE BOOL, INT32 E FLOAT64
# ============================================================
#
# USE QUANDO O PROFESSOR PEDIR:
#
# - publicar se alguma condição é verdadeira ou falsa;
# - avisar se uma tarefa terminou;
# - publicar a quantidade de objetos encontrados;
# - publicar uma contagem;
# - enviar uma distância;
# - enviar uma área calculada;
# - enviar uma velocidade ou outra medida numérica.
#
# PARA QUE SERVE:
#
# Este publisher envia valores simples para outros nós.
#
# Bool:
# envia True ou False.
#
# Int32:
# envia números inteiros, como uma quantidade de objetos.
#
# Float64:
# envia números decimais, como distância, área ou velocidade.
#
# PARA ONDE ENVIA:
#
# Neste exemplo:
#
# Bool envia para /tarefa_finalizada.
# Int32 envia para /quantidade_objetos.
# Float64 envia para /distancia_objeto.
#
# ONDE COLOCA A INFORMAÇÃO:
#
# Os três tipos utilizam:
#
# msg.data
#
# EXEMPLOS:
#
# msg_bool.data = True
# msg_int.data = 5
# msg_float.data = 1.75
#
# O QUE VOCÊ PODE PRECISAR TROCAR:
#
# - o tipo Bool, Int32 ou Float64;
# - o nome do tópico;
# - o valor colocado em msg.data;
# - a condição usada para calcular o valor.


class PublisherDados(Node):

    def __init__(self):

        super().__init__('publisher_dados')

        # Publica verdadeiro ou falso.
        self.bool_pub = self.create_publisher(
            Bool,
            '/tarefa_finalizada',
            10
        )

        # Publica um número inteiro.
        self.int_pub = self.create_publisher(
            Int32,
            '/quantidade_objetos',
            10
        )

        # Publica um número decimal.
        self.float_pub = self.create_publisher(
            Float64,
            '/distancia_objeto',
            10
        )

        # Valores usados no exemplo.
        self.finalizado = False
        self.quantidade = 0
        self.distancia = 2.0

        self.timer = self.create_timer(
            1.0,
            self.publicar
        )

    def publicar(self):

        # Cria e publica uma mensagem Bool.
        msg_bool = Bool()
        msg_bool.data = self.finalizado
        self.bool_pub.publish(msg_bool)

        # Cria e publica uma mensagem Int32.
        msg_int = Int32()
        msg_int.data = self.quantidade
        self.int_pub.publish(msg_int)

        # Cria e publica uma mensagem Float64.
        msg_float = Float64()
        msg_float.data = self.distancia
        self.float_pub.publish(msg_float)

        self.get_logger().info(
            f'Finalizado: {self.finalizado} | '
            f'Quantidade: {self.quantidade} | '
            f'Distância: {self.distancia:.2f}'
        )

        # Apenas para mostrar os valores mudando.
        self.quantidade += 1
        self.distancia -= 0.1

        # Depois de contar cinco objetos,
        # publica que a tarefa terminou.
        if self.quantidade >= 5:
            self.finalizado = True

        # Impede a distância de ficar negativa.
        if self.distancia < 0.0:
            self.distancia = 0.0


# ============================================================
# PUBLISHER DE TWIST
# ============================================================
#
# USE QUANDO O PROFESSOR PEDIR:
#
# - fazer o robô andar para frente;
# - fazer o robô andar para trás;
# - fazer o robô girar;
# - fazer o robô parar;
# - realizar uma sequência de movimentos;
# - controlar o robô usando informações do Odom ou do Laser;
# - executar uma instrução recebida de outro nó.
#
# PARA QUE SERVE:
#
# Este publisher envia comandos de velocidade para o robô.
#
# Ele não recebe a posição nem verifica obstáculos.
# Ele apenas informa qual velocidade o robô deve executar.
#
# PARA ONDE ENVIA:
#
# Normalmente, envia para:
#
# /cmd_vel
#
# O simulador recebe essa mensagem e movimenta o robô.
#
# ONDE COLOCA A INFORMAÇÃO:
#
# Velocidade para frente ou para trás:
#
# msg.linear.x
#
# Velocidade de giro:
#
# msg.angular.z
#
# EXEMPLOS:
#
# msg.linear.x = 0.2
# anda para frente.
#
# msg.linear.x = -0.2
# anda para trás.
#
# msg.angular.z = 0.3
# gira para a esquerda.
#
# msg.angular.z = -0.3
# gira para a direita.
#
# Um Twist vazio faz o robô parar:
#
# msg = Twist()
#
# O QUE VOCÊ PODE PRECISAR TROCAR:
#
# - o tópico '/cmd_vel';
# - a velocidade linear;
# - a velocidade angular;
# - as condições que escolhem o movimento.


class PublisherTwist(Node):

    def __init__(self):

        super().__init__('publisher_twist')

        # Cria o publisher de velocidade.
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Conta quantas vezes publicar foi executada.
        self.contador = 0

        # Publica velocidade dez vezes por segundo.
        self.timer = self.create_timer(
            0.1,
            self.publicar
        )

    def publicar(self):

        # Começa com todas as velocidades zeradas.
        msg = Twist()

        # Primeiros dois segundos:
        # anda para frente.
        if self.contador < 20:
            msg.linear.x = 0.2
            acao = 'andando para frente'

        # Durante o próximo segundo:
        # gira para a esquerda.
        elif self.contador < 30:
            msg.angular.z = 0.5
            acao = 'girando para a esquerda'

        # Depois disso:
        # para o robô.
        else:
            acao = 'parado'

        self.publisher.publish(msg)

        self.get_logger().info(acao)

        self.contador += 1


# ============================================================
# PUBLISHER DE ODOMETRY
# ============================================================
#
# USE QUANDO O PROFESSOR PEDIR:
#
# - publicar uma posição;
# - publicar uma orientação;
# - publicar uma velocidade estimada;
# - criar dados fictícios de odometria;
# - republicar dados de posição em outro tópico;
# - simular o deslocamento de um robô.
#
# ATENÇÃO:
#
# Normalmente, o simulador já publica /odom.
#
# Nesse caso, seu código será um SUBSCRIBER de Odometry,
# e não um publisher.
#
# Use este publisher somente se o enunciado realmente pedir
# para criar, simular ou republicar dados de odometria.
#
# PARA QUE SERVE:
#
# Este publisher envia informações sobre:
#
# - posição do robô;
# - orientação do robô;
# - velocidade linear;
# - velocidade angular.
#
# PARA ONDE ENVIA:
#
# Neste exemplo, envia para:
#
# /odom_exemplo
#
# ONDE COLOCA A INFORMAÇÃO:
#
# Posição:
#
# msg.pose.pose.position.x
# msg.pose.pose.position.y
# msg.pose.pose.position.z
#
# Orientação:
#
# msg.pose.pose.orientation.x
# msg.pose.pose.orientation.y
# msg.pose.pose.orientation.z
# msg.pose.pose.orientation.w
#
# Velocidade:
#
# msg.twist.twist.linear.x
# msg.twist.twist.angular.z
#
# O QUE VOCÊ PODE PRECISAR TROCAR:
#
# - o tópico;
# - a posição publicada;
# - a orientação;
# - a velocidade;
# - os nomes dos frames.


class PublisherOdom(Node):

    def __init__(self):

        super().__init__('publisher_odom')

        self.publisher = self.create_publisher(
            Odometry,
            '/odom_exemplo',
            10
        )

        # Valores fictícios usados no exemplo.
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.timer = self.create_timer(
            0.1,
            self.publicar
        )

    def publicar(self):

        msg = Odometry()

        # Coloca o horário atual na mensagem.
        msg.header.stamp = self.get_clock().now().to_msg()

        # Sistema de coordenadas da posição.
        msg.header.frame_id = 'odom'

        # Sistema de coordenadas preso ao robô.
        msg.child_frame_id = 'base_footprint'

        # Posição do robô.
        msg.pose.pose.position.x = self.x
        msg.pose.pose.position.y = self.y
        msg.pose.pose.position.z = 0.0

        # Converte o yaw para quaternion.
        #
        # Como o robô gira ao redor do eixo Z,
        # preenchemos principalmente orientation.z e orientation.w.
        msg.pose.pose.orientation.x = 0.0
        msg.pose.pose.orientation.y = 0.0
        msg.pose.pose.orientation.z = math.sin(self.yaw / 2)
        msg.pose.pose.orientation.w = math.cos(self.yaw / 2)

        # Velocidades informadas pelo Odom.
        msg.twist.twist.linear.x = 0.2
        msg.twist.twist.angular.z = 0.0

        self.publisher.publish(msg)

        self.get_logger().info(
            f'Publicando posição: '
            f'x={self.x:.2f}, y={self.y:.2f}'
        )

        # Simula um robô avançando no eixo X.
        self.x += 0.02


# ============================================================
# PUBLISHER DE LASERSCAN
# ============================================================
#
# USE QUANDO O PROFESSOR PEDIR:
#
# - criar medições fictícias de um sensor Laser;
# - simular obstáculos;
# - publicar uma lista de distâncias;
# - testar outro nó que recebe Laser;
# - republicar medições processadas em outro tópico.
#
# ATENÇÃO:
#
# Normalmente, o simulador já publica o tópico /scan.
#
# Nesse caso, seu código será um SUBSCRIBER de LaserScan,
# porque queremos receber as distâncias medidas pelo sensor.
#
# Use este publisher somente se o enunciado pedir para
# criar, simular ou republicar medições.
#
# PARA QUE SERVE:
#
# Este publisher envia uma lista de distâncias medidas
# ao redor do robô.
#
# Cada posição da lista representa uma direção.
#
# No exemplo com 360 medições:
#
# índice 0: frente;
# índice 90: esquerda;
# índice 180: trás;
# índice 270: direita.
#
# PARA ONDE ENVIA:
#
# Neste exemplo, envia para:
#
# /scan_exemplo
#
# ONDE COLOCA A INFORMAÇÃO:
#
# As distâncias ficam em:
#
# msg.ranges
#
# EXEMPLO:
#
# msg.ranges[0] = 0.5
#
# Isso representa um objeto a 0.5 metro na frente.
#
# O QUE VOCÊ PODE PRECISAR TROCAR:
#
# - o tópico;
# - a quantidade de medições;
# - os ângulos mínimo e máximo;
# - o incremento angular;
# - as distâncias colocadas em msg.ranges.


class PublisherLaser(Node):

    def __init__(self):

        super().__init__('publisher_laser')

        self.publisher = self.create_publisher(
            LaserScan,
            '/scan_exemplo',
            10
        )

        self.timer = self.create_timer(
            0.1,
            self.publicar
        )

    def publicar(self):

        msg = LaserScan()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_scan'

        # O sensor começa em zero grau.
        msg.angle_min = 0.0

        # O sensor completa uma volta inteira.
        msg.angle_max = 2 * math.pi

        # Teremos 360 leituras:
        # uma para cada grau.
        msg.angle_increment = (2 * math.pi) / 360

        msg.time_increment = 0.0
        msg.scan_time = 0.1

        # Menor e maior distância medidas pelo sensor.
        msg.range_min = 0.12
        msg.range_max = 3.5

        # Começa considerando todas as direções livres.
        ranges = np.full(
            360,
            float('inf')
        )

        # Obstáculo a 40 centímetros na frente.
        #
        # A frente está na divisão entre o começo
        # e o final da lista.
        ranges[0:10] = 0.4
        ranges[350:360] = 0.4

        # Objeto a 1 metro na esquerda.
        ranges[80:100] = 1.0

        # Objeto a 2 metros na direita.
        ranges[260:280] = 2.0

        # LaserScan precisa receber uma lista comum.
        msg.ranges = ranges.tolist()

        self.publisher.publish(msg)

        self.get_logger().info(
            'Laser publicado: frente=0.4 m, '
            'esquerda=1.0 m, direita=2.0 m'
        )


# ============================================================
# PUBLISHER DE IMAGE
# ============================================================
#
# USE QUANDO O PROFESSOR PEDIR:
#
# - publicar uma imagem;
# - enviar uma imagem processada para outro nó;
# - publicar o resultado de uma segmentação;
# - publicar uma imagem com contornos desenhados;
# - mostrar objetos identificados;
# - publicar uma imagem com círculos ou caixas;
# - criar uma imagem para testar outro nó.
#
# ATENÇÃO:
#
# Normalmente, a câmera do simulador já publica uma imagem.
#
# Nesse caso, seu programa será um SUBSCRIBER da câmera.
#
# O publisher será utilizado se você precisar enviar
# a imagem processada para outro tópico.
#
# PARA QUE SERVE:
#
# Este publisher transforma uma imagem do OpenCV em uma
# mensagem ROS e envia essa imagem para outro tópico.
#
# PARA ONDE ENVIA:
#
# Neste exemplo, envia para:
#
# /imagem_exemplo
#
# Outro nó poderá receber essa imagem usando um subscriber
# do tipo sensor_msgs/msg/Image.
#
# COMO A IMAGEM É CONVERTIDA:
#
# Uma imagem do OpenCV é um array NumPy.
#
# CvBridge transforma o array em uma mensagem ROS:
#
# msg = self.bridge.cv2_to_imgmsg(
#     imagem,
#     encoding='bgr8'
# )
#
# bgr8 significa que a imagem possui três canais:
#
# azul, verde e vermelho.
#
# O QUE VOCÊ PODE PRECISAR TROCAR:
#
# - o tópico;
# - a imagem que será publicada;
# - os desenhos feitos na imagem;
# - a codificação da imagem;
# - o frame da câmera.


class PublisherImagem(Node):

    def __init__(self):

        super().__init__('publisher_imagem')

        self.publisher = self.create_publisher(
            Image,
            '/imagem_exemplo',
            10
        )

        # Faz a conversão entre OpenCV e ROS.
        self.bridge = CvBridge()

        # Posição inicial do círculo.
        self.posicao_x = 50

        self.timer = self.create_timer(
            0.1,
            self.publicar
        )

    def publicar(self):

        # Cria uma imagem preta:
        #
        # 480 pixels de altura;
        # 640 pixels de largura;
        # 3 canais de cor.
        imagem = np.zeros(
            (480, 640, 3),
            dtype=np.uint8
        )

        # Desenha um círculo vermelho.
        cv2.circle(
            imagem,
            (self.posicao_x, 240),
            40,
            (0, 0, 255),
            -1
        )

        # Escreve um texto na imagem.
        cv2.putText(
            imagem,
            'Objeto detectado',
            (180, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        # Converte a imagem OpenCV para ROS Image.
        msg = self.bridge.cv2_to_imgmsg(
            imagem,
            encoding='bgr8'
        )

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera'

        self.publisher.publish(msg)

        self.get_logger().info(
            'Imagem publicada'
        )

        # Faz o círculo andar para a direita.
        self.posicao_x += 10

        # Quando o círculo sair da imagem,
        # volta para o começo.
        if self.posicao_x > 590:
            self.posicao_x = 50


def main(args=None):

    # Inicia a ROS 2.
    rclpy.init(args=args)

    # Relaciona o nome de cada exemplo com sua classe.
    exemplos = {
        'string': PublisherString,
        'dados': PublisherDados,
        'twist': PublisherTwist,
        'odom': PublisherOdom,
        'laser': PublisherLaser,
        'imagem': PublisherImagem
    }

    # Verifica se o exemplo escolhido existe.
    if EXEMPLO not in exemplos:
        raise ValueError(
            f'Exemplo inválido: {EXEMPLO}'
        )

    # Cria somente o publisher escolhido.
    node = exemplos[EXEMPLO]()

    # Mantém o nó funcionando.
    rclpy.spin(node)

    # Encerra o nó.
    node.destroy_node()

    # Encerra a ROS 2.
    rclpy.shutdown()


if __name__ == '__main__':
    main()