from datetime import datetime

class MovimientoCaja:
    def __init__(
        self,
        fecha: str,
        id_medio_pago: int,
        tipo: str,
        concepto: str,
        id_cuenta_contable: int,
        monto: float,
        observacion: str = ""
    ):
        self.fecha = fecha
        self.id_medio_pago = id_medio_pago
        self.tipo = tipo 
        self.concepto = concepto
        self.id_cuenta_contable = id_cuenta_contable
        self.monto = monto
        self.observacion = observacion

    def mostrar(self):  # ✅ Dentro de la clase
        print(f"📅 Fecha        : {self.fecha}")
        print(f"💸 Tipo         : {self.tipo.capitalize()}")
        print(f"🧾  Concepto     : {self.concepto}")
        print(f"💰 Monto        : {self.monto}")
        print(f"🏦 Medio de pago (ID): {self.id_medio_pago}")
        print(f"📊 Cuenta contable (ID): {self.id_cuenta_contable}")
        if self.observacion:
            print(f"📝 Observación  : {self.observacion}")
