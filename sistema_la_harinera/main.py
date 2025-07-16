# Punto de entrada principal del sistema
import sys
import os
from datetime import datetime

# 🔧 Agrega la ruta del directorio raíz del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from helpers.clientes import menu_abm_clientes
from helpers.caja import menu_caja

def limpiar_pantalla():
  """Limpia la pantalla de la consola."""
  if os.name == 'nt':
    # Windows
    os.system('cls')
  else:
    # Linux, macOS, etc.
    os.system('clear')

def menu_principal():
    while True:
        limpiar_pantalla()
        print("=== SISTEMA LA HARINERA ===")
        print("1. ABM de Clientes")
        print("2. Caja")
        print("0. Salir del sistema")

        opcion = input("Selecciona una opción (0-1): ").strip()
        limpiar_pantalla()
        
        if opcion == "1":
            menu_abm_clientes()
        elif opcion == "2":
            menu_caja()
        elif opcion == "0":
            print("👋Saliendo del sistema.")
            break
        else:
            print("⚠️ Opción inválida. Intenta nuevamente.")
        
if __name__ == "__main__":
    menu_principal()


