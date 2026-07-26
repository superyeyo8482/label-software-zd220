# ======================================================
# models.py - Modelo de datos para Label Software
# ======================================================

class Producto:
    """Modelo de datos para un producto de joyería."""
    
    def __init__(self, proveedor, id_producto, material="", tipo="", 
                 actualizado="", gramos="0", precio="0", cantidad=1):
        self.proveedor = proveedor
        self.id = id_producto
        self.material = material if material else "-"
        self.tipo = tipo if tipo else "-"
        self.actualizado = actualizado if actualizado else "-"
        self.gramos = gramos if gramos else "0"
        self.precio = precio if precio else "0"
        self.cantidad = cantidad if cantidad else 1
    
    def to_dict(self):
        """Convierte el producto a diccionario para CSV."""
        return {
            'proveedor': self.proveedor,
            'id': self.id,
            'material': self.material,
            'tipo': self.tipo,
            'actualizado': self.actualizado,
            'gramos': self.gramos,
            'precio': self.precio,
            'cantidad': self.cantidad
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea un Producto desde un diccionario (para CSV)."""
        return cls(
            proveedor=data.get('proveedor', ''),
            id_producto=data.get('id', ''),
            material=data.get('material', ''),
            tipo=data.get('tipo', ''),
            actualizado=data.get('actualizado', ''),
            gramos=data.get('gramos', '0'),
            precio=data.get('precio', '0'),
            cantidad=int(data.get('cantidad', 1))
        )
