# Mostrar somente objetos das cores escolhidas

## Quando usar

Use este código quando o professor pedir:

- criar uma máscara de determinada cor;
- segmentar objetos vermelhos, azuis ou de outra cor;
- mostrar somente os objetos selecionados;
- deixar o restante da imagem preto;
- identificar e contar os objetos da máscara;
- combinar máscaras de diferentes cores;
- aplicar uma máscara na imagem original.

---

## O que é a máscara?

A máscara é uma imagem em preto e branco:

- branco: pixel selecionado;
- preto: pixel ignorado.

Depois aplicamos:

    cv2.bitwise_and(imagem, imagem, mask=mascara)

O resultado mantém os pixels selecionados e deixa o restante preto.

---

## Uma única cor

Mostrar somente objetos vermelhos:

    python3 mostrar_apenas_cor_escolhida.py imagens/entrada.png --cores vermelho

Mostrar somente objetos azuis:

    python3 mostrar_apenas_cor_escolhida.py imagens/entrada.png --cores azul

---

## Várias cores

Mostrar objetos vermelhos e azuis:

    python3 mostrar_apenas_cor_escolhida.py imagens/entrada.png --cores vermelho azul

Mostrar vermelho, amarelo e verde:

    python3 mostrar_apenas_cor_escolhida.py imagens/entrada.png --cores vermelho amarelo verde

As máscaras são unidas com `cv2.bitwise_or`.

---

## Fundo preto ou branco

Fundo preto:

    --fundo preto

Fundo branco:

    --fundo branco

Exemplo:

    python3 mostrar_apenas_cor_escolhida.py imagens/entrada.png --cores vermelho --fundo branco

---

## Arquivos gerados

    resultados/mascara_vermelho.png
    resultados/mascara_combinada.png
    resultados/objetos_isolados.png
    resultados/objetos_identificados.png

Será criada uma máscara individual para cada cor solicitada.

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

- [ ] Converti a imagem de BGR para HSV.
- [ ] Criei a máscara da cor solicitada.
- [ ] Para vermelho, utilizei duas faixas.
- [ ] Limpei a máscara.
- [ ] Encontrei os contornos.
- [ ] Removi objetos abaixo da área mínima.
- [ ] Criei uma máscara somente com objetos válidos.
- [ ] Uni as máscaras com `bitwise_or`.
- [ ] Apliquei a máscara usando `bitwise_and`.
- [ ] Contei os objetos encontrados.
- [ ] Desenhei os centros e contornos.
- [ ] Salvei a máscara e a imagem final.

cd .\mostrar_apenas_cor_escolhida


Mostrar somente os balões vermelhos:

& "C:\Users\rafoe\anaconda\python.exe" .\mostrar_apenas_cor_escolhida.py .\imagens\entrada.png --cores vermelho --fundo preto --area-minima 500

Mostrar somente vermelho e azul:

& "C:\Users\rafoe\anaconda\python.exe" .\mostrar_apenas_cor_escolhida.py .\imagens\entrada.png --cores vermelho azul --fundo preto --area-minima 500