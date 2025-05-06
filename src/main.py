"""
Killer Potato: La Venganza de la Papa
Un juego de acción 2D donde una papa mutante busca vengarse de la humanidad.

Desarrollado por: Juan Sebastian Silva Piñeros
"""

import pygame
import sys
import os

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
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Creado directorio: {directory}")

# Comprobar si existe archivo de configuración, si no, crearlo
def ensure_config():
    config_file = "config/settings.py"
    if not os.path.exists(config_file):
        # Crear archivo de configuración predeterminado
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
    
    # Importar configuración
    try:
        from config.settings import WIDTH, HEIGHT, TITLE, MUSIC_VOLUME, SFX_VOLUME
    except ImportError:
        print("Error al importar configuración. Usando valores predeterminados.")
        WIDTH, HEIGHT = 800, 600
        TITLE = "Killer Potato: La Venganza de la Papa"
        MUSIC_VOLUME, SFX_VOLUME = 0.7, 0.8
    
    # Inicializar Pygame
    pygame.init()
    pygame.mixer.init()
    pygame.font.init()
    
    # Configurar volumen
    pygame.mixer.music.set_volume(MUSIC_VOLUME)
    
    # Mostrar pantalla de carga mientras se importan módulos
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    
    # Dibujar pantalla de carga básica
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont('Arial', 24)
    loading_text = font.render("Cargando...", True, (255, 255, 255))
    screen.blit(loading_text, (WIDTH//2 - loading_text.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    
    # Importar menú (y otros módulos necesarios)
    try:
        import menu
        print("Módulos cargados correctamente.")
    except ImportError as e:
        print(f"Error al importar módulos: {e}")
        error_text = font.render(f"Error: {e}", True, (255, 0, 0))
        screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2 + 40))
        pygame.display.flip()
        pygame.time.delay(5000)
        return
    
    # Iniciar el menú principal
    menu.main()

# Punto de entrada principal
if __name__ == "__main__":
    initialize_game()