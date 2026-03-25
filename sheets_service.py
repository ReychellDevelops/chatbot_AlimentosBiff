# en este archivo se realiza la conexion con la api de sheets para realizar cambios (como agregar ordenes y detalle de ordenes)

import os
import json
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ---------------- CONFIG ----------------
load_dotenv()

# almacenamos lo que nos trae .env
CATALOG_SHEET_ID = os.getenv("CATALOG_SHEET_ID") 
ORDERS_SHEET_ID = os.getenv("ORDERS_SHEET_ID")

ORDERS_SHEET = "ordenes" # hoja del sheet donde se registran las ordenes
DETAIL_SHEET = "detalle_orden" # hoja 2 del sheet en donde se registra el detalle de las ordenes

# permisos a spreedsheets y drive para acceder a google sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ---------------- CONEXION BASE ----------------
def get_client():
    creds_raw = os.getenv("GOOGLE_CREDENTIALS")

    if not creds_raw:
        raise Exception("❌ GOOGLE_CREDENTIALS no está configurado")

    try:
        creds_dict = json.loads(creds_raw)
    except Exception as e:
        raise Exception(f"❌ Error parseando credenciales: {e}")

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=SCOPES
    )
    client = gspread.authorize(creds)

    return client

# ---------------- CATALOGO (obtener referencias de carnes registradas en el sheet) ----------------
def get_products():
    client = get_client()
    sheet = client.open_by_key(CATALOG_SHEET_ID).sheet1
    return sheet.get_all_records()

# ---------------- PEDIDOS (obtener acceso a hoja 1 del sheet "orden")----------------
def get_orders_ws():
    client = get_client()
    return client.open_by_key(ORDERS_SHEET_ID).worksheet(ORDERS_SHEET)
#obtener acceso a hoja 2 del sheet "detalle_orden" 
def get_detail_ws():
    client = get_client()
    return client.open_by_key(ORDERS_SHEET_ID).worksheet(DETAIL_SHEET)

# -------- generar id de orden ----------
def generate_order_id():
    sheet = get_orders_ws()
    records = sheet.get_all_records()

    if not records:
        return 1001

    ids = []

    for row in records:
        try:
            ids.append(int(row["order_id"]))
        except:
            continue

    if not ids:
        return 1001

    return max(ids) + 1

# -------- guardar encabezado y datos de orden ----------
def save_order_header(phone, name, tipo_cliente, total_precio, total_peso, sede):

    sheet = get_orders_ws()
    order_id = generate_order_id()

    row = [
        order_id,
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        phone,
        name,
        tipo_cliente,
        total_precio, 
        total_peso,
        "pendiente",
        sede   
    ]

    sheet.append_row(row)

    return order_id

# -------- guardar detalle de orden----------
def save_order_detail(order_id, cart, sede):

    sheet = get_detail_ws()
    rows = []

    for item in cart:
        rows.append([
            order_id,
            item["referencia"],
            item["product"],
            item["units"],
            item["tipo_unidad"],
            item["precio_kg"],
            item["peso_promedio_unitario"],
            item["peso_aprox_total"],
            item["precio_aprox"],
            sede
        ])

    sheet.append_rows(rows, value_input_option="USER_ENTERED")

#----------obtener ofertas----------
def get_offers(sede):

    client = get_client()
    sheet = client.open_by_key(CATALOG_SHEET_ID).worksheet("ofertas")
    records = sheet.get_all_records()

    ofertas_activas = [
        o for o in records
        if str(o["activa"]).lower() == "true"
        and (o["sede"] == sede or o["sede"] == "Todas")
    ]

    return ofertas_activas