# Funciones de manejo de clientes

import os
import time
import pandas as pd
from helpers.conexion_sql import obtener_conexion
from modelos.modelo_cliente import Cliente

def limpiar_pantalla():
  """Limpia la pantalla de la consola."""
  if os.name == 'nt':
    # Windows
    os.system('cls')
  else:
    # Linux, macOS, etc.
    os.system('clear')

def cargar_y_comparar_clientes():
    """
    Carga clientes desde archivo Excel y los compara con la base de datos.
    Inserta nuevos, actualiza modificados, ignora los iguales.
    """
    ##from modelos.modelo_cliente import Cliente
    ##import pandas as pd
    ##import os

    archivo = os.path.join("datos", "Clients-Report.xlsx")
    if not os.path.exists(archivo):
        print(f"❌ No se encontró el archivo en: {archivo}")
        return

    try:
        df = pd.read_excel(archivo, skiprows=1)
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return

    # Normalizar y renombrar columnas
    df = df.rename(columns={
        'Nombre de la Organización': 'Nombre',
        'Número de contacto': 'Telefono',
        'Correo electrónico': 'Email',
        'Dirección': 'Direccion',
        'Identificación del impuesto': 'CUIT'
    })

    df = df[['Nombre', 'Telefono', 'Email', 'Direccion', 'CUIT']]
    df.dropna(subset=['Nombre', 'Telefono'], inplace=True)

    nuevos = []
    actualizados = []
    iguales = []

    conn = obtener_conexion()
    if conn is None:
        return

    cursor = conn.cursor()

    for _, row in df.iterrows():
        cliente = Cliente(
            nombre=row['Nombre'],
            telefono=str(row['Telefono']),
            email=row.get('Email', ''),
            direccion=row.get('Direccion', ''),
            cuit=str(row.get('CUIT', '')).strip() if pd.notna(row.get('CUIT')) else ''
        )

        # Buscar cliente existente
        if cliente.cuit:
            cursor.execute("""
                SELECT ID_Cliente, Nombre, Telefono, Email, Direccion, CUIT 
                FROM Cliente WHERE CUIT = ? AND Activo = 1
            """, (cliente.cuit,))
        else:
            cursor.execute("""
                SELECT ID_Cliente, Nombre, Telefono, Email, Direccion, CUIT 
                FROM Cliente WHERE Nombre = ? AND Telefono = ? AND Activo = 1
            """, (cliente.nombre, cliente.telefono))

        row_db = cursor.fetchone()

        if row_db is None:
            # Cliente nuevo
            cursor.execute("""
                INSERT INTO Cliente (Nombre, Telefono, Email, Direccion, CUIT, Activo)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (cliente.nombre, cliente.telefono, cliente.email or None, cliente.direccion or None, cliente.cuit or None))
            nuevos.append(cliente.nombre)
        else:
            # Comprobar si hay diferencias
            if (
                cliente.nombre != row_db.Nombre or
                cliente.telefono != row_db.Telefono or
                cliente.email != (row_db.Email or "") or
                cliente.direccion != (row_db.Direccion or "") or
                cliente.cuit != (row_db.CUIT or "")
            ):
                cursor.execute("""
                    UPDATE Cliente
                    SET Nombre = ?, Telefono = ?, Email = ?, Direccion = ?, CUIT = ?
                    WHERE ID_Cliente = ?
                """, (cliente.nombre, cliente.telefono, cliente.email or None, cliente.direccion or None, cliente.cuit or None, row_db.ID_Cliente))
                actualizados.append(cliente.nombre)
            else:
                iguales.append(cliente.nombre)

    conn.commit()
    conn.close()

    print("\n📥 Resultado de la carga de clientes desde archivo:")
    print(f"🟢 Nuevos insertados : {len(nuevos)}")
    print(f"🟡 Actualizados      : {len(actualizados)}")
    print(f"⚪ Sin cambios       : {len(iguales)}")

def mostrar_clientes():
    """
    Consulta y muestra todos los clientes activos desde la base de datos.
    """
    conn = obtener_conexion()
    if conn is None:
        return

    df = pd.read_sql("SELECT * FROM Cliente WHERE Activo = 1 ORDER BY Nombre", conn)
    conn.close()

    print("📋 Clientes activos en base de datos:")
    print(df.to_string(index=False))
    
def alta_manual_cliente():
    """
    Crea un nuevo cliente con confirmación previa, usando objeto Cliente.
    """
    print("\n🆕 Alta de cliente manual")
    nombre = input("Nombre: ").strip()
    telefono = input("Teléfono: ").strip()
    email = input("Email (opcional): ").strip()
    direccion = input("Dirección (opcional): ").strip()
    cuit = input("CUIT (opcional): ").strip()

    nuevo = Cliente(nombre, telefono, email, direccion, cuit)

    if not nuevo.es_valido():
        print("❌ Nombre y Teléfono son obligatorios.")
        return

    nuevo.mostrar()
    confirmar = input("\n¿Deseás guardar este cliente? (S/N): ").strip().lower()
    if confirmar != "s":
        print("❌ Operación cancelada.")
        return

    conn = obtener_conexion()
    if conn is None:
        return

    cursor = conn.cursor()

    # Verificar duplicado
    cursor.execute("""
        SELECT COUNT(*) FROM Cliente 
        WHERE Nombre = ? AND Telefono = ? AND Activo = 1
    """, (nuevo.nombre, nuevo.telefono))
    existe = cursor.fetchone()[0]

    if existe:
        print("⚠️ Ya existe un cliente activo con ese Nombre y Teléfono.")
        conn.close()
        return

    # Insertar
    cursor.execute("""
        INSERT INTO Cliente (Nombre, Telefono, Email, Direccion, CUIT, Activo)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (nuevo.nombre, nuevo.telefono, nuevo.email or None, nuevo.direccion or None, nuevo.cuit or None))

    conn.commit()
    conn.close()

    print("✅ Cliente creado correctamente.")

def modificar_cliente():
    """
    Modifica un cliente activo existente buscando por nombre parcial.
    Permite cambiar campos individuales con confirmación.
    """
    from modelos.modelo_cliente import Cliente

    print("\n✏️ Modificación de cliente")
    termino = input("Buscar cliente por nombre (o parte del nombre): ").strip()

    if not termino:
        print("❌ Debe ingresar un valor de búsqueda.")
        return

    conn = obtener_conexion()
    if conn is None:
        return

    cursor = conn.cursor()
    cursor.execute("""
        SELECT ID_Cliente, Nombre, Telefono, Email, Direccion, CUIT
        FROM Cliente
        WHERE Nombre LIKE ? AND Activo = 1
        ORDER BY Nombre
    """, ('%' + termino + '%',))
    resultados = cursor.fetchall()

    if not resultados:
        print("⚠️ No se encontraron clientes con ese nombre.")
        conn.close()
        return

    # Mostrar y seleccionar cliente
    if len(resultados) > 1:
        print("\n🔎 Resultados encontrados:")
        for i, row in enumerate(resultados, 1):
            print(f"{i}. {row.Nombre} - Tel: {row.Telefono}")

        seleccion = input("Selecciona el número del cliente a modificar: ").strip()
        if not seleccion.isdigit() or int(seleccion) < 1 or int(seleccion) > len(resultados):
            print("❌ Selección inválida.")
            conn.close()
            return

        cliente_db = resultados[int(seleccion) - 1]
    else:
        cliente_db = resultados[0]

    # Construimos objeto actual
    cliente_original = Cliente(
        cliente_db.Nombre,
        cliente_db.Telefono,
        cliente_db.Email or "",
        cliente_db.Direccion or "",
        cliente_db.CUIT or ""
    )
    id_cliente = cliente_db.ID_Cliente

    print("\n📄 Datos actuales:")
    cliente_original.mostrar()

    # Ingresar nuevos datos
    print("\n📝 Dejar en blanco para mantener el valor actual.")
    nuevo_nombre = input(f"Nuevo nombre [{cliente_original.nombre}]: ").strip() or cliente_original.nombre
    nuevo_telefono = input(f"Nuevo teléfono [{cliente_original.telefono}]: ").strip() or cliente_original.telefono
    nuevo_email = input(f"Nuevo email [{cliente_original.email}]: ").strip() or cliente_original.email
    nuevo_direccion = input(f"Nueva dirección [{cliente_original.direccion}]: ").strip() or cliente_original.direccion
    nuevo_cuit = input(f"Nuevo CUIT [{cliente_original.cuit}]: ").strip() or cliente_original.cuit

    modificado = Cliente(nuevo_nombre, nuevo_telefono, nuevo_email, nuevo_direccion, nuevo_cuit)

    print("\n📄 Datos modificados:")
    modificado.mostrar()

    confirmar = input("\n¿Deseás guardar los cambios? (S/N): ").strip().lower()
    if confirmar != "s":
        print("❌ Modificación cancelada.")
        conn.close()
        return

    # Actualizar
    cursor.execute("""
        UPDATE Cliente
        SET Nombre = ?, Telefono = ?, Email = ?, Direccion = ?, CUIT = ?
        WHERE ID_Cliente = ?
    """, (modificado.nombre, modificado.telefono, modificado.email, modificado.direccion, modificado.cuit, id_cliente))

    conn.commit()
    conn.close()
    print("✅ Cliente modificado correctamente.")
    
def baja_cliente():
    """
    Realiza una baja lógica de un cliente activo buscado por nombre.
    """
    print("\n🗑️ Baja de cliente")
    termino = input("Buscar cliente por nombre (o parte del nombre): ").strip()

    if not termino:
        print("❌ Debe ingresar un valor de búsqueda.")
        return

    conn = obtener_conexion()
    if conn is None:
        return

    cursor = conn.cursor()
    cursor.execute("""
        SELECT ID_Cliente, Nombre, Telefono
        FROM Cliente
        WHERE Nombre LIKE ? AND Activo = 1
        ORDER BY Nombre
    """, ('%' + termino + '%',))
    resultados = cursor.fetchall()

    if not resultados:
        print("⚠️ No se encontraron clientes activos con ese nombre.")
        conn.close()
        return

    # Mostrar y seleccionar
    if len(resultados) > 1:
        print("\n🔎 Clientes encontrados:")
        for i, row in enumerate(resultados, 1):
            print(f"{i}. {row.Nombre} - Tel: {row.Telefono}")

        seleccion = input("Selecciona el número del cliente a dar de baja: ").strip()
        if not seleccion.isdigit() or int(seleccion) < 1 or int(seleccion) > len(resultados):
            print("❌ Selección inválida.")
            conn.close()
            return

        cliente = resultados[int(seleccion) - 1]
    else:
        cliente = resultados[0]

    print(f"\n¿Confirmás que querés dar de baja al cliente '{cliente.Nombre}'?")
    confirmar = input("Escribí S para confirmar: ").strip().lower()

    if confirmar != "s":
        print("❌ Operación cancelada.")
        conn.close()
        return

    cursor.execute("""
        UPDATE Cliente
        SET Activo = 0
        WHERE ID_Cliente = ?
    """, (cliente.ID_Cliente,))

    conn.commit()
    conn.close()
    print("✅ Cliente dado de baja correctamente.")
    
def menu_abm_clientes():
    """
    Submenú interactivo para el ABM de clientes.
    """
    while True:
        limpiar_pantalla()
        print("\n=== ABM DE CLIENTES ===")
        print("1. Cargar clientes desde archivo")
        print("2. Alta manual de cliente")
        print("3. Modificar cliente")
        print("4. Baja de cliente")
        print("5. Mostrar clientes activos")
        print("0. Volver al menú principal")

        opcion = input("Selecciona una opción (0-5): ").strip()
        limpiar_pantalla()

        if opcion == "1":
            cargar_y_comparar_clientes()
        elif opcion == "2":
            alta_manual_cliente()
        elif opcion == "3":
            modificar_cliente()
        elif opcion == "4":
            baja_cliente()
        elif opcion == "5":
            mostrar_clientes()
        elif opcion == "0":
            break
        else:
            print("⚠️ Opción inválida. Intenta nuevamente.")
            time.sleep(3)
            
