# Contar objetos de determinada cor

## Quando usar

Use este código quando o professor fornecer uma imagem com vários objetos e pedir:

- segmentar uma determinada cor;
- contar quantos objetos dessa cor existem;
- ignorar pequenos ruídos;
- desenhar os objetos encontrados;
- salvar a máscara e o resultado;
- funcionar com diferentes imagens semelhantes.

Exemplos:

- contar balões vermelhos;
- contar bolas azuis;
- contar latinhas vermelhas;
- contar blocos amarelos;
- contar figuras verdes.

---

## Estrutura

    contar_objetos_por_cor/
    ├── README.md
    ├── contar_objetos_por_cor.py
    ├── requirements.txt
    ├── imagens/
    │   └── entrada.png
    └── resultados/

A imagem original deve ser colocada dentro da pasta `imagens`.

Os resultados serão salvos automaticamente dentro da pasta `resultados`.

---

## Fluxo do processamento

1. Carregar a imagem.
2. Converter de BGR para HSV.
3. Selecionar a faixa da cor desejada.
4. Criar uma máscara binária.
5. Aplicar abertura para remover pontos pequenos.
6. Aplicar fechamento para preencher pequenos buracos.
7. Encontrar os contornos externos.
8. Ignorar contornos menores que a área mínima.
9. Contar os contornos restantes.
10. Desenhar uma caixa em cada objeto encontrado.
11. Salvar a máscara e a imagem final.

---

## Por que usar HSV?

No OpenCV, uma imagem normalmente é carregada em BGR.

O HSV separa:

- H: tipo da cor;
- S: intensidade da cor;
- V: brilho.

Isso facilita selecionar uma cor mesmo quando existem pequenas mudanças
de iluminação.

---

## Cores disponíveis

O código já possui valores iniciais para:

- vermelho;
- laranja;
- amarelo;
- verde;
- azul;
- roxo;
- branco;
- preto.

Esses valores são coringas. Dependendo da iluminação da imagem, pode ser
necessário ajustar os limites HSV.

---

## Atenção com o vermelho

No HSV do OpenCV, o vermelho aparece no começo e no final da escala de H.

Por isso, o código utiliza duas máscaras:

    vermelho baixo: H entre 0 e 10
    vermelho alto: H entre 170 e 180

Depois, as duas máscaras são unidas com `cv2.bitwise_or`.

---

## Área mínima

A área mínima serve para não contar pequenos ruídos como objetos.

Por exemplo:

    area_minima = 500

Significa que qualquer contorno com área menor que 500 pixels será ignorado.

Se objetos verdadeiros estiverem sendo ignorados, diminua a área mínima.

Se pequenos ruídos estiverem sendo contados, aumente a área mínima.

---

## Executar com os valores padrão

A configuração padrão procura objetos vermelhos na imagem:

    imagens/entrada.png

Execute:

    python3 contar_objetos_por_cor.py

---

## Escolher outra imagem e outra cor

Contar objetos azuis:

    python3 contar_objetos_por_cor.py imagens/foto.png --cor azul

Contar objetos amarelos:

    python3 contar_objetos_por_cor.py imagens/foto.png --cor amarelo

Alterar a área mínima:

    python3 contar_objetos_por_cor.py imagens/foto.png --cor verde --area-minima 1000

Não abrir as janelas e somente salvar os resultados:

    python3 contar_objetos_por_cor.py imagens/foto.png --cor vermelho --sem-janela

---

## Resultados

O programa salva:

    resultados/mascara.png
    resultados/objetos_encontrados.png

Também imprime no terminal:

    Cor procurada: vermelho
    Quantidade de objetos encontrados: 4

---

## O que normalmente alterar na prova

Se o professor mudar a cor:

    --cor azul

Se mudar a imagem:

    python3 contar_objetos_por_cor.py CAMINHO_DA_IMAGEM

Se os objetos forem menores:

    --area-minima 100

Se estiver contando ruído:

    --area-minima 1000

Se nenhuma faixa pronta funcionar, altere o dicionário `FAIXAS_HSV`
dentro do código.

---

## Checklist

- [ ] A imagem foi carregada corretamente.
- [ ] Converti a imagem de BGR para HSV.
- [ ] Escolhi a cor solicitada.
- [ ] Para vermelho, utilizei duas faixas HSV.
- [ ] Criei a máscara com `cv2.inRange`.
- [ ] Uni as máscaras quando existia mais de uma faixa.
- [ ] Apliquei abertura para remover ruído.
- [ ] Apliquei fechamento para preencher buracos.
- [ ] Usei `cv2.findContours`.
- [ ] Usei `cv2.RETR_EXTERNAL`.
- [ ] Filtrei os contornos pela área mínima.
- [ ] Contei somente os contornos válidos.
- [ ] Desenhei uma caixa em cada objeto.
- [ ] Mostrei a quantidade na imagem.
- [ ] Salvei a máscara e o resultado.