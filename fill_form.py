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

# ------------------ Configuration Parameters ------------------
SENDER_X = 45
SENDER_Y_OFFSET = 72       # Distance from the top (page_height - offset)
SENDER_LINE_HEIGHT = 14
RECEIVER_OFFSET = 280

ITEM_START_X = 30
ITEM_START_Y_OFFSET = 156   # Distance from the top (page_height - offset)
LINE_HEIGHT = 15

# Offsets for item columns relative to ITEM_START_X:
ITEM_INDEX_OFFSET = 3       # index column
ITEM_NAME_OFFSET  = 30      # name column
ITEM_QTY_OFFSET   = 400     # quantity column
ITEM_PRICE_OFFSET = 453     # price column

# Fixed position for the total line (regardless of number of items)
ITEM_TOTAL_Y_OFFSET = 228   # total line drawn at: page_height - ITEM_TOTAL_Y_OFFSET

# ------------------ Date Configuration ------------------
DATE_Y_OFFSET = 358         # Date line drawn at: page_height - DATE_Y_OFFSET
DATE_DAY_X_OFFSET = 154
DATE_MONTH_X_OFFSET = DATE_DAY_X_OFFSET + 42
DATE_YEAR_X_OFFSET = DATE_DAY_X_OFFSET + 165
# X offset for sender's city at date line
SENDER_CITY_DATE_X_OFFSET = 20

# Duplicate offsets: duplicate form drawn with offset (0, -DUPLICATE_OFFSET_Y)
DUPLICATE_OFFSET_X = 0
DUPLICATE_OFFSET_Y = 392

WINDOW_GEOMETRY = "1080x1600+0+0"

FONT_NAME = "DejaVuSans"
FONT_SIZE_PEOPLE = 7
FONT_SIZE_ITEMS = 10
# ------------------ End of Configuration ------------------

# Register font (DejaVuSans is installed by default on Ubuntu)
pdfmetrics.registerFont(TTFont(FONT_NAME, '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))

# --- Load PDF and JSON data ---
reader = PdfReader("correios.pdf")
original_page = reader.pages[0]
with open("input.json", "r") as f:
    data = json.load(f)

def format_brl(amount):
    return f"{amount:.2f}".replace('.', ',') + " R$"

items_total = sum(item["Qty"] * item["Price"] for item in data["Itens"])
total_qty = sum(item["Qty"] for item in data["Itens"])

media_box = original_page.mediabox
page_width, page_height = float(media_box.width), float(media_box.height)

sender_y = page_height - SENDER_Y_OFFSET
item_start_y = page_height - ITEM_START_Y_OFFSET

sender_coords = {
    "Name":    (SENDER_X, sender_y),
    "Address": (SENDER_X + 18, sender_y - 1 * SENDER_LINE_HEIGHT),
    "City":    (SENDER_X + 5, sender_y - 3 * SENDER_LINE_HEIGHT),
    "State":   (SENDER_X + 213, sender_y - 3 * SENDER_LINE_HEIGHT),
    "Zip":     (SENDER_X - 8, sender_y - 4 * SENDER_LINE_HEIGHT),
    "Tax_id":  (SENDER_X + 165, sender_y - 4 * SENDER_LINE_HEIGHT)
}
receiver_coords = { 
    key: (coords[0] + RECEIVER_OFFSET, coords[1])
    for key, coords in sender_coords.items() 
}

# --- Get current date in Portuguese ---
today = datetime.now()
day = today.day
month = today.month
year = today.year
months_pt = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# ------------------ Drawing Functions ------------------
def draw_fields(c, coords, data_dict, font_size, offset_x=0, offset_y=0):
    c.setFont(FONT_NAME, font_size)
    for field, (x, y) in coords.items():
        c.drawString(x + offset_x, y + offset_y, data_dict.get(field, ''))

def draw_date_and_city(c, offset_x=0, offset_y=0):
    c.setFont(FONT_NAME, FONT_SIZE_ITEMS)
    date_y = page_height - DATE_Y_OFFSET + offset_y
    c.drawString(offset_x + DATE_DAY_X_OFFSET, date_y, f"{day}")
    c.drawString(offset_x + DATE_MONTH_X_OFFSET, date_y, months_pt.get(month, ""))
    c.drawString(offset_x + DATE_YEAR_X_OFFSET, date_y, f"{year}")
    c.drawString(offset_x + SENDER_CITY_DATE_X_OFFSET, date_y, data["Sender"].get("City", ""))

def draw_form(c, offset_x=0, offset_y=0):
    # Draw sender and receiver info
    draw_fields(c, sender_coords, data["Sender"], FONT_SIZE_PEOPLE, offset_x, offset_y)
    draw_fields(c, receiver_coords, data["Receiver"], FONT_SIZE_PEOPLE, offset_x, offset_y)
    # Draw items list with column offsets
    c.setFont(FONT_NAME, FONT_SIZE_ITEMS)
    y_pos = item_start_y + offset_y - LINE_HEIGHT
    for idx, item in enumerate(data["Itens"], start=1):
        price = format_brl(item['Price'])
        c.drawString(ITEM_START_X + ITEM_INDEX_OFFSET + offset_x, y_pos, f"{idx}")
        c.drawString(ITEM_START_X + ITEM_NAME_OFFSET + offset_x, y_pos, f"{item['Name']}")
        c.drawString(ITEM_START_X + ITEM_QTY_OFFSET + offset_x, y_pos, f"{item['Qty']}")
        c.drawString(ITEM_START_X + ITEM_PRICE_OFFSET + offset_x, y_pos, f"{price}")
        y_pos -= LINE_HEIGHT
    # Draw totals at fixed position
    total_line_y = page_height - ITEM_TOTAL_Y_OFFSET + offset_y
    c.drawString(ITEM_START_X + ITEM_QTY_OFFSET + offset_x, total_line_y, f"{total_qty}")
    c.drawString(ITEM_START_X + ITEM_PRICE_OFFSET + offset_x, total_line_y, f"{format_brl(items_total)}")
    # Draw date and sender's city
    draw_date_and_city(c, offset_x, offset_y)

# ------------------ Create Overlay ------------------
packet = io.BytesIO()
c = canvas.Canvas(packet, pagesize=(page_width, page_height))

# Loop for two copies: original (i=0) and duplicate (i=1)
for i in range(2):
    offset_x = i * DUPLICATE_OFFSET_X  # Always 0 per config
    offset_y = i * (-DUPLICATE_OFFSET_Y)
    draw_form(c, offset_x, offset_y)

c.save()
packet.seek(0)
overlay_page = PdfReader(packet).pages[0]
original_page.merge_page(overlay_page)

writer = PdfWriter()
writer.add_page(original_page)
with open("output.pdf", "wb") as out_file:
    writer.write(out_file)
print("PDF generated successfully as output.pdf")

pages = convert_from_path("output.pdf", dpi=150)
if not pages:
    raise Exception("No pages found in the PDF.")
page_image = pages[0]

root = tk.Tk()
root.title("PDF Viewer")
root.geometry(WINDOW_GEOMETRY)

# Removed key bindings and terminal listener

tk_image = ImageTk.PhotoImage(page_image)
tk.Label(root, image=tk_image).pack(expand=True, fill='both')
root.mainloop()
