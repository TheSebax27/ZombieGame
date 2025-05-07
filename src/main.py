"""
Killer Potato: La Venganza de la Papa
Un juego de acción 2D donde una papa mutante busca vengarse de la humanidad.

Desarrollado por: Juan Sebastian Silva Piñeros
"""

import sys
import os

# Asegurar que estamos en el directorio correcto para importaciones relativas
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Asegurarnos de que existe la estructura de directorios adecuada
def ensure_directories():
    directories = [
        "assets",
        "assets/fonts",
        "assets/images",
        "assets/images/characters",
        "assets/images/backgrounds",
        "assets/images/ui",
        "assets/images/items",
        "assets/images/effects",
        "assets/images/obstacles",
        "assets/sounds",
        "assets/sounds/music",
        "assets/sounds/sfx",
        "assets/dialogue",
        "assets/levels",
        "assets/save",
        "config"
    ]
    
    for directory in directories:
        full_path = os.path.join(parent_dir, directory)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            print(f"Creado directorio: {full_path}")

# Comprobar si existe archivo de configuración, si no, crearlo
def ensure_config():
    config_file = os.path.join(parent_dir, "config/settings.py")
    if not os.path.exists(config_file):
        # Crear archivo de configuración predeterminado
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            f.write('''"""
Configuración global para el juego Killer Potato
Contiene constantes y ajustes que se utilizan en todo el juego
"""

# Configuración de pantalla
WIDTH = 800
HEIGHT = 600
FPS = 60
TITLE = "Killer Potato: La Venganza de la Papa"

# Opciones de jugabilidad
DIFFICULTY = "normal"  # "easy", "normal", "hard"
MUSIC_VOLUME = 0.7     # 0.0 a 1.0
SFX_VOLUME = 0.8       # 0.0 a 1.0
FULLSCREEN = False
SHOW_FPS = False

# Opciones de desarrollo
DEBUG_MODE = False
INVINCIBLE = False
UNLIMITED_AMMO = False

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)
DARK_GREEN = (0, 100, 0)
DARK_RED = (139, 0, 0)
POTATO_BROWN = (139, 69, 19)
POTATO_LIGHT = (210, 180, 140)
''')
        print(f"Creado archivo de configuración: {config_file}")

# Inicializar el juego
def initialize_game():
    # Asegurar que tenemos la estructura de directorios y configuración
    ensure_directories()
    ensure_config()
    
    try:
        # Importar módulos necesarios
        import pygame
        print("Pygame importado correctamente.")
        
        # Inicializar Pygame
        pygame.init()
        pygame.mixer.init()
        pygame.font.init()
        
        # Importar el módulo de menú
        from src import menu
        print("¡Juego inicializado correctamente!")
        
        # Iniciar el menú principal
        menu.main()
        
    except ImportError as e:
        print(f"Error al importar módulos: {e}")
        print("\nPara solucionar este problema, asegúrate de tener instalado pygame:")
        print("  pip install pygame")
        input("\nPresiona Enter para salir...")
        sys.exit(1)
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        input("\nPresiona Enter para salir...")
        sys.exit(1)

# Punto de entrada principal con manejo de excepciones
if __name__ == "__main__":
    try:
        initialize_game()
    except Exception as e:
        print(f"Error al iniciar el juego: {e}")
        input("\nPresiona Enter para salir...")