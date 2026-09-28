# Distância entre os centros de dois objetos

## Quando usar

Use este código quando o professor pedir:

- encontrar o centro de dois objetos;
- calcular a distância entre os centros;
- desenhar uma linha entre os objetos;
- comparar objetos de cores diferentes;
- calcular a distância entre dois objetos da mesma cor;
- encontrar os objetos mais próximos ou mais distantes.

---

## Modos disponíveis

### maiores

Seleciona o maior objeto de cada cor.

Se as duas cores forem iguais, seleciona os dois maiores objetos.

Exemplo:

    --modo maiores

### mais-proximos

Seleciona o par de objetos com a menor distância entre os centros.

Exemplo:

    --modo mais-proximos

### mais-distantes

Seleciona o par com a maior distância entre os centros.

Exemplo:

    --modo mais-distantes

---

## Fórmula da distância

Se os centros forem:

    centro 1 = (x1, y1)
    centro 2 = (x2, y2)

A distância em pixels será:

    distancia = sqrt((x2 - x1)² + (y2 - y1)²)

O resultado é medido em pixels.

Para transformar em centímetros ou metros, seria necessária uma calibração
da câmera ou uma referência de tamanho conhecida.

---

## Duas cores diferentes

Para calcular a distância entre um objeto vermelho e um azul:

    python3 distancia_entre_objetos.py imagens/entrada.png --cor-1 vermelho --cor-2 azul

Nesse caso, por padrão, será usado o maior objeto vermelho e o maior azul.

---

## Dois objetos da mesma cor

Para escolher os dois maiores objetos vermelhos:

    python3 distancia_entre_objetos.py imagens/entrada.png --cor-1 vermelho --cor-2 vermelho

Para encontrar os dois objetos vermelhos mais próximos:

    python3 distancia_entre_objetos.py imagens/entrada.png --cor-1 vermelho --cor-2 vermelho --modo mais-proximos

---

## Objetos mais próximos de cores diferentes

Para encontrar o balão vermelho e o azul mais próximos:

    python3 distancia_entre_objetos.py imagens/entrada.png --cor-1 vermelho --cor-2 azul --modo mais-proximos

---

## Resultados

O programa salva:

    resultados/mascara_cor_1.png
    resultados/mascara_cor_2.png
    resultados/distancia_entre_objetos.png

Também imprime:

- centro do objeto 1;
- centro do objeto 2;
- área de cada objeto;
- distância entre os centros.

---

## Cores disponíveis

- vermelho;
- laranja;
- amarelo;
- verde;
- ciano;
- azul;
- roxo;
- rosa;
- branco;
- preto.

---

## Checklist

- [ ] Segmentei a primeira cor.
- [ ] Segmentei a segunda cor.
- [ ] Limpei as máscaras.
- [ ] Encontrei os contornos.
- [ ] Removi contornos menores que a área mínima.
- [ ] Calculei o centro de cada contorno.
- [ ] Escolhi corretamente os dois objetos.
- [ ] Calculei delta X.
- [ ] Calculei delta Y.
- [ ] Usei a fórmula da distância.
- [ ] Desenhei os dois centros.
- [ ] Desenhei uma linha entre os centros.
- [ ] Mostrei a distância na imagem.