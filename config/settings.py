"""
Configuración global para el juego Killer Potato
Contiene constantes y ajustes que se utilizan en todo el juego
"""

# Importar pygame para las constantes de teclado
import pygame

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
UNLOCK_ALL_LEVELS = False

# Ajustes de dificultad
DIFFICULTY_SETTINGS = {
    "easy": {
        "player_health": 150,
        "player_damage_multiplier": 1.2,
        "enemy_health_multiplier": 0.8,
        "enemy_damage_multiplier": 0.8,
        "enemy_speed_multiplier": 0.9,
        "pickup_spawn_chance": 0.4,
        "boss_health_multiplier": 0.9
    },
    "normal": {
        "player_health": 100,
        "player_damage_multiplier": 1.0,
        "enemy_health_multiplier": 1.0,
        "enemy_damage_multiplier": 1.0,
        "enemy_speed_multiplier": 1.0,
        "pickup_spawn_chance": 0.3,
        "boss_health_multiplier": 1.0
    },
    "hard": {
        "player_health": 80,
        "player_damage_multiplier": 0.9,
        "enemy_health_multiplier": 1.2,
        "enemy_damage_multiplier": 1.2,
        "enemy_speed_multiplier": 1.1,
        "pickup_spawn_chance": 0.2,
        "boss_health_multiplier": 1.2
    }
}

# Ajustes de armas
WEAPONS = {
    "fork": {
        "name": "Tenedor", 
        "damage": 25, 
        "ammo": 30, 
        "max_ammo": 30, 
        "reload_time": 15, 
        "fire_rate": 20,
        "projectile_type": "normal",
        "projectile_count": 1,
        "projectile_speed": 12,
        "sound": "assets/sounds/sfx/fork_attack.wav"
    },
    "spoon": {
        "name": "Cuchara", 
        "damage": 75, 
        "ammo": 20, 
        "max_ammo": 20, 
        "reload_time": 40, 
        "fire_rate": 50,
        "projectile_type": "explosive",
        "projectile_count": 1,
        "projectile_speed": 10,
        "sound": "assets/sounds/sfx/spoon_attack.wav"
    },
    "knife": {
        "name": "Cuchillo", 
        "damage": 40, 
        "ammo": 30, 
        "max_ammo": 30, 
        "reload_time": 30, 
        "fire_rate": 10,
        "projectile_type": "rapid",
        "projectile_count": 1,
        "projectile_speed": 15,
        "sound": "assets/sounds/sfx/knife_attack.wav"
    },
    "spatula": {
        "name": "Espátula", 
        "damage": 30, 
        "ammo": 25, 
        "max_ammo": 25, 
        "reload_time": 20, 
        "fire_rate": 15,
        "projectile_type": "spread",
        "projectile_count": 3,
        "projectile_speed": 11,
        "sound": "assets/sounds/sfx/spatula_attack.wav"
    },
    "rolling_pin": {
        "name": "Rodillo", 
        "damage": 50, 
        "ammo": 15, 
        "max_ammo": 15, 
        "reload_time": 45, 
        "fire_rate": 60,
        "projectile_type": "beam",
        "projectile_count": 1,
        "projectile_speed": 20,
        "sound": "assets/sounds/sfx/rolling_pin_attack.wav"
    }
}

# Ajustes de enemigos
ENEMY_TYPES = {
    "guard": {
        "health_base": 50,
        "damage": 5,
        "speed": 1.0,
        "attack_cooldown": 50,
        "value": 10
    },
    "robot": {
        "health_base": 80,
        "damage": 8,
        "speed": 0.7,
        "attack_cooldown": 60,
        "value": 20
    },
    "chef": {
        "health_base": 60,
        "damage": 12,
        "speed": 1.2,
        "attack_cooldown": 70,
        "value": 30
    },
    "minion": {
        "health_base": 30,
        "damage": 3,
        "speed": 1.5,
        "attack_cooldown": 40,
        "value": 5
    }
}

# Boss para cada nivel múltiplo de 5
BOSSES = {
    5: "chef_supremo",
    10: "robot_jefe",
    15: "chef_supremo_enraged",
    20: "robot_jefe_ultimate"
}

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

# Ajustes de progresión del jugador
XP_SETTINGS = {
    "base_threshold": 100,  # XP necesaria para el nivel 2
    "threshold_multiplier": 1.5,  # Multiplicador para cada nivel
    "enemy_base_xp": {
        "guard": 10,
        "robot": 20,
        "chef": 30,
        "minion": 5
    },
    "boss_base_xp": 200,
    "level_up_health_bonus": 10,
    "skill_points_per_level": 1
}

# Rutas de archivos importantes
SAVE_FILE = "assets/save/progress.json"
HIGHSCORE_FILE = "assets/save/highscores.json"

# Controles (teclas por defecto)
CONTROLS = {
    "up": [pygame.K_w, pygame.K_UP],
    "down": [pygame.K_s, pygame.K_DOWN],
    "left": [pygame.K_a, pygame.K_LEFT],
    "right": [pygame.K_d, pygame.K_RIGHT],
    "attack": [1],  # Botón izquierdo del ratón
    "reload": [pygame.K_r],
    "weapon_prev": [-1],  # Rueda del ratón hacia arriba
    "weapon_next": [1],  # Rueda del ratón hacia abajo
    "pause": [pygame.K_p, pygame.K_ESCAPE],
    "interact": [pygame.K_e, pygame.K_SPACE],
    "skills": [pygame.K_TAB]
}