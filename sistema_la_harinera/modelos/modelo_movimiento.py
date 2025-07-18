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

class MovimientoAsiento:
    def __init__(self, id_cuenta: int, debe: float = 0.0, haber: float = 0.0, observacion: str = ""):
        self.id_cuenta = id_cuenta
        self.debe = debe
        self.haber = haber
        self.observacion = observacion

    def mostrar(self):
        print(f"  Cuenta (ID): {self.id_cuenta} | Debe: {self.debe} | Haber: {self.haber} | Obs: {self.observacion}")

class AsientoContable:
    def __init__(self, fecha: str, movimientos: list, origen: str = "", id_origen: int = None, observacion: str = ""):
        self.fecha = fecha  # formato "YYYY-MM-DD"
        self.movimientos = movimientos  # lista de MovimientoAsiento
        self.origen = origen
        self.id_origen = id_origen
        self.observacion = observacion

    def mostrar(self):
        print(f"Asiento del {self.fecha} | Origen: {self.origen} | ID Origen: {self.id_origen}")
        print(f"Observación: {self.observacion}")
        print("Movimientos:")
        for mov in self.movimientos:
            mov.mostrar()
