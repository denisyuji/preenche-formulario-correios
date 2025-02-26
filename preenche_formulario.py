import json
import io
import sys
import threading
import tty
import termios
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter
import tkinter as tk
from pdf2image import convert_from_path
from PIL import Image, ImageTk

# ------------------ Parâmetros de Configuração ------------------
REMETENTE_X = 45
REMETENTE_Y_OFFSET = 72       # Distância do topo (altura_pagina - offset)
REMETENTE_ALTURA_LINHA = 14
DESTINATARIO_OFFSET = 280

ITEM_INICIO_X = 30
ITEM_INICIO_Y_OFFSET = 156   # Distância do topo (altura_pagina - offset)
ALTURA_LINHA = 15

# Offsets das colunas dos itens em relação a ITEM_INICIO_X:
ITEM_INDICE_OFFSET = 3       # coluna índice
ITEM_NOME_OFFSET  = 30      # coluna nome
ITEM_QTD_OFFSET   = 400     # coluna quantidade
ITEM_PRECO_OFFSET = 453     # coluna preço

# Posição fixa para a linha do total (independente do número de itens)
ITEM_TOTAL_Y_OFFSET = 228   # total desenhado em: altura_pagina - ITEM_TOTAL_Y_OFFSET

# ------------------ Configuração da Data ------------------
DATA_Y_OFFSET = 358         # Linha da data desenhada em: altura_pagina - DATA_Y_OFFSET
DATA_DIA_X_OFFSET = 154
DATA_MES_X_OFFSET = DATA_DIA_X_OFFSET + 42
DATA_ANO_X_OFFSET = DATA_DIA_X_OFFSET + 165
# Offset X da cidade do remetente na linha da data
CIDADE_REMETENTE_DATA_X_OFFSET = 20

# Offsets para duplicata: formulário duplicado com deslocamento (0, -DUPLICATA_OFFSET_Y)
DUPLICATA_OFFSET_X = 0
DUPLICATA_OFFSET_Y = 392

GEOMETRIA_JANELA = "1080x1600+0+0"

NOME_FONTE = "DejaVuSans"
TAMANHO_FONTE_PESSOAS = 7
TAMANHO_FONTE_ITENS = 10
# ------------------ Fim da Configuração ------------------

# Registrar fonte (DejaVuSans está instalada por padrão no Ubuntu)
pdfmetrics.registerFont(TTFont(NOME_FONTE, '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))

# --- Carregar PDF e dados JSON ---
leitor = PdfReader("correios.pdf")
pagina_original = leitor.pages[0]
with open("dados.json", "r") as f:
    dados = json.load(f)

def formatar_brl(valor):
    return f"{valor:.2f}".replace('.', ',') + " R$"

total_itens = sum(item["Quantidade"] * item["Preco"] for item in dados["Itens"])
quantidade_total = sum(item["Quantidade"] for item in dados["Itens"])

caixa_midia = pagina_original.mediabox
largura_pagina, altura_pagina = float(caixa_midia.width), float(caixa_midia.height)

remetente_y = altura_pagina - REMETENTE_Y_OFFSET
item_inicio_y = altura_pagina - ITEM_INICIO_Y_OFFSET

coordenadas_remetente = {
    "Nome":    (REMETENTE_X, remetente_y),
    "Endereco": (REMETENTE_X + 18, remetente_y - 1 * REMETENTE_ALTURA_LINHA),
    "Cidade":    (REMETENTE_X + 5, remetente_y - 3 * REMETENTE_ALTURA_LINHA),
    "Estado":   (REMETENTE_X + 213, remetente_y - 3 * REMETENTE_ALTURA_LINHA),
    "CEP":     (REMETENTE_X - 8, remetente_y - 4 * REMETENTE_ALTURA_LINHA),
    "CPF_CNPJ":  (REMETENTE_X + 165, remetente_y - 4 * REMETENTE_ALTURA_LINHA)
}
coordenadas_destinatario = { 
    chave: (coordenadas[0] + DESTINATARIO_OFFSET, coordenadas[1])
    for chave, coordenadas in coordenadas_remetente.items() 
}

# --- Obter data atual em português ---
hoje = datetime.now()
dia = hoje.day
mes = hoje.month
ano = hoje.year
meses_pt = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# ------------------ Funções de Desenho ------------------
def desenhar_campos(c, coordenadas, dados_dict, tamanho_fonte, offset_x=0, offset_y=0):
    c.setFont(NOME_FONTE, tamanho_fonte)
    for campo, (x, y) in coordenadas.items():
        c.drawString(x + offset_x, y + offset_y, dados_dict.get(campo, ''))

def desenhar_data_e_cidade(c, offset_x=0, offset_y=0):
    c.setFont(NOME_FONTE, TAMANHO_FONTE_ITENS)
    data_y = altura_pagina - DATA_Y_OFFSET + offset_y
    c.drawString(offset_x + DATA_DIA_X_OFFSET, data_y, f"{dia}")
    c.drawString(offset_x + DATA_MES_X_OFFSET, data_y, meses_pt.get(mes, ""))
    c.drawString(offset_x + DATA_ANO_X_OFFSET, data_y, f"{ano}")
    c.drawString(offset_x + CIDADE_REMETENTE_DATA_X_OFFSET, data_y, dados["Remetente"].get("Cidade", ""))

def desenhar_formulario(c, offset_x=0, offset_y=0):
    # Desenhar informações do remetente e destinatário
    desenhar_campos(c, coordenadas_remetente, dados["Remetente"], TAMANHO_FONTE_PESSOAS, offset_x, offset_y)
    desenhar_campos(c, coordenadas_destinatario, dados["Destinatario"], TAMANHO_FONTE_PESSOAS, offset_x, offset_y)
    # Desenhar lista de itens com os deslocamentos de coluna
    c.setFont(NOME_FONTE, TAMANHO_FONTE_ITENS)
    y_pos = item_inicio_y + offset_y - ALTURA_LINHA
    for idx, item in enumerate(dados["Itens"], start=1):
        preco = formatar_brl(item['Preco'])
        c.drawString(ITEM_INICIO_X + ITEM_INDICE_OFFSET + offset_x, y_pos, f"{idx}")
        c.drawString(ITEM_INICIO_X + ITEM_NOME_OFFSET + offset_x, y_pos, f"{item['Nome']}")
        c.drawString(ITEM_INICIO_X + ITEM_QTD_OFFSET + offset_x, y_pos, f"{item['Quantidade']}")
        c.drawString(ITEM_INICIO_X + ITEM_PRECO_OFFSET + offset_x, y_pos, f"{preco}")
        y_pos -= ALTURA_LINHA
    # Desenhar totais em posição fixa
    total_linha_y = altura_pagina - ITEM_TOTAL_Y_OFFSET + offset_y
    c.drawString(ITEM_INICIO_X + ITEM_QTD_OFFSET + offset_x, total_linha_y, f"{quantidade_total}")
    c.drawString(ITEM_INICIO_X + ITEM_PRECO_OFFSET + offset_x, total_linha_y, f"{formatar_brl(total_itens)}")
    # Desenhar data e cidade do remetente
    desenhar_data_e_cidade(c, offset_x, offset_y)

# ------------------ Criar sobreposição ------------------
pacote = io.BytesIO()
c = canvas.Canvas(pacote, pagesize=(largura_pagina, altura_pagina))

for i in range(2):
    offset_x = i * DUPLICATA_OFFSET_X
    offset_y = i * (-DUPLICATA_OFFSET_Y)
    desenhar_formulario(c, offset_x, offset_y)

c.save()
pacote.seek(0)
pagina_overlay = PdfReader(pacote).pages[0]
pagina_original.merge_page(pagina_overlay)

escritor = PdfWriter()
escritor.add_page(pagina_original)
with open("formulario_preenchido.pdf", "wb") as arquivo_saida:
    escritor.write(arquivo_saida)
print("PDF gerado com sucesso como formulario_preenchido.pdf")
