#!/usr/bin/env python3

import argparse
from pathlib import Path

import cv2
import numpy as np


# =============================================================
# CONFIGURAÇÃO PADRÃO
# =============================================================

# Se executar sem argumentos, esta será a imagem utilizada.
CAMINHO_PADRAO = 'imagens/entrada.png'

# Cor procurada quando nenhuma cor for informada no terminal.
COR_PADRAO = 'vermelho'

# Contornos menores que este valor serão ignorados.
AREA_MINIMA_PADRAO = 500.0

# Tamanho do kernel usado para limpar a máscara.
# Use números ímpares, como 3, 5 ou 7.
TAMANHO_KERNEL = 5


# =============================================================
# FAIXAS DE CORES EM HSV
# =============================================================

# Cada cor possui uma lista de faixas.
#
# A maioria das cores usa somente uma faixa.
# O vermelho utiliza duas porque aparece no começo e no final
# da escala HSV do OpenCV.
#
# SE O PROFESSOR PEDIR OUTRA COR:
# 1. adicione a cor neste dicionário;
# 2. informe os limites inferior e superior;
# 3. execute usando --cor nome_da_cor.
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

    'azul': [
        (
            np.array([90, 70, 40]),
            np.array([130, 255, 255])
        ),
    ],

    'roxo': [
        (
            np.array([130, 60, 40]),
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


class ContadorObjetosPorCor:
    """
    USE QUANDO O PROFESSOR PEDIR:

    - contar objetos de uma determinada cor;
    - segmentar uma imagem;
    - remover ruídos da máscara;
    - encontrar componentes ou contornos;
    - ignorar objetos menores que uma área mínima.

    O método run recebe uma imagem já carregada.

    Isso segue o padrão comum das provas:
    - run processa a imagem;
    - main carrega, exibe e salva.
    """

    def __init__(
        self,
        cor=COR_PADRAO,
        area_minima=AREA_MINIMA_PADRAO,
        tamanho_kernel=TAMANHO_KERNEL
    ):
        # Converte o nome da cor para letras minúsculas.
        self.cor = cor.lower()

        # Área mínima necessária para um contorno ser considerado objeto.
        self.area_minima = float(area_minima)

        # Verifica se a cor existe no dicionário.
        if self.cor not in FAIXAS_HSV:
            cores = ', '.join(FAIXAS_HSV.keys())

            raise ValueError(
                f'Cor "{self.cor}" não cadastrada. '
                f'Cores disponíveis: {cores}'
            )

        # Garante que o tamanho do kernel seja positivo e ímpar.
        tamanho_kernel = max(1, int(tamanho_kernel))

        if tamanho_kernel % 2 == 0:
            tamanho_kernel += 1

        # Kernel utilizado nas operações morfológicas.
        self.kernel = np.ones(
            (tamanho_kernel, tamanho_kernel),
            dtype=np.uint8
        )

    # =========================================================
    # CRIAÇÃO DA MÁSCARA
    # =========================================================

    def criar_mascara(self, imagem):
        """
        Converte a imagem para HSV e seleciona a cor desejada.

        Retorna uma imagem binária:

        - pixel branco: pertence à cor;
        - pixel preto: não pertence à cor.
        """

        # As imagens carregadas pelo cv2.imread estão em BGR.
        imagem_hsv = cv2.cvtColor(
            imagem,
            cv2.COLOR_BGR2HSV
        )

        # Começa com uma máscara completamente preta.
        mascara_final = np.zeros(
            imagem.shape[:2],
            dtype=np.uint8
        )

        # Percorre todas as faixas cadastradas para a cor.
        #
        # Para vermelho, este loop cria duas máscaras e as une.
        for limite_inferior, limite_superior in FAIXAS_HSV[self.cor]:
            mascara_da_faixa = cv2.inRange(
                imagem_hsv,
                limite_inferior,
                limite_superior
            )

            # OR mantém branco quando pelo menos uma máscara é branca.
            mascara_final = cv2.bitwise_or(
                mascara_final,
                mascara_da_faixa
            )

        return mascara_final

    # =========================================================
    # LIMPEZA DA MÁSCARA
    # =========================================================

    def limpar_mascara(self, mascara):
        """
        Melhora a máscara utilizando operações morfológicas.

        Abertura:
            remove pequenos pontos brancos.

        Fechamento:
            preenche pequenos buracos pretos dentro dos objetos.
        """

        mascara_aberta = cv2.morphologyEx(
            mascara,
            cv2.MORPH_OPEN,
            self.kernel,
            iterations=1
        )

        mascara_limpa = cv2.morphologyEx(
            mascara_aberta,
            cv2.MORPH_CLOSE,
            self.kernel,
            iterations=2
        )

        return mascara_limpa

    # =========================================================
    # ENCONTRAR OBJETOS
    # =========================================================

    def encontrar_contornos_validos(self, mascara):
        """
        Encontra os contornos externos e remove os muito pequenos.
        """

        contornos, _ = cv2.findContours(
            mascara.copy(),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        contornos_validos = []

        for contorno in contornos:
            area = cv2.contourArea(contorno)

            # Somente considera objetos maiores que a área mínima.
            if area >= self.area_minima:
                contornos_validos.append(contorno)

        # Ordena da esquerda para a direita.
        # Isso faz os números dos objetos ficarem mais previsíveis.
        contornos_validos.sort(
            key=lambda contorno: cv2.boundingRect(contorno)[0]
        )

        return contornos_validos

    # =========================================================
    # DESENHAR RESULTADO
    # =========================================================

    def desenhar_resultado(self, imagem, contornos):
        """
        Desenha uma caixa e um número em cada objeto encontrado.
        """

        resultado = imagem.copy()

        for numero, contorno in enumerate(contornos, start=1):
            # Caixa que envolve o contorno.
            x, y, largura, altura = cv2.boundingRect(contorno)

            # Desenha a caixa em verde.
            cv2.rectangle(
                resultado,
                (x, y),
                (x + largura, y + altura),
                (0, 255, 0),
                2
            )

            # Escreve o número do objeto.
            cv2.putText(
                resultado,
                f'Objeto {numero}',
                (x, max(25, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2
            )

        quantidade = len(contornos)

        # Cria um fundo preto para o texto ficar legível.
        cv2.rectangle(
            resultado,
            (10, 10),
            (500, 55),
            (0, 0, 0),
            -1
        )

        cv2.putText(
            resultado,
            f'Quantidade: {quantidade}',
            (20, 43),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 255),
            2
        )

        return resultado

    # =========================================================
    # MÉTODO PRINCIPAL
    # =========================================================

    def run(self, imagem):
        """
        Recebe uma imagem BGR e retorna:

        1. imagem com os objetos marcados;
        2. máscara limpa;
        3. quantidade de objetos encontrados.

        O método não carrega a imagem do disco.
        Quem faz isso é a função main.
        """

        if imagem is None:
            raise ValueError('A imagem recebida é inválida.')

        # 1. Segmenta a cor.
        mascara = self.criar_mascara(imagem)

        # 2. Remove ruídos e preenche buracos.
        mascara_limpa = self.limpar_mascara(mascara)

        # 3. Encontra os objetos válidos.
        contornos_validos = self.encontrar_contornos_validos(
            mascara_limpa
        )

        # 4. Desenha os objetos na imagem.
        resultado = self.desenhar_resultado(
            imagem,
            contornos_validos
        )

        quantidade = len(contornos_validos)

        return resultado, mascara_limpa, quantidade


# =============================================================
# ARGUMENTOS DO TERMINAL
# =============================================================

def ler_argumentos():
    """
    Permite escolher imagem, cor e área sem alterar o código.
    """

    parser = argparse.ArgumentParser(
        description='Conta objetos de determinada cor em uma imagem.'
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
        help='Cor dos objetos que serão contados.'
    )

    parser.add_argument(
        '--area-minima',
        type=float,
        default=AREA_MINIMA_PADRAO,
        help='Área mínima para considerar um contorno como objeto.'
    )

    parser.add_argument(
        '--sem-janela',
        action='store_true',
        help='Salva os resultados sem abrir janelas.'
    )

    return parser.parse_args()


# =============================================================
# MAIN
# =============================================================

def main():
    argumentos = ler_argumentos()

    caminho_imagem = Path(argumentos.imagem)

    # Carrega a imagem no formato BGR.
    imagem = cv2.imread(str(caminho_imagem))

    if imagem is None:
        print(
            f'ERRO: não foi possível carregar a imagem:\n'
            f'{caminho_imagem}'
        )
        return

    try:
        detector = ContadorObjetosPorCor(
            cor=argumentos.cor,
            area_minima=argumentos.area_minima
        )

        resultado, mascara, quantidade = detector.run(imagem)

    except ValueError as erro:
        print(f'ERRO: {erro}')
        return

    # Cria a pasta de resultados caso ela não exista.
    pasta_resultados = Path('resultados')
    pasta_resultados.mkdir(parents=True, exist_ok=True)

    caminho_mascara = pasta_resultados / 'mascara.png'
    caminho_resultado = (
        pasta_resultados / 'objetos_encontrados.png'
    )

    # Salva os resultados.
    cv2.imwrite(str(caminho_mascara), mascara)
    cv2.imwrite(str(caminho_resultado), resultado)

    print('==========================================')
    print('RESULTADO')
    print('==========================================')
    print(f'Imagem: {caminho_imagem}')
    print(f'Cor procurada: {argumentos.cor}')
    print(f'Área mínima: {argumentos.area_minima:.1f} pixels')
    print(f'Quantidade de objetos encontrados: {quantidade}')
    print(f'Máscara salva em: {caminho_mascara}')
    print(f'Resultado salvo em: {caminho_resultado}')
    print('==========================================')

    # Abre as janelas, a menos que --sem-janela seja utilizado.
    if not argumentos.sem_janela:
        cv2.imshow('Imagem original', imagem)
        cv2.imshow('Mascara limpa', mascara)
        cv2.imshow('Objetos encontrados', resultado)

        print('Pressione qualquer tecla nas imagens para fechar.')

        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

# python3 contar_objetos_por_cor.py imagens/entrada.png --cor vermelho --area-minima 500

#cores incluidas
#vermelho
#laranja
#amarelo
#verde
#azul
#roxo
#branco
#preto