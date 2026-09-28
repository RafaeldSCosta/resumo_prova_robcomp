#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np


# =============================================================
# CONFIGURAÇÕES
# =============================================================

CAMINHO_PADRAO = 'imagens/entrada.png'
CORES_PADRAO = ['vermelho']

AREA_MINIMA_PADRAO = 500.0
TAMANHO_KERNEL = 5


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
            np.array([11, 100, 80]),
            np.array([24, 255, 255])
        ),
    ],

    'amarelo': [
        (
            np.array([25, 80, 80]),
            np.array([35, 255, 255])
        ),
    ],

    'verde': [
        (
            np.array([36, 60, 40]),
            np.array([79, 255, 255])
        ),
    ],

    'ciano': [
        (
            np.array([80, 50, 50]),
            np.array([99, 255, 255])
        ),
    ],

    'azul': [
        (
            np.array([100, 70, 40]),
            np.array([130, 255, 255])
        ),
    ],

    'roxo': [
        (
            np.array([131, 60, 40]),
            np.array([149, 255, 255])
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


# Cor usada para desenhar cada categoria.
# O formato do OpenCV é BGR, e não RGB.
CORES_DESENHO = {
    'vermelho': (0, 0, 255),
    'laranja': (0, 128, 255),
    'amarelo': (0, 255, 255),
    'verde': (0, 200, 0),
    'ciano': (255, 255, 0),
    'azul': (255, 0, 0),
    'roxo': (180, 0, 180),
    'rosa': (203, 192, 255),
    'branco': (255, 255, 255),
    'preto': (50, 50, 50),
}


class EncontrarMaiorObjeto:
    """
    USE QUANDO O PROFESSOR PEDIR:

    - encontrar o maior objeto;
    - comparar áreas;
    - encontrar o maior objeto de uma cor;
    - comparar objetos de diferentes cores;
    - ordenar objetos do maior para o menor.

    O método run recebe uma imagem já carregada.
    """

    def __init__(
        self,
        cores=None,
        area_minima=AREA_MINIMA_PADRAO
    ):
        if cores is None:
            cores = CORES_PADRAO

        # Remove cores repetidas, mantendo a ordem.
        self.cores = list(
            dict.fromkeys(
                cor.lower() for cor in cores
            )
        )

        self.area_minima = float(area_minima)

        for cor in self.cores:
            if cor not in FAIXAS_HSV:
                raise ValueError(
                    f'Cor não cadastrada: {cor}'
                )

        self.kernel = np.ones(
            (TAMANHO_KERNEL, TAMANHO_KERNEL),
            dtype=np.uint8
        )

    # =========================================================
    # MÁSCARA
    # =========================================================

    def criar_mascara(self, imagem_hsv, cor):
        """
        Cria uma máscara para uma cor.
        """

        mascara_final = np.zeros(
            imagem_hsv.shape[:2],
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
        Remove ruídos pequenos e preenche buracos.
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
    # ENCONTRAR OBJETOS
    # =========================================================

    def encontrar_objetos_da_cor(self, mascara, cor):
        """
        Encontra todos os objetos válidos de uma cor.
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
                'cor': cor,
                'area': area,
                'centro': (centro_x, centro_y),
                'x': x,
                'y': y,
                'largura': largura,
                'altura': altura,
                'contorno': contorno,
            })

        return objetos

    # =========================================================
    # DESENHAR
    # =========================================================

    def desenhar_todos_objetos(self, imagem, objetos):
        """
        Desenha todos os objetos encontrados com contorno fino.
        """

        resultado = imagem.copy()

        for indice, objeto in enumerate(objetos, start=1):
            cor_nome = objeto['cor']
            cor_desenho = CORES_DESENHO[cor_nome]

            cv2.drawContours(
                resultado,
                [objeto['contorno']],
                -1,
                cor_desenho,
                2
            )

            centro_x, centro_y = objeto['centro']

            cv2.circle(
                resultado,
                (centro_x, centro_y),
                4,
                cor_desenho,
                -1
            )

            cv2.putText(
                resultado,
                f'{indice}: {cor_nome}',
                (
                    objeto['x'],
                    max(20, objeto['y'] - 8)
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                cor_desenho,
                2
            )

        return resultado

    def destacar_maior(self, resultado, maior_objeto):
        """
        Destaca o maior objeto com contorno, caixa e centro.
        """

        contorno = maior_objeto['contorno']
        area = maior_objeto['area']
        cor = maior_objeto['cor']

        centro_x, centro_y = maior_objeto['centro']

        x = maior_objeto['x']
        y = maior_objeto['y']
        largura = maior_objeto['largura']
        altura = maior_objeto['altura']

        # Contorno verde grosso.
        cv2.drawContours(
            resultado,
            [contorno],
            -1,
            (0, 255, 0),
            5
        )

        # Caixa branca ao redor do maior.
        cv2.rectangle(
            resultado,
            (x, y),
            (x + largura, y + altura),
            (255, 255, 255),
            3
        )

        # Centro do maior objeto.
        cv2.circle(
            resultado,
            (centro_x, centro_y),
            9,
            (0, 0, 255),
            -1
        )

        # Fundo para o texto.
        texto_y = max(65, y - 15)

        cv2.rectangle(
            resultado,
            (x, texto_y - 55),
            (min(resultado.shape[1] - 1, x + 350), texto_y + 5),
            (0, 0, 0),
            -1
        )

        cv2.putText(
            resultado,
            'MAIOR OBJETO',
            (x + 5, texto_y - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.70,
            (0, 255, 0),
            2
        )

        cv2.putText(
            resultado,
            f'{cor} - area: {area:.0f}',
            (x + 5, texto_y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.60,
            (0, 255, 255),
            2
        )

        return resultado

    # =========================================================
    # RUN
    # =========================================================

    def run(self, imagem):
        """
        Retorna:

        1. imagem final;
        2. máscara combinada;
        3. lista ordenada de objetos;
        4. maior objeto.
        """

        if imagem is None:
            raise ValueError('A imagem recebida é inválida.')

        imagem_hsv = cv2.cvtColor(
            imagem,
            cv2.COLOR_BGR2HSV
        )

        mascara_combinada = np.zeros(
            imagem.shape[:2],
            dtype=np.uint8
        )

        todos_objetos = []

        # Processa cada cor solicitada.
        for cor in self.cores:
            mascara_cor = self.criar_mascara(
                imagem_hsv,
                cor
            )

            mascara_cor = self.limpar_mascara(
                mascara_cor
            )

            mascara_combinada = cv2.bitwise_or(
                mascara_combinada,
                mascara_cor
            )

            objetos_da_cor = self.encontrar_objetos_da_cor(
                mascara_cor,
                cor
            )

            todos_objetos.extend(
                objetos_da_cor
            )

        if not todos_objetos:
            raise ValueError(
                'Nenhum objeto válido foi encontrado.'
            )

        # Ordena do maior para o menor.
        objetos_ordenados = sorted(
            todos_objetos,
            key=lambda objeto: objeto['area'],
            reverse=True
        )

        # O primeiro da lista é o maior.
        maior_objeto = objetos_ordenados[0]

        resultado = self.desenhar_todos_objetos(
            imagem,
            objetos_ordenados
        )

        resultado = self.destacar_maior(
            resultado,
            maior_objeto
        )

        return (
            resultado,
            mascara_combinada,
            objetos_ordenados,
            maior_objeto
        )


# =============================================================
# CSV
# =============================================================

def salvar_ranking_csv(objetos, caminho):
    """
    Salva os objetos do maior para o menor.
    """

    campos = [
        'posicao',
        'cor',
        'area',
        'centro_x',
        'centro_y',
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

        for posicao, objeto in enumerate(objetos, start=1):
            centro_x, centro_y = objeto['centro']

            escritor.writerow({
                'posicao': posicao,
                'cor': objeto['cor'],
                'area': round(objeto['area'], 2),
                'centro_x': centro_x,
                'centro_y': centro_y,
            })


# =============================================================
# ARGUMENTOS
# =============================================================

def ler_argumentos():
    parser = argparse.ArgumentParser(
        description='Encontra o maior objeto da imagem.'
    )

    parser.add_argument(
        'imagem',
        nargs='?',
        default=CAMINHO_PADRAO,
        help='Caminho da imagem.'
    )

    parser.add_argument(
        '--cores',
        nargs='+',
        default=CORES_PADRAO,
        choices=list(FAIXAS_HSV.keys()),
        help='Cores que serão comparadas.'
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
        help='Salva os resultados sem abrir janelas.'
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
        detector = EncontrarMaiorObjeto(
            cores=argumentos.cores,
            area_minima=argumentos.area_minima
        )

        (
            resultado,
            mascara,
            objetos,
            maior_objeto
        ) = detector.run(imagem)

    except ValueError as erro:
        print(f'ERRO: {erro}')
        return

    pasta_resultados = Path('resultados')
    pasta_resultados.mkdir(
        parents=True,
        exist_ok=True
    )

    caminho_mascara = (
        pasta_resultados / 'mascara_combinada.png'
    )

    caminho_resultado = (
        pasta_resultados / 'maior_objeto.png'
    )

    caminho_csv = (
        pasta_resultados / 'ranking_areas.csv'
    )

    cv2.imwrite(
        str(caminho_mascara),
        mascara
    )

    cv2.imwrite(
        str(caminho_resultado),
        resultado
    )

    salvar_ranking_csv(
        objetos,
        caminho_csv
    )

    print('==========================================')
    print('RANKING DE ÁREAS')
    print('==========================================')

    for posicao, objeto in enumerate(objetos, start=1):
        print(
            f'{posicao}º - '
            f'{objeto["cor"]}: '
            f'{objeto["area"]:.2f} pixels '
            f'no centro {objeto["centro"]}'
        )

    print('==========================================')
    print('MAIOR OBJETO')
    print('==========================================')
    print(f'Cor: {maior_objeto["cor"]}')
    print(f'Área: {maior_objeto["area"]:.2f} pixels')
    print(f'Centro: {maior_objeto["centro"]}')
    print('==========================================')
    print(f'Resultado salvo em: {caminho_resultado}')
    print(f'Ranking salvo em: {caminho_csv}')

    if not argumentos.sem_janela:
        cv2.imshow(
            'Mascara combinada',
            mascara
        )

        cv2.imshow(
            'Maior objeto',
            resultado
        )

        print('Pressione qualquer tecla nas imagens para fechar.')

        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()