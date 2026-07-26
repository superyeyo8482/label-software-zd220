# ======================================================
# csv_io.py - Carga y guardado de CSV (sin campos obligatorios)
# ======================================================

import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox


def cargar(self):
    """Carga productos desde un archivo CSV. Sin campos obligatorios."""
    archivo = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
    if archivo:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                nuevos = []
                errores = []
                for idx, row in enumerate(reader, start=1):
                    proveedor = row.get('proveedor', '').strip()
                    idProd = row.get('id', '').strip()
                    
                    # Sin campos obligatorios: se cargan todos los datos tal como vienen
                    nuevos.append({
                        'proveedor': proveedor,
                        'id': idProd,
                        'material': row.get('material', '-').strip(),
                        'tipo': row.get('tipo', '-').strip(),
                        'actualizado': row.get('actualizado', '-').strip(),
                        'gramos': row.get('gramos', '0').strip(),
                        'precio': row.get('precio', '0').strip(),
                        'cantidad': int(row.get('cantidad', 1))
                    })
                
                if nuevos:
                    self.productos.extend(nuevos)
                    self.check_vars.extend([tk.BooleanVar(value=False) for _ in nuevos])
                    self.actualizar_tabla()
                    msg = f"✅ Se cargaron {len(nuevos)} productos."
                    if errores:
                        msg += f"\n⚠️ {len(errores)} advertencias"
                    messagebox.showinfo("Carga completada", msg)
                else:
                    messagebox.showwarning("Error", "No se pudo cargar ningún producto")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar:\n{e}")


def guardar(self):
    """Guarda la lista de productos en un archivo CSV."""
    if not self.productos:
        messagebox.showwarning("Lista vacía", "No hay productos que guardar.")
        return
    archivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
    if archivo:
        with open(archivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['proveedor','id','material','tipo','actualizado','gramos','precio','cantidad'])
            writer.writeheader()
            writer.writerows(self.productos)
        messagebox.showinfo("Guardado", f"Lista guardada en {archivo}")
