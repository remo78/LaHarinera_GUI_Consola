from helpers.conexion_sql import obtener_conexion

def probar_conexion():
    conexion = obtener_conexion()
    if conexion:
        print("✅ Conexión exitosa a SQL Server")
        conexion.close()
    else:
        print("❌ No se pudo conectar a SQL Server")

probar_conexion()
