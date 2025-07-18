from datetime import datetime
from .conexion_sql import obtener_conexion
from modelos.modelo_movimiento import AsientoContable, MovimientoAsiento    

def crear_asiento_contable(asiento: AsientoContable):
    """
    Crea un asiento contable y sus movimientos usando objetos AsientoContable y MovimientoAsiento.
    """
    movimientos = asiento.movimientos
    if not movimientos or len(movimientos) < 2:
        print("❌ Un asiento debe tener al menos un DEBE y un HABER.")
        return

    suma_debe = sum(m.debe or 0 for m in movimientos)
    suma_haber = sum(m.haber or 0 for m in movimientos)

    if round(suma_debe, 2) != round(suma_haber, 2):
        print(f"❌ El asiento no está balanceado. Debe: {suma_debe} | Haber: {suma_haber}")
        return

    try:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            # Insertar asiento contable
            cursor.execute("""
                INSERT INTO AsientoContable (Fecha, Origen, ID_Origen, Observacion, Activo)
                OUTPUT INSERTED.ID_Asiento
                VALUES (?, ?, ?, ?, 1)
            """, (asiento.fecha, asiento.origen, asiento.id_origen, asiento.observacion))
            resultado = cursor.fetchone()
            if not resultado:
                print("❌ No se pudo crear el asiento contable.")
                conn.rollback()
                return
            id_asiento = resultado[0]

            # Insertar movimientos
            for mov in movimientos:
                cursor.execute("""
                    INSERT INTO MovimientoAsiento (ID_Asiento, ID_Cuenta, Debe, Haber, Observacion)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    id_asiento,
                    mov.id_cuenta,
                    mov.debe or 0,
                    mov.haber or 0,
                    mov.observacion
                ))
            conn.commit()
            print(f"✅ Asiento contable #{id_asiento} registrado correctamente.")
            return id_asiento
    except Exception as e:
        print(f"❌ Error al registrar asiento contable: {e}")

def consultar_libro_diario(desde=None, hasta=None):
    """
    Consulta el libro diario (asientos + movimientos) en un rango de fechas.
    """
    try:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            query = """
                SELECT a.ID_Asiento, a.Fecha, a.Observacion, m.ID_Cuenta, m.Debe, m.Haber, m.Observacion AS ObsMov
                FROM AsientoContable a
                JOIN MovimientoAsiento m ON a.ID_Asiento = m.ID_Asiento
                WHERE a.Activo = 1
            """
            params = []
            if desde:
                query += " AND a.Fecha >= ?"
                params.append(desde)
            if hasta:
                query += " AND a.Fecha <= ?"
                params.append(hasta)
            query += " ORDER BY a.Fecha, a.ID_Asiento"
            cursor.execute(query, params)
            return cursor.fetchall()
    except Exception as e:
        print(f"❌ Error al consultar libro diario: {e}")
        return []

def consultar_libro_mayor(id_cuenta=None):
    """
    Consulta el libro mayor agrupando movimientos por cuenta.
    """
    try:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            query = """
                SELECT m.ID_Cuenta, c.NombreCuenta,
                    SUM(m.Debe) AS TotalDebe,
                    SUM(m.Haber) AS TotalHaber,
                    SUM(ISNULL(m.Debe,0) - ISNULL(m.Haber,0)) AS Saldo
                FROM MovimientoAsiento m
                JOIN CuentaContable c ON m.ID_Cuenta = c.ID_Cuenta
                JOIN AsientoContable a ON m.ID_Asiento = a.ID_Asiento
                WHERE a.Activo = 1
            """
            params = []
            if id_cuenta:
                query += " AND m.ID_Cuenta = ?"
                params.append(id_cuenta)
            query += " GROUP BY m.ID_Cuenta, c.NombreCuenta ORDER BY m.ID_Cuenta"
            cursor.execute(query, params)
            return cursor.fetchall()
    except Exception as e:
        print(f"❌ Error al consultar libro mayor: {e}")
        return []

def balance_sumas_saldos():
    """
    Consulta el balance de sumas y saldos agrupando por cuenta.
    """
    try:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.ID_Cuenta, c.NombreCuenta,
                    SUM(ISNULL(m.Debe,0)) AS SumaDebe,
                    SUM(ISNULL(m.Haber,0)) AS SumaHaber,
                    SUM(ISNULL(m.Debe,0) - ISNULL(m.Haber,0)) AS Saldo
                FROM MovimientoAsiento m
                JOIN CuentaContable c ON m.ID_Cuenta = c.ID_Cuenta
                JOIN AsientoContable a ON m.ID_Asiento = a.ID_Asiento
                WHERE a.Activo = 1
                GROUP BY m.ID_Cuenta, c.NombreCuenta
                ORDER BY m.ID_Cuenta
            """)
            return cursor.fetchall()
    except Exception as e:
        print(f"❌ Error al consultar balance de sumas y saldos: {e}")
        return []

def menu_asientos():
    while True:
        print("\n📒 MENÚ ASIENTOS CONTABLES")
        print("1. Crear asiento contable manual")
        print("2. Consultar libro diario")
        print("3. Consultar libro mayor")
        print("4. Balance de sumas y saldos")
        print("0. Volver al menú principal")

        opcion = input("Seleccioná una opción: ").strip()

        if opcion == "1":
            crear_asiento_contable_manual()
        elif opcion == "2":
            consultar_libro_diario_interactivo()
        elif opcion == "3":
            consultar_libro_mayor_interactivo()
        elif opcion == "4":
            consultar_balance_sumas_saldos()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida.")

def crear_asiento_contable_manual():
    print("\n📝 Crear asiento contable manual")
    fecha = input("Fecha (YYYY-MM-DD) [hoy por defecto]: ").strip() or datetime.today().strftime("%Y-%m-%d")
    origen = input("Origen (opcional): ").strip()
    id_origen = input("ID Origen (opcional): ").strip()
    id_origen = int(id_origen) if id_origen.isdigit() else None
    observacion = input("Observación (opcional): ").strip()

    movimientos = []
    while True:
        print("\nAgregar movimiento:")
        id_cuenta = input("ID de cuenta: ").strip()
        if not id_cuenta.isdigit():
            print("ID de cuenta inválido.")
            continue
        debe = input("Debe (0 si no aplica): ").replace(",", ".").strip()
        haber = input("Haber (0 si no aplica): ").replace(",", ".").strip()
        try:
            debe = float(debe) if debe else 0.0
            haber = float(haber) if haber else 0.0
        except ValueError:
            print("Debe y Haber deben ser números.")
            continue
        obs_mov = input("Observación del movimiento (opcional): ").strip()
        movimientos.append(MovimientoAsiento(int(id_cuenta), debe, haber, obs_mov))
        otro = input("¿Agregar otro movimiento? (S/N): ").strip().lower()
        if otro != "s":
            break

    asiento = AsientoContable(
        fecha=fecha,
        movimientos=movimientos,
        origen=origen,
        id_origen=id_origen,
        observacion=observacion
    )
    crear_asiento_contable(asiento)

def consultar_libro_diario_interactivo():
    print("\n📖 Consultar libro diario")
    desde = input("Fecha desde (YYYY-MM-DD, opcional): ").strip() or None
    hasta = input("Fecha hasta (YYYY-MM-DD, opcional): ").strip() or None
    resultados = consultar_libro_diario(desde, hasta)
    if resultados:
        print("\nID | Fecha       | Cuenta | Debe      | Haber     | Obs")
        print("-" * 70)
        for r in resultados:
            print(f"{r.ID_Asiento:<3}| {r.Fecha} | {r.ID_Cuenta:<6}| {r.Debe:>10.2f}| {r.Haber:>10.2f}| {r.ObsMov}")
    else:
        print("No hay asientos en ese rango.")

def consultar_libro_mayor_interactivo():
    print("\n📚 Consultar libro mayor")
    id_cuenta = input("ID de cuenta (opcional, enter para todas): ").strip()
    id_cuenta = int(id_cuenta) if id_cuenta.isdigit() else None
    resultados = consultar_libro_mayor(id_cuenta)
    if resultados:
        print("\nID | Cuenta           | Total Debe | Total Haber | Saldo")
        print("-" * 60)
        for r in resultados:
            print(f"{r.ID_Cuenta:<3}| {r.NombreCuenta:<16}| {r.TotalDebe:>10.2f}| {r.TotalHaber:>11.2f}| {r.Saldo:>10.2f}")
    else:
        print("No hay movimientos para mostrar.")

def consultar_balance_sumas_saldos():
    print("\n📊 Balance de sumas y saldos")
    resultados = balance_sumas_saldos()
    if resultados:
        print("\nID | Cuenta           | Suma Debe | Suma Haber | Saldo")
        print("-" * 60)
        for r in resultados:
            print(f"{r.ID_Cuenta:<3}| {r.NombreCuenta:<16}| {r.SumaDebe:>9.2f}| {r.SumaHaber:>10.2f}| {r.Saldo:>10.2f}")
    else:
        print("No hay saldos para mostrar.")