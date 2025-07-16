from datetime import datetime
from modelos.modelo_movimiento import MovimientoCaja
from helpers.conexion_sql import obtener_conexion

def menu_caja():
    while True:
        print("\n📦 MENÚ CAJA")
        print("1. Registrar ingreso manual")
        print("2. Registrar egreso manual")
        print("3. Ver movimientos por rango")
        print("4. Ver saldo por medio de pago")
        print("5. Obtener Saldo Total")
        print("0. Volver al menú principal")

        opcion = input("Seleccioná una opción: ").strip()

        if opcion == "1":
            registrar_ingreso_manual()
        elif opcion == "2":
            registrar_egreso_manual()
        elif opcion == "3":
            mostrar_movimientos_por_rango()
        elif opcion == "4":
            obtener_saldo_por_medio_pago()
        elif opcion == "5":
            obtener_saldo_total()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida.")


def registrar_ingreso_manual():
    print("\n🔹 Registro de ingreso manual")

    # 1. Fecha
    fecha_input = input("📅 Ingrese la fecha (dd/mm/aaaa) [hoy por defecto]: ").strip()
    if not fecha_input:
        fecha = datetime.today().strftime("%d/%m/%Y")
    else:
        try:
            datetime.strptime(fecha_input, "%d/%m/%Y")
            fecha = fecha_input
        except ValueError:
            print("❌ Fecha inválida. Formato esperado: dd/mm/aaaa.")
            return

    # 2. Concepto
    concepto = input("🧾 Ingrese el concepto: ").strip()
    if not concepto:
        print("❌ El concepto no puede estar vacío.")
        return

    # 3. Monto
    monto_input = input("💰 Ingrese el monto: ").replace(",", ".").strip()
    try:
        monto = float(monto_input)
        if monto <= 0:
            raise ValueError
    except ValueError:
        print("❌ Monto inválido.")
        return

    # 4. Medios de pago disponibles
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ID_MedioPago, Nombre FROM MedioPago WHERE Activo = 1")
        medios = cursor.fetchall()
        if not medios:
            print("⚠️ No hay medios de pago activos.")
            return
        print("🏦 Medios de pago:")
        for id_mp, nombre in medios:
            print(f"  {id_mp} - {nombre}")

    id_medio_pago = input("Seleccione el ID del medio de pago: ").strip()
    if not id_medio_pago.isdigit():
        print("❌ ID inválido.")
        return

    # 5. Cuentas contables disponibles
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ID_Cuenta, NombreCuenta FROM CuentaContable WHERE Activo = 1")
        cuentas = cursor.fetchall()
        if not cuentas:
            print("⚠️ No hay cuentas contables activas.")
            return
        print("📊 Cuentas contables:")
        for id_c, nombre in cuentas:
            print(f"  {id_c} - {nombre}")

    id_cuenta = input("Seleccione el ID de la cuenta contable: ").strip()
    if not id_cuenta.isdigit():
        print("❌ ID inválido.")
        return

    # 6. Observación (opcional)
    observacion = input("📝 Observación (opcional): ").strip()

    # 7. Crear objeto MovimientoCaja
    ingreso = MovimientoCaja(
        fecha=fecha,
        id_medio_pago=int(id_medio_pago),
        tipo='Ingreso',
        concepto=concepto,
        id_cuenta_contable=int(id_cuenta),
        monto=monto,
        observacion=observacion
    )

    # 8. Confirmación
    print("\n🧾 Resumen del ingreso:")
    ingreso.mostrar()
    confirmar = input("\n¿Desea guardar este ingreso? (S/N): ").strip().lower()
    if confirmar != 's':
        print("⛔ Ingreso cancelado.")
        return

    # 9. Guardar en base de datos
    try:
        with obtener_conexion() as conn:
            cursor = conn.cursor()

            # Insertar movimiento en CajaDiaria
            fecha_sql = datetime.strptime(ingreso.fecha, "%d/%m/%Y").strftime("%Y-%m-%d")

            # Usamos OUTPUT para capturar el ID directamente
            cursor.execute("""
                INSERT INTO CajaDiaria (Fecha, ID_MedioPago, Tipo, Concepto, ID_CuentaContable, Monto, Observacion)
                OUTPUT INSERTED.ID_Caja
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                fecha_sql,
                ingreso.id_medio_pago,
                ingreso.tipo.capitalize(),
                ingreso.concepto,
                ingreso.id_cuenta_contable,
                ingreso.monto,
                ingreso.observacion
            ))

            resultado = cursor.fetchone()
            if resultado is None:
                print("❌ No se pudo obtener el ID del movimiento recién insertado.")
                conn.rollback()
                return

            id_movimiento = resultado[0]


            # Registrar asiento contable ANTES del commit para incluirlo en la transacción
            registrar_asiento_por_movimiento(ingreso, id_movimiento)

            # Confirmar todo junto
            conn.commit()
            print("✅ Ingreso registrado correctamente.")

    except Exception as e:
        print(f"❌ Error al registrar ingreso: {e}")

def registrar_egreso_manual():
    print("\n🔻 Registro de egreso manual")

    # 1. Fecha
    fecha_input = input("📅 Ingrese la fecha (dd/mm/aaaa) [hoy por defecto]: ").strip()
    if not fecha_input:
        fecha = datetime.today().strftime("%d/%m/%Y")
    else:
        try:
            datetime.strptime(fecha_input, "%d/%m/%Y")
            fecha = fecha_input
        except ValueError:
            print("❌ Fecha inválida. Formato esperado: dd/mm/aaaa.")
            return

    # 2. Concepto
    concepto = input("🧾 Ingrese el concepto del egreso: ").strip()
    if not concepto:
        print("❌ El concepto no puede estar vacío.")
        return

    # 3. Monto
    monto_input = input("💰 Ingrese el monto: ").replace(",", ".").strip()
    try:
        monto = float(monto_input)
        if monto <= 0:
            raise ValueError
    except ValueError:
        print("❌ Monto inválido.")
        return

    # 4. Medios de pago disponibles
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ID_MedioPago, Nombre FROM MedioPago WHERE Activo = 1")
        medios = cursor.fetchall()
        if not medios:
            print("⚠️ No hay medios de pago activos.")
            return
        print("🏦 Medios de pago:")
        for id_mp, nombre in medios:
            print(f"  {id_mp} - {nombre}")

    id_medio_pago = input("Seleccione el ID del medio de pago: ").strip()
    if not id_medio_pago.isdigit():
        print("❌ ID inválido.")
        return

    # 5. Cuentas contables disponibles
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ID_Cuenta, NombreCuenta FROM CuentaContable WHERE Activo = 1")
        cuentas = cursor.fetchall()
        if not cuentas:
            print("⚠️ No hay cuentas contables activas.")
            return
        print("📊 Cuentas contables:")
        for id_c, nombre in cuentas:
            print(f"  {id_c} - {nombre}")

    id_cuenta = input("Seleccione el ID de la cuenta contable: ").strip()
    if not id_cuenta.isdigit():
        print("❌ ID inválido.")
        return

    # 6. Observación (opcional)
    observacion = input("📝 Observación (opcional): ").strip()

    # 7. Crear objeto MovimientoCaja
    egreso = MovimientoCaja(
        fecha=fecha,
        id_medio_pago=int(id_medio_pago),
        tipo='Egreso',  # ✅ Respetando el nuevo CHECK
        concepto=concepto,
        id_cuenta_contable=int(id_cuenta),
        monto=monto,
        observacion=observacion
    )

    # 8. Confirmación
    print("\n🧾 Resumen del egreso:")
    egreso.mostrar()
    confirmar = input("\n¿Desea guardar este egreso? (S/N): ").strip().lower()
    if confirmar != 's':
        print("⛔ Egreso cancelado.")
        return

    # 9. Guardar en base de datos
    try:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            fecha_sql = datetime.strptime(egreso.fecha, "%d/%m/%Y").strftime("%Y-%m-%d")

            cursor.execute("""
                INSERT INTO CajaDiaria (Fecha, ID_MedioPago, Tipo, Concepto, ID_CuentaContable, Monto, Observacion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                fecha_sql,
                egreso.id_medio_pago,
                egreso.tipo.capitalize(),
                egreso.concepto,
                egreso.id_cuenta_contable,
                egreso.monto,
                egreso.observacion
            ))

            # Obtener el ID del movimiento recién insertado
            cursor.execute("SELECT SCOPE_IDENTITY()")
            id_movimiento = int(cursor.fetchone()[0])

            conn.commit()
            print("✅ Egreso registrado correctamente.")

            # 📘 Registrar asiento contable
            registrar_asiento_por_movimiento(egreso, id_movimiento)
            
    except Exception as e:
        print(f"❌ Error al registrar egreso: {e}")

def mostrar_movimientos_por_rango():
    print("\n📅 Consultar movimientos por rango de fechas")
    
    hoy = datetime.today().strftime("%d/%m/%Y")
    fecha_desde = input(f"📆 Fecha DESDE (dd/mm/aaaa) [hoy por defecto]: ").strip() or hoy
    fecha_hasta = input(f"📆 Fecha HASTA (dd/mm/aaaa) [hoy por defecto]: ").strip() or hoy

    # Validar fechas
    try:
        fecha_desde_dt = datetime.strptime(fecha_desde, "%d/%m/%Y")
        fecha_hasta_dt = datetime.strptime(fecha_hasta, "%d/%m/%Y")
    except ValueError:
        print("❌ Formato de fecha inválido. Use dd/mm/aaaa.")
        return

    if fecha_desde_dt > fecha_hasta_dt:
        print("❌ La fecha 'desde' no puede ser posterior a la fecha 'hasta'.")
        return

    try:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Fecha, ID_MedioPago, Tipo, Concepto, ID_CuentaContable, Monto, Observacion
                FROM CajaDiaria
                WHERE Fecha BETWEEN ? AND ?
                ORDER BY Fecha ASC
            """, (
                fecha_desde_dt.strftime("%Y-%m-%d"),
                fecha_hasta_dt.strftime("%Y-%m-%d")
            ))

            resultados = cursor.fetchall()
            if not resultados:
                print("📭 No se encontraron movimientos en ese rango.")
                return

            print(f"\n📄 Movimientos entre {fecha_desde} y {fecha_hasta}:\n")
            for fila in resultados:
                movimiento = MovimientoCaja(
                    fecha=fila.Fecha.strftime("%d/%m/%Y"),
                    id_medio_pago=fila.ID_MedioPago,
                    tipo=fila.Tipo,
                    concepto=fila.Concepto,
                    id_cuenta_contable=fila.ID_CuentaContable,
                    monto=float(fila.Monto),
                    observacion=fila.Observacion or ""
                )
                print("-" * 30)
                movimiento.mostrar()

    except Exception as e:
        print(f"❌ Error al recuperar movimientos: {e}")

def obtener_saldo_por_medio_pago():
    print("\n💰 Saldo por medio de pago:")

    try:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    mp.Nombre AS MedioPago,
                    SUM(CASE WHEN cd.Tipo = 'Ingreso' THEN cd.Monto ELSE -cd.Monto END) AS Saldo
                FROM CajaDiaria cd
                JOIN MedioPago mp ON cd.ID_MedioPago = mp.ID_MedioPago
                GROUP BY mp.Nombre
                ORDER BY mp.Nombre
            """)
            resultados = cursor.fetchall()

            if not resultados:
                print("📭 No hay movimientos registrados.")
                return

            for medio, saldo in resultados:
                print(f"🏦 {medio:<15} ➡️ ${saldo:,.2f}")

    except Exception as e:
        print(f"❌ Error al calcular saldo por medio de pago: {e}")

def obtener_saldo_total():
    print("\n💼 Saldo total de caja:")

    try:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN Tipo = 'Ingreso' THEN Monto ELSE -Monto END) AS SaldoTotal
                FROM CajaDiaria
            """)
            resultado = cursor.fetchone()

            saldo_total = resultado.SaldoTotal if resultado.SaldoTotal is not None else 0.0
            print(f"\n💲 Saldo total: ${saldo_total:,.2f}")

    except Exception as e:
        print(f"❌ Error al calcular saldo total: {e}")

def registrar_asiento_por_movimiento(movimiento: MovimientoCaja, id_caja_diaria: int):
    try:
        with obtener_conexion() as conn:
            cursor = conn.cursor()

            # Obtener cuenta contable del medio de pago (efectivo, banco, etc.)
            cursor.execute("""
                SELECT ID_CuentaContable 
                FROM MedioPago 
                WHERE ID_MedioPago = ?
            """, (movimiento.id_medio_pago,))
            resultado = cursor.fetchone()

            if not resultado or resultado[0] is None:
                print("❌ No se encontró la cuenta contable del medio de pago.")
                return

            cuenta_caja = resultado[0]

            # Insertar los dos registros contables
            fecha_sql = datetime.strptime(movimiento.fecha, "%d/%m/%Y").strftime("%Y-%m-%d")

            if movimiento.tipo.lower() == 'ingreso':
                # Caja (Debe), Cuenta asociada (Haber)
                cursor.execute("""
                    INSERT INTO AsientoContable 
                    (Fecha, ID_Cuenta, Debe, Haber, Origen, ID_Origen, Observacion)
                    VALUES (?, ?, ?, 0, 'CajaDiaria', ?, ?)
                """, (fecha_sql, cuenta_caja, movimiento.monto, id_caja_diaria, movimiento.concepto))

                cursor.execute("""
                    INSERT INTO AsientoContable 
                    (Fecha, ID_Cuenta, Debe, Haber, Origen, ID_Origen, Observacion)
                    VALUES (?, ?, 0, ?, 'CajaDiaria', ?, ?)
                """, (fecha_sql, movimiento.id_cuenta_contable, movimiento.monto, id_caja_diaria, movimiento.concepto))

            elif movimiento.tipo.lower() == 'egreso':
                # Cuenta asociada (Debe), Caja (Haber)
                cursor.execute("""
                    INSERT INTO AsientoContable 
                    (Fecha, ID_Cuenta, Debe, Haber, Origen, ID_Origen, Observacion)
                    VALUES (?, ?, ?, 0, 'CajaDiaria', ?, ?)
                """, (fecha_sql, movimiento.id_cuenta_contable, movimiento.monto, id_caja_diaria, movimiento.concepto))

                cursor.execute("""
                    INSERT INTO AsientoContable 
                    (Fecha, ID_Cuenta, Debe, Haber, Origen, ID_Origen, Observacion)
                    VALUES (?, ?, 0, ?, 'CajaDiaria', ?, ?)
                """, (fecha_sql, cuenta_caja, movimiento.monto, id_caja_diaria, movimiento.concepto))

            conn.commit()
            print("📘 Asiento contable generado correctamente.")

    except Exception as e:
        print(f"❌ Error al generar asiento contable: {e}")
