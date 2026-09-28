#!/usr/bin/env python3

import argparse
import itertools
import math
from pathlib import Path

import cv2
import numpy as np


# =============================================================
# CONFIGURAÇÕES
# =============================================================

CAMINHO_PADRAO = 'imagens/entrada.png'

COR_1_PADRAO = 'vermelho'
COR_2_PADRAO = 'azul'

AREA_MINIMA_PADRAO = 500.0
TAMANHO_KERNEL = 5

MODOS_DISPONIVEIS = [
    'maiores',
    'mais-proximos',
    'mais-distantes',
]


# =============================================================
# FAIXAS HSV
# =============================================================

FAIXAS_HSV = {
    'vermelho': [
        (
            np.array([0, 80, 50]),
            np.array([10, 255, 255])
        ),
        (
            np.array([170, 80, 50]),
            np.array([180, 255, 255])
        ),
    ],

    'laranja': [
        (
            np.array([10, 100, 80]),
            np.array([25, 255, 255])
        ),
    ],

    'amarelo': [
        (
            np.array([20, 80, 80]),
            np.array([35, 255, 255])
        ),
    ],

    'verde': [
        (
            np.array([35, 60, 40]),
            np.array([85, 255, 255])
        ),
    ],

    'ciano': [
        (
            np.array([80, 50, 50]),
            np.array([100, 255, 255])
        ),
    ],

    'azul': [
        (
            np.array([90, 70, 40]),
            np.array([130, 255, 255])
        ),
    ],

    'roxo': [
        (
            np.array([130, 60, 40]),
            np.array([155, 255, 255])
        ),
    ],

    'rosa': [
        (
            np.array([150, 50, 70]),
            np.array([169, 255, 255])
        ),
    ],

    'branco': [
        (
            np.array([0, 0, 180]),
            np.array([180, 70, 255])
        ),
    ],

    'preto': [
        (
            np.array([0, 0, 0]),
            np.array([180, 255, 60])
        ),
    ],
}


class CalculadorDistanciaObjetos:
    """
    USE QUANDO O PROFESSOR PEDIR:

    - calcular a distância entre dois objetos;
    - calcular a distância entre os centros;
    - encontrar objetos mais próximos;
    - encontrar objetos mais distantes;
    - trabalhar com duas cores;
    - trabalhar com dois objetos da mesma cor.

    O método run recebe uma imagem já carregada.
    """

    def __init__(
        self,
        cor_1=COR_1_PADRAO,
        cor_2=COR_2_PADRAO,
        area_minima=AREA_MINIMA_PADRAO,
        modo='maiores'
    ):
        self.cor_1 = cor_1.lower()
        self.cor_2 = cor_2.lower()

        self.area_minima = float(area_minima)
        self.modo = modo

        if self.cor_1 not in FAIXAS_HSV:
            raise ValueError(
                f'Cor 1 não cadastrada: {self.cor_1}'
            )

        if self.cor_2 not in FAIXAS_HSV:
            raise ValueError(
                f'Cor 2 não cadastrada: {self.cor_2}'
            )

        if self.modo not in MODOS_DISPONIVEIS:
            raise ValueError(
                f'Modo inválido: {self.modo}'
            )

        self.kernel = np.ones(
            (TAMANHO_KERNEL, TAMANHO_KERNEL),
            dtype=np.uint8
        )

    # =========================================================
    # SEGMENTAÇÃO
    # =========================================================

    def criar_mascara(self, imagem, cor):
        """
        Cria uma máscara para a cor escolhida.
        """

        imagem_hsv = cv2.cvtColor(
            imagem,
            cv2.COLOR_BGR2HSV
        )

        mascara_final = np.zeros(
            imagem.shape[:2],
            dtype=np.uint8
        )

        for limite_inferior, limite_superior in FAIXAS_HSV[cor]:
            mascara_da_faixa = cv2.inRange(
                imagem_hsv,
                limite_inferior,
                limite_superior
            )

            mascara_final = cv2.bitwise_or(
                mascara_final,
                mascara_da_faixa
            )

        return mascara_final

    def limpar_mascara(self, mascara):
        """
        Remove pontos pequenos e preenche buracos.
        """

        mascara = cv2.morphologyEx(
            mascara,
            cv2.MORPH_OPEN,
            self.kernel,
            iterations=1
        )

        mascara = cv2.morphologyEx(
            mascara,
            cv2.MORPH_CLOSE,
            self.kernel,
            iterations=2
        )

        return mascara

    # =========================================================
    # OBJETOS
    # =========================================================

    def encontrar_objetos(self, mascara):
        """
        Encontra todos os objetos válidos da máscara.

        Cada objeto é representado por um dicionário contendo:

        - contorno;
        - área;
        - centro;
        - caixa delimitadora.
        """

        contornos, _ = cv2.findContours(
            mascara.copy(),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        objetos = []

        for contorno in contornos:
            area = cv2.contourArea(contorno)

            if area < self.area_minima:
                continue

            momentos = cv2.moments(contorno)

            if momentos['m00'] != 0:
                centro_x = int(
                    momentos['m10'] / momentos['m00']
                )

                centro_y = int(
                    momentos['m01'] / momentos['m00']
                )

            else:
                x, y, largura, altura = cv2.boundingRect(contorno)

                centro_x = x + largura // 2
                centro_y = y + altura // 2

            x, y, largura, altura = cv2.boundingRect(contorno)

            objetos.append({
                'contorno': contorno,
                'area': area,
                'centro': (centro_x, centro_y),
                'x': x,
                'y': y,
                'largura': largura,
                'altura': altura,
            })

        return objetos

    # =========================================================
    # DISTÂNCIA
    # =========================================================

    def calcular_distancia(self, objeto_1, objeto_2):
        """
        Calcula a distância euclidiana entre os centros.
        """

        x_1, y_1 = objeto_1['centro']
        x_2, y_2 = objeto_2['centro']

        delta_x = x_2 - x_1
        delta_y = y_2 - y_1

        distancia = math.sqrt(
            delta_x ** 2 + delta_y ** 2
        )

        return distancia

    # =========================================================
    # ESCOLHER OS DOIS OBJETOS
    # =========================================================

    def escolher_par_mesma_cor(self, objetos):
        """
        Escolhe dois objetos quando as duas cores são iguais.
        """

        if len(objetos) < 2:
            raise ValueError(
                f'Foram encontrados apenas {len(objetos)} '
                f'objetos da cor {self.cor_1}. São necessários 2.'
            )

        if self.modo == 'maiores':
            objetos_ordenados = sorted(
                objetos,
                key=lambda objeto: objeto['area'],
                reverse=True
            )

            return objetos_ordenados[0], objetos_ordenados[1]

        # Cria todas as combinações possíveis sem repetir objetos.
        pares = list(
            itertools.combinations(objetos, 2)
        )

        if self.modo == 'mais-proximos':
            return min(
                pares,
                key=lambda par: self.calcular_distancia(
                    par[0],
                    par[1]
                )
            )

        # Se chegou aqui, o modo é mais-distantes.
        return max(
            pares,
            key=lambda par: self.calcular_distancia(
                par[0],
                par[1]
            )
        )

    def escolher_par_cores_diferentes(
        self,
        objetos_cor_1,
        objetos_cor_2
    ):
        """
        Escolhe um objeto de cada cor.
        """

        if not objetos_cor_1:
            raise ValueError(
                f'Nenhum objeto {self.cor_1} foi encontrado.'
            )

        if not objetos_cor_2:
            raise ValueError(
                f'Nenhum objeto {self.cor_2} foi encontrado.'
            )

        if self.modo == 'maiores':
            objeto_1 = max(
                objetos_cor_1,
                key=lambda objeto: objeto['area']
            )

            objeto_2 = max(
                objetos_cor_2,
                key=lambda objeto: objeto['area']
            )

            return objeto_1, objeto_2

        # Produto cartesiano:
        # cria todos os pares possíveis entre as duas cores.
        pares = list(
            itertools.product(
                objetos_cor_1,
                objetos_cor_2
            )
        )

        if self.modo == 'mais-proximos':
            return min(
                pares,
                key=lambda par: self.calcular_distancia(
                    par[0],
                    par[1]
                )
            )

        return max(
            pares,
            key=lambda par: self.calcular_distancia(
                par[0],
                par[1]
            )
        )

    # =========================================================
    # DESENHAR
    # =========================================================

    def desenhar_resultado(
        self,
        imagem,
        objeto_1,
        objeto_2,
        distancia
    ):
        """
        Desenha os dois objetos, seus centros e a distância.
        """

        resultado = imagem.copy()

        centro_1 = objeto_1['centro']
        centro_2 = objeto_2['centro']

        # Objeto 1 em verde.
        cv2.drawContours(
            resultado,
            [objeto_1['contorno']],
            -1,
            (0, 255, 0),
            3
        )

        # Objeto 2 em azul.
        cv2.drawContours(
            resultado,
            [objeto_2['contorno']],
            -1,
            (255, 0, 0),
            3
        )

        # Centro do objeto 1.
        cv2.circle(
            resultado,
            centro_1,
            8,
            (0, 255, 0),
            -1
        )

        # Centro do objeto 2.
        cv2.circle(
            resultado,
            centro_2,
            8,
            (255, 0, 0),
            -1
        )

        # Linha ligando os centros.
        cv2.line(
            resultado,
            centro_1,
            centro_2,
            (0, 255, 255),
            3
        )

        # Ponto médio da linha.
        meio_x = (centro_1[0] + centro_2[0]) // 2
        meio_y = (centro_1[1] + centro_2[1]) // 2

        # Fundo para o texto da distância.
        cv2.rectangle(
            resultado,
            (meio_x - 100, meio_y - 35),
            (meio_x + 150, meio_y + 5),
            (0, 0, 0),
            -1
        )

        cv2.putText(
            resultado,
            f'{distancia:.2f} pixels',
            (meio_x - 90, meio_y - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.70,
            (0, 255, 255),
            2
        )

        # Identificação do primeiro objeto.
        cv2.putText(
            resultado,
            f'1: {self.cor_1} {centro_1}',
            (centro_1[0] + 10, centro_1[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 0),
            2
        )

        # Identificação do segundo objeto.
        cv2.putText(
            resultado,
            f'2: {self.cor_2} {centro_2}',
            (centro_2[0] + 10, centro_2[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 0, 0),
            2
        )

        return resultado

    # =========================================================
    # RUN
    # =========================================================

    def run(self, imagem):
        """
        Recebe a imagem e retorna:

        1. imagem com o resultado;
        2. primeira máscara;
        3. segunda máscara;
        4. primeiro objeto;
        5. segundo objeto;
        6. distância entre os centros.
        """

        if imagem is None:
            raise ValueError('A imagem recebida é inválida.')

        # Cria e limpa a primeira máscara.
        mascara_1 = self.criar_mascara(
            imagem,
            self.cor_1
        )

        mascara_1 = self.limpar_mascara(
            mascara_1
        )

        objetos_cor_1 = self.encontrar_objetos(
            mascara_1
        )

        # Se as cores são iguais, não precisa processar novamente.
        if self.cor_1 == self.cor_2:
            mascara_2 = mascara_1.copy()

            objeto_1, objeto_2 = (
                self.escolher_par_mesma_cor(
                    objetos_cor_1
                )
            )

        else:
            mascara_2 = self.criar_mascara(
                imagem,
                self.cor_2
            )

            mascara_2 = self.limpar_mascara(
                mascara_2
            )

            objetos_cor_2 = self.encontrar_objetos(
                mascara_2
            )

            objeto_1, objeto_2 = (
                self.escolher_par_cores_diferentes(
                    objetos_cor_1,
                    objetos_cor_2
                )
            )

        distancia = self.calcular_distancia(
            objeto_1,
            objeto_2
        )

        resultado = self.desenhar_resultado(
            imagem,
            objeto_1,
            objeto_2,
            distancia
        )

        return (
            resultado,
            mascara_1,
            mascara_2,
            objeto_1,
            objeto_2,
            distancia
        )


# =============================================================
# ARGUMENTOS
# =============================================================

def ler_argumentos():
    parser = argparse.ArgumentParser(
        description=(
            'Calcula a distância entre os centros de dois objetos.'
        )
    )

    parser.add_argument(
        'imagem',
        nargs='?',
        default=CAMINHO_PADRAO,
        help='Caminho da imagem.'
    )

    parser.add_argument(
        '--cor-1',
        default=COR_1_PADRAO,
        choices=list(FAIXAS_HSV.keys()),
        help='Cor do primeiro objeto.'
    )

    parser.add_argument(
        '--cor-2',
        default=COR_2_PADRAO,
        choices=list(FAIXAS_HSV.keys()),
        help='Cor do segundo objeto.'
    )

    parser.add_argument(
        '--modo',
        default='maiores',
        choices=MODOS_DISPONIVEIS,
        help='Forma de escolher os objetos.'
    )

    parser.add_argument(
        '--area-minima',
        type=float,
        default=AREA_MINIMA_PADRAO,
        help='Área mínima dos objetos.'
    )

    parser.add_argument(
        '--sem-janela',
        action='store_true',
        help='Salva sem abrir janelas.'
    )

    return parser.parse_args()


# =============================================================
# MAIN
# =============================================================

def main():
    argumentos = ler_argumentos()

    caminho_imagem = Path(argumentos.imagem)

    imagem = cv2.imread(
        str(caminho_imagem)
    )

    if imagem is None:
        print(
            f'ERRO: não foi possível carregar:\n'
            f'{caminho_imagem}'
        )
        return

    try:
        calculador = CalculadorDistanciaObjetos(
            cor_1=argumentos.cor_1,
            cor_2=argumentos.cor_2,
            area_minima=argumentos.area_minima,
            modo=argumentos.modo
        )

        (
            resultado,
            mascara_1,
            mascara_2,
            objeto_1,
            objeto_2,
            distancia
        ) = calculador.run(imagem)

    except ValueError as erro:
        print(f'ERRO: {erro}')
        return

    pasta_resultados = Path('resultados')
    pasta_resultados.mkdir(
        parents=True,
        exist_ok=True
    )

    caminho_mascara_1 = (
        pasta_resultados / 'mascara_cor_1.png'
    )

    caminho_mascara_2 = (
        pasta_resultados / 'mascara_cor_2.png'
    )

    caminho_resultado = (
        pasta_resultados / 'distancia_entre_objetos.png'
    )

    cv2.imwrite(
        str(caminho_mascara_1),
        mascara_1
    )

    cv2.imwrite(
        str(caminho_mascara_2),
        mascara_2
    )

    cv2.imwrite(
        str(caminho_resultado),
        resultado
    )

    print('==========================================')
    print('DISTÂNCIA ENTRE OS OBJETOS')
    print('==========================================')
    print(f'Modo utilizado: {argumentos.modo}')
    print('------------------------------------------')
    print(f'Objeto 1: {argumentos.cor_1}')
    print(f'  Centro: {objeto_1["centro"]}')
    print(f'  Área: {objeto_1["area"]:.2f} pixels')
    print('------------------------------------------')
    print(f'Objeto 2: {argumentos.cor_2}')
    print(f'  Centro: {objeto_2["centro"]}')
    print(f'  Área: {objeto_2["area"]:.2f} pixels')
    print('------------------------------------------')
    print(f'Distância: {distancia:.2f} pixels')
    print('==========================================')
    print(f'Resultado salvo em: {caminho_resultado}')

    if not argumentos.sem_janela:
        cv2.imshow(
            'Mascara da primeira cor',
            mascara_1
        )

        cv2.imshow(
            'Mascara da segunda cor',
            mascara_2
        )

        cv2.imshow(
            'Distancia entre os objetos',
            resultado
        )

        print('Pressione qualquer tecla nas imagens para fechar.')

        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()