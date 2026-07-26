# ======================================================
# gui.py - Interfaz gráfica para Label Software
# ======================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import threading
import time
import os
import json
import sys

# Importar módulos internos
from config import NOMBRE_IMPRESORA, LS_VAL, LT_VAL, CLAVE_MAESTRA, PLANTILLA_ZPL
from models import Producto
from licensing import validar_licencia
from printing import enviar_zpl, generar_zpl
from excel_paste import pegar_desde_excel as paste_func
from csv_io import cargar, guardar
from i18n import TEXTOS


class EtiquetadoraApp:
    def __init__(self, root):
        self.root = root
        self.idioma = 'es'
        self.productos = []
        self.check_vars = []
        self.imprimiendo = False
        self.stop_impresion = False

        ls_saved, lt_saved = self.cargar_configuracion()
        self.ls_var = tk.IntVar(value=ls_saved)
        self.lt_var = tk.IntVar(value=lt_saved)

        self.crear_widgets()
        self.actualizar_tabla()
        self.actualizar_resumen()
        self.cargar_ejemplos()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def t(self, key):
        return TEXTOS[self.idioma].get(key, key)

    def cargar_configuracion(self):
        config_file = "etiquetadora_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config.get('ls', LS_VAL), config.get('lt', LT_VAL)
            except:
                return LS_VAL, LT_VAL
        return LS_VAL, LT_VAL

    def guardar_configuracion(self):
        config = {'ls': self.ls_var.get(), 'lt': self.lt_var.get()}
        try:
            with open("etiquetadora_config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except:
            pass

    def on_closing(self):
        self.stop_impresion = True
        self.guardar_configuracion()
        self.root.destroy()

    def _focus_next(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def generar_id(self, proveedor):
        count = sum(1 for p in self.productos if p['proveedor'] == proveedor) + 1
        return f"{proveedor}-{count:03d}"

    # ---------- INTERFAZ GRÁFICA ----------
    def crear_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Formulario
        self.frame_form = ttk.LabelFrame(main_frame, text=self.t('nuevo_producto'), padding=10)
        self.frame_form.pack(fill=tk.X, pady=(0,5))
        inner_frame = tk.Frame(self.frame_form)
        inner_frame.pack(fill=tk.X, padx=5, pady=5)
        col_izq = tk.Frame(inner_frame)
        col_izq.grid(row=0, column=0, padx=(0, 20), sticky="n")
        col_der = tk.Frame(inner_frame)
        col_der.grid(row=0, column=1, padx=(0, 0), sticky="n")
        ENTRY_WIDTH = 25
        campos_izq = [
            ("proveedor", self.t('proveedor')),
            ("id", self.t('id')),
            ("material", self.t('material')),
            ("tipo", self.t('tipo'))
        ]
        self.entries = {}
        for key, label in campos_izq:
            row_frame = tk.Frame(col_izq)
            row_frame.pack(fill=tk.X, pady=4)
            lbl = ttk.Label(row_frame, text=label, width=22, anchor="e")
            lbl.pack(side=tk.LEFT, padx=(0, 8))
            entry = ttk.Entry(row_frame, width=ENTRY_WIDTH)
            entry.pack(side=tk.LEFT)
            self.entries[key] = entry
            entry.bind('<Return>', self._focus_next)
        campos_der = [
            ("actualizado", self.t('actualizado')),
            ("gramos", self.t('gramos')),
            ("precio", self.t('precio')),
            ("cantidad", self.t('cantidad'))
        ]
        for key, label in campos_der:
            row_frame = tk.Frame(col_der)
            row_frame.pack(fill=tk.X, pady=4)
            lbl = ttk.Label(row_frame, text=label, width=22, anchor="e")
            lbl.pack(side=tk.LEFT, padx=(0, 8))
            entry = ttk.Entry(row_frame, width=ENTRY_WIDTH)
            entry.pack(side=tk.LEFT)
            self.entries[key] = entry
            if key != "cantidad":
                entry.bind('<Return>', self._focus_next)
            else:
                entry.bind('<Return>', lambda event: self.agregar())
        btn_frame = tk.Frame(self.frame_form)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        self.btn_agregar = ttk.Button(btn_frame, text=self.t('agregar'), command=self.agregar, width=35)
        self.btn_agregar.pack()

        # Ajustes
        self.frame_offset = ttk.LabelFrame(main_frame, text=self.t('ajustes'), padding=8)
        self.frame_offset.pack(fill=tk.X, pady=5)
        ajustes_frame = tk.Frame(self.frame_offset)
        ajustes_frame.pack()
        ttk.Label(ajustes_frame, text=self.t('ls')).grid(row=0, column=0, padx=5)
        ls_spin = ttk.Spinbox(ajustes_frame, from_=-200, to=200, increment=1, textvariable=self.ls_var, width=8)
        ls_spin.grid(row=0, column=1, padx=5)
        ttk.Label(ajustes_frame, text=self.t('lt')).grid(row=0, column=2, padx=5)
        lt_spin = ttk.Spinbox(ajustes_frame, from_=-200, to=200, increment=1, textvariable=self.lt_var, width=8)
        lt_spin.grid(row=0, column=3, padx=5)
        self.btn_test = ttk.Button(ajustes_frame, text=self.t('imprimir_prueba'), command=self.probar_offset)
        self.btn_test.grid(row=0, column=4, padx=10)

        # Botones
        self.frame_botones = ttk.LabelFrame(main_frame, text=self.t('acciones'), padding=8)
        self.frame_botones.pack(fill=tk.X, pady=5)
        btn_eliminar = ttk.Button(self.frame_botones, text=self.t('eliminar'), command=self.eliminar, width=25)
        btn_eliminar.grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        btn_duplicar = ttk.Button(self.frame_botones, text=self.t('duplicar'), command=self.duplicar, width=25)
        btn_duplicar.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.btn_imprimir_sel = ttk.Button(self.frame_botones, text=self.t('imprimir_sel'), command=self.imprimir_chequeados, width=25)
        self.btn_imprimir_sel.grid(row=0, column=2, padx=5, pady=2, sticky="ew")
        self.btn_imprimir_todos = ttk.Button(self.frame_botones, text=self.t('imprimir_todos'), command=self.imprimir_todos, width=25)
        self.btn_imprimir_todos.grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        self.btn_stop = tk.Button(self.frame_botones, text=self.t('stop'), command=self.detener_impresion,
                                  bg="#f44336", fg="white", font=("Arial", 10, "bold"),
                                  width=25, height=1, relief="raised")
        self.btn_stop.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.btn_pegar = ttk.Button(self.frame_botones, text=self.t('pegar_excel'), command=self.pegar_desde_excel, width=25)
        self.btn_pegar.grid(row=1, column=2, padx=5, pady=2, sticky="ew")
        self.btn_limpiar = ttk.Button(self.frame_botones, text=self.t('limpiar'), command=self.limpiar, width=25)
        self.btn_limpiar.grid(row=2, column=0, padx=5, pady=2, sticky="ew")
        self.btn_cargar = ttk.Button(self.frame_botones, text=self.t('cargar_csv'), command=self.cargar, width=25)
        self.btn_cargar.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.btn_guardar = ttk.Button(self.frame_botones, text=self.t('guardar_csv'), command=self.guardar, width=25)
        self.btn_guardar.grid(row=2, column=2, padx=5, pady=2, sticky="ew")
        btn_salir = ttk.Button(self.frame_botones, text=self.t('salir'), command=self.root.destroy, width=25)
        btn_salir.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        for col in range(3):
            self.frame_botones.columnconfigure(col, weight=1)

        # Tabla
        self.frame_tabla = ttk.LabelFrame(main_frame, text=self.t('lista_productos'), padding=8)
        self.frame_tabla.pack(fill=tk.BOTH, expand=True, pady=5)
        tree_frame = ttk.Frame(self.frame_tabla)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        columnas = ("No.", "✓", "Proveedor", "ID", "Material", "Tipo", "Act", "Gramos", "Precio", "Cantidad")
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show="headings",
                                  yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        self.tree.heading("No.", text="#")
        self.tree.column("No.", width=40, anchor='center', stretch=False)
        self.tree.heading("✓", text="✓")
        self.tree.column("✓", width=40, anchor='center', stretch=False)
        col_widths = {"Proveedor": 80, "ID": 100, "Material": 120, "Tipo": 120,
                      "Act": 50, "Gramos": 70, "Precio": 100, "Cantidad": 80}
        for col in columnas[2:]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 100))
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        self.tree.bind('<ButtonRelease-1>', self.on_click_check)
        self.tree.bind('<Double-1>', self.editar_celda)

        # Resumen
        self.frame_resumen = ttk.LabelFrame(main_frame, text=self.t('resumen'), padding=8)
        self.frame_resumen.pack(fill=tk.X, pady=5)
        self.label_productos = ttk.Label(self.frame_resumen, text=f"{self.t('productos_distintos')} 0", 
                                         font=("Arial", 11, "bold"), foreground="#2c5f8a")
        self.label_productos.pack(side=tk.LEFT, padx=10, pady=3)
        self.label_total_articulos = ttk.Label(self.frame_resumen, text="📊 Total artículos: 0", 
                                               font=("Arial", 11, "bold"), foreground="#2c5f8a")
        self.label_total_articulos.pack(side=tk.LEFT, padx=10, pady=3)
        self.label_etiquetas = ttk.Label(self.frame_resumen, text=f"{self.t('total_etiquetas')} 0", 
                                         font=("Arial", 11, "bold"), foreground="#2c5f8a")
        self.label_etiquetas.pack(side=tk.LEFT, padx=10, pady=3)
        self.label_valor = ttk.Label(self.frame_resumen, text=f"{self.t('valor_total')} $0", 
                                     font=("Arial", 11, "bold"), foreground="#2c5f8a")
        self.label_valor.pack(side=tk.LEFT, padx=10, pady=3)
        self.label_estado = ttk.Label(self.frame_resumen, text=self.t('listo'), foreground="green", font=("Arial", 10))
        self.label_estado.pack(side=tk.RIGHT, padx=10, pady=3)

    # ---------- FUNCIONES PRINCIPALES ----------
    def actualizar_resumen(self):
        num_productos = len(self.productos)
        total_articulos = sum(p['cantidad'] for p in self.productos)
        total_etiquetas = sum(p['cantidad'] for p in self.productos)
        total_precio = 0.0
        for p in self.productos:
            try:
                total_precio += float(p['precio']) * p['cantidad']
            except:
                pass
        self.label_productos.config(text=f"{self.t('productos_distintos')} {num_productos}")
        self.label_total_articulos.config(text=f"📊 Total artículos: {total_articulos}")
        self.label_etiquetas.config(text=f"{self.t('total_etiquetas')} {total_etiquetas}")
        self.label_valor.config(text=f"{self.t('valor_total')} ${total_precio:,.0f}")

    def actualizar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, prod in enumerate(self.productos, start=1):
            check = "✓" if self.check_vars[i-1].get() else ""
            self.tree.insert("", tk.END, values=(
                i,
                check,
                prod['proveedor'], prod['id'], prod['material'],
                prod['tipo'], prod['actualizado'], prod['gramos'],
                prod['precio'], prod['cantidad']
            ))
        if self.productos:
            total_etiquetas = sum(p['cantidad'] for p in self.productos)
            total_precio = 0.0
            for p in self.productos:
                try:
                    total_precio += float(p['precio']) * p['cantidad']
                except:
                    pass
            self.tree.insert("", tk.END, values=(
                "TOTAL",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                f"${total_precio:,.0f}" if total_precio > 0 else "",
                total_etiquetas if total_etiquetas > 0 else ""
            ), tags=('total',))
            self.tree.tag_configure('total', font=('Arial', 10, 'bold'), background='#e8f0f8')
        self.actualizar_resumen()

    def agregar(self):
        proveedor = self.entries['proveedor'].get().strip()
        idProd = self.entries['id'].get().strip()
        material = self.entries['material'].get().strip()
        tipo = self.entries['tipo'].get().strip()
        actualizado = self.entries['actualizado'].get().strip()
        gramos = self.entries['gramos'].get().strip()
        precio = self.entries['precio'].get().strip()
        cantidad = self.entries['cantidad'].get().strip()
        
        try:
            cant = int(cantidad) if cantidad else 0
        except ValueError:
            messagebox.showwarning("Cantidad inválida", "Debe ser un número entero.")
            return
        
        nuevo = {
            'proveedor': proveedor,
            'id': idProd,
            'material': material,
            'tipo': tipo,
            'actualizado': actualizado,
            'gramos': gramos,
            'precio': precio,
            'cantidad': cant
        }
        self.productos.append(nuevo)
        self.check_vars.append(tk.BooleanVar(value=False))
        self.actualizar_tabla()
        for key in self.entries:
            self.entries[key].delete(0, tk.END)
        self.entries['cantidad'].insert(0, "1")
        self.entries['proveedor'].focus()

    def pegar_desde_excel(self):
        paste_func(self)

    def cargar(self):
        cargar(self)

    def guardar(self):
        guardar(self)

    def probar_offset(self):
        self.guardar_configuracion()
        ejemplo = {
            'proveedor': 'AB',
            'id': 'TEST',
            'material': 'ORO 10k',
            'tipo': 'ANILLO',
            'actualizado': 'S',
            'gramos': '008',
            'precio': '1000',
            'cantidad': 1
        }
        zpl = generar_zpl(ejemplo, self.ls_var.get(), self.lt_var.get())
        if enviar_zpl(zpl):
            messagebox.showinfo("Prueba", "Etiqueta de prueba enviada. Verifica la posición.")

    def detener_impresion(self):
        if self.imprimiendo:
            self.stop_impresion = True
            self.label_estado.config(text="🛑 Deteniendo...", foreground="red")
        else:
            messagebox.showinfo("Sin impresión", "No hay ninguna impresión en curso.")

    def _imprimir(self, lista):
        if not lista:
            return
        total_etiquetas = sum(p['cantidad'] for p in lista)
        respuesta = messagebox.askyesno("Confirmar impresión", 
            f"📊 Productos: {len(lista)}\n"
            f"🏷️ Etiquetas: {total_etiquetas}\n"
            f"💰 Valor total: ${sum(float(p['precio']) * p['cantidad'] for p in lista):,.0f}\n\n"
            f"¿Imprimir?"
        )
        if not respuesta:
            return
        self.stop_impresion = False
        self.imprimiendo = True
        self.label_estado.config(text="🖨️ Imprimiendo...", foreground="orange")
        hilo = threading.Thread(target=self._impresion_hilo, args=(lista, total_etiquetas))
        hilo.daemon = True
        hilo.start()

    def _impresion_hilo(self, lista, total_etiquetas):
        ls = self.ls_var.get()
        lt = self.lt_var.get()
        total = 0
        try:
            for prod in lista:
                if self.stop_impresion:
                    break
                for _ in range(prod['cantidad']):
                    if self.stop_impresion:
                        break
                    zpl = generar_zpl(prod, ls, lt)
                    if not enviar_zpl(zpl):
                        self.root.after(0, lambda: self.label_estado.config(text="❌ Error", foreground="red"))
                        self.imprimiendo = False
                        return
                    total += 1
                    self.root.after(0, lambda t=total: self.label_estado.config(text=f"🖨️ {t}/{total_etiquetas}", foreground="orange"))
                    time.sleep(0.1)
            if not self.stop_impresion:
                enviar_zpl("~FF")
                self.root.after(0, lambda: self.label_estado.config(text=self.t('listo'), foreground="green"))
                self.root.after(0, lambda: messagebox.showinfo("Éxito", f"Se imprimieron {total} etiquetas."))
            else:
                self.root.after(0, lambda: self.label_estado.config(text="⏹️ Detenido", foreground="orange"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error en impresión: {e}"))
        finally:
            self.imprimiendo = False
            self.stop_impresion = False

    def imprimir_chequeados(self):
        if self.imprimiendo:
            messagebox.showwarning("Impresión en curso", "Espera a que termine o usa STOP.")
            return
        indices = [i for i, var in enumerate(self.check_vars) if var.get()]
        if not indices:
            messagebox.showinfo("Sin selección", "Marca productos con ✓")
            return
        self._imprimir([self.productos[i] for i in indices])

    def imprimir_todos(self):
        if self.imprimiendo:
            messagebox.showwarning("Impresión en curso", "Espera a que termine o usa STOP.")
            return
        if not self.productos:
            messagebox.showinfo("Sin datos", "Lista vacía")
            return
        self._imprimir(self.productos)

    def eliminar(self):
        indices = [i for i, var in enumerate(self.check_vars) if var.get()]
        if not indices:
            messagebox.showinfo("Sin selección", "Marca las filas a eliminar.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar {len(indices)} producto(s)?"):
            for i in sorted(indices, reverse=True):
                del self.productos[i]
                del self.check_vars[i]
            self.actualizar_tabla()

    def duplicar(self):
        indices = [i for i, var in enumerate(self.check_vars) if var.get()]
        if not indices:
            messagebox.showinfo("Selecciona", "Marca la fila que quieras duplicar.")
            return
        idx = indices[0]
        copia = self.productos[idx].copy()
        copia['cantidad'] = 1
        self.productos.append(copia)
        self.check_vars.append(tk.BooleanVar(value=False))
        self.actualizar_tabla()

    def limpiar(self):
        if messagebox.askyesno("Limpiar", "¿Borrar todos los productos de la lista?"):
            self.productos.clear()
            self.check_vars.clear()
            self.actualizar_tabla()

    def editar_celda(self, event):
        if hasattr(self, 'edit_entry') and self.edit_entry:
            return
        item = self.tree.identify_row(event.y)
        if not item:
            return
        column = self.tree.identify_column(event.x)
        idx = self.tree.index(item)
        if idx >= len(self.productos):
            return
        col_index = int(column[1:]) - 1
        if col_index <= 1:
            return
        self._crear_entry_edicion(item, idx, col_index)

    def _crear_entry_edicion(self, item, idx, col_index):
        valores = list(self.tree.item(item, 'values'))
        valor_actual = valores[col_index]
        x, y, w, h = self.tree.bbox(item, f"#{col_index+1}")
        entry = tk.Entry(self.tree, font=('TkDefaultFont', 10))
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, str(valor_actual))
        entry.select_range(0, tk.END)
        entry.focus()
        self.edit_entry = entry
        self.edit_item = (item, idx, col_index)

        def guardar(event=None):
            new_val = entry.get().strip()
            self._guardar_edicion(idx, col_index, new_val)
            entry.destroy()
            self.edit_entry = None
            self.edit_item = None
        entry.bind('<Return>', lambda e: guardar())
        entry.bind('<FocusOut>', lambda e: guardar())

    def _guardar_edicion(self, idx, col_index, new_val):
        if col_index == 2:
            self.productos[idx]['proveedor'] = new_val
        elif col_index == 3:
            self.productos[idx]['id'] = new_val
        elif col_index == 4:
            self.productos[idx]['material'] = new_val
        elif col_index == 5:
            self.productos[idx]['tipo'] = new_val
        elif col_index == 6:
            self.productos[idx]['actualizado'] = new_val
        elif col_index == 7:
            try:
                g = int(float(new_val)) if new_val else 0
                self.productos[idx]['gramos'] = str(g)
            except:
                self.productos[idx]['gramos'] = "0"
        elif col_index == 8:
            self.productos[idx]['precio'] = new_val
        elif col_index == 9:
            try:
                self.productos[idx]['cantidad'] = int(new_val)
                if self.productos[idx]['cantidad'] < 1:
                    self.productos[idx]['cantidad'] = 1
            except:
                messagebox.showwarning("Error", "Cantidad debe ser número")
                return
        self.actualizar_tabla()

    def on_click_check(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#2":
                item = self.tree.identify_row(event.y)
                if item:
                    idx = self.tree.index(item)
                    if idx < len(self.check_vars):
                        self.check_vars[idx].set(not self.check_vars[idx].get())
                        self.actualizar_tabla()

    def cargar_ejemplos(self):
        ejemplos = [
            {'proveedor':'AB','id':'OR001','material':'ORO 10k','tipo':'ANILLO','actualizado':'S','gramos':'8','precio':'150000','cantidad':2},
            {'proveedor':'CD','id':'PL002','material':'PLATA 925','tipo':'PULSERA','actualizado':'N','gramos':'15','precio':'85000','cantidad':1}
        ]
        for prod in ejemplos:
            self.productos.append(prod)
            self.check_vars.append(tk.BooleanVar(value=False))
        self.actualizar_tabla()
