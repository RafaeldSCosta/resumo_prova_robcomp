# Robô comandado por outro agente

## Quando usar este código

Use este pacote quando o professor pedir que o robô:

- receba instruções enviadas por outro nó;
- identifique comandos como frente, trás, direita, esquerda e parar;
- transforme uma mensagem recebida em movimento;
- publique informações sobre seu estado;
- use publisher e subscriber no mesmo nó;
- converse com um agente, orquestrador ou controlador externo.

O código utiliza mensagens String para facilitar os testes.

Na prova, o professor pode utilizar uma mensagem personalizada. Nesse caso, será
necessário descobrir o tipo da mensagem e substituir String pelo tipo informado.

---

## O que cada nó faz

### robo_comandado_node

Este é o nó principal.

Ele:

1. assina o tópico /comando_robo;
2. recebe uma mensagem String;
3. interpreta o comando;
4. seleciona um estado da máquina de estados;
5. publica a velocidade em /cmd_vel;
6. publica seu estado em /status_robo.

### agente_teste_node

Este nó existe somente para testar o robô.

Ele:

1. publica comandos no tópico /comando_robo;
2. recebe as respostas publicadas em /status_robo;
3. envia automaticamente uma sequência de comandos.

Na prova, provavelmente o simulador ou o agente do professor substituirá este nó.

---

## Tópicos utilizados

| Tópico | Tipo | Função |
|---|---|---|
| /comando_robo | std_msgs/msg/String | Recebe as instruções |
| /status_robo | std_msgs/msg/String | Envia o estado do robô |
| /cmd_vel | geometry_msgs/msg/Twist | Controla o movimento |

---

## Comandos aceitos

| Mensagem recebida | Comportamento |
|---|---|
| frente | Anda para frente |
| tras | Anda para trás |
| direita | Gira para a direita |
| esquerda | Gira para a esquerda |
| parar | Para o robô |

Também são aceitos alguns nomes alternativos, como `andar`, `voltar` e `stop`.

O TurtleBot não anda lateralmente. Para ir para a direita ou esquerda, ele gira
utilizando `angular.z`.

---

## Fluxo do programa

1. O agente publica uma String em /comando_robo.
2. A função receber_comando é chamada automaticamente.
3. O comando é convertido em um estado.
4. O timer chama control a cada 0.1 segundo.
5. control executa a função do estado atual.
6. A função do estado prepara self.twist.
7. control publica self.twist em /cmd_vel.
8. O robô publica seu status em /status_robo.

A função control é a única que publica em /cmd_vel.

---

## Como adaptar para uma mensagem da prova

Primeiro, descubra o tópico e o tipo:

    ros2 topic list
    ros2 topic info /NOME_DO_TOPICO
    ros2 topic type /NOME_DO_TOPICO

Depois, veja os campos:

    ros2 interface show pacote/msg/TipoDaMensagem
    ros2 topic echo /NOME_DO_TOPICO --once

Se o tipo fornecido for, por exemplo:

    robcomp_interfaces/msg/Comando

Substitua:

    from std_msgs.msg import String

por:

    from robcomp_interfaces.msg import Comando

Depois substitua:

    self.create_subscription(
        String,
        '/comando_robo',
        self.receber_comando,
        10
    )

por:

    self.create_subscription(
        Comando,
        '/topico_da_prova',
        self.receber_comando,
        10
    )

Finalmente, dentro de receber_comando, substitua:

    comando = msg.data

pelo campo correto, por exemplo:

    comando = msg.instrucao

Sempre use `ros2 interface show` para descobrir o nome e o tipo de cada campo.

---

## Como adicionar um comando

Se o professor adicionar a instrução `comemorar`, faça três alterações.

Primeiro, adicione uma função:

    def comemorar(self):
        self.twist = Twist()
        self.twist.angular.z = 1.0

Depois, coloque a função na máquina de estados:

    'comemorar': self.comemorar,

Por último, coloque o comando no dicionário:

    'comemorar': 'comemorar',

---

## Compilar

No terminal:

    cd ~/colcon_ws
    colcon build --packages-select robo_comandado
    source install/setup.bash

Sempre compile novamente depois de alterar `setup.py`.

---

## Executar

Primeiro, inicie o simulador usando o mapa fornecido pelo professor.

Em outro terminal:

    source ~/colcon_ws/install/setup.bash
    ros2 run robo_comandado robo

Para iniciar o agente de teste:

    source ~/colcon_ws/install/setup.bash
    ros2 run robo_comandado agente_teste

---

## Testar sem o agente

Também é possível publicar um comando manualmente.

Andar para frente:

    ros2 topic pub --once /comando_robo std_msgs/msg/String "{data: 'frente'}"

Girar para a esquerda:

    ros2 topic pub --once /comando_robo std_msgs/msg/String "{data: 'esquerda'}"

Parar:

    ros2 topic pub --once /comando_robo std_msgs/msg/String "{data: 'parar'}"

Ver as respostas do robô:

    ros2 topic echo /status_robo

Ver as velocidades:

    ros2 topic echo /cmd_vel

---

## Checklist

- [ ] Criei o pacote dentro de `~/colcon_ws/src`.
- [ ] Coloquei os arquivos Python dentro da pasta Python do pacote.
- [ ] Configurei os nós em `setup.py`.
- [ ] Compilei usando `colcon build --packages-select robo_comandado`.
- [ ] Executei `source install/setup.bash`.
- [ ] Iniciei o simulador.
- [ ] Iniciei o nó `robo`.
- [ ] Testei os comandos.
- [ ] O robô para ao receber `parar`.
- [ ] O tópico e o tipo da mensagem estão iguais aos do enunciado.
- [ ] A função `control` é a única que publica em `/cmd_vel`.