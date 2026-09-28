# Guia — Nós, Tópicos e Mensagens

> Use este guia quando o professor fornecer um tópico e você precisar descobrir como receber, interpretar ou enviar informações.

---

# 1. Qual arquivo devo abrir?

| O professor pediu... | Arquivo |
|---|---|
| Criar apenas um nó ROS 2 | `no_ros.py` |
| Enviar uma informação | `publisher.py` |
| Publicar em um tópico | `publisher.py` |
| Receber uma informação | `subscriber.py` |
| Assinar ou escutar um tópico | `subscriber.py` |
| Receber e depois responder | `publisher_subscriber.py` |
| Publicar e assinar no mesmo tópico | `publisher_subscriber.py` |
| Resolver a APS 2 | Arquivos `aps2_*_resolvido.py` |

---

# 2. O que são nós, tópicos e mensagens?

## Nó

É um programa executado pela ROS 2.

Exemplo:

```python
class MeuNo(Node):
```

## Tópico

É o canal utilizado para trocar informações.

Exemplos:

```text
/cmd_vel
/odom
/scan
/publisher
/simon_says
```

## Mensagem

É o formato da informação enviada pelo tópico.

Exemplos:

```text
std_msgs/msg/String
geometry_msgs/msg/Twist
nav_msgs/msg/Odometry
sensor_msgs/msg/LaserScan
```

Um tópico aceita um tipo específico de mensagem.

---

# 3. Publisher ou subscriber?

## Use publisher quando precisar enviar

Exemplos de enunciado:

- “Publique uma mensagem.”
- “Envie uma resposta.”
- “Informe que o robô terminou.”
- “Publique a velocidade.”
- “Avise ao agente quais caminhos estão livres.”

Arquivo:

```text
publisher.py
```

## Use subscriber quando precisar receber

Exemplos de enunciado:

- “Receba as instruções do agente.”
- “Inscreva-se no tópico.”
- “Leia a mensagem publicada.”
- “Receba a posição do robô.”
- “Receba o comando para sair do laboratório.”

Arquivo:

```text
subscriber.py
```

## Use os dois quando precisar conversar

Exemplos:

- receber uma instrução e enviar uma confirmação;
- receber um comando e publicar o resultado;
- receber uma mensagem do agente e responder;
- publicar e assinar no mesmo tópico.

Arquivo:

```text
publisher_subscriber.py
```

---

# 4. Passo a passo para investigar um tópico

Se o professor fornecer apenas o nome do tópico, siga esta ordem.

## Passo 1 — Abra o mapa ou programa que cria o tópico

O tópico só aparecerá enquanto o nó responsável estiver executando.

Exemplo:

```
ros2 launch my_gazebo NOME_DO_MAPA.launch.py
```

---

## Passo 2 — Veja todos os tópicos

```
ros2 topic list
```

Procure o tópico informado no enunciado.

Exemplo:

```text
/simon_says
```

---

## Passo 3 — Descubra o tipo da mensagem

```
ros2 topic info /NOME_DO_TOPICO
```

Exemplo:

```
ros2 topic info /cmd_vel
```

A saída terá algo parecido com:

```text
Type: geometry_msgs/msg/Twist
Publisher count: 1
Subscription count: 1
```

O trecho mais importante é:

```text
Type: geometry_msgs/msg/Twist
```

---

## Passo 4 — Veja os campos da mensagem

Copie o tipo mostrado pelo comando anterior:

```
ros2 interface show geometry_msgs/msg/Twist
```

A saída mostrará os campos existentes:

```text
Vector3 linear
Vector3 angular
```

E dentro deles:

```text
float64 x
float64 y
float64 z
```

Agora sabemos que podemos usar:

```python
msg.linear.x
msg.angular.z
```

---

## Passo 5 — Veja uma mensagem real

```
ros2 topic echo /NOME_DO_TOPICO --once
```

Exemplo:

```
ros2 topic echo /odom --once
```

Isso permite descobrir:

- quais campos estão sendo preenchidos;
- quais valores aparecem;
- como o agente escreve as instruções;
- se o texto contém letras maiúsculas;
- se existe algum prefixo obrigatório;
- quais valores representam cada situação.

Para acompanhar continuamente:

```
ros2 topic echo /NOME_DO_TOPICO
```

Encerre com:

```
Ctrl+C
```

---

# 5. Sequência completa para um tópico desconhecido

Se o professor disser apenas:

> Use o tópico `/agente`.

Execute:

```
ros2 topic list
```

Depois:

```
ros2 topic info /agente
```

Imagine que o resultado seja:

```text
Type: robcomp_interfaces/msg/Instrucao
```

Veja os campos:

```
ros2 interface show robcomp_interfaces/msg/Instrucao
```

Depois veja uma mensagem real:

```
ros2 topic echo /agente --once
```

Somente depois disso escreva o subscriber ou publisher.

---

# 6. Como transformar o tipo em um import?

O comando pode mostrar:

```text
std_msgs/msg/String
```

O import fica:

```python
from std_msgs.msg import String
```

---

Se mostrar:

```text
geometry_msgs/msg/Twist
```

O import fica:

```python
from geometry_msgs.msg import Twist
```

---

Se mostrar:

```text
nav_msgs/msg/Odometry
```

O import fica:

```python
from nav_msgs.msg import Odometry
```

---

Se mostrar:

```text
robcomp_interfaces/msg/GameStatus
```

O import fica:

```python
from robcomp_interfaces.msg import GameStatus
```

## Regra

O tipo:

```text
PACOTE/msg/MENSAGEM
```

Vira:

```python
from PACOTE.msg import MENSAGEM
```

---

# 7. Como entender o que uma mensagem carrega?

Execute:

```
ros2 interface show PACOTE/msg/MENSAGEM
```

Exemplo:

```
ros2 interface show std_msgs/msg/String
```

Resultado:

```text
string data
```

Isso significa que a mensagem possui o campo:

```python
msg.data
```

Para preencher:

```python
msg.data = 'Olá'
```

Para ler dentro do callback:

```python
texto_recebido = msg.data
```

---

# 8. Mensagem personalizada

As mensagens de `robcomp_interfaces` podem possuir vários campos.

Exemplo imaginário:

```text
string message
string status
string student_name
float64 timestamp
```

Para criar e preencher:

```python
msg = TipoDaMensagem()

msg.message = 'Estou pronto'
msg.status = 'READY'
msg.student_name = 'SEU NOME'
msg.timestamp = 0.0
```

Para receber:

```python
def callback(self, msg):
    texto = msg.message
    status = msg.status
    nome = msg.student_name
    horario = msg.timestamp
```

> Não invente os campos. Sempre use `ros2 interface show` para descobrir os nomes reais.

---

# 9. Como identificar o significado dos campos?

O tipo mostra o nome e o formato, mas nem sempre explica a regra do jogo.

Para descobrir o significado:

1. Leia o enunciado.
2. Execute `ros2 interface show`.
3. Execute `ros2 topic echo`.
4. Observe mensagens reais.
5. Veja os valores possíveis descritos no enunciado.

Exemplo:

```text
string command
string status
```

O enunciado pode dizer:

```text
command:
    "forward"
    "left"
    "right"
    "stop"

status:
    "READY"
    "IN_PROGRESS"
    "DONE"
```

No callback:

```python
def callback(self, msg):
    comando = msg.command
    status = msg.status

    if comando == 'forward':
        self.robot_state = 'forward'

    elif comando == 'left':
        self.robot_state = 'left'

    elif comando == 'right':
        self.robot_state = 'right'

    elif comando == 'stop':
        self.robot_state = 'stop'
```

---

# 10. Receber instruções escritas

Imagine que o agente publique:

```text
Saia do laboratório
```

ou:

```text
Volte para trás
```

Dentro do callback:

```python
def callback(self, msg):
    instrucao = msg.data

    if instrucao == 'Saia do laboratório':
        self.robot_state = 'sair'

    elif instrucao == 'Volte para trás':
        self.robot_state = 'voltar'
```

## Se o texto puder variar entre maiúsculas e minúsculas

```python
instrucao = msg.data.lower()
```

Depois:

```python
if instrucao == 'saia do laboratório':
```

## Se bastar encontrar uma palavra

```python
if 'saia' in instrucao:
    self.robot_state = 'sair'

elif 'volte' in instrucao:
    self.robot_state = 'voltar'
```

> Se o enunciado exigir uma frase exata, compare com a frase exata.

---

# 11. Evitar processar a mesma mensagem várias vezes

Se o agente publica várias vezes ou o timer chama `control`, pode ser necessário guardar a última instrução.

No `__init__`:

```python
self.ultima_instrucao = None
```

No callback:

```python
def callback(self, msg):
    instrucao = msg.data

    if instrucao == self.ultima_instrucao:
        return

    self.ultima_instrucao = instrucao

    # Processar a nova instrução aqui
```

Isso ajuda a evitar:

- responder várias vezes;
- reiniciar uma ação;
- publicar mensagens repetidas;
- “spamar” outro nó.

---

# 12. Testar um tópico pelo terminal

Antes de depender do outro nó, você pode publicar uma mensagem manualmente.

Para `std_msgs/msg/String`:

```
ros2 topic pub -1 /agente std_msgs/msg/String "{data: 'Saia do laboratório'}"
```

O argumento `-1` publica apenas uma vez.

Se seu subscriber estiver funcionando, o callback receberá essa mensagem.

---

# 13. Descobrir os nós em execução

Listar os nós:

```
ros2 node list
```

Ver informações de um nó:

```
ros2 node info /NOME_DO_NO
```

Isso mostra:

- tópicos publicados;
- tópicos assinados;
- serviços;
- ações.

Use quando você sabe o nome do nó, mas não sabe quais tópicos ele utiliza.

---

# 14. Ver quem publica e quem recebe

Execute:

```
ros2 topic info /NOME_DO_TOPICO
```

Observe:

```text
Publisher count
Subscription count
```

## `Publisher count: 0`

Ninguém está enviando mensagens naquele momento.

Confira se o agente, simulador ou teleop está executando.

## `Subscription count: 0`

Ninguém está recebendo as mensagens.

Confira se seu subscriber está executando e se o nome do tópico está correto.

---

# 15. Gravar mensagens com ROS Bag

Use quando quiser registrar os dados de um tópico para repetir depois.

Gravar:

```
ros2 bag record /TOPICO_1 /TOPICO_2 -o nome_da_gravacao
```

Exemplo:

```
ros2 bag record /scan /camera/image_raw -o teste_robo
```

Encerrar a gravação:

```
Ctrl+C
```

Reproduzir:

```
ros2 bag play teste_robo
```

Listar informações:

```
ros2 bag info teste_robo
```

---

# 16. Erros comuns

## O tópico não aparece

- O mapa ou agente pode não estar executando.
- O nome pode estar diferente.
- O terminal pode não ter executado o `source`.
- O pacote necessário pode não ter sido compilado.

Tente:

```
source ~/colcon_ws/install/setup.bash
ros2 topic list
```

---

## O callback não executa

Confira:

- nome do tópico;
- tipo da mensagem;
- se o subscriber foi guardado em `self`;
- se existe `rclpy.spin(node)`;
- se o nó está executando;
- se existe algum publisher no tópico.

---

## `ModuleNotFoundError`

Confira:

- nome do pacote da mensagem;
- import;
- dependências do pacote;
- atualização do `my_simulation`;
- compilação e `source`.

---

## A mensagem não possui o campo usado

Se ocorrer:

```text
AttributeError
```

provavelmente o campo está errado.

Veja novamente:

```
ros2 interface show PACOTE/msg/MENSAGEM
```

Não use `msg.data` automaticamente. Mensagens personalizadas podem usar outro nome.

---

## O código recebe, mas não responde

Confira:

- se o publisher foi criado;
- se a mensagem foi preenchida;
- se chamou `.publish(msg)`;
- se publicou no tópico correto;
- se a resposta exige algum campo obrigatório.

---

# 17. Passo a passo durante a prova

1. Abra o mapa ou agente.
2. Execute `ros2 topic list`.
3. Localize o tópico pedido.
4. Execute `ros2 topic info`.
5. Copie o tipo da mensagem.
6. Execute `ros2 interface show`.
7. Anote os campos.
8. Execute `ros2 topic echo --once`.
9. Observe uma mensagem real.
10. Decida se precisa enviar, receber ou fazer os dois.
11. Abra o arquivo coringa correspondente.
12. Troque o tópico, tipo e campos.
13. Configure o executável no `setup.py`.
14. Compile.
15. Execute o `source`.
16. Rode o nó.
17. Teste pelo terminal.
18. Teste com o agente real da questão.

---

# 18. Checklist

- [ ] Abri o mapa ou agente que cria o tópico.
- [ ] Encontrei o tópico com `ros2 topic list`.
- [ ] Descobri o tipo com `ros2 topic info`.
- [ ] Vi os campos com `ros2 interface show`.
- [ ] Observei uma mensagem com `ros2 topic echo`.
- [ ] Entendi o significado de cada campo.
- [ ] Decidi se preciso de publisher, subscriber ou ambos.
- [ ] Fiz o import correspondente ao tipo.
- [ ] Usei o nome exato do tópico.
- [ ] Preenchi todos os campos obrigatórios.
- [ ] Evitei publicar a mesma resposta várias vezes.
- [ ] Testei o subscriber publicando pelo terminal.
- [ ] Configurei o executável no `setup.py`.
- [ ] Compilei o pacote.
- [ ] Executei o `source`.
- [ ] Confirmei que o callback está recebendo mensagens.