# Robô para sair de um labirinto

cd ~/colcon_ws/src

ros2 pkg create --build-type ament_python robo_labirinto --dependencies rclpy geometry_msgs sensor_msgs nav_msgs std_msgs

## Quando usar

Use este pacote quando o professor pedir que o robô:

- saia de um labirinto;
- navegue utilizando o sensor laser;
- não colida com as paredes;
- tome decisões usando máquina de estados;
- siga a parede direita;
- encontre passagens laterais;
- faça curvas de aproximadamente 90 ou 180 graus;
- publique `start` e `stop` em um tópico de monitoramento.

---

## Estratégia

O código utiliza a regra da mão direita:

1. Se existe uma passagem à direita, gira para a direita.
2. Se a frente está bloqueada e a esquerda está livre, gira à esquerda.
3. Se a frente e os dois lados estão bloqueados, gira 180 graus.
4. Caso contrário, anda seguindo a parede direita.

O laser toma as decisões e a Odom controla os ângulos das curvas.

---

## Tópicos

| Tópico | Tipo | Função |
|---|---|---|
| /scan | sensor_msgs/msg/LaserScan | Detecta paredes |
| /odom | nav_msgs/msg/Odometry | Mede o ângulo do robô |
| /cmd_vel | geometry_msgs/msg/Twist | Controla o movimento |
| /watcher | std_msgs/msg/String | Publica start e stop |
| /status_labirinto | std_msgs/msg/String | Publica o estado |

---

## Estados

### navegar

Consulta o laser e decide se deve:

- andar;
- virar à direita;
- virar à esquerda;
- dar meia-volta;
- finalizar.

### girar

Utiliza o ângulo da Odom para completar a rotação solicitada.

### parar

Zera todas as velocidades.

---

## Valores importantes

No começo de `robo_labirinto.py`:

    DISTANCIA_FRONTAL_SEGURA = 0.55
    ABERTURA_DIREITA = 0.90
    DISTANCIA_PAREDE_DIREITA = 0.45

Se o robô chegar muito perto das paredes, aumente a distância frontal.

Se ele estiver entrando em aberturas pequenas que não deveria, aumente
`ABERTURA_DIREITA`.

---

## Detecção da saída

O código considera que encontrou a saída quando frente, direita e esquerda
permanecem abertas durante várias execuções consecutivas.

Essa é uma solução coringa.

Se o enunciado fornecer uma coordenada exata de saída, é melhor substituir
a função `verificar_saida` por uma verificação de X e Y usando Odom.

Exemplo:

    if self.x > 5.0:
        return True

A maneira correta depende do mapa entregue pelo professor.

---

## Limitação importante

A regra da mão direita funciona bem quando as paredes do labirinto são
conectadas.

Em um labirinto com ilhas ou paredes internas desconectadas, o robô pode
entrar em um ciclo. Nesse caso, seria necessário guardar posições visitadas
ou adaptar a estratégia ao mapa da prova.

---

## Compilar

    cd ~/colcon_ws
    colcon build --packages-select robo_labirinto
    source install/setup.bash

---

## Executar

Primeiro, inicie o mapa fornecido pelo professor.

Depois:

    ros2 run robo_labirinto labirinto

Para acompanhar os estados:

    ros2 topic echo /status_labirinto

Para acompanhar o monitor:

    ros2 topic echo /watcher

---

## Checklist

- [ ] O tópico `/scan` existe.
- [ ] O tópico `/odom` existe.
- [ ] O robô espera os sensores antes de andar.
- [ ] A frente do laser está correta.
- [ ] A direita do laser está correta.
- [ ] A esquerda do laser está correta.
- [ ] O robô publica `start` no começo.
- [ ] A função `control` é a única que publica em `/cmd_vel`.
- [ ] Não existem `sleep` ou loops infinitos.
- [ ] O robô gira para a direita quando encontra passagem.
- [ ] O robô gira para a esquerda quando a frente bloqueia.
- [ ] O robô dá meia-volta em um beco sem saída.
- [ ] O robô para quando detecta a saída.
- [ ] O robô publica `stop` quando termina.

cd ~/colcon_ws

colcon build --packages-select robo_labirinto

source install/setup.bash

ros2 run robo_labirinto labirinto