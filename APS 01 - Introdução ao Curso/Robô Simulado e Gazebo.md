# Robô Simulado e Gazebo

> Guia para abrir o mapa, testar o robô e executar uma questão no simulador.

---

## Visão geral

Na prova, teremos apenas o robô simulado no computador.

A organização normal será:

| Terminal | Utilização |
|---|---|
| Terminal 1 | Abrir o mapa no Gazebo |
| Terminal 2 | Executar o código da questão |
| Terminal 3 | Ver tópicos, mensagens ou câmera |

O mapa e o meu código são executados separadamente, mas se comunicam pelos tópicos da ROS 2.

---

# 1. Abrir o mapa

O enunciado informará qual arquivo de mapa deve ser usado.

O formato do comando é:

```
ros2 launch my_gazebo NOME_DO_MAPA.launch.py
```

Exemplo utilizado no handout:

```
ros2 launch my_gazebo pista-23B.launch.py
```

Outro exemplo:

```
ros2 launch my_gazebo vazio.launch.py
```

> Use exatamente o mapa informado no enunciado.

Não feche o terminal do mapa. Se ele for encerrado com `Ctrl+C`, o simulador também será encerrado.

---

# 2. Diferença entre `launch` e `run`

## `ros2 launch`

Utilizado para iniciar um arquivo de lançamento.

Normalmente abre várias coisas juntas:

- Gazebo;
- mapa;
- robô;
- sensores;
- outros nós necessários.

Exemplo:

```
ros2 launch my_gazebo pista-23B.launch.py
```

## `ros2 run`

Utilizado para executar apenas um programa ou nó.

Exemplo:

```
ros2 run prova_ai q1
```

Resumo:

| Objetivo | Comando |
|---|---|
| Abrir mapa e simulador | `ros2 launch` |
| Executar minha questão | `ros2 run` |

---

# 3. Testar o robô pelo teclado

Primeiro, abra o mapa:

```
ros2 launch my_gazebo pista-23B.launch.py
```

Em outro terminal, execute o controle pelo teclado:

```
ros2 run turtlebot3_teleop teleop_keyboard
```

## Teclas

| Tecla | Movimento |
|---|---|
| `w` | Frente |
| `x` | Ré |
| `a` | Esquerda |
| `d` | Direita |
| `s` | Parar |

O terminal do teleop precisa estar selecionado para receber as teclas.

Para encerrar:

```
Ctrl+C
```

> Encerre o teleop antes de executar seu código. O teleop e sua questão podem tentar controlar o robô ao mesmo tempo.

---

# 4. Executar o mapa e a questão

## Terminal 1 — mapa

```
source ~/colcon_ws/install/setup.bash
ros2 launch my_gazebo NOME_DO_MAPA.launch.py
```

## Terminal 2 — questão

```
source ~/colcon_ws/install/setup.bash
ros2 run prova_ai q1
```

Se o pacote tiver outro nome, troque `prova_ai`.

Se o executável tiver outro nome, troque `q1`.

---

# 5. Entender a comunicação

O mapa não é importado dentro do código Python.

O simulador cria o robô e disponibiliza tópicos.

Seu código utiliza esses tópicos para receber sensores e enviar comandos.

| Tópico | Utilização |
|---|---|
| `/cmd_vel` | Enviar velocidade |
| `/odom` | Receber posição e orientação |
| `/scan` | Receber distâncias do laser |
| Tópico da câmera | Receber imagens |

O funcionamento é:

1. O Gazebo simula o robô e os sensores.
2. Os sensores publicam informações em tópicos.
3. Seu código recebe essas informações.
4. Seu código toma uma decisão.
5. Seu código publica uma velocidade em `/cmd_vel`.
6. O robô simulado se movimenta.

---

# 6. Verificar se o simulador está funcionando

Com o mapa aberto, execute em outro terminal:

```
ros2 topic list
```

Procure principalmente:

```
/cmd_vel
/odom
/scan
```

Se esses tópicos estiverem aparecendo, o robô e os sensores provavelmente foram iniciados corretamente.

---

# 7. Verificar um tópico

Para descobrir o tipo da mensagem:

```
ros2 topic info /cmd_vel
```

Exemplos:

```
ros2 topic info /odom
ros2 topic info /scan
```

Tipos esperados:

| Tópico | Tipo comum |
|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` |
| `/odom` | `nav_msgs/msg/Odometry` |
| `/scan` | `sensor_msgs/msg/LaserScan` |

A investigação completa de tópicos ficará no guia da APS 2.

---

# 8. Ver uma mensagem

Para acompanhar as mensagens de um tópico:

```
ros2 topic echo /odom
```

Para mostrar apenas uma mensagem:

```
ros2 topic echo /odom --once
```

Outros exemplos:

```
ros2 topic echo /scan --once
ros2 topic echo /cmd_vel
```

Para encerrar um `echo` contínuo:

```
Ctrl+C
```

---

# 9. Abrir a câmera simulada

Com o mapa aberto:

```
ros2 run rqt_image_view rqt_image_view
```

Na janela, selecione o tópico correto da câmera.

Para procurar os tópicos de imagem:

```
ros2 topic list | grep image
```

Se a imagem não aparecer:

1. Confirme que o mapa possui câmera.
2. Procure os tópicos contendo `image`.
3. Selecione o tópico correto no `rqt_image_view`.
4. Aguarde alguns segundos para a primeira imagem aparecer.

---

# 10. Enviar velocidade pelo terminal

O robô recebe velocidades pelo tópico `/cmd_vel`.

Para enviar uma única mensagem:

```
ros2 topic pub -1 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

Esse comando manda o robô andar para frente.

Campos principais:

| Campo | Significado |
|---|---|
| `linear.x` positivo | Frente |
| `linear.x` negativo | Ré |
| `angular.z` positivo | Girar para a esquerda |
| `angular.z` negativo | Girar para a direita |
| Ambos iguais a zero | Parar |

---

# 11. Parar o robô em uma emergência

Primeiro, encerre o programa que está controlando o robô:

```
Ctrl+C
```

Depois, envie velocidade zero:

```
ros2 topic pub -1 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

> Apenas enviar velocidade zero pode não resolver se outro código continuar publicando velocidades. Encerre esse código primeiro.

---

# 12. Comando rápido `sos`

Se o alias `sos` já estiver configurado no `robotica.sh`, basta executar:

```
sos
```

Se ainda não estiver, abra:

```
code /$HOME/robotica.sh
```

Adicione:

```
alias sos='ros2 topic pub -1 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"'
```

Salve e abra um terminal novo.

---

# 13. Reiniciar o mapa

Se precisar começar a questão novamente:

1. Encerre seu código com `Ctrl+C`.
2. Encerre o mapa com `Ctrl+C`.
3. Feche o Gazebo, caso continue aberto.
4. Abra o mapa novamente.
5. Execute seu nó novamente.

## Terminal 1

```
ros2 launch my_gazebo NOME_DO_MAPA.launch.py
```

## Terminal 2

```
source ~/colcon_ws/install/setup.bash
ros2 run prova_ai q1
```

Isso faz o robô voltar à posição inicial definida pelo mapa.

---

# 14. Erros comuns

## O mapa não abre

Confira:

- nome do mapa;
- extensão `.launch.py`;
- pacote `my_gazebo`;
- atualização do `my_simulation`;
- compilação do workspace;
- execução do `source`.

Tente:

```
cd ~/colcon_ws
colcon build
source ~/colcon_ws/install/setup.bash
```

Depois:

```
ros2 launch my_gazebo NOME_DO_MAPA.launch.py
```

---

## O mapa abre, mas o robô não se move

Confira:

- se seu nó está executando;
- se `/cmd_vel` existe;
- se o publisher usa `geometry_msgs/msg/Twist`;
- se o nome do tópico está correto;
- se o timer está chamando `control`;
- se o teleop foi encerrado;
- se a velocidade não está sendo zerada logo depois.

Observe os comandos enviados:

```
ros2 topic echo /cmd_vel
```

---

## O robô não para

1. Encerre seu código com `Ctrl+C`.
2. Encerre o teleop, caso esteja aberto.
3. Execute `sos` ou publique velocidade zero.

---

## Os sensores não aparecem

Liste os tópicos:

```
ros2 topic list
```

Se `/scan` ou `/odom` não aparecerem:

1. confira se o mapa terminou de carregar;
2. aguarde alguns segundos;
3. encerre e abra o mapa novamente;
4. confira se o `my_simulation` precisa ser atualizado.

---

## A câmera não aparece

Procure o tópico correto:

```
ros2 topic list | grep image
```

Depois abra:

```
ros2 run rqt_image_view rqt_image_view
```

Selecione manualmente o tópico encontrado.

---

# 15. Organização rápida dos terminais

## Terminal 1 — simulador

```
ros2 launch my_gazebo NOME_DO_MAPA.launch.py
```

## Terminal 2 — código da questão

```
source ~/colcon_ws/install/setup.bash
ros2 run prova_ai q1
```

## Terminal 3 — diagnóstico

Escolha o comando necessário:

```
ros2 topic list
```

```
ros2 topic echo /cmd_vel
```

```
ros2 topic echo /odom --once
```

```
ros2 topic echo /scan --once
```

```
ros2 run rqt_image_view rqt_image_view
```

---

# 16. Checklist

- [ ] Li qual mapa o enunciado exige.
- [ ] Abri o mapa usando `ros2 launch`.
- [ ] Mantive o terminal do simulador aberto.
- [ ] Testei o robô com o teleop, se necessário.
- [ ] Encerrei o teleop antes de executar meu código.
- [ ] Executei minha questão com `ros2 run`.
- [ ] Verifiquei se `/cmd_vel` existe.
- [ ] Verifiquei se `/odom` existe.
- [ ] Verifiquei se `/scan` existe.
- [ ] Conferi o tópico correto da câmera.
- [ ] Sei encerrar meu código usando `Ctrl+C`.
- [ ] Sei parar o robô usando `sos` ou velocidade zero.
- [ ] Sei reiniciar o mapa para voltar à posição inicial.