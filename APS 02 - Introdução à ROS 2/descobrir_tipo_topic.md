# Descobrir o Tipo e o Conteúdo de um Tópico

Use este guia quando o professor fornecer um tópico e você precisar descobrir:

- Qual mensagem ele transporta.
- O que existe dentro da mensagem.
- Qual `import` usar no Python.
- Quais campos acessar.
- Como criar o subscriber.
- Se o tópico está realmente funcionando.

---

## Passo 1 — Listar os tópicos disponíveis

No terminal, rode:

```
ros2 topic list
```

Esse comando mostra todos os tópicos que estão funcionando naquele momento.

Exemplo:

```
/cmd_vel
/odom
/scan
/camera/image_raw
/instrucao
```

Se o tópico esperado não aparecer, verifique se o simulador ou o nó responsável por ele está funcionando.

---

## Passo 2 — Descobrir o tipo da mensagem

Use:

```
ros2 topic info /nome_do_topico
```

Exemplo com Odom:

```
ros2 topic info /odom
```

A saída mostrará algo parecido com:

```
Type: nav_msgs/msg/Odometry
Publisher count: 1
Subscription count: 0
```

A parte mais importante é:

```
Type: nav_msgs/msg/Odometry
```

Isso significa que:

- O pacote é `nav_msgs`.
- A mensagem é `Odometry`.
- O import no Python será:

```python
from nav_msgs.msg import Odometry
```

Também é possível mostrar diretamente o tipo usando:

```
ros2 topic type /odom
```

---

## Passo 3 — Transformar o tipo em um import

A ROS mostra o tipo neste formato:

```
pacote/msg/Mensagem
```

No Python, transforme em:

```python
from pacote.msg import Mensagem
```

### Exemplos

| Tipo mostrado pela ROS | Import no Python |
|---|---|
| `std_msgs/msg/String` | `from std_msgs.msg import String` |
| `std_msgs/msg/Bool` | `from std_msgs.msg import Bool` |
| `std_msgs/msg/Int32` | `from std_msgs.msg import Int32` |
| `std_msgs/msg/Float64` | `from std_msgs.msg import Float64` |
| `geometry_msgs/msg/Twist` | `from geometry_msgs.msg import Twist` |
| `nav_msgs/msg/Odometry` | `from nav_msgs.msg import Odometry` |
| `sensor_msgs/msg/LaserScan` | `from sensor_msgs.msg import LaserScan` |
| `sensor_msgs/msg/Image` | `from sensor_msgs.msg import Image` |

---

## Passo 4 — Descobrir o que a mensagem carrega

Depois de descobrir o tipo, use:

```
ros2 interface show TIPO_DA_MENSAGEM
```

Exemplo com Odom:

```
ros2 interface show nav_msgs/msg/Odometry
```

Exemplo com Laser:

```
ros2 interface show sensor_msgs/msg/LaserScan
```

Exemplo com Twist:

```
ros2 interface show geometry_msgs/msg/Twist
```

Esse comando mostra todos os campos existentes na mensagem.

---

## Passo 5 — Ver uma mensagem real

Use:

```
ros2 topic echo /nome_do_topico
```

Exemplo:

```
ros2 topic echo /odom
```

Para mostrar apenas uma mensagem:

```
ros2 topic echo /odom --once
```

O `echo` é importante porque mostra:

- Os campos da mensagem.
- Os valores atuais.
- Como os campos ficam organizados.
- Se o tópico realmente está publicando.

Para encerrar o `echo`, use `Ctrl+C`.

---

# Exemplo completo — Descobrindo o Odom

O professor forneceu:

```
/odom
```

Primeiro, descubra o tipo:

```
ros2 topic info /odom
```

Resultado:

```
Type: nav_msgs/msg/Odometry
```

Portanto, o import será:

```python
from nav_msgs.msg import Odometry
```

Veja a estrutura:

```
ros2 interface show nav_msgs/msg/Odometry
```

Veja uma mensagem real:

```
ros2 topic echo /odom --once
```

Os campos mais importantes são:

```python
msg.pose.pose.position.x
msg.pose.pose.position.y
msg.pose.pose.orientation
msg.twist.twist.linear.x
msg.twist.twist.angular.z
```

Subscriber:

```python
self.odom_sub = self.create_subscription(
    Odometry,
    '/odom',
    self.odom_callback,
    10
)
```

Callback:

```python
def odom_callback(self, msg: Odometry):

    self.x = msg.pose.pose.position.x
    self.y = msg.pose.pose.position.y
```

---

# Exemplo completo — Descobrindo o Laser

O professor forneceu:

```
/scan
```

Descubra o tipo:

```
ros2 topic info /scan
```

Resultado:

```
Type: sensor_msgs/msg/LaserScan
```

Import:

```python
from sensor_msgs.msg import LaserScan
```

Veja a estrutura:

```
ros2 interface show sensor_msgs/msg/LaserScan
```

Veja uma mensagem:

```
ros2 topic echo /scan --once
```

O principal campo é:

```python
msg.ranges
```

Ele contém a lista de distâncias medidas pelo sensor.

Subscriber:

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy

self.laser_sub = self.create_subscription(
    LaserScan,
    '/scan',
    self.laser_callback,
    QoSProfile(
        depth=10,
        reliability=ReliabilityPolicy.BEST_EFFORT
    )
)
```

Callback:

```python
def laser_callback(self, msg: LaserScan):

    self.laser = msg.ranges

    self.frente = msg.ranges[0]
    self.esquerda = msg.ranges[90]
    self.tras = msg.ranges[180]
    self.direita = msg.ranges[270]
```

---

# Exemplo completo — Descobrindo a Imagem

O professor forneceu um tópico de câmera, por exemplo:

```
/camera/image_raw
```

Descubra o tipo:

```
ros2 topic info /camera/image_raw
```

Resultado esperado:

```
Type: sensor_msgs/msg/Image
```

Import:

```python
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
```

Veja a estrutura:

```
ros2 interface show sensor_msgs/msg/Image
```

Crie o `CvBridge` dentro do `__init__`:

```python
self.bridge = CvBridge()
```

Crie o subscriber:

```python
self.imagem_sub = self.create_subscription(
    Image,
    '/camera/image_raw',
    self.imagem_callback,
    10
)
```

Converta a mensagem para OpenCV:

```python
def imagem_callback(self, msg: Image):

    imagem = self.bridge.imgmsg_to_cv2(
        msg,
        desired_encoding='bgr8'
    )
```

Depois da conversão, `imagem` pode ser usada com OpenCV:

```python
imagem_hsv = cv2.cvtColor(
    imagem,
    cv2.COLOR_BGR2HSV
)
```

---

# Exemplo completo — Descobrindo uma String

O professor forneceu:

```
/instrucao
```

Descubra o tipo:

```
ros2 topic info /instrucao
```

Resultado:

```
Type: std_msgs/msg/String
```

Import:

```python
from std_msgs.msg import String
```

Veja a estrutura:

```
ros2 interface show std_msgs/msg/String
```

A estrutura mostrará:

```
string data
```

Isso significa que o texto fica em:

```python
msg.data
```

Subscriber:

```python
self.instrucao_sub = self.create_subscription(
    String,
    '/instrucao',
    self.instrucao_callback,
    10
)
```

Callback:

```python
def instrucao_callback(self, msg: String):

    self.instrucao = msg.data
```

---

# Exemplo completo — Descobrindo um Twist

O professor forneceu:

```
/cmd_vel
```

Descubra o tipo:

```
ros2 topic info /cmd_vel
```

Resultado:

```
Type: geometry_msgs/msg/Twist
```

Import:

```python
from geometry_msgs.msg import Twist
```

Veja a estrutura:

```
ros2 interface show geometry_msgs/msg/Twist
```

Os campos mais importantes são:

```python
msg.linear.x
msg.angular.z
```

Subscriber para acompanhar a velocidade:

```python
self.vel_sub = self.create_subscription(
    Twist,
    '/cmd_vel',
    self.vel_callback,
    10
)
```

Callback:

```python
def vel_callback(self, msg: Twist):

    self.velocidade_linear = msg.linear.x
    self.velocidade_angular = msg.angular.z
```

---

# Campos mais usados

| Tipo | Campo | Significado |
|---|---|---|
| `String` | `msg.data` | Texto |
| `Bool` | `msg.data` | Verdadeiro ou falso |
| `Int32` | `msg.data` | Número inteiro |
| `Float64` | `msg.data` | Número decimal |
| `Twist` | `msg.linear.x` | Velocidade para frente ou para trás |
| `Twist` | `msg.angular.z` | Velocidade de giro |
| `Odometry` | `msg.pose.pose.position.x` | Posição X |
| `Odometry` | `msg.pose.pose.position.y` | Posição Y |
| `Odometry` | `msg.pose.pose.orientation` | Orientação em quaternion |
| `LaserScan` | `msg.ranges` | Lista de distâncias |
| `Image` | Mensagem completa | Imagem que será convertida pelo CvBridge |

---

# Modelo coringa para criar o subscriber

Depois de descobrir o tópico e o tipo, adapte este modelo:

```python
from pacote.msg import TipoDaMensagem
```

Dentro do `__init__`:

```python
self.subscription = self.create_subscription(
    TipoDaMensagem,
    '/nome_do_topico',
    self.callback,
    10
)
```

Callback:

```python
def callback(self, msg: TipoDaMensagem):

    self.valor = msg.campo_da_mensagem
```

Você precisa substituir quatro coisas:

```python
pacote
TipoDaMensagem
/nome_do_topico
msg.campo_da_mensagem
```

---

# Publisher ou subscriber?

Use subscriber quando a informação já existe e você precisa recebê-la.

Exemplos:

- Receber posição do `/odom`.
- Receber distâncias do `/scan`.
- Receber imagem da câmera.
- Receber instruções de outro nó.

Use publisher quando você precisa enviar uma informação.

Exemplos:

- Enviar velocidade para `/cmd_vel`.
- Enviar uma resposta.
- Publicar a quantidade de objetos.
- Avisar que uma tarefa terminou.

Muitas questões usarão os dois:

```text
receber informação
        ↓
processar
        ↓
tomar uma decisão
        ↓
publicar uma resposta
```

Exemplos:

```text
/scan → detectar obstáculo → /cmd_vel
```

```text
/odom → verificar posição → /cmd_vel
```

```text
/camera/image_raw → contar objetos → /quantidade_objetos
```

```text
/instrucao → escolher movimento → /cmd_vel
```

---

# Se o tópico não aparecer

Verifique:

- [ ] O simulador está aberto.
- [ ] O nó que publica o tópico está funcionando.
- [ ] O nome do tópico está escrito corretamente.
- [ ] O terminal recebeu o `source`.
- [ ] Você executou `ros2 topic list`.
- [ ] Não fechou o programa responsável pelo tópico.

---

# Se o subscriber não receber mensagens

Verifique:

- [ ] O tipo usado no código é igual ao mostrado por `ros2 topic info`.
- [ ] O tópico usado no código está escrito corretamente.
- [ ] O import corresponde ao tipo da mensagem.
- [ ] A callback foi passada sem parênteses.
- [ ] O campo acessado realmente existe.
- [ ] O programa está executando `rclpy.spin`.
- [ ] O QoS é compatível com o tópico.
- [ ] Para Laser ou câmera, testou `BEST_EFFORT`.

A callback deve ser passada assim:

```python
self.callback
```

Não assim:

```python
self.callback()
```

---

# Checklist para a prova

- [ ] Rodei `ros2 topic list`.
- [ ] Encontrei o tópico fornecido.
- [ ] Rodei `ros2 topic info /topico`.
- [ ] Anotei o tipo completo da mensagem.
- [ ] Transformei o tipo no import correto.
- [ ] Rodei `ros2 interface show`.
- [ ] Descobri quais campos preciso acessar.
- [ ] Rodei `ros2 topic echo /topico --once`.
- [ ] Conferi os valores reais da mensagem.
- [ ] Criei o subscriber com o tipo correto.
- [ ] Usei o nome correto do tópico.
- [ ] Passei a callback sem `()`.
- [ ] A callback recebe `msg`.
- [ ] Acessei o campo correto dentro de `msg`.
- [ ] Usei `BEST_EFFORT` se necessário.
- [ ] Usei as informações recebidas para resolver o enunciado.