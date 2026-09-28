import cv2
import numpy as np


# Troque pelo caminho da imagem fornecida.
CAMINHO_IMAGEM = 'imagem.jpg'


# Escolha o exemplo:
#
# 'marcar_roi'
# 'recortar_roi'
# 'alterar_roi'
# 'estatisticas'
# 'encontrar_pixels'
# 'processar_roi'
# 'todos'
EXEMPLO = 'todos'


class UsarROI:

    # ============================================================
    # USANDO ROI E NUMPY
    # ============================================================
    #
    # ROI significa Region of Interest:
    #
    # região de interesse.
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - trabalhar somente com uma parte da imagem;
    # - recortar uma região;
    # - analisar apenas uma área;
    # - calcular estatísticas dos pixels;
    # - encontrar coordenadas;
    # - modificar somente uma região;
    # - procurar um objeto apenas em parte da imagem.
    #
    # REGRA IMPORTANTE:
    #
    # Para cortar uma matriz:
    #
    # imagem[y1:y2, x1:x2]
    #
    # Primeiro usamos Y porque Y representa as linhas.
    #
    # Depois usamos X porque X representa as colunas.

    def __init__(self):

        self.imagem = None

        # Coordenadas da ROI.
        #
        # Elas serão definidas depois que soubermos
        # o tamanho da imagem.
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0

    def carregar_imagem(self, caminho):

        self.imagem = cv2.imread(caminho)

        if self.imagem is None:

            raise FileNotFoundError(
                f'Não foi possível abrir: {caminho}'
            )

        altura, largura = self.imagem.shape[:2]

        # Neste exemplo, a ROI será a região central.
        #
        # Na prova, troque pelas coordenadas fornecidas
        # ou pela região que deseja analisar.
        self.x1 = largura // 4
        self.x2 = 3 * largura // 4

        self.y1 = altura // 4
        self.y2 = 3 * altura // 4

        print(f'Imagem: {largura}x{altura}')

        print(
            f'ROI: x={self.x1}:{self.x2}, '
            f'y={self.y1}:{self.y2}'
        )

    def obter_roi(self):

        # Cria a ROI usando fatiamento.
        #
        # O valor final não está incluído.
        roi = self.imagem[
            self.y1:self.y2,
            self.x1:self.x2
        ]

        return roi

    # ============================================================
    # MARCAR UMA ROI
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - mostrar onde fica a região de interesse;
    # - desenhar uma caixa em determinada região;
    # - conferir visualmente as coordenadas.
    #
    # Para desenhar, usamos:
    #
    # (x, y)
    #
    # Diferentemente do recorte, que usa:
    #
    # [y, x]

    def marcar_roi(self):

        resultado = self.imagem.copy()

        cv2.rectangle(
            resultado,
            (self.x1, self.y1),
            (self.x2, self.y2),
            (0, 255, 255),
            3
        )

        cv2.putText(
            resultado,
            'ROI',
            (self.x1, max(self.y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        cv2.imshow(
            'ROI marcada',
            resultado
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # RECORTAR UMA ROI
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - cortar determinada parte da imagem;
    # - criar uma nova imagem contendo somente a ROI;
    # - ignorar o restante da imagem.

    def recortar_roi(self):

        roi = self.obter_roi()

        print(
            f'Formato da imagem: {self.imagem.shape}'
        )

        print(
            f'Formato da ROI: {roi.shape}'
        )

        cv2.imshow(
            'Imagem original',
            self.imagem
        )

        cv2.imshow(
            'ROI recortada',
            roi
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # ALTERAR SOMENTE A ROI
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - pintar uma região;
    # - apagar uma parte da imagem;
    # - modificar apenas uma área;
    # - manter o restante da imagem igual.
    #
    # IMPORTANTE:
    #
    # Se não quiser alterar a imagem original,
    # faça uma cópia antes.

    def alterar_roi(self):

        resultado = self.imagem.copy()

        # Pinta toda a ROI de verde.
        resultado[
            self.y1:self.y2,
            self.x1:self.x2
        ] = (0, 255, 0)

        cv2.imshow(
            'Imagem original',
            self.imagem
        )

        cv2.imshow(
            'ROI alterada',
            resultado
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # CALCULAR ESTATÍSTICAS
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - calcular o menor valor;
    # - calcular o maior valor;
    # - calcular a média dos pixels;
    # - comparar regiões;
    # - calcular a intensidade média.
    #
    # NumPy possui:
    #
    # np.min
    # np.max
    # np.mean
    # np.sum
    # np.unique

    def calcular_estatisticas(self):

        roi = self.obter_roi()

        menor = np.min(roi)
        maior = np.max(roi)
        media = np.mean(roi)
        soma = np.sum(roi)

        print(f'Menor valor: {menor}')
        print(f'Maior valor: {maior}')
        print(f'Média geral: {media:.2f}')
        print(f'Soma dos valores: {soma}')

        # Calcula a média de cada canal.
        media_azul = np.mean(roi[:, :, 0])
        media_verde = np.mean(roi[:, :, 1])
        media_vermelho = np.mean(roi[:, :, 2])

        print(f'Média do azul: {media_azul:.2f}')
        print(f'Média do verde: {media_verde:.2f}')
        print(
            f'Média do vermelho: {media_vermelho:.2f}'
        )

        # Mostra os valores únicos da ROI.
        #
        # Em uma imagem grande, essa lista pode ser longa.
        valores_unicos = np.unique(roi)

        print(
            f'Quantidade de valores diferentes: '
            f'{len(valores_unicos)}'
        )

    # ============================================================
    # ENCONTRAR PIXELS COM NUMPY
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - encontrar pixels que cumprem uma condição;
    # - encontrar coordenadas;
    # - contar pixels;
    # - localizar regiões claras ou escuras.
    #
    # np.where devolve os índices onde
    # uma condição é verdadeira.

    def encontrar_pixels(self):

        # Converte para tons de cinza.
        cinza = cv2.cvtColor(
            self.imagem,
            cv2.COLOR_BGR2GRAY
        )

        # Procura pixels com intensidade maior que 200.
        linhas, colunas = np.where(
            cinza > 200
        )

        quantidade = len(linhas)

        print(
            f'Pixels com intensidade maior que 200: '
            f'{quantidade}'
        )

        if quantidade > 0:

            # O primeiro resultado encontrado.
            primeira_linha = linhas[0]
            primeira_coluna = colunas[0]

            print(
                f'Primeiro pixel encontrado: '
                f'linha={primeira_linha}, '
                f'coluna={primeira_coluna}'
            )

            # Calcula a posição média dos pixels.
            centro_y = int(np.mean(linhas))
            centro_x = int(np.mean(colunas))

            print(
                f'Centro aproximado: '
                f'x={centro_x}, y={centro_y}'
            )

            resultado = self.imagem.copy()

            cv2.circle(
                resultado,
                (centro_x, centro_y),
                10,
                (0, 0, 255),
                -1
            )

            cv2.imshow(
                'Centro dos pixels encontrados',
                resultado
            )

            cv2.waitKey(0)
            cv2.destroyAllWindows()

    # ============================================================
    # PROCESSAR SOMENTE A ROI
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - aplicar um processamento somente em uma região;
    # - deixar apenas a ROI em cinza;
    # - aplicar filtro somente em parte da imagem.
    #
    # Neste exemplo, somente a ROI será convertida
    # para tons de cinza.

    def processar_roi(self):

        resultado = self.imagem.copy()

        roi = resultado[
            self.y1:self.y2,
            self.x1:self.x2
        ]

        # Converte a ROI para cinza.
        roi_cinza = cv2.cvtColor(
            roi,
            cv2.COLOR_BGR2GRAY
        )

        # A imagem original possui três canais.
        #
        # Por isso, convertemos a ROI cinza novamente
        # para três canais antes de colocá-la no resultado.
        roi_cinza_bgr = cv2.cvtColor(
            roi_cinza,
            cv2.COLOR_GRAY2BGR
        )

        resultado[
            self.y1:self.y2,
            self.x1:self.x2
        ] = roi_cinza_bgr

        cv2.rectangle(
            resultado,
            (self.x1, self.y1),
            (self.x2, self.y2),
            (0, 255, 255),
            2
        )

        cv2.imshow(
            'Somente a ROI em cinza',
            resultado
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # MOSTRAR TODOS OS PRINCIPAIS RESULTADOS
    # ============================================================

    def mostrar_todos(self):

        roi = self.obter_roi()

        resultado = self.imagem.copy()

        cv2.rectangle(
            resultado,
            (self.x1, self.y1),
            (self.x2, self.y2),
            (0, 255, 255),
            3
        )

        centro_x = (self.x1 + self.x2) // 2
        centro_y = (self.y1 + self.y2) // 2

        cv2.circle(
            resultado,
            (centro_x, centro_y),
            10,
            (0, 0, 255),
            -1
        )

        print(
            f'Centro da ROI: '
            f'x={centro_x}, y={centro_y}'
        )

        print(
            f'Média da ROI: {np.mean(roi):.2f}'
        )

        cv2.imshow(
            'Imagem com ROI',
            resultado
        )

        cv2.imshow(
            'ROI recortada',
            roi
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():

    processador = UsarROI()

    processador.carregar_imagem(
        CAMINHO_IMAGEM
    )

    exemplos = {
        'marcar_roi': processador.marcar_roi,
        'recortar_roi': processador.recortar_roi,
        'alterar_roi': processador.alterar_roi,
        'estatisticas': processador.calcular_estatisticas,
        'encontrar_pixels': processador.encontrar_pixels,
        'processar_roi': processador.processar_roi,
        'todos': processador.mostrar_todos
    }

    if EXEMPLO not in exemplos:

        raise ValueError(
            f'Exemplo inválido: {EXEMPLO}'
        )

    exemplos[EXEMPLO]()


if __name__ == '__main__':
    main()