from datetime import datetime

class ImportVentas:
    def __init__(self, nro, fecha, presupuesto, cliente, producto, cod_prod, cantidad, precio, descuento, imponible, impuesto, total):
        self.nro = nro
        self.fecha = fecha
        self.presupuesto = presupuesto
        self.cliente = cliente
        self.producto = producto
        self.cod_prod = cod_prod
        self.cantidad = cantidad
        self.precio = precio
        self.descuento = descuento
        self.imponible = imponible
        self.impuesto = impuesto
        self.total = total

    def mostrar(self):
        print(f"""
        Nro        : {self.nro}
        Fecha      : {self.fecha}
        Presupuesto: {self.presupuesto}
        Cliente    : {self.cliente}
        Producto   : {self.producto}
        Cod Prod   : {self.cod_prod}
        Cantidad   : {self.cantidad}
        Precio     : {self.precio}
        Descuento  : {self.descuento}
        Imponible  : {self.imponible}
        Impuesto   : {self.impuesto}
        Total      : {self.total}
        """)

