# ======================================================
# printing.py - Generación ZPL y comunicación con impresora
# ======================================================

import platform
import win32print
from tkinter import messagebox
from config import NOMBRE_IMPRESORA, PLANTILLA_ZPL


def generar_zpl(producto, ls, lt):
    """Genera el código ZPL para una etiqueta."""
    precio = producto['precio']
    try:
        precio_float = float(precio)
        precio_str = f"{precio_float:,.0f}".replace(",", ",")
    except:
        precio_str = str(precio)
    
    return PLANTILLA_ZPL.format(
        ls=ls, lt=lt,
        precio=precio_str,
        proveedor=producto['proveedor'].upper(),
        idProducto=producto['id'].upper(),
        material=producto['material'].upper(),
        tipo=producto['tipo'].upper(),
        actualizado=producto['actualizado'].upper(),
        gramos=producto["gramos"]
    )


def enviar_zpl(zpl):
    """Envía código ZPL a la impresora Zebra."""
    if platform.system() == "Windows":
        try:
            h = win32print.OpenPrinter(NOMBRE_IMPRESORA)
            win32print.StartDocPrinter(h, 1, ("etiqueta", None, "RAW"))
            win32print.StartPagePrinter(h)
            win32print.WritePrinter(h, zpl.encode())
            win32print.EndPagePrinter(h)
            win32print.EndDocPrinter(h)
            win32print.ClosePrinter(h)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir:\n{e}")
            return False
    else:
        try:
            with open("/dev/usb/lp0", "wb") as lp:
                lp.write(zpl.encode())
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir (Linux):\n{e}")
            return False

