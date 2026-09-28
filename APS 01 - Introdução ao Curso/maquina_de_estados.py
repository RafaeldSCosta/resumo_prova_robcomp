"""
MÁQUINA DE ESTADOS — CÓDIGO CORINGA

USE ESTE ARQUIVO QUANDO O ENUNCIADO PEDIR:

- Criar estados para o robô.
- Utilizar self.robot_state.
- Utilizar self.state_machine.
- Criar uma função para cada ação.
- Escolher uma ação dentro de control.
- Executar a ação através de um dicionário.

EXEMPLOS DE ESTADOS:

- forward: andar para frente;
- left: virar ou mover para esquerda;
- right: virar ou mover para direita;
- wait: esperar uma informação;
- search: procurar algo;
- stop: parar;
- done: indicar que a tarefa terminou.

Você não precisa utilizar todos.
Apague os estados que não aparecem na questão.
"""


class ControleRobo:

    def __init__(self):
        """
        Coloque aqui:

        1. O estado inicial.
        2. O dicionário de estados.
        3. As informações usadas para decidir o próximo estado.
        """

        # ----------------------------------------------------
        # ESTADO INICIAL
        # ----------------------------------------------------

        # Se o enunciado disser:
        # "O robô deve começar andando para frente"
        self.robot_state = 'forward'

        # Se disser:
        # "O robô deve começar parado"
        # self.robot_state = 'stop'

        # Se disser:
        # "O robô deve começar procurando"
        # self.robot_state = 'search'

        # ----------------------------------------------------
        # DICIONÁRIO DE ESTADOS
        # ----------------------------------------------------

        """
        Para cada estado, coloque a função correspondente.

        Não coloque parênteses dentro do dicionário.

        CERTO:
            'forward': self.forward

        ERRADO:
            'forward': self.forward()
        """

        self.state_machine = {
            'forward': self.forward,
            'left': self.left,
            'right': self.right,
            'wait': self.wait,
            'search': self.search,
            'stop': self.stop,
            'done': self.done,
        }

        # ----------------------------------------------------
        # INFORMAÇÕES PARA TESTAR AS DECISÕES
        # ----------------------------------------------------

        # Na questão real, essas informações podem ser
        # atualizadas pelo mapa, laser, odometria ou câmera.

        self.obstaculo_frente = False
        self.esquerda_livre = False
        self.direita_livre = False
        self.objetivo_encontrado = False
        self.comando_recebido = False
        self.tarefa_finalizada = False

        # Variáveis usadas apenas neste exemplo
        self.velocidade_linear = 0.0
        self.velocidade_angular = 0.0

    # ========================================================
    # ESTADO: ANDAR PARA FRENTE
    # ========================================================

    def forward(self):
        """
        USE QUANDO ELE PEDIR:

        - andar para frente;
        - seguir reto;
        - continuar o percurso;
        - avançar até encontrar alguma condição.
        """

        self.velocidade_linear = 0.2
        self.velocidade_angular = 0.0

        print('Ação: andando para frente')

        # ----------------------------------------------------
        # SE ELE PEDIR PARA PARAR AO ENCONTRAR O OBJETIVO
        # ----------------------------------------------------

        if self.objetivo_encontrado:
            self.robot_state = 'stop'

        # ----------------------------------------------------
        # SE ELE PEDIR PARA DESVIAR DE UM OBSTÁCULO
        # ----------------------------------------------------

        elif self.obstaculo_frente:
            # Escolher o próximo estado
            # A função escolhida será executada na próxima
            # chamada de control.

            if self.esquerda_livre:
                self.robot_state = 'left'

            elif self.direita_livre:
                self.robot_state = 'right'

            else:
                self.robot_state = 'stop'

    # ========================================================
    # ESTADO: IR OU GIRAR PARA A ESQUERDA
    # ========================================================

    def left(self):
        """
        USE QUANDO ELE PEDIR:

        - mover para esquerda;
        - girar para esquerda;
        - desviar pela esquerda.

        Os valores abaixo são apenas exemplos.
        No robô da ROS, utilizaremos Twist.
        """

        self.velocidade_linear = 0.0
        self.velocidade_angular = 0.5

        print('Ação: girando para esquerda')

        # ----------------------------------------------------
        # SE ELE PEDIR PARA VOLTAR A ANDAR DEPOIS DO GIRO
        # ----------------------------------------------------

        # Na questão real, essa condição pode usar:
        # - ângulo atual;
        # - tempo;
        # - posição;
        # - resultado de uma ação.
        giro_finalizado = True

        if giro_finalizado:
            self.robot_state = 'forward'

    # ========================================================
    # ESTADO: IR OU GIRAR PARA A DIREITA
    # ========================================================

    def right(self):
        """
        USE QUANDO ELE PEDIR:

        - mover para direita;
        - girar para direita;
        - desviar pela direita.
        """

        self.velocidade_linear = 0.0
        self.velocidade_angular = -0.5

        print('Ação: girando para direita')

        giro_finalizado = True

        if giro_finalizado:
            self.robot_state = 'forward'

    # ========================================================
    # ESTADO: ESPERAR
    # ========================================================

    def wait(self):
        """
        USE QUANDO ELE PEDIR:

        - aguardar uma mensagem;
        - esperar uma instrução;
        - permanecer parado até receber um comando;
        - esperar outro agente responder.
        """

        self.velocidade_linear = 0.0
        self.velocidade_angular = 0.0

        print('Ação: esperando uma instrução')

        # ----------------------------------------------------
        # SE ELE PEDIR PARA AGIR DEPOIS DE RECEBER UM COMANDO
        # ----------------------------------------------------

        if self.comando_recebido:
            self.robot_state = 'forward'

    # ========================================================
    # ESTADO: PROCURAR
    # ========================================================

    def search(self):
        """
        USE QUANDO ELE PEDIR:

        - procurar um objeto;
        - procurar uma cor;
        - girar até encontrar algo;
        - explorar o ambiente.
        """

        # Girar parado enquanto procura
        self.velocidade_linear = 0.0
        self.velocidade_angular = 0.3

        print('Ação: procurando')

        # ----------------------------------------------------
        # SE ELE PEDIR PARA PARAR QUANDO ENCONTRAR
        # ----------------------------------------------------

        if self.objetivo_encontrado:
            self.robot_state = 'stop'

    # ========================================================
    # ESTADO: PARAR
    # ========================================================

    def stop(self):
        """
        USE QUANDO ELE PEDIR:

        - parar o robô;
        - zerar a velocidade;
        - encerrar uma ação;
        - preparar a finalização.
        """

        self.velocidade_linear = 0.0
        self.velocidade_angular = 0.0

        print('Ação: robô parado')

        # ----------------------------------------------------
        # SE stop FOR APENAS UMA PARADA TEMPORÁRIA
        # ----------------------------------------------------

        # Exemplo:
        #
        # if recebeu_novo_comando:
        #     self.robot_state = 'forward'

        # ----------------------------------------------------
        # SE stop SIGNIFICAR QUE A TAREFA ACABOU
        # ----------------------------------------------------

        self.tarefa_finalizada = True
        self.robot_state = 'done'

    # ========================================================
    # ESTADO: FINALIZADO
    # ========================================================

    def done(self):
        """
        USE QUANDO A QUESTÃO TRABALHAR COM AÇÕES QUE POSSUEM
        INÍCIO E FIM.

        O robô permanece parado e a variável
        tarefa_finalizada continua verdadeira.
        """

        self.velocidade_linear = 0.0
        self.velocidade_angular = 0.0
        self.tarefa_finalizada = True

        print('Ação: tarefa finalizada')

    # ========================================================
    # ESCOLHER E EXECUTAR A AÇÃO ATUAL
    # ========================================================

    def control(self):
        """
        Esta função normalmente é chamada várias vezes.

        Ela:

        1. Mostra o estado atual.
        2. Procura a função no dicionário.
        3. Executa a função encontrada.
        """

        print(f'\nEstado atual: {self.robot_state}')

        # Executar a função correspondente ao estado atual
        self.state_machine[self.robot_state]()

        print(f'Próximo estado: {self.robot_state}')


# ============================================================
# COMO ADICIONAR UM NOVO ESTADO
# ============================================================

"""
EXEMPLO:

O professor pediu um estado chamado celebrate.

PASSO 1 — Crie a função dentro da classe:

    def celebrate(self):
        print('Comemorando')
        self.robot_state = 'stop'


PASSO 2 — Adicione ao dicionário:

    self.state_machine = {
        ...
        'celebrate': self.celebrate,
    }


PASSO 3 — Troque para esse estado quando necessário:

    if venceu_o_jogo:
        self.robot_state = 'celebrate'


PASSO 4 — A função control executará automaticamente:

    self.state_machine[self.robot_state]()
"""


# ============================================================
# SE A DECISÃO PRECISAR FICAR DENTRO DE control
# ============================================================

"""
Algumas questões pedem que control escolha o estado antes
de executar a função.

Nesse caso, control pode ser escrito assim:

    def control(self):

        if self.objetivo_encontrado:
            self.robot_state = 'stop'

        elif self.obstaculo_frente and self.esquerda_livre:
            self.robot_state = 'left'

        elif self.obstaculo_frente and self.direita_livre:
            self.robot_state = 'right'

        else:
            self.robot_state = 'forward'

        self.state_machine[self.robot_state]()


ATENÇÃO:

Em algumas provas, o professor exige que control seja idêntica
ao base_control.py.

Se ele disser isso, NÃO coloque decisões novas dentro de control.

Coloque as decisões dentro dos estados:

    def forward(self):
        if condição:
            self.robot_state = 'left'
"""


# ============================================================
# COMO EVITAR ERRO DE ESTADO INVÁLIDO
# ============================================================

"""
Se robot_state tiver um nome que não existe no dicionário:

    self.robot_state = 'andar'

mas o dicionário possuir somente:

    'forward': self.forward

o programa dará KeyError.


Para verificar antes de executar:

    if self.robot_state in self.state_machine:
        self.state_machine[self.robot_state]()
    else:
        print(f'Estado inválido: {self.robot_state}')
        self.robot_state = 'stop'
"""


# ============================================================
# TESTES
# ============================================================

def main():
    controle = ControleRobo()

    # --------------------------------------------------------
    # TESTE 1 — Caminho livre
    # --------------------------------------------------------

    print('\n========== TESTE: CAMINHO LIVRE ==========')

    controle.robot_state = 'forward'
    controle.obstaculo_frente = False
    controle.objetivo_encontrado = False

    controle.control()

    # --------------------------------------------------------
    # TESTE 2 — Obstáculo e esquerda livre
    # --------------------------------------------------------

    print('\n========== TESTE: DESVIAR PELA ESQUERDA ==========')

    controle.robot_state = 'forward'
    controle.obstaculo_frente = True
    controle.esquerda_livre = True
    controle.direita_livre = False

    # Primeira chamada identifica o obstáculo
    controle.control()

    # Segunda chamada executa o estado left
    controle.control()

    # --------------------------------------------------------
    # TESTE 3 — Obstáculo e direita livre
    # --------------------------------------------------------

    print('\n========== TESTE: DESVIAR PELA DIREITA ==========')

    controle.robot_state = 'forward'
    controle.obstaculo_frente = True
    controle.esquerda_livre = False
    controle.direita_livre = True

    controle.control()
    controle.control()

    # --------------------------------------------------------
    # TESTE 4 — Esperar uma instrução
    # --------------------------------------------------------

    print('\n========== TESTE: ESPERAR COMANDO ==========')

    controle.robot_state = 'wait'
    controle.comando_recebido = False

    controle.control()

    controle.comando_recebido = True
    controle.control()

    # --------------------------------------------------------
    # TESTE 5 — Encontrou o objetivo
    # --------------------------------------------------------

    print('\n========== TESTE: OBJETIVO ENCONTRADO ==========')

    controle.robot_state = 'forward'
    controle.objetivo_encontrado = True

    controle.control()
    controle.control()
    controle.control()


if __name__ == '__main__':
    main()


"""
============================================================
RESUMO — COMO ADAPTAR
============================================================

1. Liste as ações pedidas no enunciado.

2. Transforme cada ação em uma função:

       def forward(self):
       def left(self):
       def stop(self):

3. Escolha o estado inicial:

       self.robot_state = 'forward'

4. Coloque as funções no dicionário:

       self.state_machine = {
           'forward': self.forward,
           'left': self.left,
           'stop': self.stop,
       }

5. Quando uma condição acontecer, troque o estado:

       if obstaculo:
           self.robot_state = 'left'

6. Execute o estado atual:

       self.state_machine[self.robot_state]()

7. Se control precisar ser idêntica ao código do professor,
   não altere control. Coloque as decisões dentro das funções.

8. Teste cada situação separadamente:

   - caminho livre;
   - obstáculo;
   - esquerda livre;
   - direita livre;
   - objetivo encontrado;
   - comando recebido;
   - finalização.

9. Apague os estados que não serão usados na questão.

10. Confirme que todos os valores atribuídos a robot_state
    possuem uma chave igual no dicionário.
"""