# ======================================================
# config.py - Configuración global del Label Software
# ======================================================

# Impresora
NOMBRE_IMPRESORA = "ZDesigner ZD220-203dpi ZPL"

# Ajustes de posición (valores por defecto)
LS_VAL = -50
LT_VAL = -43

# Clave maestra para licencias (NO CAMBIAR)
CLAVE_MAESTRA = b'qJjQH8bZJ4yJjHtPqM7t2Hh5VvJjQqP3xR5sT1uVvWw=='

# Plantilla ZPL para las etiquetas
PLANTILLA_ZPL = """^XA
^PW600
^LS{ls}
^LT{lt}
^MD25
^PR4
^FO15,15^A0N,35,35^FD${precio}^FS
^FO15,75^A0N,20,20^FD{proveedor}^FS
^FO70,75^A0N,18,18^FD{idProducto}^FS
^FO15,105^A0N,20,20^FD{tipo}^FS
^FO115,105^A0N,18,18^FD{gramos}^FS
^FO15,135^A0N,20,20^FD{material}^FS
^FO115,135^A0N,18,18^FD{actualizado}^FS
^XZ"""
