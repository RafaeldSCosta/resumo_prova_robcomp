import cv2


# Troque pelo caminho da imagem fornecida na prova.
CAMINHO_IMAGEM = 'imagem.jpg'


# Escolha o exemplo que deseja executar:
#
# 'mostrar'
# 'informacoes'
# 'cinza'
# 'canais'
# 'transpor'
# 'todos'
EXEMPLO = 'todos'


class ProcessarImagem:

    # ============================================================
    # LER E PROCESSAR UMA IMAGEM
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - abrir uma imagem;
    # - mostrar uma imagem;
    # - verificar altura e largura;
    # - acessar pixels;
    # - converter a imagem para cinza;
    # - separar os canais azul, verde e vermelho;
    # - transpor a imagem;
    # - trabalhar com a imagem como matriz NumPy.
    #
    # IMPORTANTE:
    #
    # O OpenCV trabalha no formato BGR:
    #
    # canal 0: azul;
    # canal 1: verde;
    # canal 2: vermelho.
    #
    # Uma imagem colorida possui:
    #
    # imagem.shape = (altura, largura, 3)

    def __init__(self):

        # As imagens começam vazias.
        #
        # Elas serão preenchidas depois que
        # carregar_imagem for executada.
        self.bgr = None
        self.cinza = None

        self.azul = None
        self.verde = None
        self.vermelho = None

    # ============================================================
    # CARREGAR UMA IMAGEM
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - ler uma imagem do computador;
    # - receber o caminho de uma imagem;
    # - armazenar a imagem em uma variável da classe.
    #
    # O QUE TROCAR:
    #
    # Troque CAMINHO_IMAGEM no começo do arquivo.
    #
    # Exemplo:
    #
    # CAMINHO_IMAGEM = 'imagens/baloes.png'

    def carregar_imagem(self, caminho):

        # imread lê o arquivo e transforma a imagem
        # em uma matriz NumPy.
        self.bgr = cv2.imread(caminho)

        # Quando o arquivo não existe ou o caminho
        # está errado, imread devolve None.
        if self.bgr is None:

            raise FileNotFoundError(
                f'Não foi possível abrir a imagem: {caminho}'
            )

        print(f'Imagem carregada: {caminho}')

    # ============================================================
    # MOSTRAR INFORMAÇÕES DA IMAGEM
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - descobrir o tamanho da imagem;
    # - descobrir quantos canais existem;
    # - acessar um pixel;
    # - verificar o tipo dos valores.
    #
    # LEMBRE:
    #
    # Na matriz, usamos:
    #
    # imagem[linha, coluna]
    #
    # Linha corresponde ao eixo Y.
    # Coluna corresponde ao eixo X.

    def mostrar_informacoes(self):

        altura, largura, canais = self.bgr.shape

        print(f'Altura: {altura} pixels')
        print(f'Largura: {largura} pixels')
        print(f'Canais: {canais}')
        print(f'Tipo dos pixels: {self.bgr.dtype}')

        # Escolhe um pixel existente na imagem.
        linha = min(100, altura - 1)
        coluna = min(200, largura - 1)

        pixel = self.bgr[linha, coluna]

        print(
            f'Pixel na linha {linha}, '
            f'coluna {coluna}: {pixel}'
        )

        # O pixel possui a ordem:
        #
        # [azul, verde, vermelho]
        azul = pixel[0]
        verde = pixel[1]
        vermelho = pixel[2]

        print(f'Azul: {azul}')
        print(f'Verde: {verde}')
        print(f'Vermelho: {vermelho}')

    # ============================================================
    # MOSTRAR A IMAGEM
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - abrir a imagem em uma janela;
    # - conferir se a leitura funcionou.
    #
    # waitKey(0):
    # espera até alguma tecla ser pressionada.
    #
    # destroyAllWindows:
    # fecha as janelas abertas pelo OpenCV.

    def mostrar_imagem(self):

        cv2.imshow(
            'Imagem original',
            self.bgr
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # CONVERTER PARA TONS DE CINZA
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - remover as cores;
    # - criar uma imagem em tons de cinza;
    # - trabalhar apenas com intensidade;
    # - preparar a imagem para uma limiarização.
    #
    # Uma imagem colorida possui formato:
    #
    # (altura, largura, 3)
    #
    # Uma imagem cinza possui formato:
    #
    # (altura, largura)

    def converter_para_cinza(self):

        self.cinza = cv2.cvtColor(
            self.bgr,
            cv2.COLOR_BGR2GRAY
        )

        print(
            f'Formato colorido: {self.bgr.shape}'
        )

        print(
            f'Formato em cinza: {self.cinza.shape}'
        )

        cv2.imshow(
            'Imagem original',
            self.bgr
        )

        cv2.imshow(
            'Imagem em tons de cinza',
            self.cinza
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # SEPARAR OS CANAIS DE COR
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - mostrar o canal azul;
    # - mostrar o canal verde;
    # - mostrar o canal vermelho;
    # - analisar uma cor separadamente.
    #
    # Quanto mais claro um pixel aparecer em um canal,
    # maior é a intensidade daquela cor nesse ponto.

    def separar_canais(self):

        self.azul, self.verde, self.vermelho = cv2.split(
            self.bgr
        )

        cv2.imshow(
            'Canal azul',
            self.azul
        )

        cv2.imshow(
            'Canal verde',
            self.verde
        )

        cv2.imshow(
            'Canal vermelho',
            self.vermelho
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # ACESSAR UM CANAL SEM USAR SPLIT
    # ============================================================
    #
    # A imagem é uma matriz com três dimensões:
    #
    # imagem[linhas, colunas, canais]
    #
    # Os dois pontos significam:
    #
    # "pegue todos os valores dessa dimensão".
    #
    # Portanto:
    #
    # imagem[:, :, 0] pega todo o canal azul.
    # imagem[:, :, 1] pega todo o canal verde.
    # imagem[:, :, 2] pega todo o canal vermelho.

    def separar_canais_com_numpy(self):

        azul = self.bgr[:, :, 0]
        verde = self.bgr[:, :, 1]
        vermelho = self.bgr[:, :, 2]

        cv2.imshow(
            'Azul usando NumPy',
            azul
        )

        cv2.imshow(
            'Verde usando NumPy',
            verde
        )

        cv2.imshow(
            'Vermelho usando NumPy',
            vermelho
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # TRANSPOR A IMAGEM
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - trocar as linhas pelas colunas;
    # - transpor a matriz da imagem;
    # - trocar altura e largura.
    #
    # A ordem original é:
    #
    # altura, largura, canais
    #
    # A nova ordem será:
    #
    # largura, altura, canais

    def transpor_imagem(self):

        transposta = self.bgr.transpose(
            (1, 0, 2)
        )

        print(
            f'Formato original: {self.bgr.shape}'
        )

        print(
            f'Formato transposto: {transposta.shape}'
        )

        cv2.imshow(
            'Original',
            self.bgr
        )

        cv2.imshow(
            'Transposta',
            transposta
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # ============================================================
    # EXECUTAR TODOS OS EXEMPLOS
    # ============================================================

    def mostrar_todos(self):

        self.mostrar_informacoes()

        # Cria a imagem cinza sem abrir outra janela.
        self.cinza = cv2.cvtColor(
            self.bgr,
            cv2.COLOR_BGR2GRAY
        )

        # Separa os canais.
        self.azul, self.verde, self.vermelho = cv2.split(
            self.bgr
        )

        # Cria a imagem transposta.
        transposta = self.bgr.transpose(
            (1, 0, 2)
        )

        cv2.imshow(
            'Original',
            self.bgr
        )

        cv2.imshow(
            'Tons de cinza',
            self.cinza
        )

        cv2.imshow(
            'Canal azul',
            self.azul
        )

        cv2.imshow(
            'Canal verde',
            self.verde
        )

        cv2.imshow(
            'Canal vermelho',
            self.vermelho
        )

        cv2.imshow(
            'Transposta',
            transposta
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():

    processador = ProcessarImagem()

    processador.carregar_imagem(
        CAMINHO_IMAGEM
    )

    exemplos = {
        'mostrar': processador.mostrar_imagem,
        'informacoes': processador.mostrar_informacoes,
        'cinza': processador.converter_para_cinza,
        'canais': processador.separar_canais,
        'transpor': processador.transpor_imagem,
        'todos': processador.mostrar_todos
    }

    if EXEMPLO not in exemplos:

        raise ValueError(
            f'Exemplo inválido: {EXEMPLO}'
        )

    exemplos[EXEMPLO]()


if __name__ == '__main__':
    main()