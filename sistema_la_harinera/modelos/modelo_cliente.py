class Cliente:
    def __init__(self, nombre, telefono, email="", direccion="", cuit=""):
        self.nombre = nombre.strip()
        self.telefono = telefono.strip()
        self.email = email.strip()
        self.direccion = direccion.strip()
        self.cuit = cuit.strip()

    def mostrar(self):
        print("\n📄 Detalle del cliente ingresado:")
        print(f"Nombre    : {self.nombre}")
        print(f"Teléfono  : {self.telefono}")
        print(f"Email     : {self.email}")
        print(f"Dirección : {self.direccion}")
        print(f"CUIT      : {self.cuit}")

    def es_valido(self):
        return self.nombre != "" and self.telefono != ""
