import cv2


# Normalmente, a câmera principal possui índice 0.
#
# Se não funcionar, teste 1, 2 ou 3.
ID_CAMERA = 0


# Escolha o processamento aplicado em cada frame:
#
# 'original'
# 'cinza'
# 'inverter_canais'
# 'transpor'
# 'recortar'
# 'espelhar'
PROCESSAMENTO = 'original'


class ProcessarWebcam:

    # ============================================================
    # CAPTURAR E PROCESSAR A WEBCAM
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - abrir a webcam;
    # - capturar uma imagem;
    # - mostrar vídeo;
    # - processar imagens em tempo real;
    # - aplicar uma transformação em cada frame;
    # - converter o vídeo para cinza;
    # - recortar a imagem da câmera.
    #
    # VideoCapture abre a câmera:
    #
    # cv2.VideoCapture(0)
    #
    # read devolve:
    #
    # conseguiu_ler:
    # True ou False.
    #
    # frame:
    # imagem atual da câmera.

    def __init__(self, id_camera):

        self.id_camera = id_camera

        # Abre a câmera.
        self.webcam = cv2.VideoCapture(
            self.id_camera
        )

        # Verifica se a câmera foi encontrada.
        if not self.webcam.isOpened():

            raise RuntimeError(
                f'Não foi possível abrir a câmera '
                f'{self.id_camera}'
            )

        print(
            f'Câmera {self.id_camera} aberta'
        )

    # ============================================================
    # CAPTURAR UM ÚNICO FRAME
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - tirar uma foto com a webcam;
    # - capturar somente uma imagem;
    # - salvar um frame;
    # - processar uma imagem da câmera sem criar vídeo.

    def capturar_um_frame(self):

        conseguiu_ler, frame = self.webcam.read()

        if not conseguiu_ler:

            raise RuntimeError(
                'Não foi possível capturar o frame'
            )

        print(
            f'Formato do frame: {frame.shape}'
        )

        cv2.imshow(
            'Frame capturado',
            frame
        )

        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return frame

    # ============================================================
    # PROCESSAR UM FRAME
    # ============================================================
    #
    # Esta função recebe uma imagem da webcam,
    # aplica o exemplo escolhido e devolve o resultado.
    #
    # Na prova, você poderá substituir estas operações
    # pelo processamento pedido no enunciado.

    def processar_frame(self, frame):

        # EXEMPLO 1 — IMAGEM ORIGINAL
        #
        # Use quando quiser apenas mostrar a webcam.
        if PROCESSAMENTO == 'original':

            resultado = frame.copy()

        # EXEMPLO 2 — TONS DE CINZA
        #
        # Use quando o professor pedir para remover
        # as informações de cor.
        elif PROCESSAMENTO == 'cinza':

            resultado = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

        # EXEMPLO 3 — INVERTER BGR PARA RGB
        #
        # Use quando o professor pedir para trocar
        # a ordem dos canais.
        elif PROCESSAMENTO == 'inverter_canais':

            resultado = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

        # EXEMPLO 4 — TRANSPOR
        #
        # Use quando o professor pedir para trocar
        # linhas e colunas.
        elif PROCESSAMENTO == 'transpor':

            resultado = frame.transpose(
                (1, 0, 2)
            )

        # EXEMPLO 5 — RECORTAR
        #
        # Use quando quiser processar somente
        # a região central da imagem.
        elif PROCESSAMENTO == 'recortar':

            altura, largura = frame.shape[:2]

            x1 = largura // 4
            x2 = 3 * largura // 4

            y1 = altura // 4
            y2 = 3 * altura // 4

            # Primeiro colocamos Y, depois X.
            resultado = frame[
                y1:y2,
                x1:x2
            ]

        # EXEMPLO 6 — ESPELHAR
        #
        # flip com valor 1 espelha horizontalmente.
        elif PROCESSAMENTO == 'espelhar':

            resultado = cv2.flip(
                frame,
                1
            )

        else:

            raise ValueError(
                f'Processamento inválido: '
                f'{PROCESSAMENTO}'
            )

        return resultado

    # ============================================================
    # SALVAR UM FRAME
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - salvar uma imagem;
    # - guardar o frame atual;
    # - criar um arquivo para testar depois.
    #
    # imwrite recebe:
    #
    # nome do arquivo;
    # imagem que será salva.

    def salvar_frame(self, frame):

        cv2.imwrite(
            'frame_salvo.png',
            frame
        )

        print('Imagem salva como frame_salvo.png')

    # ============================================================
    # MOSTRAR VÍDEO CONTINUAMENTE
    # ============================================================
    #
    # USE QUANDO O PROFESSOR PEDIR:
    #
    # - mostrar a webcam em tempo real;
    # - processar todos os frames;
    # - criar um loop de vídeo.
    #
    # Para fechar:
    #
    # pressione ESC;
    # ou pressione Q.

    def executar(self):

        print('Pressione ESC ou Q para fechar')
        print('Pressione S para salvar o frame atual')

        try:

            while True:

                conseguiu_ler, frame = self.webcam.read()

                if not conseguiu_ler:

                    print(
                        'Não foi possível ler a webcam'
                    )

                    break

                # Aplica o processamento escolhido.
                resultado = self.processar_frame(
                    frame
                )

                # Adiciona o nome do processamento
                # somente em imagens coloridas.
                if len(resultado.shape) == 3:

                    cv2.putText(
                        resultado,
                        f'Modo: {PROCESSAMENTO}',
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )

                cv2.imshow(
                    'Webcam',
                    resultado
                )

                # Espera uma tecla por 1 milissegundo.
                tecla = cv2.waitKey(1) & 0xFF

                # ESC possui código 27.
                if tecla == 27:
                    break

                # Também fecha ao pressionar Q.
                if tecla == ord('q'):
                    break

                # Salva o frame ao pressionar S.
                if tecla == ord('s'):
                    self.salvar_frame(resultado)

        finally:

            # O finally garante que a câmera será fechada,
            # mesmo se acontecer algum erro.
            self.webcam.release()

            cv2.destroyAllWindows()

            print('Câmera fechada')


def main():

    processador = ProcessarWebcam(
        ID_CAMERA
    )

    # Para capturar apenas uma imagem:
    #
    # frame = processador.capturar_um_frame()
    # processador.salvar_frame(frame)
    # processador.webcam.release()

    # Para mostrar o vídeo continuamente:
    processador.executar()


if __name__ == '__main__':
    main()