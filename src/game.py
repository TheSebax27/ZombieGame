import pygame
import sys
import random
import math
import os
from pygame.locals import *

# Asegurarnos que los módulos son encontrados
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Inicializar Pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()  # Inicializar mezclador de audio

# Configuración de pantalla
try:
    from config.settings import WIDTH, HEIGHT, FPS, TITLE, DIFFICULTY_SETTINGS, DIFFICULTY
except ImportError:
    WIDTH, HEIGHT = 800, 600
    FPS = 60
    TITLE = "Killer Potato: La Venganza de la Papa"
    DIFFICULTY = "normal"
    DIFFICULTY_SETTINGS = {
        "normal": {
            "player_health": 100,
            "player_damage_multiplier": 1.0,
            "enemy_health_multiplier": 1.0,
            "enemy_damage_multiplier": 1.0,
            "enemy_speed_multiplier": 1.0,
            "pickup_spawn_chance": 0.3,
            "boss_health_multiplier": 1.0
        }
    }

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)

# Cargar fuentes
try:
    font = pygame.font.Font("assets/fonts/potato.ttf", 24)
    big_font = pygame.font.Font("assets/fonts/potato.ttf", 36)
except:
    font = pygame.font.SysFont('Arial', 24)
    big_font = pygame.font.SysFont('Arial', 36)

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

# Función para cargar imágenes con manejo de errores
def load_image(path, scale=None):
    try:
        image = pygame.image.load(path).convert_alpha()
        if scale:
            image = pygame.transform.scale(image, scale)
        return image
    except pygame.error as e:
        print(f"No se pudo cargar la imagen {path}: {e}")
        # Crear una superficie de reemplazo
        surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.rect(surface, (POTATO_BROWN), surface.get_rect(), 1)
        pygame.draw.line(surface, (POTATO_BROWN), (0, 0), (50, 50), 2)
        pygame.draw.line(surface, (POTATO_BROWN), (50, 0), (0, 50), 2)
        return surface

# Clase para objetos recogibles (power-ups, armas, etc.)
class Pickup:
    def __init__(self, x, y, pickup_type):
        self.x = x
        self.y = y
        self.type = pickup_type
        self.radius = 15
        self.bob_offset = 0
        self.bob_speed = 0.1
        self.bob_direction = 1
        self.rotation = 0
        self.rotation_speed = 2
        self.lifetime = 600  # 10 segundos a 60 FPS
        
        # Cargar imagen según tipo
        try:
            if pickup_type == "health":
                self.image = load_image("assets/images/items/health_pickup.png", (30, 30))
            elif pickup_type == "ammo":
                self.image = load_image("assets/images/items/ammo_pickup.png", (30, 30))
            elif pickup_type == "speed":
                self.image = load_image("assets/images/items/speed_pickup.png", (30, 30))
            else:
                self.image = load_image("assets/images/items/generic_pickup.png", (30, 30))
        except:
            # Si no se puede cargar la imagen, crear una superficie básica
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            color = GREEN if pickup_type == "health" else RED if pickup_type == "ammo" else BLUE
            pygame.draw.circle(self.image, color, (15, 15), 15)
            
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        # Efecto de oscilación vertical
        self.bob_offset += self.bob_speed * self.bob_direction
        if abs(self.bob_offset) > 5:
            self.bob_direction *= -1
            
        # Efecto de rotación
        self.rotation = (self.rotation + self.rotation_speed) % 360
        
        # Actualizar rectángulo
        if hasattr(self, 'rect'):
            self.rect.center = (self.x, self.y + self.bob_offset)
        
        # Reducir tiempo de vida
        self.lifetime -= 1
    
    def draw(self, screen):
        try:
            # Rotar imagen
            rotated_image = pygame.transform.rotate(self.image, self.rotation)
            rotated_rect = rotated_image.get_rect(center=(self.x, self.y + self.bob_offset))
            
            # Dibujar pickup
            screen.blit(rotated_image, rotated_rect.topleft)
            
            # Opcional: dibujar brillo alrededor del objeto
            glow_radius = self.radius + 5 + int(math.sin(pygame.time.get_ticks() / 200) * 3)
            glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            
            # Color del brillo según tipo
            if self.type == "health":
                glow_color = (255, 0, 0, 50)
            elif self.type == "ammo":
                glow_color = (255, 255, 0, 50)
            elif self.type == "speed":
                glow_color = (0, 255, 255, 50)
            else:
                glow_color = (255, 255, 255, 50)
                
            pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (self.x - glow_radius, self.y - glow_radius + self.bob_offset))
        except Exception as e:
            # Método de respaldo para dibujar
            color = GREEN if self.type == "health" else RED if self.type == "ammo" else BLUE
            pygame.draw.circle(screen, color, (int(self.x), int(self.y + self.bob_offset)), self.radius)
    
    def is_collected(self, player):
        # Comprobar si el jugador toca el objeto
        distance = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
        return distance < self.radius + player.radius
    
    def is_expired(self):
        return self.lifetime <= 0
        
    def apply_effect(self, player):
        # Aplicar efecto según tipo
        if self.type == "health":
            player.health = min(player.max_health, player.health + 25)
            return "Salud +25"
        elif self.type == "ammo":
            weapon = player.weapons[player.current_weapon]
            weapon["ammo"] = weapon["max_ammo"]
            return f"{weapon['name']} recargada"
        elif self.type == "speed":
            player.speed += 0.5
            return "Velocidad +0.5"
        return "Objeto recogido"

# Importar diálogos
try:
    from src.dialogue import DialogBox, load_dialogues, show_cutscene, show_tutorial
except ImportError:
    # Implementación de respaldo si no se pueden importar
    from dialogue import DialogBox, load_dialogues, show_cutscene, show_tutorial
except Exception as e:
    print(f"Error al cargar diálogos: {e}")
    # Definir clase de respaldo
    class DialogBox:
        def __init__(self):
            self.visible = False
            self.text = ""
            self.speaker = ""
            self.position = "bottom"
            self.width = WIDTH - 100
            self.height = 150
            self.x = 50
            self.y = HEIGHT - 200
            self.text_color = WHITE
            self.bg_color = (0, 0, 0, 180)
            self.border_color = POTATO_BROWN
            self.font = font
            self.portrait = None
            self.display_index = 0
            self.display_speed = 2
            self.display_counter = 0
            self.next_dialog = None
            self.complete = False
            self.dialog_queue = []
        
        def set_dialog(self, text, speaker="", portrait=None, position="bottom", next_dialog=None):
            self.text = text
            self.speaker = speaker
            self.position = position
            self.display_index = 0
            self.display_counter = 0
            self.complete = False
            self.next_dialog = next_dialog
            self.visible = True
        
        def update(self):
            if not self.visible:
                return
                
            if not self.complete:
                self.display_counter += 1
                if self.display_counter >= self.display_speed:
                    self.display_counter = 0
                    self.display_index += 1
                    
                    if self.display_index >= len(self.text):
                        self.complete = True
                        self.display_index = len(self.text)
        
        def draw(self, surface):
            if not self.visible:
                return
                
            # Dibujar el fondo del cuadro de diálogo
            dialog_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            dialog_surface.fill(self.bg_color)
            
            # Borde
            pygame.draw.rect(dialog_surface, self.border_color, (0, 0, self.width, self.height), 2, border_radius=10)
            
            # Dibujar retrato si existe
            if self.portrait:
                surface.blit(self.portrait, (self.x + 10, self.y + (self.height - self.portrait.get_height()) // 2))
                text_start_x = 120
            else:
                text_start_x = 20
            
            # Dibujar nombre del hablante
            if self.speaker:
                speaker_surface = self.font.render(self.speaker, True, RED)
                dialog_surface.blit(speaker_surface, (text_start_x, 10))
                text_start_y = 40
            else:
                text_start_y = 20
            
            # Dibujar texto con animación de escritura
            displayed_text = self.text[:self.display_index]
            
            # Ajuste de texto para que no se salga del cuadro
            max_width = self.width - text_start_x - 20
            words = displayed_text.split(' ')
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + word + " "
                if self.font.size(test_line)[0] < max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)
            
            # Dibujar líneas de texto
            for i, line in enumerate(lines):
                text_surface = self.font.render(line, True, self.text_color)
                dialog_surface.blit(text_surface, (text_start_x, text_start_y + i * 30))
            
            # Indicador de continuar
            if self.complete:
                pygame.draw.polygon(dialog_surface, WHITE, 
                                  [(self.width - 30, self.height - 20), 
                                   (self.width - 10, self.height - 20), 
                                   (self.width - 20, self.height - 10)])
            
            # Dibujar el cuadro de diálogo en la superficie principal
            surface.blit(dialog_surface, (self.x, self.y))
        
        def handle_input(self, event):
            if not self.visible:
                return False
                
            if event.type == KEYDOWN:
                if event.key == K_SPACE or event.key == K_RETURN or event.key == K_z:
                    if self.complete:
                        if self.next_dialog:
                            dialog_text, speaker, portrait = self.next_dialog
                            self.set_dialog(dialog_text, speaker, portrait)
                            return True
                        else:
                            self.visible = False
                            return True
                    else:
                        # Mostrar todo el texto inmediatamente
                        self.display_index = len(self.text)
                        self.complete = True
                        return True
            
            return False
    
    # Funciones de respaldo
    def load_dialogues(level):
        return {"intro": [{"text": f"Nivel {level}! ¡Hora de aplastar humanos!", "speaker": "Killer Potato"}]}
    
    def show_cutscene(screen, level):
        pass
    
    def show_tutorial(screen, level):
        pass

# Clase para efectos de disparo/ataque
class AttackEffect:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.lifetime = 5  # Duración del efecto en frames
        self.image = load_image("assets/images/items/attack_effect.png", (30, 15))
        self.rotated_image = pygame.transform.rotate(self.image, -math.degrees(angle))
        self.rect = self.rotated_image.get_rect(center=(x, y))
    
    def update(self):
        self.lifetime -= 1
    
    def draw(self, screen):
        screen.blit(self.rotated_image, self.rect.topleft)
    
    def is_finished(self):
        return self.lifetime <= 0

# Importar clases necesarias
try:
    from src.player import Player
    from src.weapons import Projectile, ShockWave
    from src.enemies import Enemy, create_random_enemy, create_boss
    from src.levels import LevelManager
except ImportError:
    try:
        from player import Player
        from weapons import Projectile, ShockWave
        from enemies import Enemy, create_random_enemy, create_boss
        from levels import LevelManager
    except ImportError as e:
        print(f"Error al importar módulos del juego: {e}")
        # Clases básicas de respaldo en caso de error
        class Player:
            def __init__(self):
                self.x = WIDTH // 2
                self.y = HEIGHT // 2
                self.radius = 20
                self.speed = 5
                self.health = 100
                self.max_health = 100
                self.damage_multiplier = 1.0
                self.score = 0
                self.level = 1
                self.current_weapon = 0
                self.facing_right = True
                
                # Cargar imágenes del jugador
                self.image_right = load_image("assets/images/characters/killer_potato_right.png", (50, 50))
                self.image_left = load_image("assets/images/characters/killer_potato_left.png", (50, 50))
                
                # Configurar armas
                self.weapons = [
                    {
                        "name": "Tenedor", 
                        "damage": 25, 
                        "ammo": 30, 
                        "max_ammo": 30, 
                        "reload_time": 15, 
                        "reload_counter": 0, 
                        "fire_rate": 20, 
                        "fire_counter": 0,
                        "image_right": load_image("assets/images/items/fork_right.png", (40, 20)),
                        "image_left": load_image("assets/images/items/fork_left.png", (40, 20)),
                        "hud_image": load_image("assets/images/ui/fork_hud.png", (80, 40))
                    }
                ]
                self.is_reloading = False
                self.can_shoot = True
                
                # Cargar HUD
                self.health_bar = load_image("assets/images/ui/health_bar.png", (250, 70))
                self.ammo_bar = load_image("assets/images/ui/ammo_bar.png", (250, 70))
                self.score_display = load_image("assets/images/ui/score_display.png", (150, 50))
                
                # Obtener rectángulo para colisiones
                self.rect = self.image_right.get_rect()
                self.update_rect()
            
            def update_rect(self):
                self.rect.center = (self.x, self.y)
            
            def draw(self, screen):
                screen.blit(self.image_right if self.facing_right else self.image_left, 
                            (self.x - 25, self.y - 25))
            
            def move(self, dx, dy, obstacles=None, level_bounds=None):
                self.x += dx * self.speed
                self.y += dy * self.speed
                self.x = max(20, min(self.x, WIDTH - 20))
                self.y = max(20, min(self.y, HEIGHT - 20))
                self.update_rect()
            
            def attack(self):
                return None, None
            
            def reload(self):
                pass
            
            def update(self):
                pass
            
            def switch_weapon(self, direction):
                pass
            
            def take_damage(self, damage):
                self.health -= damage
                if self.health < 0:
                    self.health = 0
            
            def draw_hud(self, screen, enemies_to_spawn=0, enemies_count=0):
                screen.blit(self.health_bar, (20, 20))
                pygame.draw.rect(screen, GREEN, (70, 50, 150 * (self.health / self.max_health), 25))
                
                screen.blit(self.score_display, (WIDTH - 170, 20))
                score_text = font.render(f"{self.score}", True, RED)
                screen.blit(score_text, (WIDTH - 110, 35))
                
                level_text = font.render(f"NIVEL: {self.level}", True, WHITE)
                screen.blit(level_text, (WIDTH - 150, 80))
        
        class Projectile:
            def __init__(self, x, y, angle, damage):
                self.x = x
                self.y = y
                self.speed = 12
                self.dx = math.cos(angle) * self.speed
                self.dy = math.sin(angle) * self.speed
                self.radius = 5
                self.damage = damage
                self.angle = angle
                self.rect = pygame.Rect(x - 5, y - 5, 10, 10)
            
            def update(self):
                self.x += self.dx
                self.y += self.dy
                self.rect.center = (self.x, self.y)
            
            def draw(self, screen):
                pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)
            
            def is_offscreen(self):
                return (self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT)
        
        class ShockWave:
            def __init__(self, x, y, damage, max_radius, wave_color=None):
                self.x = x
                self.y = y
                self.damage = damage
                self.current_radius = 10
                self.max_radius = max_radius
                self.growth_speed = 5
                self.alpha = 200
                self.fade_speed = 2
                self.hits = set()
            
            def update(self):
                self.current_radius += self.growth_speed
                if self.current_radius > self.max_radius * 0.5:
                    self.growth_speed = max(1, self.growth_speed * 0.95)
                    self.alpha -= self.fade_speed
                    self.fade_speed *= 1.05
                return self.is_finished()
            
            def draw(self, screen):
                pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), int(self.current_radius), 2)
            
            def check_collision(self, entity_rect):
                return False
            
            def is_finished(self):
                return self.current_radius >= self.max_radius or self.alpha <= 0
        
        class Enemy:
            def __init__(self, level, enemy_type="human"):
                self.radius = 20
                self.speed = 1 + level * 0.2
                self.health = 50 + level * 10
                self.max_health = 50 + level * 10
                self.damage = 5 + level
                self.attack_cooldown = 50
                self.attack_counter = 0
                self.facing_right = True
                self.hit_effect = 0
                self.enemy_type = enemy_type
                
                self.x = random.randint(50, WIDTH - 50)
                self.y = random.randint(50, HEIGHT - 50)
                
                self.image = load_image("assets/images/characters/human_right.png", (50, 50))
                self.rect = self.image.get_rect(center=(self.x, self.y))
            
            def update(self, player_x, player_y):
                dx = player_x - self.x
                dy = player_y - self.y
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist > 0:
                    dx /= dist
                    dy /= dist
                
                self.x += dx * self.speed
                self.y += dy * self.speed
                self.facing_right = dx > 0
                self.rect.center = (self.x, self.y)
                
                if self.attack_counter > 0:
                    self.attack_counter -= 1
                
                if self.hit_effect > 0:
                    self.hit_effect -= 1
            
            def draw(self, screen):
                pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)
            
            def take_damage(self, damage):
                self.health -= damage
                self.hit_effect = 5
                return self.is_dead()
            
            def is_dead(self):
                return self.health <= 0
            
            def can_attack(self):
                return self.attack_counter <= 0
            
            def attack(self, player):
                if self.can_attack():
                    player.take_damage(self.damage)
                    self.attack_counter = self.attack_cooldown
                    return True
                return False
        
        def create_random_enemy(level):
            return Enemy(level)
        
        def create_boss(level):
            return None
        
        class LevelManager:
            def __init__(self):
                self.current_level = None
                
            def load_level(self, level_number):
                # Crear nivel básico
                self.current_level = type('Level', (), {})()
                self.current_level.name = f"Nivel {level_number}"
                self.current_level.obstacles = []
                self.current_level.enemies_to_spawn = 10 + level_number * 3
                self.current_level.linear = False
                self.current_level.scroll_offset_x = 0
                self.current_level.scroll_offset_y = 0
                self.current_level.scroll_width = WIDTH
                self.current_level.get_level_bounds = lambda: (0, 0, WIDTH, HEIGHT)
                self.current_level.get_exit_point = lambda: (WIDTH - 50, HEIGHT // 2)
                self.current_level.get_spawn_point = lambda: (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
                self.current_level.get_adjusted_player_position = lambda x, y: (x, y)
                self.current_level.draw = lambda screen, offset_x, offset_y: None
                self.current_level.update = lambda player_x, player_y: None
                self.current_level.mark_completed = lambda: None
                
                return self.current_level
                
            def next_level(self):
                return self.load_level(1)
                
            def show_level_intro(self, screen):
                pass

# Función para dibujar la pantalla de pausa
def draw_pause_screen(screen):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))  # Semi-transparente negro
    screen.blit(overlay, (0, 0))
    
    pause_text = big_font.render("JUEGO PAUSADO", True, WHITE)
    continue_text = font.render("Presiona P para continuar", True, WHITE)
    
    screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 20))

# Función para dibujar pantalla de game over mejorada
def draw_game_over_screen(screen, score, level, time_played):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))  # Más opaco para mejor contraste
    screen.blit(overlay, (0, 0))
    
    game_over_text = big_font.render("GAME OVER", True, RED)
    
    # Convertir tiempo en formato minutos:segundos
    minutes = time_played // 60
    seconds = time_played % 60
    time_text = font.render(f"Tiempo jugado: {minutes}m {seconds}s", True, WHITE)
    
    score_text = font.render(f"Puntuación: {score}", True, WHITE)
    level_text = font.render(f"Nivel alcanzado: {level}", True, WHITE)
    restart_text = font.render("Presiona ENTER para reiniciar", True, WHITE)
    
    # Añadir efecto de sangre/salsa en la parte superior
    try:
        splatter = load_image("assets/images/ui/sauce_splatter.png", (300, 150))
        screen.blit(splatter, (WIDTH//2 - 150, 50))
    except:
        pass
    
    # Posicionar texto con mejor espaciado
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 20))
    screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 + 20))
    screen.blit(time_text, (WIDTH//2 - time_text.get_width()//2, HEIGHT//2 + 60))
    
    # Efecto de parpadeo para el texto de reinicio
    if pygame.time.get_ticks() % 1000 < 700:  # Parpadeo más lento
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 120))

# Función principal del juego mejorada
def main():
    global enemies, enemies_to_spawn  # Para acceso desde métodos de clase
    
    clock = pygame.time.Clock()
    
    # Intentar cargar el sistema de niveles
    try:
        level_manager = LevelManager()
        current_level = level_manager.load_level(1)
        use_level_system = True
        
        print(f"Sistema de niveles cargado correctamente. Nivel actual: {current_level.name}")
        
        # Valores iniciales desde el nivel
        level_width = current_level.scroll_width if hasattr(current_level, 'linear') and current_level.linear else WIDTH
        level_height = HEIGHT
        enemies_in_level = current_level.enemies_to_spawn
        enemies_to_spawn = enemies_in_level
        obstacles = current_level.obstacles if hasattr(current_level, 'obstacles') else []
        level_obstacles = obstacles
        
        # Mostrar introducción del nivel
        level_manager.show_level_intro(screen)
    except Exception as e:
        print(f"Error al cargar sistema de niveles: {e}")
        print("Usando modo arena por defecto...")
        use_level_system = False
        current_level = None
        
        # Valores predeterminados para el modo arena
        level_width = WIDTH
        level_height = HEIGHT
        enemies_in_level = 15  # Inicial
        enemies_to_spawn = enemies_in_level
        obstacles = []
        level_obstacles = obstacles
    
    # Cargar imágenes de fondo
    try:
        background = load_image("assets/images/backgrounds/game_background.png", (WIDTH, HEIGHT))
    except:
        # Si no se puede cargar la imagen, crear un fondo de color
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill(GRAY)
    
    player = Player()
    projectiles = []
    attack_effects = []
    enemies = []
    pickups = []
    
    level = 1
    spawn_cooldown = 60  # frames entre spawn de enemigos
    spawn_counter = 0
    
    level_complete = False
    level_timer = 180  # Pausa entre niveles (3 segundos a 60 FPS)
    
    game_over = False
    paused = False
    
    # Contadores de estadísticas
    time_played = 0  # Tiempo en frames (60 por segundo)
    enemy_kills = 0
    
    # Diálogo inicial
    dialog = DialogBox()
    show_intro_dialog = True
    
    if show_intro_dialog:
        # Intentar cargar diálogos del nivel actual
        try:
            if use_level_system:
                level_dialogues = load_dialogues(1)
                intro_dialog = level_dialogues.get("intro", [])[0]
                
                dialog.set_dialog(
                    intro_dialog.get("text", "¡Por fin he escapado! Hora de vengarse."), 
                    intro_dialog.get("speaker", "Killer Potato"), 
                    intro_dialog.get("portrait", "assets/images/characters/killer_potato_dialog.png"),
                    intro_dialog.get("position", "bottom")
                )
            else:
                # Diálogo predeterminado si no hay sistema de niveles
                dialog.set_dialog(
                    "¡Por fin he escapado! Ahora es hora de vengarme de los humanos que nos convirtieron en... esto.", 
                    "Killer Potato", 
                    "assets/images/characters/killer_potato_dialog.png",
                    "bottom",
                    ("Veo que hay guardias de seguridad adelante. ¡Tendré que abrirme paso a través de ellos!", 
                     "Killer Potato", 
                     "assets/images/characters/killer_potato_dialog.png")
                )
        except Exception as e:
            print(f"Error al cargar diálogos: {e}")
            # Diálogo predeterminado
            dialog.set_dialog(
                "¡Por fin he escapado! Ahora es hora de vengarme.", 
                "Killer Potato", 
                "assets/images/characters/killer_potato_dialog.png"
            )
    
    running = True
    while running:
        # Obtener el tiempo transcurrido para estadísticas
        if not game_over and not paused and not dialog.visible:
            time_played += 1
        
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            if event.type == KEYDOWN:
                if event.key == K_p:  # Tecla de pausa
                    paused = not paused
                
                # Manejo de diálogos
                if dialog.visible:
                    dialog.handle_input(event)
                
                if not paused and not game_over and not dialog.visible:
                    if event.key == K_r:
                        player.reload()
                    if event.key == K_1:
                        player.current_weapon = 0
                    if event.key == K_2 and len(player.weapons) > 1:
                        player.current_weapon = 1
                    if event.key == K_3 and len(player.weapons) > 2:
                        player.current_weapon = 2
                    if event.key == K_SPACE and level_complete:
                        # Iniciar próximo nivel
                        level += 1
                        player.level = level
                        
                        if use_level_system:
                            # Cargar siguiente nivel
                            current_level = level_manager.next_level()
                            if hasattr(current_level, 'enemies_to_spawn'):
                                enemies_in_level = current_level.enemies_to_spawn
                            else:
                                enemies_in_level = 5 + level * 2
                                
                            if hasattr(current_level, 'obstacles'):
                                obstacles = current_level.obstacles
                            else:
                                obstacles = []
                                
                            level_obstacles = obstacles
                            
                            # Mostrar introducción del nuevo nivel
                            level_manager.show_level_intro(screen)
                        else:
                            # Incrementar dificultad en modo arena
                            enemies_in_level = 5 + level * 2
                            
                        enemies_to_spawn = enemies_in_level
                        level_complete = False
                
                if game_over and event.key == K_RETURN:
                    # Reiniciar juego
                    player = Player()
                    projectiles = []
                    attack_effects = []
                    enemies = []
                    pickups = []
                    level = 1
                    
                    if use_level_system:
                        # Reiniciar desde el nivel 1
                        current_level = level_manager.load_level(1)
                        if hasattr(current_level, 'enemies_to_spawn'):
                            enemies_in_level = current_level.enemies_to_spawn
                        else:
                            enemies_in_level = 5
                            
                        if hasattr(current_level, 'obstacles'):
                            obstacles = current_level.obstacles
                        else:
                            obstacles = []
                            
                        level_obstacles = obstacles
                    else:
                        enemies_in_level = 5
                        
                    enemies_to_spawn = enemies_in_level
                    spawn_cooldown = 60
                    spawn_counter = 0
                    level_complete = False
                    game_over = False
                    time_played = 0
                    enemy_kills = 0
            
            if not paused and not game_over and not dialog.visible:
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    projectile, effect = player.attack()
                    if projectile:
                        projectiles.append(projectile)
                    if effect:
                        attack_effects.append(effect)
                
                if event.type == MOUSEWHEEL:
                    player.switch_weapon(event.y)
        
        # Actualizar diálogo
        dialog.update()
        
        if dialog.visible:
            # Dibujar juego pero congelar actualizaciones
            if use_level_system and current_level:
                current_level.draw(screen, current_level.scroll_offset_x, current_level.scroll_offset_y)
            else:
                screen.blit(background, (0, 0))
            
            # Dibujar jugador y enemigos
            player.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
                
            # Dibujar HUD
            player.draw_hud(screen, enemies_to_spawn, len(enemies))
            
            # Dibujar diálogo
            dialog.draw(screen)
            
            pygame.display.flip()
            clock.tick(60)
            continue
            
        if paused:
            draw_pause_screen(screen)
            pygame.display.flip()
            continue
            
        if game_over:
            draw_game_over_screen(screen, player.score, level, time_played // 60)  # Convertir frames a segundos
            pygame.display.flip()
            continue
        
        # Lógica de juego
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[K_w] or keys[K_UP]:
            dy -= 1
        if keys[K_s] or keys[K_DOWN]:
            dy += 1
        if keys[K_a] or keys[K_LEFT]:
            dx -= 1
        if keys[K_d] or keys[K_RIGHT]:
            dx += 1
        
        # Normalizar diagonal
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        
        # Actualizar posición del jugador dependiendo del sistema de niveles
        if use_level_system and hasattr(current_level, 'get_level_bounds') and hasattr(current_level, 'get_adjusted_player_position'):
            # Ajustar posición para niveles lineales
            player.move(dx, dy, level_obstacles, current_level.get_level_bounds())
            player_x, player_y = current_level.get_adjusted_player_position(player.x, player.y)
            player.x, player.y = player_x, player_y
            player.update_rect()
            
            # Actualizar nivel
            if hasattr(current_level, 'update'):
                current_level.update(player.x, player.y)
        else:
            # Movimiento normal para modo arena
            player.move(dx, dy, obstacles)
        
        # Actualizar jugador
        player.update()
        
        # Actualizar efectos de ataque
        for effect in attack_effects[:]:
            effect.update()
            if effect.is_finished():
                attack_effects.remove(effect)
        
        # Actualizar proyectiles
        for projectile in projectiles[:]:
            projectile.update()
            
            # Comprobar colisión con obstáculos
            if use_level_system and level_obstacles:
                for obstacle in level_obstacles:
                    # Ajustar posición del obstáculo para niveles lineales
                    if hasattr(current_level, 'linear') and current_level.linear and hasattr(obstacle, 'rect'):
                        obstacle_x = obstacle.x - current_level.scroll_offset_x
                        obstacle_y = obstacle.y
                        obstacle_rect = pygame.Rect(obstacle_x, obstacle_y, obstacle.width, obstacle.height)
                    elif hasattr(obstacle, 'rect'):
                        obstacle_rect = obstacle.rect
                    else:
                        # Si el obstáculo no tiene rect, crear uno básico
                        obstacle_rect = pygame.Rect(obstacle.x, obstacle.y, 50, 50)
                    
                    if hasattr(projectile, 'rect'):
                        collision = obstacle_rect.colliderect(projectile.rect)
                    else:
                        # Si el proyectil no tiene rect, comprobar con círculo
                        collision = obstacle_rect.collidepoint(projectile.x, projectile.y)
                        
                    if collision:
                        projectiles.remove(projectile)
                        
                        # Si el obstáculo es destructible, dañarlo
                        if hasattr(obstacle, 'destructible') and obstacle.destructible:
                            if hasattr(obstacle, 'take_damage'):
                                if obstacle.take_damage(projectile.damage):
                                    level_obstacles.remove(obstacle)
                        break
            
            # Eliminar proyectiles fuera de pantalla
            if hasattr(projectile, 'is_offscreen'):
                if projectile.is_offscreen():
                    projectiles.remove(projectile)
            # Alternativa si no tiene método is_offscreen
            elif projectile.x < 0 or projectile.x > WIDTH or projectile.y < 0 or projectile.y > HEIGHT:
                projectiles.remove(projectile)
        
        # Actualizar enemigos y comprobar colisiones
        for enemy in enemies[:]:
            # En niveles lineales, ajustar posición de enemigos
            if use_level_system and hasattr(current_level, 'linear') and current_level.linear:
                enemy.update(player.x, player.y, level_obstacles)
            else:
                enemy.update(player.x, player.y, obstacles)
            
            # Comprobar colisión con jugador
            if hasattr(player, 'rect') and hasattr(enemy, 'rect'):
                if player.rect.colliderect(enemy.rect):
                    enemy.attack(player)
            else:
                # Alternativa si no tienen rectángulos
                dist = math.sqrt((player.x - enemy.x) ** 2 + (player.y - enemy.y) ** 2)
                if dist < player.radius + enemy.radius:
                    enemy.attack(player)
            
            # Comprobar colisión con proyectiles
            for projectile in projectiles[:]:
                if projectile in projectiles:  # Verificar que aún existe
                    if hasattr(enemy, 'rect') and hasattr(projectile, 'rect'):
                        if enemy.rect.colliderect(projectile.rect):
                            enemy.take_damage(projectile.damage)
                            projectiles.remove(projectile)
                            break
                    else:
                        # Alternativa si no tienen rectángulos
                        dist = math.sqrt((projectile.x - enemy.x) ** 2 + (projectile.y - enemy.y) ** 2)
                        if dist < enemy.radius + projectile.radius:
                            enemy.take_damage(projectile.damage)
                            if projectile in projectiles:  # Verificar que aún existe
                                projectiles.remove(projectile)
                            break
            
            # Eliminar enemigos muertos
            if enemy.is_dead():
                # Posibilidad de soltar pickup
                pickup_chance = 0.3  # 30% de probabilidad base
                
                # En niveles con sistema, usar configuración de dificultad
                if use_level_system and 'DIFFICULTY_SETTINGS' in globals():
                    difficulty_config = DIFFICULTY_SETTINGS.get(DIFFICULTY, DIFFICULTY_SETTINGS["normal"])
                    pickup_chance = difficulty_config.get("pickup_spawn_chance", 0.3)
                
                if random.random() < pickup_chance:
                    pickup_type = random.choice(["health", "ammo", "speed"])
                    # Usar clase Pickup definida en este archivo
                    pickups.append(Pickup(enemy.x, enemy.y, pickup_type))
                
                player.score += 10
                enemy_kills += 1
                enemies.remove(enemy)
        
        # Actualizar pickups
        for pickup in pickups[:]:
            if hasattr(pickup, 'update'):
                pickup.update()
            
            # Comprobar si el jugador recoge el pickup
            if pickup.is_collected(player):
                message = pickup.apply_effect(player)
                # Reproducir sonido de recogida
                try:
                    pickup_sound = pygame.mixer.Sound("assets/sounds/sfx/pickup.wav")
                    pickup_sound.play()
                except:
                    pass
                pickups.remove(pickup)
            elif hasattr(pickup, 'is_expired') and pickup.is_expired():
                pickups.remove(pickup)
        
        # Generar enemigos
        if not level_complete and enemies_to_spawn > 0:
            if spawn_counter <= 0:
                # Elegir tipo de enemigo basado en nivel
                enemy = create_random_enemy(level)
                
                # En niveles con sistema, usar punto de spawn del nivel
                if use_level_system and hasattr(current_level, 'get_spawn_point'):
                    spawn_x, spawn_y = current_level.get_spawn_point()
                    enemy.x = spawn_x
                    enemy.y = spawn_y
                    if hasattr(enemy, 'update_rect'):
                        enemy.update_rect()
                    
                enemies.append(enemy)
                enemies_to_spawn -= 1
                spawn_counter = spawn_cooldown
            else:
                spawn_counter -= 1
        
        # Comprobar condiciones de victoria en sistema de niveles
        if use_level_system and not level_complete:
            # Verificar si el jugador está en el punto de salida
            if hasattr(current_level, 'get_exit_point'):
                exit_x, exit_y = current_level.get_exit_point()
                distance_to_exit = math.sqrt((player.x - exit_x)**2 + (player.y - exit_y)**2)
                
                # Nivel completado si no hay más enemigos y se llega a la salida
                if enemies_to_spawn <= 0 and len(enemies) == 0 and distance_to_exit < 50:
                    level_complete = True
                    level_timer = 180  # Reiniciar temporizador entre niveles
                    
                    # Marcar nivel como completado
                    if hasattr(current_level, 'mark_completed'):
                        current_level.mark_completed()
                    
                    # Mostrar diálogo de nivel completado
                    try:
                        level_dialogues = load_dialogues(level)
                        complete_dialog = level_dialogues.get("level_complete", [])[0]
                        
                        dialog.set_dialog(
                            complete_dialog.get("text", f"¡Nivel {level} completado!"), 
                            complete_dialog.get("speaker", "Sistema"), 
                            complete_dialog.get("portrait", None),
                            complete_dialog.get("position", "top")
                        )
                    except Exception as e:
                        print(f"Error al cargar diálogo de nivel completado: {e}")
        else:
            # En modo arena, completar nivel cuando no quedan enemigos
            if not level_complete and enemies_to_spawn <= 0 and len(enemies) == 0:
                level_complete = True
                level_timer = 180  # Reiniciar temporizador entre niveles
        
        # Actualizar temporizador entre niveles
        if level_complete:
            level_timer -= 1
        
        # Comprobar si el jugador ha muerto
        if player.health <= 0:
            game_over = True
            # Reproducir sonido de Game Over
            try:
                game_over_sound = pygame.mixer.Sound("assets/sounds/sfx/game_over.wav")
                game_over_sound.play()
            except:
                pass
        
        # Dibujar todo
        if use_level_system and hasattr(current_level, 'draw'):
            current_level.draw(screen, current_level.scroll_offset_x, current_level.scroll_offset_y)
            
            # Dibujar punto de salida si nivel está casi completado
            if enemies_to_spawn <= 0 and len(enemies) == 0:
                exit_x, exit_y = current_level.get_exit_point()
                
                # Efecto pulsante para salida
                pulse = abs(math.sin(pygame.time.get_ticks() / 500)) * 5
                exit_radius = 25 + pulse
                
                # Círculo de salida
                exit_surface = pygame.Surface((exit_radius*2, exit_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(exit_surface, (0, 255, 0, 150), (exit_radius, exit_radius), exit_radius)
                screen.blit(exit_surface, (exit_x - exit_radius, exit_y - exit_radius))
                
                # Texto "SALIDA"
                exit_text = font.render("SALIDA", True, GREEN)
                screen.blit(exit_text, (exit_x - exit_text.get_width()//2, exit_y - exit_radius - 30))
        else:
            screen.blit(background, (0, 0))
        
        # Dibujar pickups
        for pickup in pickups:
            pickup.draw(screen)
            
        # Dibujar proyectiles
        for projectile in projectiles:
            projectile.draw(screen)
            
        # Dibujar enemigos
        for enemy in enemies:
            enemy.draw(screen)
            
        # Dibujar jugador
        player.draw(screen)
        
        # Dibujar efectos de ataque
        for effect in attack_effects:
            effect.draw(screen)
        
        # Dibujar HUD
        player.draw_hud(screen, enemies_to_spawn, len(enemies))
        
        # Mensaje de nivel completado
        if level_complete:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))  # Semi-transparente
            screen.blit(overlay, (0, 0))
            
            complete_text = big_font.render(f"¡NIVEL {level} COMPLETADO!", True, WHITE)
            next_text = font.render("Presiona ESPACIO para iniciar el siguiente nivel", True, WHITE)
            screen.blit(complete_text, (WIDTH//2 - complete_text.get_width()//2, HEIGHT//2 - 30))
            screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 + 20))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()