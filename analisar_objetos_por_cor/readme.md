# Analisar objetos por cor

## Quando usar

Use este código quando o professor pedir:

- contar objetos de determinadas cores;
- calcular a área de cada objeto;
- encontrar o centro de cada objeto;
- descobrir o maior objeto da imagem;
- encontrar o maior objeto de cada cor;
- descobrir qual cor ocupa a maior área;
- comparar diferentes cores;
- criar máscaras para várias cores.

---

## Resultados calculados

Para cada objeto:

- cor;
- área;
- centro X;
- centro Y;
- caixa delimitadora.

Para cada cor:

- quantidade de objetos;
- área total;
- maior objeto daquela cor.

Para a imagem completa:

- maior objeto individual;
- cor com maior área total;
- ranking das cores.

---

## Diferença importante

### Maior objeto individual

É o contorno individual com maior área.

Exemplo:

    maior objeto: balão azul com 20.000 pixels

### Cor dominante

É a soma das áreas de todos os objetos daquela cor.

Exemplo:

    vermelho:
        5 objetos
        área total: 70.000 pixels

    azul:
        3 objetos
        área total: 50.000 pixels

Nesse caso, vermelho é a cor dominante, mesmo que o maior objeto
individual seja azul.

---

## Executar

Analisar vermelho, azul, amarelo e verde:

    python3 analisar_objetos_por_cor.py imagens/entrada.png --cores vermelho azul amarelo verde

Analisar somente vermelho e rosa:

    python3 analisar_objetos_por_cor.py imagens/entrada.png --cores vermelho rosa

Alterar a área mínima:

    python3 analisar_objetos_por_cor.py imagens/entrada.png --cores vermelho azul --area-minima 1000

---

## Arquivos gerados

    resultados/resultado_completo.png
    resultados/mascara_combinada.png
    resultados/mascara_vermelho.png
    resultados/mascara_azul.png
    resultados/objetos.csv
    resultados/resumo_cores.csv

Será criada uma máscara para cada cor solicitada.

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
- marrom;
- branco;
- cinza;
- preto.

---

## Checklist

- [ ] Escolhi as cores solicitadas.
- [ ] Converti a imagem para HSV.
- [ ] Criei uma máscara para cada cor.
- [ ] Limpei cada máscara.
- [ ] Encontrei os contornos externos.
- [ ] Removi contornos menores que a área mínima.
- [ ] Contei os objetos de cada cor.
- [ ] Calculei a área de cada objeto.
- [ ] Calculei o centro de cada objeto.
- [ ] Somei as áreas de cada cor.
- [ ] Encontrei o maior objeto individual.
- [ ] Encontrei o maior objeto de cada cor.
- [ ] Encontrei a cor dominante.
- [ ] Salvei as máscaras e os resultados.


cd .\analisar_objetos_por_cor

& "C:\Users\rafoe\anaconda\python.exe" .\analisar_objetos_por_cor.py .\imagens\entrada.png --cores vermelho azul amarelo verde ciano rosa --area-minima 500