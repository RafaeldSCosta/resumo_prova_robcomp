# Robô comandado com desvio de obstáculos

## Quando usar

Use este pacote quando o professor pedir que o robô:

- receba instruções por um tópico;
- ande para frente ou para trás;
- gire para a direita ou esquerda;
- consulte o sensor laser antes de se movimentar;
- pare ou desvie quando encontrar um obstáculo;
- publique seu estado para outro agente;
- utilize publisher, subscriber e máquina de estados.

---

## Comportamento

O robô recebe comandos no tópico `/comando_robo`.

Comandos aceitos:

| Comando | Comportamento |
|---|---|
| frente | Anda para frente se o caminho estiver livre |
| tras | Anda para trás se a região traseira estiver livre |
| direita | Gira para a direita |
| esquerda | Gira para a esquerda |
| parar | Para completamente |

Se receber `frente` e encontrar um obstáculo, o robô compara as
distâncias da esquerda e da direita.

- Se a esquerda estiver mais livre, gira para a esquerda.
- Se a direita estiver mais livre, gira para a direita.
- Quando a frente estiver livre novamente, volta a andar.

---

## Tópicos utilizados

| Tópico | Tipo | Função |
|---|---|---|
| /comando_robo | std_msgs/msg/String | Recebe instruções |
| /status_robo | std_msgs/msg/String | Publica o estado |
| /scan | sensor_msgs/msg/LaserScan | Recebe o laser |
| /cmd_vel | geometry_msgs/msg/Twist | Controla o robô |

---

## Regiões do laser

O código separa o laser em quatro regiões:

- frente: aproximadamente 0 graus;
- esquerda: aproximadamente +90 graus;
- direita: aproximadamente -90 graus;
- traseira: aproximadamente 180 graus.

A função `menor_distancia_setor` encontra a menor distância dentro
de cada região.

Isso é mais seguro do que consultar somente um raio do laser, porque
um obstáculo pode não estar exatamente no centro.

---

## Valores importantes

No começo de `robo_com_desvio.py` existem valores que podem ser alterados:

    DISTANCIA_SEGURA_FRENTE = 0.60
    DISTANCIA_LIBERAR_FRENTE = 0.85
    DISTANCIA_SEGURA_TRASEIRA = 0.45

- `DISTANCIA_SEGURA_FRENTE`: começa a desviar abaixo dessa distância.
- `DISTANCIA_LIBERAR_FRENTE`: volta a andar quando a frente superar essa distância.
- `DISTANCIA_SEGURA_TRASEIRA`: impede o robô de bater ao recuar.

Utilizar dois limites diferentes na frente ajuda a evitar que o robô fique
alternando rapidamente entre andar e desviar.

---

## Como adaptar para a prova

Primeiro, descubra os tópicos:

    ros2 topic list

Depois, veja o tipo do tópico do agente:

    ros2 topic info /NOME_DO_TOPICO
    ros2 topic type /NOME_DO_TOPICO

Veja os campos da mensagem:

    ros2 interface show pacote/msg/TipoDaMensagem
    ros2 topic echo /NOME_DO_TOPICO --once

Se o professor usar uma mensagem personalizada, substitua:

    from std_msgs.msg import String

pelo tipo correto.

Também substitua, no subscriber:

    String,
    '/comando_robo',

pelo tipo e tópico fornecidos.

Dentro de `receber_comando`, substitua:

    comando = msg.data

pelo campo correto, por exemplo:

    comando = msg.instrucao

Não altere `LaserScan` se o laser continuar sendo publicado no tópico `/scan`.

---

## Compilar

    cd ~/colcon_ws
    colcon build --packages-select robo_com_desvio
    source install/setup.bash

---

## Executar

Primeiro, inicie o simulador no mapa fornecido pelo professor.

Depois, execute o robô:

    source ~/colcon_ws/install/setup.bash
    ros2 run robo_com_desvio robo

Para executar o agente de teste:

    source ~/colcon_ws/install/setup.bash
    ros2 run robo_com_desvio agente_teste

---

## Testar manualmente

Andar para frente:

    ros2 topic pub --once /comando_robo std_msgs/msg/String "{data: 'frente'}"

Andar para trás:

    ros2 topic pub --once /comando_robo std_msgs/msg/String "{data: 'tras'}"

Girar para a esquerda:

    ros2 topic pub --once /comando_robo std_msgs/msg/String "{data: 'esquerda'}"

Parar:

    ros2 topic pub --once /comando_robo std_msgs/msg/String "{data: 'parar'}"

Ver o laser:

    ros2 topic echo /scan --once

Ver as respostas:

    ros2 topic echo /status_robo

Ver a velocidade:

    ros2 topic echo /cmd_vel

---

## Checklist

- [ ] O simulador está aberto.
- [ ] O tópico `/scan` existe.
- [ ] O tipo do `/scan` é `sensor_msgs/msg/LaserScan`.
- [ ] O robô começa parado.
- [ ] O robô não anda antes de receber o laser.
- [ ] O comando `frente` faz o robô avançar.
- [ ] O robô desvia quando encontra um obstáculo.
- [ ] O robô escolhe o lado com mais espaço.
- [ ] O robô volta a andar depois do desvio.
- [ ] O comando `tras` verifica a região traseira.
- [ ] Um comando desconhecido para o robô.
- [ ] Somente `control` publica em `/cmd_vel`.
- [ ] O código não utiliza `sleep`.