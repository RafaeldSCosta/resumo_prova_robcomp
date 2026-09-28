# Robô que percorre uma distância recebida pelo tópico

## Quando usar

Use este pacote quando o professor pedir que o robô:

- receba uma distância de outro nó;
- percorra uma distância positiva ou negativa;
- utilize Odom para medir o movimento;
- pare ao alcançar um objetivo;
- avise quando começou ou terminou;
- receba parâmetros por um tópico;
- utilize publisher, subscriber e máquina de estados.

---

## Comportamento

O robô recebe um número no tópico `/distancia_desejada`.

Exemplos:

| Distância | Comportamento |
|---|---|
| 1.0 | Anda 1 metro para frente |
| 0.5 | Anda 50 centímetros para frente |
| -1.0 | Anda 1 metro para trás |
| -0.3 | Anda 30 centímetros para trás |
| 0.0 | Permanece parado |

O sinal determina a direção.

O módulo do número determina a distância:

    direcao = sinal da distância
    objetivo = valor absoluto da distância

---

## Tópicos utilizados

| Tópico | Tipo | Função |
|---|---|---|
| /distancia_desejada | std_msgs/msg/Float64 | Recebe a distância |
| /odom | nav_msgs/msg/Odometry | Recebe a posição |
| /cmd_vel | geometry_msgs/msg/Twist | Controla o robô |
| /status_distancia | std_msgs/msg/String | Publica o estado |

---

## Como a distância é calculada

Quando um comando é recebido, o programa salva:

    x_inicial
    y_inicial

Durante o movimento, consulta a posição atual:

    x_atual
    y_atual

A distância percorrida é:

    sqrt((x_atual - x_inicial)² + (y_atual - y_inicial)²)

Quando a distância percorrida fica próxima da distância desejada,
o robô para e publica `DONE`.

---

## Atenção

A distância calculada é o deslocamento entre a posição inicial e a posição
atual.

Este código é ideal para movimentos aproximadamente retos.

Se o robô fizer uma curva muito grande durante o movimento, a distância em
linha reta não será igual ao comprimento total do caminho percorrido.

---

## Valores que podem ser alterados

No começo do código:

    VELOCIDADE_NORMAL = 0.20
    VELOCIDADE_APROXIMACAO = 0.08
    DISTANCIA_PARA_REDUZIR = 0.15
    TOLERANCIA = 0.03

- `VELOCIDADE_NORMAL`: velocidade usada no começo.
- `VELOCIDADE_APROXIMACAO`: velocidade próxima do objetivo.
- `DISTANCIA_PARA_REDUZIR`: quando começa a diminuir a velocidade.
- `TOLERANCIA`: diferença aceita entre a distância pedida e percorrida.

---

## Como adaptar para outro tipo de mensagem

Descubra o tópico e o tipo:

    ros2 topic list
    ros2 topic info /NOME_DO_TOPICO
    ros2 topic type /NOME_DO_TOPICO

Veja os campos:

    ros2 interface show pacote/msg/TipoDaMensagem
    ros2 topic echo /NOME_DO_TOPICO --once

Se a mensagem da prova for, por exemplo:

    robcomp_interfaces/msg/ComandoDistancia

Substitua:

    from std_msgs.msg import Float64

por:

    from robcomp_interfaces.msg import ComandoDistancia

Depois substitua no subscriber:

    Float64,
    '/distancia_desejada',

pelo tipo e tópico fornecidos.

Dentro de `receber_distancia`, substitua:

    distancia = msg.data

pelo campo correto, por exemplo:

    distancia = msg.distancia

---

## Compilar

    cd ~/colcon_ws
    colcon build --packages-select robo_distancia
    source install/setup.bash

---

## Executar

Primeiro, inicie o simulador fornecido pelo professor.

Depois execute o robô:

    source ~/colcon_ws/install/setup.bash
    ros2 run robo_distancia robo

Para executar o agente de teste:

    source ~/colcon_ws/install/setup.bash
    ros2 run robo_distancia agente_teste

---

## Testar manualmente

Andar 1 metro para frente:

    ros2 topic pub --once /distancia_desejada std_msgs/msg/Float64 "{data: 1.0}"

Andar 50 centímetros para trás:

    ros2 topic pub --once /distancia_desejada std_msgs/msg/Float64 "{data: -0.5}"

Ver o status:

    ros2 topic echo /status_distancia

Ver a posição:

    ros2 topic echo /odom --once

Ver a velocidade:

    ros2 topic echo /cmd_vel

---

## Checklist

- [ ] O simulador está aberto.
- [ ] O tópico `/odom` existe.
- [ ] O tipo do tópico é `nav_msgs/msg/Odometry`.
- [ ] O robô espera receber a primeira Odom.
- [ ] O valor positivo faz o robô andar para frente.
- [ ] O valor negativo faz o robô andar para trás.
- [ ] A posição inicial é salva quando o comando chega.
- [ ] A distância é calculada usando X e Y.
- [ ] O robô reduz a velocidade próximo do objetivo.
- [ ] O robô para dentro da tolerância.
- [ ] O status `DONE` é publicado somente uma vez.
- [ ] Uma nova distância reinicia a medição.
- [ ] Somente `control` publica em `/cmd_vel`.
- [ ] O código não utiliza `sleep`.