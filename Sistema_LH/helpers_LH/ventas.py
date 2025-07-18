import csv
import pyodbc
from modelos_LH.clases_LH import ImportVentas
from datetime import datetime

def normalizar_fecha(fecha_str):
    # Convierte a formato YYYY-MM-DD para SQL
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            fecha = datetime.strptime(fecha_str.strip(), fmt)
            return fecha.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return fecha_str.strip()

def normalizar_float(valor):
    # Elimina espacios, reemplaza comas por puntos y convierte a float
    valor = valor.replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(valor)
    except Exception:
        return 0.0

def normalizar_entero(valor):
    valor = valor.replace(" ", "").replace(",", ".")
    try:
        return int(float(valor))
    except Exception:
        return 0

def importar_ventas_csv_a_sql(ruta_csv, conexion_sql):
    ventas = []
    with open(ruta_csv, newline='', encoding='utf-8') as archivo:
        # Saltar las primeras 3 líneas
        for _ in range(3):
            next(archivo)
        reader = csv.DictReader(archivo, delimiter=';')
        for row in reader:
            venta = ImportVentas(
                nro=normalizar_entero(row['Nº']),
                fecha=normalizar_fecha(row['Fecha']),
                presupuesto=row['Factura no.'],
                cliente=row['nombre del cliente'],
                producto=row['nombre del producto'],
                cod_prod=row['Código de producto'],
                cantidad=normalizar_float(row['Cantidad']),
                precio=normalizar_float(row['Tarifa']),
                descuento=normalizar_float(row['Descuento']),
                imponible=normalizar_float(row['Imponible']),
                impuesto=normalizar_float(row['Impuesto']),
                total=normalizar_float(row['Monto tras impuesto'])
            )
            ventas.append(venta)
    try:
        with pyodbc.connect(conexion_sql) as conn:
            cursor = conn.cursor()
            for venta in ventas:
                cursor.execute("""
                    INSERT INTO Ventas ([Nro], [Fecha], [Presupuesto], [Cliente], [Producto], [Cod Prod], [Cantidad], [Precio], [Descuento], [Imponible], [Impuesto], [Total])
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                int(venta.nro),                          # int
                str(venta.fecha) if venta.fecha else "", # date como string YYYY-MM-DD
                str(venta.presupuesto) if venta.presupuesto else "",
                str(venta.cliente) if venta.cliente else "",
                str(venta.producto) if venta.producto else "",
                str(venta.cod_prod) if venta.cod_prod else "",
                float(venta.cantidad) if venta.cantidad else 0.0,
                float(venta.precio) if venta.precio else 0.0,
                float(venta.descuento) if venta.descuento else 0.0,
                float(venta.imponible) if venta.imponible else 0.0,
                float(venta.impuesto) if venta.impuesto else 0.0,
                float(venta.total) if venta.total else 0.0
                )
            conn.commit()
        print(f"✅ Se importaron {len(ventas)} ventas correctamente.")
    except Exception as e:
        print(f"❌ Error al importar ventas: {e}")

def mostrar_ventas_sql(conexion_sql):
    try:
        with pyodbc.connect(conexion_sql) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT [Nro], [Fecha], [Presupuesto], [Cliente], [Producto], [Cod Prod], [Cantidad], [Precio], [Descuento], [Imponible], [Impuesto], [Total] FROM Ventas")
            rows = cursor.fetchall()
            for row in rows:
                venta = ImportVentas(
                    nro=row.Nro,
                    fecha=row.Fecha,
                    presupuesto=row.Presupuesto,
                    cliente=row.Cliente,
                    producto=row.Producto,
                    cod_prod=row.Cod_Prod if hasattr(row, "Cod_Prod") else row[5],
                    cantidad=row.Cantidad,
                    precio=row.Precio,
                    descuento=row.Descuento,
                    imponible=row.Imponible,
                    impuesto=row.Impuesto,
                    total=row.Total
                )
                print(venta.nro, venta.fecha, venta.presupuesto, venta.cliente, venta.producto, venta.cod_prod, venta.cantidad, venta.precio, venta.descuento, venta.imponible, venta.impuesto, venta.total)
    except Exception as e:
        print(f"❌ Error al mostrar ventas: {e}")