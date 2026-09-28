import cv2
import numpy as np


# Troque pelo caminho da imagem da prova.
CAMINHO_IMAGEM = 'imagem.jpg'


# Escolha o exemplo:
#
# 'criar'
# 'copiar'
# 'cortar'
# 'desenhar'
# 'colar_recorte'
# 'todos'
EXEMPLO = 'todos'


class EditarImagem:

    # ============================================================
    # CRIAR, CORTAR E DESENHAR EM IMAGENS
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - criar uma imagem vazia;
    # - criar uma imagem preta, branca ou colorida;
    # - copiar uma imagem;
    # - cortar uma região;
    # - selecionar uma parte da imagem;
    # - desenhar retângulos, círculos ou linhas;
    # - escrever textos;
    # - colar um recorte em outra região.
    #
    # REGRA MAIS IMPORTANTE:
    #
    # Pontos e desenhos usam:
    #
    # (x, y)
    #
    # Recortes de matriz usam:
    #
    # imagem[y1:y2, x1:x2]
    #
    # Portanto, no recorte colocamos primeiro Y
    # e depois X.

    def __init__(self):

        self.imagem = None

    def carregar_imagem(self, caminho):

        # Lê a imagem no formato BGR.
        self.imagem = cv2.imread(caminho)

        if self.imagem is None:

            raise FileNotFoundError(
                f'Não foi possível abrir: {caminho}'
            )

        print(f'Imagem carregada: {caminho}')
        print(f'Formato: {self.imagem.shape}')

    # ============================================================
    # CRIAR UMA IMAGEM VAZIA
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - criar uma imagem do zero;
    # - criar uma tela preta;
    # - criar uma tela branca;
    # - criar uma imagem de determinada cor.
    #
    # np.zeros cria uma matriz preenchida com zeros.
    #
    # No BGR:
    #
    # (0, 0, 0)       = preto
    # (255, 255, 255) = branco
    # (255, 0, 0)     = azul
    # (0, 255, 0)     = verde
    # (0, 0, 255)     = vermelho

    def criar_imagens(self):

        altura = 480
        largura = 640

        # Cria uma imagem preta.
        imagem_preta = np.zeros(
            (altura, largura, 3),
            dtype=np.uint8
        )

        # Cria uma imagem branca com o mesmo tamanho.
        imagem_branca = np.full(
            (altura, largura, 3),
            255,
            dtype=np.uint8
        )

        # Cria uma imagem azul.
        imagem_azul = np.zeros(
            (altura, largura, 3),
            dtype=np.uint8
        )

        # Preenche todos os pixels com azul.
        imagem_azul[:] = (255, 0, 0)

        # Cria uma imagem com uma cor personalizada.
        imagem_colorida = np.zeros(
            (altura, largura, 3),
            dtype=np.uint8
        )

        # BGR: azul, verde e vermelho.
        imagem_colorida[:] = (80, 150, 220)

        cv2.imshow(
            'Imagem preta',
            imagem_preta
        )

        cv2.imshow(
            'Imagem branca',
            imagem_branca
        )

        cv2.imshow(
            'Imagem azul',
            imagem_azul
        )

        cv2.imshow(
            'Imagem colorida',
            imagem_colorida
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # COPIAR UMA IMAGEM
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - alterar uma imagem sem modificar a original;
    # - criar uma imagem de saída;
    # - desenhar em uma cópia.
    #
    # Use:
    #
    # copia = imagem.copy()
    #
    # Evite:
    #
    # copia = imagem
    #
    # No segundo caso, as duas variáveis apontam para
    # a mesma imagem. Alterar uma também altera a outra.

    def copiar_imagem(self):

        copia = self.imagem.copy()

        # Pinta uma região da cópia de vermelho.
        copia[
            50:200,
            50:300
        ] = (0, 0, 255)

        cv2.imshow(
            'Imagem original',
            self.imagem
        )

        cv2.imshow(
            'Cópia alterada',
            copia
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # CORTAR UMA REGIÃO
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - recortar um objeto;
    # - selecionar uma região;
    # - trabalhar somente com uma parte da imagem;
    # - criar uma ROI retangular.
    #
    # Recorte:
    #
    # imagem[y1:y2, x1:x2]
    #
    # x representa a coluna.
    # y representa a linha.
    #
    # O valor final não está incluído.
    #
    # Se usar:
    #
    # imagem[100:300, 200:500]
    #
    # O recorte vai:
    #
    # de Y = 100 até Y = 299;
    # de X = 200 até X = 499.

    def cortar_imagem(self):

        altura, largura = self.imagem.shape[:2]

        # Define uma região central.
        x1 = largura // 4
        x2 = 3 * largura // 4

        y1 = altura // 4
        y2 = 3 * altura // 4

        # Primeiro Y, depois X.
        recorte = self.imagem[
            y1:y2,
            x1:x2
        ]

        print(
            f'Imagem original: {self.imagem.shape}'
        )

        print(
            f'Recorte: {recorte.shape}'
        )

        cv2.imshow(
            'Imagem original',
            self.imagem
        )

        cv2.imshow(
            'Região recortada',
            recorte
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # DESENHAR NA IMAGEM
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - marcar uma região;
    # - desenhar uma caixa em um objeto;
    # - marcar o centro de um objeto;
    # - desenhar uma linha;
    # - escrever um resultado na imagem.
    #
    # Nos desenhos, as coordenadas são:
    #
    # (x, y)

    def desenhar_na_imagem(self):

        # Faz uma cópia para preservar a original.
        resultado = self.imagem.copy()

        altura, largura = resultado.shape[:2]

        centro_x = largura // 2
        centro_y = altura // 2

        # Desenha um retângulo verde.
        #
        # Parâmetros:
        #
        # imagem;
        # canto superior esquerdo;
        # canto inferior direito;
        # cor BGR;
        # espessura.
        cv2.rectangle(
            resultado,
            (50, 50),
            (250, 200),
            (0, 255, 0),
            3
        )

        # Desenha um círculo vermelho no centro.
        #
        # -1 preenche o círculo.
        cv2.circle(
            resultado,
            (centro_x, centro_y),
            30,
            (0, 0, 255),
            -1
        )

        # Desenha uma linha azul.
        cv2.line(
            resultado,
            (0, 0),
            (largura - 1, altura - 1),
            (255, 0, 0),
            3
        )

        # Escreve um texto na imagem.
        cv2.putText(
            resultado,
            'Objeto encontrado',
            (50, altura - 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            'Resultado',
            resultado
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # COLAR UM RECORTE
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - copiar uma região para outro lugar;
    # - substituir uma parte da imagem;
    # - montar uma nova imagem;
    # - duplicar um objeto.
    #
    # A região de destino precisa possuir exatamente
    # o mesmo tamanho do recorte.

    def colar_recorte(self):

        resultado = self.imagem.copy()

        altura, largura = resultado.shape[:2]

        # Evita usar coordenadas maiores que a imagem.
        tamanho = min(
            100,
            altura // 3,
            largura // 3
        )

        # Recorta um quadrado do canto superior esquerdo.
        recorte = resultado[
            0:tamanho,
            0:tamanho
        ].copy()

        # Define a posição onde o recorte será colado.
        destino_x = largura - tamanho
        destino_y = altura - tamanho

        # A região de destino possui o mesmo tamanho.
        resultado[
            destino_y:destino_y + tamanho,
            destino_x:destino_x + tamanho
        ] = recorte

        cv2.imshow(
            'Imagem original',
            self.imagem
        )

        cv2.imshow(
            'Recorte colado',
            resultado
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # MOSTRAR TODOS OS EXEMPLOS
    # ============================================================

    def mostrar_todos(self):

        resultado = self.imagem.copy()

        altura, largura = resultado.shape[:2]

        # Região central.
        x1 = largura // 4
        x2 = 3 * largura // 4

        y1 = altura // 4
        y2 = 3 * altura // 4

        recorte = resultado[
            y1:y2,
            x1:x2
        ]

        # Marca na imagem onde o recorte foi feito.
        cv2.rectangle(
            resultado,
            (x1, y1),
            (x2, y2),
            (0, 255, 255),
            3
        )

        # Marca o centro da imagem.
        cv2.circle(
            resultado,
            (largura // 2, altura // 2),
            15,
            (0, 0, 255),
            -1
        )

        cv2.putText(
            resultado,
            'Regiao de interesse',
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        cv2.imshow(
            'Imagem marcada',
            resultado
        )

        cv2.imshow(
            'Região recortada',
            recorte
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():

    editor = EditarImagem()

    # O exemplo de criação não precisa carregar
    # uma imagem existente.
    if EXEMPLO == 'criar':

        editor.criar_imagens()
        return

    # Os outros exemplos precisam de uma imagem.
    editor.carregar_imagem(
        CAMINHO_IMAGEM
    )

    exemplos = {
        'copiar': editor.copiar_imagem,
        'cortar': editor.cortar_imagem,
        'desenhar': editor.desenhar_na_imagem,
        'colar_recorte': editor.colar_recorte,
        'todos': editor.mostrar_todos
    }

    if EXEMPLO not in exemplos:

        raise ValueError(
            f'Exemplo inválido: {EXEMPLO}'
        )

    exemplos[EXEMPLO]()


if __name__ == '__main__':
    main()

# Para desenhar:
#(x, y)

# Para cortar:
#imagem[y1:y2, x1:x2]