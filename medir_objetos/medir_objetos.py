#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np


# =============================================================
# CONFIGURAÇÕES PADRÃO
# =============================================================

CAMINHO_PADRAO = 'imagens/entrada.png'
COR_PADRAO = 'vermelho'
AREA_MINIMA_PADRAO = 500.0
TAMANHO_KERNEL = 5


# =============================================================
# FAIXAS HSV
# =============================================================

# Os valores são coringas.
# Dependendo da iluminação, ajuste os limites.
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


class MedidorObjetos:
    """
    USE QUANDO O PROFESSOR PEDIR:

    - encontrar a área dos objetos;
    - encontrar o centro dos objetos;
    - encontrar a posição de cada objeto;
    - desenhar os contornos e centros;
    - retornar uma lista com as medidas.

    O método run recebe a imagem já carregada.
    """

    def __init__(
        self,
        cor=COR_PADRAO,
        area_minima=AREA_MINIMA_PADRAO,
        tamanho_kernel=TAMANHO_KERNEL
    ):
        self.cor = cor.lower()
        self.area_minima = float(area_minima)

        if self.cor not in FAIXAS_HSV:
            cores = ', '.join(FAIXAS_HSV.keys())

            raise ValueError(
                f'Cor "{self.cor}" não cadastrada. '
                f'Cores disponíveis: {cores}'
            )

        tamanho_kernel = max(1, int(tamanho_kernel))

        if tamanho_kernel % 2 == 0:
            tamanho_kernel += 1

        self.kernel = np.ones(
            (tamanho_kernel, tamanho_kernel),
            dtype=np.uint8
        )

    # =========================================================
    # MÁSCARA
    # =========================================================

    def criar_mascara(self, imagem):
        """
        Cria uma máscara binária para a cor escolhida.
        """

        imagem_hsv = cv2.cvtColor(
            imagem,
            cv2.COLOR_BGR2HSV
        )

        mascara_final = np.zeros(
            imagem.shape[:2],
            dtype=np.uint8
        )

        for limite_inferior, limite_superior in FAIXAS_HSV[self.cor]:
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
        Remove pequenos pontos e preenche pequenos buracos.
        """

        # Abertura: remove ruídos brancos pequenos.
        mascara_aberta = cv2.morphologyEx(
            mascara,
            cv2.MORPH_OPEN,
            self.kernel,
            iterations=1
        )

        # Fechamento: preenche buracos dentro dos objetos.
        mascara_limpa = cv2.morphologyEx(
            mascara_aberta,
            cv2.MORPH_CLOSE,
            self.kernel,
            iterations=2
        )

        return mascara_limpa

    # =========================================================
    # CONTORNOS
    # =========================================================

    def encontrar_contornos_validos(self, mascara):
        """
        Encontra somente contornos externos com área suficiente.
        """

        contornos, _ = cv2.findContours(
            mascara.copy(),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        contornos_validos = []

        for contorno in contornos:
            area = cv2.contourArea(contorno)

            if area >= self.area_minima:
                contornos_validos.append(contorno)

        # Ordena da esquerda para a direita.
        contornos_validos.sort(
            key=lambda contorno: cv2.boundingRect(contorno)[0]
        )

        return contornos_validos

    # =========================================================
    # MEDIDAS
    # =========================================================

    def medir_contorno(self, contorno, numero):
        """
        Calcula a área, o centro e a caixa de um contorno.
        """

        # Área em pixels quadrados.
        area = cv2.contourArea(contorno)

        # Calcula os momentos geométricos do contorno.
        momentos = cv2.moments(contorno)

        # m00 normalmente corresponde à área do contorno.
        #
        # Precisamos verificar se é diferente de zero para evitar
        # uma divisão por zero.
        if momentos['m00'] != 0:
            centro_x = int(
                momentos['m10'] / momentos['m00']
            )

            centro_y = int(
                momentos['m01'] / momentos['m00']
            )

        else:
            # Caso raro: usa o centro da caixa delimitadora.
            x, y, largura, altura = cv2.boundingRect(contorno)

            centro_x = x + largura // 2
            centro_y = y + altura // 2

        # Caixa delimitadora do objeto.
        x, y, largura, altura = cv2.boundingRect(contorno)

        # Retorna todas as informações em um dicionário.
        return {
            'numero': numero,
            'area': area,
            'centro_x': centro_x,
            'centro_y': centro_y,
            'x': x,
            'y': y,
            'largura': largura,
            'altura': altura,
            'contorno': contorno,
        }

    def medir_objetos(self, contornos):
        """
        Mede todos os contornos e retorna uma lista de dicionários.
        """

        objetos = []

        for numero, contorno in enumerate(contornos, start=1):
            objeto = self.medir_contorno(
                contorno,
                numero
            )

            objetos.append(objeto)

        return objetos

    # =========================================================
    # DESENHAR RESULTADO
    # =========================================================

    def desenhar_resultado(self, imagem, objetos):
        """
        Desenha contorno, caixa, centro, área e coordenadas.
        """

        resultado = imagem.copy()

        for objeto in objetos:
            numero = objeto['numero']
            area = objeto['area']
            centro_x = objeto['centro_x']
            centro_y = objeto['centro_y']

            x = objeto['x']
            y = objeto['y']
            largura = objeto['largura']
            altura = objeto['altura']

            contorno = objeto['contorno']

            # Desenha o contorno em verde.
            cv2.drawContours(
                resultado,
                [contorno],
                -1,
                (0, 255, 0),
                2
            )

            # Desenha a caixa delimitadora em azul.
            cv2.rectangle(
                resultado,
                (x, y),
                (x + largura, y + altura),
                (255, 0, 0),
                2
            )

            # Desenha o centro como um círculo vermelho.
            cv2.circle(
                resultado,
                (centro_x, centro_y),
                6,
                (0, 0, 255),
                -1
            )

            # Escreve o número do objeto.
            cv2.putText(
                resultado,
                f'Objeto {numero}',
                (x, max(25, y - 35)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2
            )

            # Escreve a área.
            cv2.putText(
                resultado,
                f'Area: {area:.0f}',
                (x, max(45, y - 15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (0, 255, 255),
                2
            )

            # Escreve as coordenadas do centro.
            cv2.putText(
                resultado,
                f'({centro_x}, {centro_y})',
                (centro_x + 10, centro_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (0, 0, 255),
                2
            )

        # Mostra a quantidade total no canto superior esquerdo.
        cv2.rectangle(
            resultado,
            (10, 10),
            (400, 55),
            (0, 0, 0),
            -1
        )

        cv2.putText(
            resultado,
            f'Objetos encontrados: {len(objetos)}',
            (20, 43),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.85,
            (0, 255, 255),
            2
        )

        return resultado

    # =========================================================
    # RUN
    # =========================================================

    def run(self, imagem):
        """
        Recebe uma imagem BGR e retorna:

        1. imagem com as medições;
        2. máscara limpa;
        3. lista de objetos.

        Cada elemento da lista contém área, centro e caixa.
        """

        if imagem is None:
            raise ValueError('A imagem recebida é inválida.')

        mascara = self.criar_mascara(imagem)

        mascara_limpa = self.limpar_mascara(
            mascara
        )

        contornos = self.encontrar_contornos_validos(
            mascara_limpa
        )

        objetos = self.medir_objetos(
            contornos
        )

        resultado = self.desenhar_resultado(
            imagem,
            objetos
        )

        return resultado, mascara_limpa, objetos


# =============================================================
# SALVAR CSV
# =============================================================

def salvar_medidas_csv(objetos, caminho):
    """
    Salva as medidas em um arquivo que pode ser aberto no Excel.
    """

    campos = [
        'objeto',
        'area',
        'centro_x',
        'centro_y',
        'x',
        'y',
        'largura',
        'altura',
    ]

    with open(
        caminho,
        mode='w',
        newline='',
        encoding='utf-8'
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=campos
        )

        escritor.writeheader()

        for objeto in objetos:
            escritor.writerow({
                'objeto': objeto['numero'],
                'area': round(objeto['area'], 2),
                'centro_x': objeto['centro_x'],
                'centro_y': objeto['centro_y'],
                'x': objeto['x'],
                'y': objeto['y'],
                'largura': objeto['largura'],
                'altura': objeto['altura'],
            })


# =============================================================
# ARGUMENTOS
# =============================================================

def ler_argumentos():
    parser = argparse.ArgumentParser(
        description='Calcula a área e o centro dos objetos.'
    )

    parser.add_argument(
        'imagem',
        nargs='?',
        default=CAMINHO_PADRAO,
        help='Caminho da imagem de entrada.'
    )

    parser.add_argument(
        '--cor',
        default=COR_PADRAO,
        choices=list(FAIXAS_HSV.keys()),
        help='Cor dos objetos.'
    )

    parser.add_argument(
        '--area-minima',
        type=float,
        default=AREA_MINIMA_PADRAO,
        help='Área mínima para considerar um contorno.'
    )

    parser.add_argument(
        '--sem-janela',
        action='store_true',
        help='Salva sem abrir as janelas.'
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
        medidor = MedidorObjetos(
            cor=argumentos.cor,
            area_minima=argumentos.area_minima
        )

        resultado, mascara, objetos = medidor.run(
            imagem
        )

    except ValueError as erro:
        print(f'ERRO: {erro}')
        return

    # Cria a pasta de resultados.
    pasta_resultados = Path('resultados')
    pasta_resultados.mkdir(
        parents=True,
        exist_ok=True
    )

    caminho_mascara = (
        pasta_resultados / 'mascara.png'
    )

    caminho_resultado = (
        pasta_resultados / 'objetos_medidos.png'
    )

    caminho_csv = (
        pasta_resultados / 'medidas.csv'
    )

    # Salva as imagens.
    cv2.imwrite(
        str(caminho_mascara),
        mascara
    )

    cv2.imwrite(
        str(caminho_resultado),
        resultado
    )

    # Salva as medidas.
    salvar_medidas_csv(
        objetos,
        caminho_csv
    )

    # Imprime as medidas no terminal.
    print('==========================================')
    print('OBJETOS ENCONTRADOS')
    print('==========================================')
    print(f'Cor procurada: {argumentos.cor}')
    print(f'Quantidade: {len(objetos)}')
    print('==========================================')

    for objeto in objetos:
        print(f'Objeto {objeto["numero"]}')
        print(f'  Área: {objeto["area"]:.2f} pixels')
        print(
            f'  Centro: '
            f'({objeto["centro_x"]}, {objeto["centro_y"]})'
        )
        print(
            f'  Caixa: x={objeto["x"]}, '
            f'y={objeto["y"]}, '
            f'largura={objeto["largura"]}, '
            f'altura={objeto["altura"]}'
        )
        print('------------------------------------------')

    print(f'Máscara salva em: {caminho_mascara}')
    print(f'Resultado salvo em: {caminho_resultado}')
    print(f'Medidas salvas em: {caminho_csv}')

    if not argumentos.sem_janela:
        cv2.imshow(
            'Imagem original',
            imagem
        )

        cv2.imshow(
            'Mascara limpa',
            mascara
        )

        cv2.imshow(
            'Area e centro dos objetos',
            resultado
        )

        print('Pressione qualquer tecla nas imagens para fechar.')

        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

# cd ..\contar_objetos_por_cor
# & "C:\Users\rafoe\anaconda\python.exe" .\contar_objetos_por_cor.py .\imagens\entrada.png --cor vermelho --area-minima 500