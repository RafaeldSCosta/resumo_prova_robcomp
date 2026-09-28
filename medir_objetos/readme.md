# Encontrar área e centro dos objetos

## Quando usar

Use este código quando o professor pedir:

- encontrar objetos de determinada cor;
- calcular a área de cada objeto;
- calcular o centro de cada objeto;
- desenhar o centro na imagem;
- informar as coordenadas dos objetos;
- descobrir a posição de cada objeto;
- gerar uma lista com as medidas encontradas.

---

## O que o código calcula

Para cada objeto, o programa encontra:

- número do objeto;
- área em pixels;
- centro X;
- centro Y;
- caixa delimitadora;
- posição e tamanho da caixa.

Exemplo de resultado:

    Objeto 1:
        Área: 15432 pixels
        Centro: (125, 240)

---

## Área

A área é calculada usando:

    cv2.contourArea(contorno)

A área é medida em pixels quadrados.

Ela não representa metros, centímetros ou uma medida real, a menos que
exista uma calibração da câmera.

---

## Centro do objeto

O centro é calculado usando os momentos do contorno:

    momentos = cv2.moments(contorno)

    centro_x = momentos["m10"] / momentos["m00"]
    centro_y = momentos["m01"] / momentos["m00"]

As coordenadas seguem o padrão da imagem:

- X aumenta da esquerda para a direita;
- Y aumenta de cima para baixo;
- o ponto (0, 0) fica no canto superior esquerdo.

---

## Cores disponíveis

O código possui valores iniciais para:

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

Dependendo da iluminação, pode ser necessário ajustar as faixas HSV.

---

## Executar

Usando os valores padrão:

    python3 medir_objetos.py

Escolhendo uma cor:

    python3 medir_objetos.py imagens/entrada.png --cor vermelho

Alterando a área mínima:

    python3 medir_objetos.py imagens/entrada.png --cor azul --area-minima 1000

No Windows, se o comando configurado for `python`:

    python medir_objetos.py imagens/entrada.png --cor vermelho

---

## Resultados

O programa cria:

    resultados/mascara.png
    resultados/objetos_medidos.png
    resultados/medidas.csv

O arquivo CSV terá uma linha para cada objeto:

    objeto,area,centro_x,centro_y,x,y,largura,altura

---

## O que alterar na prova

Se o professor mudar a imagem:

    python3 medir_objetos.py CAMINHO_DA_IMAGEM

Se mudar a cor:

    --cor amarelo

Se estiver contando ruídos:

    --area-minima 1000

Se estiver ignorando objetos pequenos:

    --area-minima 100

Se o professor fornecer limites HSV específicos, altere o dicionário
`FAIXAS_HSV` dentro do código.

---

## Checklist

- [ ] Carreguei a imagem.
- [ ] Converti BGR para HSV.
- [ ] Criei a máscara da cor pedida.
- [ ] Limpei a máscara.
- [ ] Encontrei os contornos externos.
- [ ] Ignorei áreas menores que a área mínima.
- [ ] Calculei a área com `cv2.contourArea`.
- [ ] Calculei os momentos com `cv2.moments`.
- [ ] Verifiquei se `m00` é diferente de zero.
- [ ] Calculei centro X usando `m10 / m00`.
- [ ] Calculei centro Y usando `m01 / m00`.
- [ ] Desenhei os centros na imagem.
- [ ] Mostrei área e coordenadas.
- [ ] Salvei os resultados.