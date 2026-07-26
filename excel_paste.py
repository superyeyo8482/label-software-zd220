# ======================================================
# excel_paste.py - Pegado desde Excel (sin campos obligatorios)
# ======================================================

import tkinter as tk
from tkinter import messagebox

def pegar_desde_excel(self):
    try:
        datos_raw = self.root.clipboard_get()
        if not datos_raw:
            messagebox.showwarning("Portapapeles vacío", "No hay datos para pegar.")
            return

        lineas = datos_raw.replace('\r', '').strip().split('\n')
        if not lineas:
            return

        sep = '\t' if '\t' in lineas[0] else ','
        respuesta = messagebox.askyesno("Encabezados", "¿La primera fila contiene los títulos?")
        inicio = 1 if respuesta else 0

        nuevos = []
        errores = []
        filas_ignoradas = 0

        for idx_fila, linea in enumerate(lineas[inicio:], start=1):
            if not linea.strip():
                continue

            celdas = linea.split(sep)
            while len(celdas) < 8:
                celdas.append('')

            proveedor = celdas[0].strip()
            idProd = celdas[1].strip()
            material = celdas[2].strip() if celdas[2].strip() else "-"
            tipo = celdas[3].strip() if celdas[3].strip() else "-"
            actualizado = celdas[4].strip() if celdas[4].strip() else "-"
            gramos_raw = celdas[5].strip()
            precio_raw = celdas[6].strip()
            cantidad_raw = celdas[7].strip()

            # Sin campos obligatorios
            if not proveedor:
                filas_ignoradas += 1
                errores.append(f"Fila {idx_fila}: Proveedor vacío")

            if not idProd:
                idProd = ""

            # Limpiar gramos
            gramos_clean = gramos_raw.lower().replace('gramos', '').replace('gr', '').replace('g', '').replace(',', '').strip()
            try:
                g = int(float(gramos_clean)) if gramos_clean else 0
                gramos = str(g)
            except ValueError:
                gramos = "0"

            # Limpiar precio
            precio_clean = precio_raw.replace("$", "").replace(" ", "").replace(",", "").replace("\xa0", "").strip()
            if precio_clean == '':
                precio_clean = '0'
            try:
                p = float(precio_clean)
                precio = f"{p:.0f}"
            except ValueError:
                try:
                    precio_clean = precio_raw.replace("$", "").replace(" ", "").replace(",", ".")
                    p = float(precio_clean)
                    precio = f"{p:.0f}"
                except ValueError:
                    precio = "0"

            # Cantidad
            try:
                cantidad = int(float(cantidad_raw)) if cantidad_raw else 1
                if cantidad < 1:
                    cantidad = 1
            except ValueError:
                cantidad = 1

            nuevos.append({
                'proveedor': proveedor,
                'id': idProd,
                'material': material,
                'tipo': tipo,
                'actualizado': actualizado,
                'gramos': gramos,
                'precio': precio,
                'cantidad': cantidad
            })

        if nuevos:
            self.productos.extend(nuevos)
            self.check_vars.extend([tk.BooleanVar(value=False) for _ in nuevos])

        self.actualizar_tabla()

        total_productos = len(self.productos)
        total_etiquetas = sum(p['cantidad'] for p in self.productos)
        total_valor = sum(float(p['precio']) * p['cantidad'] for p in self.productos)

        msg = f"📊 RESUMEN DEL LOTE\n"
        msg += f"📦 Productos en lista: {total_productos}\n"
        msg += f"🏷️ Etiquetas a imprimir: {total_etiquetas}\n"
        msg += f"💰 Valor total: ${total_valor:,.0f}\n"

        if nuevos:
            msg += f"\n✅ Se agregaron {len(nuevos)} productos nuevos."
        else:
            msg += "\n⚠️ No se agregaron productos nuevos."

        if filas_ignoradas > 0:
            msg += f"\n⚠️ {filas_ignoradas} filas sin proveedor (se mostraron igual)."
        if errores:
            msg += f"\n⚠️ {len(errores)} errores adicionales."

        messagebox.showinfo("Pegado completado", msg)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo pegar:\n{str(e)}")
