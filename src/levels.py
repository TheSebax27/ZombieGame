"""
Módulo de niveles para Killer Potato
Define la estructura, diseño y progresión de los niveles del juego
"""

import pygame
import random
import math
import json
import os
from pygame.locals import *

# Inicializar pygame si no está inicializado
if not pygame.get_init():
    pygame.init()

# Configuración de pantalla (tomar de config o usar valores por defecto)
try:
    from config.settings import WIDTH, HEIGHT
except ImportError:
    WIDTH, HEIGHT = 800, 600

# Importar módulos necesarios
try:
    from dialogue import load_dialogues, show_cutscene, show_tutorial
    from enemies import create_random_enemy, create_boss
except ImportError:
    pass

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
        pygame.draw.rect(surface, (255, 0, 0), surface.get_rect(), 1)
        pygame.draw.line(surface, (255, 0, 0), (0, 0), (50, 50), 2)
        pygame.draw.line(surface, (255, 0, 0), (50, 0), (0, 50), 2)
        return surface

# Clase para obstáculos y elementos interactivos
class Obstacle:
    def __init__(self, x, y, width, height, obstacle_type="wall"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = obstacle_type
        self.destructible = False
        self.health = 0
        self.image = None
        
        # Configurar según tipo
        if obstacle_type == "wall":
            try:
                self.image = load_image("assets/images/obstacles/wall.png", (width, height))
            except:
                pass
        elif obstacle_type == "table":
            try:
                self.image = load_image("assets/images/obstacles/table.png", (width, height))
            except:
                pass
            self.destructible = True
            self.health = 30
        elif obstacle_type == "crate":
            try:
                self.image = load_image("assets/images/obstacles/crate.png", (width, height))
            except:
                pass
            self.destructible = True
            self.health = 20
        elif obstacle_type == "barrel":
            try:
                self.image = load_image("assets/images/obstacles/barrel.png", (width, height))
            except:
                pass
            self.destructible = True
            self.health = 15
        
        # Rectángulo para colisiones
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            # Dibujar rectángulo como fallback
            if self.type == "wall":
                color = GRAY
            elif self.type == "table":
                color = POTATO_BROWN
            elif self.type == "crate":
                color = (193, 154, 107)  # Marrón claro
            elif self.type == "barrel":
                color = (165, 42, 42)  # Marrón rojizo
            else:
                color = BLACK
                
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)  # Borde
    
    def take_damage(self, damage):
        """Aplicar daño al obstáculo"""
        if not self.destructible:
            return False
            
        self.health -= damage
        if self.health <= 0:
            return True  # Destruido
        return False

# Clase para "checkpoints" o puntos de control
class Checkpoint:
    def __init__(self, x, y, checkpoint_id):
        self.x = x
        self.y = y
        self.id = checkpoint_id
        self.radius = 30
        self.active = False
        self.animation_counter = 0
        
        # Intentar cargar imágenes
        try:
            self.inactive_image = load_image("assets/images/items/checkpoint_inactive.png", (60, 60))
            self.active_image = load_image("assets/images/items/checkpoint_active.png", (60, 60))
        except:
            self.inactive_image = None
            self.active_image = None
            
        # Rectángulo para colisiones
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius*2, self.radius*2)
    
    def update(self):
        """Actualizar animación"""
        self.animation_counter = (self.animation_counter + 1) % 60  # Ciclo de 1 segundo a 60 FPS
    
    def draw(self, screen):
        """Dibujar checkpoint"""
        if self.active and self.active_image:
            # Efecto de pulso para checkpoint activo
            pulse = math.sin(self.animation_counter / 10) * 5
            scale_factor = 1 + pulse * 0.01
            scaled_image = pygame.transform.scale(
                self.active_image, 
                (int(self.active_image.get_width() * scale_factor), 
                 int(self.active_image.get_height() * scale_factor))
            )
            screen.blit(scaled_image, (self.x - scaled_image.get_width()//2, self.y - scaled_image.get_height()//2))
        elif not self.active and self.inactive_image:
            screen.blit(self.inactive_image, (self.x - self.inactive_image.get_width()//2, self.y - self.inactive_image.get_height()//2))
        else:
            # Dibujo fallback si no hay imágenes
            if self.active:
                color = GREEN
            else:
                color = GRAY
                
            pygame.draw.circle(screen, color, (self.x, self.y), self.radius)
            pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius, 2)  # Borde
    
    def activate(self):
        """Activar checkpoint"""
        if not self.active:
            self.active = True
            
            # Reproducir sonido si existe
            try:
                checkpoint_sound = pygame.mixer.Sound("assets/sounds/sfx/checkpoint.wav")
                checkpoint_sound.play()
            except:
                pass
            
            return True
        return False

# Clase para representar un nivel
class Level:
    def __init__(self, level_number):
        self.level_number = level_number
        self.name = f"Nivel {level_number}"
        self.description = ""
        self.background = None
        self.obstacles = []
        self.checkpoints = []
        self.spawn_points = []
        self.exit_point = (0, 0)
        self.enemies_to_spawn = 0
        self.boss = None
        self.spawn_rate = 60  # Frames entre generación de enemigos
        self.dialogues = []
        self.completed = False
        self.linear = True  # Modo lineal (avance horizontal)
        self.scroll_offset_x = 0
        self.scroll_offset_y = 0
        self.scroll_width = WIDTH * 3  # Ancho total del nivel para scroll
        self.scroll_speed = 1  # Velocidad de desplazamiento para niveles lineales
        
        # Cargar nivel
        self.load_level(level_number)
    
    def load_level(self, level_number):
        """Cargar datos del nivel desde archivo o generar dinámicamente"""
        level_file = f"assets/levels/level{level_number}.json"
        
        try:
            # Intentar cargar desde archivo
            with open(level_file, 'r') as file:
                level_data = json.load(file)
                
                self.name = level_data.get("name", f"Nivel {level_number}")
                self.description = level_data.get("description", "")
                
                # Cargar fondo
                background_path = level_data.get("background", "")
                if background_path:
                    try:
                        self.background = load_image(background_path, (WIDTH, HEIGHT))
                    except:
                        self.background = self.generate_default_background()
                else:
                    self.background = self.generate_default_background()
                
                # Cargar scroll si es nivel lineal
                self.linear = level_data.get("linear", True)
                if self.linear:
                    # Para niveles lineales, el fondo es más ancho
                    self.scroll_width = level_data.get("scroll_width", WIDTH * 3)
                    try:
                        self.background = load_image(background_path, (self.scroll_width, HEIGHT))
                    except:
                        self.background = self.generate_default_background(self.scroll_width)
                
                # Cargar obstáculos
                for obstacle_data in level_data.get("obstacles", []):
                    obstacle = Obstacle(
                        obstacle_data.get("x", 0),
                        obstacle_data.get("y", 0),
                        obstacle_data.get("width", 50),
                        obstacle_data.get("height", 50),
                        obstacle_data.get("type", "wall")
                    )
                    self.obstacles.append(obstacle)
                
                # Cargar checkpoints
                for checkpoint_data in level_data.get("checkpoints", []):
                    checkpoint = Checkpoint(
                        checkpoint_data.get("x", 0),
                        checkpoint_data.get("y", 0),
                        checkpoint_data.get("id", 0)
                    )
                    self.checkpoints.append(checkpoint)
                
                # Otros datos
                self.spawn_points = level_data.get("spawn_points", [(100, 100), (WIDTH-100, 100), (WIDTH-100, HEIGHT-100), (100, HEIGHT-100)])
                self.exit_point = level_data.get("exit_point", (WIDTH//2, HEIGHT//2))
                self.enemies_to_spawn = level_data.get("enemies_count", 5 + level_number * 2)
                self.spawn_rate = level_data.get("spawn_rate", 60)
                
                # Boss específico (si hay)
                if "boss" in level_data and level_data["boss"]:
                    self.boss = level_data["boss"]
                    
                print(f"Nivel {level_number} cargado con éxito desde archivo.")
                
        except (FileNotFoundError, json.JSONDecodeError):
            # Generar nivel dinámicamente
            print(f"Generando nivel {level_number} dinámicamente...")
            self.generate_level(level_number)
    
    def generate_level(self, level_number):
        """Generar nivel dinámicamente si no hay archivo"""
        self.name = f"Nivel {level_number}"
        self.description = f"¡Mata a todos los enemigos para avanzar al nivel {level_number + 1}!"
        
        # Determinar tipo de nivel
        if level_number % 5 == 0:  # Cada 5 niveles, nivel de jefe
            self.generate_boss_level(level_number)
        elif level_number % 2 == 0:  # Niveles pares, nivel lineal
            self.generate_linear_level(level_number)
        else:  # Niveles impares, nivel arena
            self.generate_arena_level(level_number)
    
    def generate_default_background(self, width=None):
        """Generar un fondo predeterminado si no se puede cargar la imagen"""
        if width is None:
            width = WIDTH
            
        bg = pygame.Surface((width, HEIGHT))
        
        # Seleccionar color según tipo de nivel
        if self.level_number % 5 == 0:  # Nivel de jefe
            base_color = (50, 0, 0)  # Rojo oscuro
        elif self.level_number % 3 == 0:  # Variante 1
            base_color = (0, 30, 60)  # Azul oscuro
        elif self.level_number % 3 == 1:  # Variante 2
            base_color = (40, 40, 0)  # Amarillo oscuro
        else:  # Variante 3
            base_color = (30, 40, 20)  # Verde oliva
            
        bg.fill(base_color)
        
        # Añadir patrón de cuadrícula o textura
        for x in range(0, width, 64):
            for y in range(0, HEIGHT, 64):
                if (x // 64 + y // 64) % 2 == 0:
                    rect = pygame.Rect(x, y, 64, 64)
                    pygame.draw.rect(bg, 
                                    (base_color[0]+10, base_color[1]+10, base_color[2]+10),
                                    rect)
                    pygame.draw.rect(bg, 
                                    (base_color[0]+5, base_color[1]+5, base_color[2]+5),
                                    rect, 1)
        
        return bg
    
    def generate_boss_level(self, level_number):
        """Generar un nivel de jefe"""
        self.name = f"NIVEL {level_number} - JEFE"
        self.description = "¡Derrota al jefe para avanzar!"
        self.boss = "chef_supremo" if level_number % 10 != 0 else "robot_jefe"
        self.linear = False
        
        # Menos enemigos normales en nivel de jefe
        self.enemies_to_spawn = 3 + level_number // 2
        
        # Generar obstáculos estratégicos
        self.obstacles = []
        
        # Añadir algunas paredes/obstáculos en el centro y esquinas
        self.obstacles.append(Obstacle(WIDTH//2 - 50, HEIGHT//2 - 50, 100, 100, "table"))
        
        for i in range(4):  # Añadir barriles en las esquinas
            x = 100 if i % 2 == 0 else WIDTH - 150
            y = 100 if i < 2 else HEIGHT - 150
            self.obstacles.append(Obstacle(x, y, 50, 50, "barrel"))
        
        # Checkpoints (generalmente no hay en niveles de jefe)
        self.checkpoints = []
        
        # Puntos de aparición de enemigos
        self.spawn_points = [
            (50, 50),
            (WIDTH - 100, 50),
            (WIDTH - 100, HEIGHT - 100),
            (50, HEIGHT - 100)
        ]
        
        # Punto de salida (generalmente el centro para el jefe)
        self.exit_point = (WIDTH // 2, HEIGHT // 2)
    
    def generate_linear_level(self, level_number):
        """Generar un nivel lineal (desplazamiento horizontal)"""
        self.name = f"Nivel {level_number} - Escape"
        self.description = "Avanza hacia la derecha y elimina todos los enemigos."
        self.linear = True
        
        # Configurar desplazamiento
        self.scroll_width = WIDTH * 3
        
        # Generar fondo apropiado
        self.background = self.generate_default_background(self.scroll_width)
        
        # Cantidad de enemigos
        self.enemies_to_spawn = 8 + level_number * 2
        
        # Generar obstáculos a lo largo del camino
        self.obstacles = []
        
        # Añadir obstáculos aleatorios
        num_obstacles = 15 + level_number * 2
        obstacle_types = ["wall", "table", "crate", "barrel"]
        
        for _ in range(num_obstacles):
            obstacle_type = random.choice(obstacle_types)
            width = random.randint(40, 80)
            height = random.randint(40, 80)
            
            # Posición dentro del nivel desplazable
            x = random.randint(0, self.scroll_width - width)
            y = random.randint(0, HEIGHT - height)
            
            # Evitar bloquear completamente el camino
            if obstacle_type == "wall" and y > HEIGHT//4 and y < 3*HEIGHT//4:
                # Asegurar que hay espacio para pasar
                y = random.choice([random.randint(0, HEIGHT//4), random.randint(3*HEIGHT//4, HEIGHT-height)])
            
            self.obstacles.append(Obstacle(x, y, width, height, obstacle_type))
        
        # Añadir checkpoints a lo largo del camino
        self.checkpoints = []
        for i in range(1, 4):  # 3 checkpoints
            x = i * (self.scroll_width // 4)
            y = HEIGHT // 2
            self.checkpoints.append(Checkpoint(x, y, i))
        
        # Puntos de aparición de enemigos distribuidos por el nivel
        self.spawn_points = []
        for i in range(6):
            x = random.randint(0, self.scroll_width - 100)
            y = random.randint(50, HEIGHT - 100)
            self.spawn_points.append((x, y))
        
        # Punto de salida al final del nivel
        self.exit_point = (self.scroll_width - 100, HEIGHT // 2)
    
    def generate_arena_level(self, level_number):
        """Generar un nivel tipo arena (sin desplazamiento)"""
        self.name = f"Nivel {level_number} - Exterminio"
        self.description = "Elimina a todos los enemigos para avanzar."
        self.linear = False
        
        # Generar fondo estándar
        self.background = self.generate_default_background()
        
        # Cantidad de enemigos
        self.enemies_to_spawn = 10 + level_number * 3
        
        # Generar obstáculos distribuidos por la arena
        self.obstacles = []
        
        # Crear un patrón de obstáculos según el nivel
        if level_number % 3 == 0:
            # Patrón circular
            center_x, center_y = WIDTH // 2, HEIGHT // 2
            radius = min(WIDTH, HEIGHT) // 3
            
            for i in range(8):
                angle = i * math.pi / 4
                x = center_x + int(math.cos(angle) * radius) - 25
                y = center_y + int(math.sin(angle) * radius) - 25
                self.obstacles.append(Obstacle(x, y, 50, 50, "crate"))
                
            # Obstáculo central
            self.obstacles.append(Obstacle(center_x - 30, center_y - 30, 60, 60, "table"))
            
        elif level_number % 3 == 1:
            # Patrón de cuadrícula
            for x in range(100, WIDTH - 100, 150):
                for y in range(100, HEIGHT - 100, 150):
                    if random.random() < 0.7:  # 70% de probabilidad
                        obstacle_type = random.choice(["wall", "table", "crate", "barrel"])
                        self.obstacles.append(Obstacle(x, y, 50, 50, obstacle_type))
                        
        else:
            # Patrón aleatorio
            num_obstacles = 10 + level_number
            for _ in range(num_obstacles):
                x = random.randint(50, WIDTH - 100)
                y = random.randint(50, HEIGHT - 100)
                obstacle_type = random.choice(["wall", "table", "crate", "barrel"])
                
                # Tamaño variable
                width = random.randint(40, 80)
                height = random.randint(40, 80)
                
                self.obstacles.append(Obstacle(x, y, width, height, obstacle_type))
        
        # Un único checkpoint en el centro
        self.checkpoints = [Checkpoint(WIDTH // 2, HEIGHT // 2, 1)]
        
        # Puntos de aparición en las esquinas
        self.spawn_points = [
            (50, 50),
            (WIDTH - 100, 50),
            (WIDTH - 100, HEIGHT - 100),
            (50, HEIGHT - 100)
        ]
        
        # Punto de salida cerca del centro
        self.exit_point = (WIDTH // 2 + random.randint(-50, 50), 
                          HEIGHT // 2 + random.randint(-50, 50))
    
    def update(self, player_x=None, player_y=None):
        """Actualizar elementos del nivel"""
        # Actualizar checkpoints
        for checkpoint in self.checkpoints:
            checkpoint.update()
            
            # Verificar si el jugador activa checkpoint
            if player_x is not None and player_y is not None:
                dist = math.sqrt((player_x - checkpoint.x)**2 + (player_y - checkpoint.y)**2)
                if dist < checkpoint.radius and not checkpoint.active:
                    checkpoint.activate()
    
    def draw(self, screen, offset_x=0, offset_y=0):
        """Dibujar el nivel en pantalla"""
        # Dibujar fondo
        if self.background:
            if self.linear:
                # Para niveles lineales, mostrar porción del fondo según desplazamiento
                screen.blit(self.background, (-offset_x, -offset_y))
            else:
                screen.blit(self.background, (0, 0))
        else:
            # Fondo negro como fallback
            screen.fill(BLACK)
        
        # Dibujar obstáculos
        for obstacle in self.obstacles:
            # Ajustar posición según desplazamiento
            if self.linear:
                draw_x = obstacle.x - offset_x
                draw_y = obstacle.y - offset_y
                
                # Solo dibujar si es visible
                if -obstacle.width <= draw_x <= WIDTH and -obstacle.height <= draw_y <= HEIGHT:
                    # Crear un rectángulo temporal para dibujo
                    temp_rect = pygame.Rect(draw_x, draw_y, obstacle.width, obstacle.height)
                    
                    if obstacle.image:
                        screen.blit(obstacle.image, (draw_x, draw_y))
                    else:
                        # Dibujo fallback
                        if obstacle.type == "wall":
                            color = GRAY
                        elif obstacle.type == "table":
                            color = POTATO_BROWN
                        elif obstacle.type == "crate":
                            color = (193, 154, 107)
                        elif obstacle.type == "barrel":
                            color = (165, 42, 42)
                        else:
                            color = BLACK
                            
                        pygame.draw.rect(screen, color, temp_rect)
                        pygame.draw.rect(screen, BLACK, temp_rect, 2)
            else:
                # Dibujo normal para niveles no lineales
                obstacle.draw(screen)
        
        # Dibujar checkpoints
        for checkpoint in self.checkpoints:
            # Ajustar posición según desplazamiento
            if self.linear:
                checkpoint_x = checkpoint.x - offset_x
                checkpoint_y = checkpoint.y - offset_y
                
                # Solo dibujar si es visible
                if -checkpoint.radius*2 <= checkpoint_x <= WIDTH + checkpoint.radius*2 and \
                   -checkpoint.radius*2 <= checkpoint_y <= HEIGHT + checkpoint.radius*2:
                    
                    if checkpoint.active and checkpoint.active_image:
                        screen.blit(checkpoint.active_image, 
                                   (checkpoint_x - checkpoint.active_image.get_width()//2, 
                                    checkpoint_y - checkpoint.active_image.get_height()//2))
                    elif not checkpoint.active and checkpoint.inactive_image:
                        screen.blit(checkpoint.inactive_image, 
                                   (checkpoint_x - checkpoint.inactive_image.get_width()//2, 
                                    checkpoint_y - checkpoint.inactive_image.get_height()//2))
                    else:
                        # Dibujo fallback
                        color = GREEN if checkpoint.active else GRAY
                        pygame.draw.circle(screen, color, (checkpoint_x, checkpoint_y), checkpoint.radius)
                        pygame.draw.circle(screen, BLACK, (checkpoint_x, checkpoint_y), checkpoint.radius, 2)
            else:
                # Dibujo normal para niveles no lineales
                checkpoint.draw(screen)
    
    def get_adjusted_player_position(self, x, y):
        """Ajustar la posición del jugador para niveles lineales"""
        if not self.linear:
            return x, y
            
        # En niveles lineales, el jugador avanza horizontalmente
        # Si se acerca al borde derecho, desplazar el nivel
        if x > WIDTH * 0.7:
            # Calcular cuánto desplazar
            move_amount = min(x - WIDTH * 0.7, self.scroll_speed * 5)
            
            # Ajustar el offset del nivel
            self.scroll_offset_x += move_amount
            
            # Limitar el offset al ancho máximo del nivel
            self.scroll_offset_x = min(self.scroll_offset_x, self.scroll_width - WIDTH)
            
            # Ajustar la posición del jugador
            x -= move_amount
        
        # Si se acerca al borde izquierdo, permitir desplazamiento hacia atrás
        elif x < WIDTH * 0.3 and self.scroll_offset_x > 0:
            # Calcular cuánto desplazar
            move_amount = min(WIDTH * 0.3 - x, self.scroll_speed * 5)
            
            # Ajustar el offset del nivel
            self.scroll_offset_x -= move_amount
            
            # Limitar el offset a 0 como mínimo
            self.scroll_offset_x = max(0, self.scroll_offset_x)
            
            # Ajustar la posición del jugador
            x += move_amount
        
        return x, y
    
    def get_obstacle_collisions(self, player_rect):
        """Verificar colisiones con obstáculos y ajustar posición"""
        collisions = []
        
        for obstacle in self.obstacles:
            # Crear un rect ajustado a la posición actual para niveles lineales
            if self.linear:
                adjusted_rect = pygame.Rect(
                    obstacle.x - self.scroll_offset_x,
                    obstacle.y - self.scroll_offset_y,
                    obstacle.width,
                    obstacle.height
                )
            else:
                adjusted_rect = obstacle.rect
                
            if player_rect.colliderect(adjusted_rect):
                collisions.append(obstacle)
                
        return collisions
    
    def get_level_bounds(self):
        """Obtener los límites del nivel"""
        if self.linear:
            return (0, 0, self.scroll_width, HEIGHT)
        else:
            return (0, 0, WIDTH, HEIGHT)
    
    def get_exit_point(self):
        """Obtener punto de salida ajustado al desplazamiento"""
        if self.linear:
            return (self.exit_point[0] - self.scroll_offset_x, 
                   self.exit_point[1] - self.scroll_offset_y)
        else:
            return self.exit_point
    
    def get_boss_spawn_point(self):
        """Obtener punto de aparición para el jefe"""
        if self.linear:
            # En niveles lineales, el jefe aparece al final
            return (self.scroll_width - 200 - self.scroll_offset_x, 
                   HEIGHT // 2)
        else:
            # En niveles normales, en el centro
            return (WIDTH // 2, HEIGHT // 2)
    
    def get_spawn_point(self):
        """Obtener un punto aleatorio para generar enemigos"""
        if not self.spawn_points:
            # Puntos por defecto si no hay definidos
            default_points = [
                (50, 50),
                (WIDTH - 100, 50),
                (WIDTH - 100, HEIGHT - 100),
                (50, HEIGHT - 100)
            ]
            point = random.choice(default_points)
        else:
            point = random.choice(self.spawn_points)
            
        # Ajustar según desplazamiento para niveles lineales
        if self.linear:
            return (point[0] - self.scroll_offset_x, 
                   point[1] - self.scroll_offset_y)
        else:
            return point
        
    def is_completed(self):
        """Verificar si el nivel está completado"""
        return self.completed
    
    def mark_completed(self):
        """Marcar nivel como completado"""
        self.completed = True
        
        # Guardar progreso si hay sistema de guardado
        self.save_progress()
        
    def save_progress(self):
        """Guardar progreso del nivel completado"""
        try:
            # Cargar progreso existente
            progress_file = "assets/save/progress.json"
            progress_data = {}
            
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as file:
                    progress_data = json.load(file)
            
            # Actualizar nivel completado
            completed_levels = progress_data.get("completed_levels", [])
            if self.level_number not in completed_levels:
                completed_levels.append(self.level_number)
                
            progress_data["completed_levels"] = completed_levels
            progress_data["last_level"] = self.level_number + 1
            
            # Guardar progreso actualizado
            os.makedirs(os.path.dirname(progress_file), exist_ok=True)
            with open(progress_file, 'w') as file:
                json.dump(progress_data, file)
                
            print(f"Progreso guardado. Nivel {self.level_number} completado.")
            
        except Exception as e:
            print(f"Error al guardar progreso: {e}")

# Clase para gestionar todos los niveles
class LevelManager:
    def __init__(self):
        self.current_level = None
        self.current_level_number = 1
        self.total_levels = 20  # Número máximo de niveles
        self.load_progress()
        
    def load_progress(self):
        """Cargar progreso del jugador"""
        try:
            progress_file = "assets/save/progress.json"
            
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as file:
                    progress_data = json.load(file)
                    
                # Obtener último nivel jugado
                self.current_level_number = progress_data.get("last_level", 1)
                
                print(f"Progreso cargado. Nivel actual: {self.current_level_number}")
            else:
                self.current_level_number = 1
                print("No se encontró archivo de progreso. Iniciando desde nivel 1.")
                
        except Exception as e:
            print(f"Error al cargar progreso: {e}")
            self.current_level_number = 1
    
    def load_level(self, level_number=None):
        """Cargar un nivel específico o el actual"""
        if level_number is None:
            level_number = self.current_level_number
            
        # Asegurar que el nivel está en rango
        level_number = max(1, min(level_number, self.total_levels))
        
        # Actualizar nivel actual
        self.current_level_number = level_number
        
        # Crear nuevo nivel
        self.current_level = Level(level_number)
        
        return self.current_level
    
    def next_level(self):
        """Avanzar al siguiente nivel"""
        if self.current_level_number < self.total_levels:
            self.current_level_number += 1
            return self.load_level()
        else:
            # Hemos completado todos los niveles
            print("¡Felicidades! Has completado todos los niveles.")
            return None
    
    def restart_level(self):
        """Reiniciar el nivel actual"""
        return self.load_level(self.current_level_number)
    
    def show_level_intro(self, screen):
        """Mostrar introducción del nivel actual"""
        if self.current_level:
            # Mostrar cutscene si es nivel de jefe o múltiplo de 5
            if self.current_level_number % 5 == 0:
                show_cutscene(screen, self.current_level_number)
                
            # Mostrar tutorial para primeros niveles
            if self.current_level_number <= 3:
                show_tutorial(screen, self.current_level_number)

# Ejemplo de uso
if __name__ == "__main__":
    # Prueba simple
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Prueba de Niveles")
    
    manager = LevelManager()
    level = manager.load_level(1)
    
    # Coordenadas de prueba para el jugador
    player_x, player_y = WIDTH // 2, HEIGHT // 2
    player_rect = pygame.Rect(player_x - 20, player_y - 20, 40, 40)
    
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Cambiar nivel con las teclas numéricas
            if event.type == pygame.KEYDOWN:
                if event.key >= pygame.K_1 and event.key <= pygame.K_9:
                    level_num = event.key - pygame.K_0
                    level = manager.load_level(level_num)
        
        # Mover jugador con teclas de flecha
        keys = pygame.key.get_pressed()
        move_speed = 5
        
        if keys[pygame.K_LEFT]:
            player_x -= move_speed
        if keys[pygame.K_RIGHT]:
            player_x += move_speed
        if keys[pygame.K_UP]:
            player_y -= move_speed
        if keys[pygame.K_DOWN]:
            player_y += move_speed
            
        # Ajustar posición en niveles lineales
        player_x, player_y = level.get_adjusted_player_position(player_x, player_y)
        
        # Actualizar rectángulo del jugador
        player_rect.center = (player_x, player_y)
        
        # Verificar colisiones
        collisions = level.get_obstacle_collisions(player_rect)
        
        # Actualizar nivel
        level.update(player_x, player_y)
        
        # Dibujar
        level.draw(screen, level.scroll_offset_x, level.scroll_offset_y)
        
        # Dibujar jugador (círculo simple para prueba)
        pygame.draw.circle(screen, (0, 255, 0), (player_x, player_y), 20)
        
        # Información de debug
        font = pygame.font.SysFont('Arial', 24)
        level_text = font.render(f"Nivel: {level.name}", True, WHITE)
        scroll_text = font.render(f"Scroll: {level.scroll_offset_x:.1f}, {level.scroll_offset_y:.1f}", True, WHITE)
        
        screen.blit(level_text, (10, 10))
        screen.blit(scroll_text, (10, 40))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()