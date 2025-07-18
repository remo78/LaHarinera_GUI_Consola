# Conexión a SQL Server
import pyodbc

def obtener_conexion():
    """
    Establece y devuelve una conexión con la base de datos La_Harinera
    usando autenticación de Windows.
    """
    server = 'DESKTOP-S6A3H3Q\\SQLEXPRESS01'
    database = 'Sistema_LH'

    try:
        conexion = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};DATABASE={database};"
            f"Trusted_Connection=yes;"
        )
        return conexion
    except Exception as e:
        print("Error al conectar con la base de datos:", e)
        return None
