# ======================================================
# licensing.py - Sistema de licencias para Label Software
# ======================================================

import hashlib
import subprocess
import platform
import os
import uuid
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
from config import CLAVE_MAESTRA


def obtener_id_equipo():
    """Obtiene un ID único basado en hardware del equipo."""
    if platform.system() == "Windows":
        nombre = platform.node()
        try:
            uuid_cpu = subprocess.getoutput("wmic csproduct get uuid").split()[1]
        except:
            uuid_cpu = "NODisponible"
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 8*6, 8)])
        return hashlib.md5(f"{nombre}{uuid_cpu}{mac}".encode()).hexdigest()
    else:
        nombre = platform.node()
        try:
            with open("/etc/machine-id", "r") as f:
                uuid_cpu = f.read().strip()
        except:
            uuid_cpu = "LINUX"
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 8*6, 8)])
        return hashlib.md5(f"{nombre}{uuid_cpu}{mac}".encode()).hexdigest()


def validar_licencia_ingresada(licencia_ingresada, id_equipo):
    """Valida una licencia contra el ID del equipo."""
    try:
        fernet = Fernet(CLAVE_MAESTRA)
        id_descifrado = fernet.decrypt(licencia_ingresada.encode()).decode()
        return id_descifrado == id_equipo
    except:
        return False


def validar_licencia():
    """Muestra la ventana de activación si no hay licencia válida."""
    archivo_licencia = "license.key"
    id_actual = obtener_id_equipo()
    
    # Si ya existe licencia, validarla
    if os.path.exists(archivo_licencia):
        with open(archivo_licencia, "r") as f:
            licencia_guardada = f.read().strip()
            if validar_licencia_ingresada(licencia_guardada, id_actual):
                return True
        os.remove(archivo_licencia)
    
    # Ventana de activación
    root_temp = tk.Tk()
    root_temp.withdraw()
    ventana = tk.Toplevel(root_temp)
    ventana.title("Activación - Label Software")
    ventana.geometry("500x300")
    ventana.resizable(False, False)
    
    tk.Label(ventana, text="Este equipo no está activado.", font=("Arial", 10)).pack(pady=10)
    tk.Label(ventana, text="ID del equipo (cópielo y envíelo a su proveedor):").pack()
    id_var = tk.StringVar(value=id_actual)
    entry_id = tk.Entry(ventana, textvariable=id_var, width=50, state="readonly")
    entry_id.pack(pady=5)
    
    def copiar_id():
        ventana.clipboard_clear()
        ventana.clipboard_append(id_actual)
        messagebox.showinfo("Copiado", "ID copiado al portapapeles")
    tk.Button(ventana, text="📋 Copiar ID", command=copiar_id).pack(pady=5)
    
    tk.Label(ventana, text="Ingrese la clave que recibió:").pack()
    clave_var = tk.StringVar()
    tk.Entry(ventana, textvariable=clave_var, width=50).pack(pady=5)
    
    def verificar():
        entrada = clave_var.get().strip()
        if validar_licencia_ingresada(entrada, id_actual):
            with open(archivo_licencia, "w") as f:
                f.write(entrada)
            messagebox.showinfo("Éxito", "Software activado correctamente")
            ventana.destroy()
            root_temp.destroy()
            return True
        else:
            messagebox.showerror("Error", "Clave inválida")
            return False
    
    tk.Button(ventana, text="Activar", command=verificar).pack(pady=10)
    ventana.protocol("WM_DELETE_WINDOW", lambda: (root_temp.destroy(), ventana.destroy()))
    root_temp.wait_window(ventana)
    return False
