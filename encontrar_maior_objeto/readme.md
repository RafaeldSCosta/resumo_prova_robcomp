# Encontrar o maior objeto da imagem

## Quando usar

Use este código quando o professor pedir:

- encontrar o maior objeto;
- comparar a área de diferentes objetos;
- encontrar o maior objeto de determinada cor;
- comparar objetos de várias cores;
- destacar o maior contorno;
- criar um ranking por área.

---

## Uma única cor

Para encontrar o maior objeto vermelho:

    python3 encontrar_maior_objeto.py imagens/entrada.png --cores vermelho

Para encontrar o maior objeto azul:

    python3 encontrar_maior_objeto.py imagens/entrada.png --cores azul

---

## Várias cores

Para comparar objetos vermelhos, azuis e amarelos:

    python3 encontrar_maior_objeto.py imagens/entrada.png --cores vermelho azul amarelo

O programa segmentará cada cor, encontrará os objetos e selecionará aquele
com a maior área.

---

## Como o maior objeto é encontrado

Para cada contorno:

    area = cv2.contourArea(contorno)

Depois, o maior é selecionado usando:

    maior_objeto = max(objetos, key=lambda objeto: objeto["area"])

---

## Resultado

Todos os objetos encontrados são desenhados com contornos mais finos.

O maior objeto recebe:

- contorno verde grosso;
- caixa delimitadora;
- centro;
- texto `MAIOR OBJETO`;
- valor da área.

O programa salva:

    resultados/mascara_combinada.png
    resultados/maior_objeto.png
    resultados/ranking_areas.csv

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

## Área mínima

A área mínima remove pequenos ruídos.

Exemplo:

    --area-minima 500

Se estiver contando sujeira:

    --area-minima 1500

Se estiver ignorando objetos pequenos:

    --area-minima 100

---

## Checklist

- [ ] Escolhi as cores que serão comparadas.
- [ ] Criei uma máscara para cada cor.
- [ ] Limpei as máscaras.
- [ ] Encontrei os contornos externos.
- [ ] Removi contornos menores que a área mínima.
- [ ] Calculei a área de cada objeto.
- [ ] Calculei o centro de cada objeto.
- [ ] Coloquei todos os objetos em uma lista.
- [ ] Usei `max` para encontrar o maior.
- [ ] Desenhei todos os contornos.
- [ ] Destaquei o maior objeto.
- [ ] Salvei o ranking das áreas.