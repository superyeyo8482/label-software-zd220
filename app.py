# ======================================================
# app.py - Punto de entrada del Label Software
# ======================================================

import tkinter as tk
import sys
import os

# Asegurar que los módulos están en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import EtiquetadoraApp
from licensing import validar_licencia

if __name__ == "__main__":
    # Validar licencia (si falla, cierra)
    if not validar_licencia():
        sys.exit()
    
    # Crear ventana principal
    root = tk.Tk()
    root.title("Label Software para Zebra ZD220 - Joyería")
    root.geometry("1300x800")
    
    # Iniciar aplicación
    app = EtiquetadoraApp(root)
    
    # Bucle principal
    root.mainloop()
