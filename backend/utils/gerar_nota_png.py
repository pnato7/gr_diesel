from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

def gerar_nota_png(dados):
    largura, altura = 900, 600
    imagem = Image.new("RGB", (largura, altura), "white")
    draw = ImageDraw.Draw(imagem)

    try:
        fonte_titulo = ImageFont.truetype("arial.ttf", 36)
        fonte = ImageFont.truetype("arial.ttf", 22)
    except:
        fonte_titulo = ImageFont.load_default()
        fonte = ImageFont.load_default()

    # Conteúdo
    draw.text((280, 30), "NOTA DE SERVIÇO", fill="black", font=fonte_titulo)

    y = 120
    for label, value in dados.items():
        draw.text((60, y), f"{label}: {value}", fill="black", font=fonte)
        y += 40

    draw.line((70, y+30, 850, y+40), fill="black", width=2)

    nome_arquivo = f"nota_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    caminho = os.path.join("static", "notas", nome_arquivo)

    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    imagem.save(caminho)

    return nome_arquivo