# ======================================================
# 🔐 GENERADOR DE LICENCIAS · LABEL SOFTWARE
# ======================================================
# La clave maestra se lee desde la variable de entorno CLAVE_MAESTRA.
# Para usarlo, configura la variable antes de ejecutar.
# ======================================================

import os
import hashlib
import subprocess
import platform
import uuid
from cryptography.fernet import Fernet

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

def generar_licencia():
    """Genera una licencia usando la clave maestra desde variables de entorno."""
    clave_maestra = os.environ.get("CLAVE_MAESTRA")
    if not clave_maestra:
        print("❌ Error: La variable de entorno CLAVE_MAESTRA no está configurada.")
        print("💡 Configúrala con: `$env:CLAVE_MAESTRA = 'tu_clave_aqui'`")
        return None
    
    id_equipo = obtener_id_equipo()
    try:
        fernet = Fernet(clave_maestra.encode())
        licencia = fernet.encrypt(id_equipo.encode()).decode()
        return licencia
    except Exception as e:
        print(f"❌ Error al generar la licencia: {e}")
        return None

if __name__ == "__main__":
    licencia = generar_licencia()
    if licencia:
        print(f"\n🔑 Licencia generada:\n{licencia}\n")
    else:
        print("\n❌ No se pudo generar la licencia.")
