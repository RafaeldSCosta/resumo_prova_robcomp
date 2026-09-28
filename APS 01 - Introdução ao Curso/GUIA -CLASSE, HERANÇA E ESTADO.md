# Guia — Classes, Herança e Estados

> Use este guia para transformar as exigências do enunciado em uma estrutura de código.

---

# 1. Qual arquivo devo abrir?

| O enunciado pede... | Arquivo |
|---|---|
| Criar uma classe | `classes_e_heranca.py` |
| Criar atributos e métodos | `classes_e_heranca.py` |
| Herdar de uma classe fornecida | `classes_e_heranca.py` |
| Utilizar `super().__init__()` | `classes_e_heranca.py` |
| Criar comportamentos ou ações | `maquina_de_estados.py` |
| Escolher ações usando estados | `maquina_de_estados.py` |
| Alterar `self.robot_state` | `maquina_de_estados.py` |
| Chamar funções por um dicionário | `maquina_de_estados.py` |
| Resolver a APS 1 completa | `aps1_resolvida.py` |

---

# 2. Quando usar uma classe?

Use uma classe quando o enunciado disser algo como:

- “Crie uma classe chamada `Control`.”
- “A classe deve possuir os atributos...”
- “Implemente os métodos...”
- “Crie um objeto da classe...”
- “A classe deve herdar de `Mapa`.”
- “A classe deve implementar um nó chamado...”

Exemplo de tradução:

> Crie uma classe chamada `Robo`, com um atributo `velocidade`, inicialmente igual a zero.

Vira:

```python
class Robo:

    def __init__(self):
        self.velocidade = 0.0
```

---

# 3. O que deve ficar no `__init__`?

Coloque no `__init__`:

- valores iniciais;
- estado inicial;
- posição inicial;
- variáveis usadas por vários métodos;
- objetos auxiliares;
- dicionário da máquina de estados.

Exemplo:

```python
def __init__(self):
    self.velocidade = 0.0
    self.robot_state = 'inicio'
    self.finalizado = False
```

Use `self` quando uma informação precisar ser acessada ou alterada por mais de um método.

---

# 4. Quando usar herança?

Use herança quando o enunciado disser:

- “A classe `Control` deve herdar de `Mapa`.”
- “Baseando-se na classe...”
- “Utilize a classe fornecida...”
- “A classe deve ser um nó ROS 2.”

Formato:

```python
class ClasseFilha(ClassePai):

    def __init__(self):
        super().__init__()
```

Exemplo com a classe `Mapa`:

```python
class Control(Mapa):

    def __init__(self):
        super().__init__()
```

Exemplo de nó ROS 2:

```python
class MeuRobo(Node):

    def __init__(self):
        super().__init__('nome_do_no')
```

> Não altere a classe fornecida pelo professor, a menos que o enunciado permita.

---

# 5. Quando usar máquina de estados?

Use uma máquina de estados quando o robô ou programa possuir vários comportamentos.

Exemplos:

- andar para frente;
- virar para a esquerda;
- virar para a direita;
- esperar;
- procurar um objeto;
- parar.

Cada comportamento vira:

1. um nome de estado;
2. uma função;
3. uma entrada no dicionário.

Exemplo:

```python
self.robot_state = 'forward'

self.state_machine = {
    'forward': self.forward,
    'left': self.left,
    'right': self.right,
    'stop': self.stop,
}
```

---

# 6. Como executar o estado atual?

A linha principal é:

```python
self.state_machine[self.robot_state]()
```

Ela faz o seguinte:

1. lê o valor de `self.robot_state`;
2. procura esse valor no dicionário;
3. encontra a função correspondente;
4. executa a função.

Exemplo:

```python
self.robot_state = 'left'
self.state_machine[self.robot_state]()
```

Isso executará:

```python
self.left()
```

---

# 7. Como trocar de estado?

Para mudar o comportamento do robô:

```python
self.robot_state = 'nome_do_proximo_estado'
```

Exemplo:

```python
if obstaculo_na_frente:
    self.robot_state = 'left'
else:
    self.robot_state = 'forward'
```

A função correspondente será executada na próxima chamada do controle.

---

# 8. Como transformar um enunciado em estados?

Exemplo de enunciado:

> O carro deve seguir para frente quando o caminho estiver livre. Se houver obstáculo, deve ir para a esquerda ou direita. Ao chegar à primeira linha, deve parar.

## Estados necessários

```text
forward
left
right
stop
```

## Funções necessárias

```python
def forward(self):
def left(self):
def right(self):
def stop(self):
```

## Dicionário necessário

```python
self.state_machine = {
    'forward': self.forward,
    'left': self.left,
    'right': self.right,
    'stop': self.stop,
}
```

## Condições necessárias

- caminho livre → `forward`;
- obstáculo com espaço à esquerda → `left`;
- obstáculo com espaço à direita → `right`;
- chegou ao final → `stop`.

---

# 9. Ordem recomendada para resolver

1. Copie os nomes exatos exigidos.
2. Crie a classe.
3. Faça a herança, se necessário.
4. Chame `super().__init__()`.
5. Crie os atributos iniciais.
6. Liste todos os comportamentos.
7. Transforme cada comportamento em uma função.
8. Monte o dicionário de estados.
9. Implemente as condições de troca.
10. Execute o estado atual no `control`.
11. Teste cada estado separadamente.
12. Teste o caminho completo.

---

# 10. Erros comuns

## Esquecer o `self`

Errado:

```python
velocidade = 0.0
```

Certo:

```python
self.velocidade = 0.0
```

---

## Colocar `()` no dicionário

Errado:

```python
self.state_machine = {
    'forward': self.forward(),
}
```

Certo:

```python
self.state_machine = {
    'forward': self.forward,
}
```

Os parênteses aparecem somente quando a função for executada:

```python
self.state_machine[self.robot_state]()
```

---

## Usar um estado que não existe

Se fizer:

```python
self.robot_state = 'girar'
```

o dicionário precisa possuir:

```python
'girar': self.girar,
```

Caso contrário, ocorrerá um `KeyError`.

---

## Esquecer o `super()`

Se a classe precisa herdar e inicializar a classe pai:

```python
class Control(Mapa):

    def __init__(self):
        super().__init__()
```

---

## Chamar um método sem parênteses

Isso não executa:

```python
self.stop
```

Isso executa:

```python
self.stop()
```

---

# 11. Checklist

- [ ] Copiei o nome exato da classe.
- [ ] Criei o `__init__`.
- [ ] Coloquei `self` nos atributos e métodos.
- [ ] Fiz a herança exigida.
- [ ] Chamei `super().__init__()`.
- [ ] Criei o estado inicial.
- [ ] Listei todos os comportamentos pedidos.
- [ ] Criei uma função para cada comportamento.
- [ ] Adicionei todas as funções ao dicionário.
- [ ] Não coloquei `()` nas funções dentro do dicionário.
- [ ] Todos os valores de `robot_state` existem no dicionário.
- [ ] Implementei as condições de troca de estado.
- [ ] O estado `stop` realmente interrompe o programa ou movimento.
- [ ] A função `control` executa o estado atual.
- [ ] Testei cada estado separadamente.