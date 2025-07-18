import os
from helpers_LH.conexion_sql_LH import obtener_conexion
from helpers_LH.test_conexion import probar_conexion
from helpers_LH.ventas import importar_ventas_csv_a_sql, mostrar_ventas_sql

def menu_principal():
    conexion_sql = obtener_conexion()
    while True:
        print("\n=== SISTEMA LH ===")
        print("1. Probar conexión SQL")
        print("2. Importar ventas desde CSV")
        print("3. Mostrar ventas desde SQL")
        print("0. Salir")
        opcion = input("Selecciona una opción: ").strip()
        if opcion == "1":
            probar_conexion(conexion_sql)
        elif opcion == "2":
            ruta_csv = r"C:\LaHarinera_GUI_Consola\Sistema_LH\datos\Detailed-Sales-Report.csv"
            importar_ventas_csv_a_sql(ruta_csv, conexion_sql)
        elif opcion == "3":
            mostrar_ventas_sql(conexion_sql)
        elif opcion == "0":
            print("👋 Saliendo del sistema.")
            break
        else:
            print("❌ Opción inválida.")

if __name__ == "__main__":
    menu_principal()

