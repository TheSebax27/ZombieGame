"""
Clase Player para Killer Potato
Define la estructura del jugador con todos sus métodos
"""

import pygame
import math
import random
from pygame.locals import *

# Configuración de pantalla (tomar de config o usar valores por defecto)
try:
    from config.settings import WIDTH, HEIGHT
except ImportError:
    WIDTH, HEIGHT = 800, 600

# Colores (definir aquí para asegurar que existan)
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

# Clase Jugador (Killer Potato)
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
            },
            {
                "name": "Cuchara", 
                "damage": 75, 
                "ammo": 20, 
                "max_ammo": 20, 
                "reload_time": 40, 
                "reload_counter": 0, 
                "fire_rate": 50, 
                "fire_counter": 0,
                "image_right": load_image("assets/images/items/spoon_right.png", (50, 20)),
                "image_left": load_image("assets/images/items/spoon_left.png", (50, 20)),
                "hud_image": load_image("assets/images/ui/spoon_hud.png", (80, 40))
            },
            {
                "name": "Cuchillo", 
                "damage": 40, 
                "ammo": 30, 
                "max_ammo": 30, 
                "reload_time": 30, 
                "reload_counter": 0, 
                "fire_rate": 10, 
                "fire_counter": 0,
                "image_right": load_image("assets/images/items/knife_right.png", (60, 20)),
                "image_left": load_image("assets/images/items/knife_left.png", (60, 20)),
                "hud_image": load_image("assets/images/ui/knife_hud.png", (80, 40))
            },
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
        # Determinar qué imagen del jugador usar según la dirección
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.facing_right = mouse_x >= self.x
        player_image = self.image_right if self.facing_right else self.image_left
        
        # Dibujar jugador
        screen.blit(player_image, (self.x - player_image.get_width() // 2, self.y - player_image.get_height() // 2))
        
        # Dibujar arma actual
        weapon = self.weapons[self.current_weapon]
        weapon_img = weapon["image_right"] if self.facing_right else weapon["image_left"]
        
        # Calcular ángulo de rotación basado en la posición del ratón
        angle = math.degrees(math.atan2(mouse_y - self.y, mouse_x - self.x))
        if not self.facing_right:
            angle += 180
        rotated_weapon = pygame.transform.rotate(weapon_img, -angle)
        
        # Posición del arma (desplazada desde el centro del jugador)
        offset_x = math.cos(math.radians(angle)) * 20
        offset_y = math.sin(math.radians(angle)) * 20
        weapon_pos = (self.x + offset_x - rotated_weapon.get_width() // 2, 
                     self.y + offset_y - rotated_weapon.get_height() // 2)
        
        screen.blit(rotated_weapon, weapon_pos)
    
    def move(self, dx, dy, obstacles=None, level_bounds=None):
        # Calcular nueva posición
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        # Verificar límites del nivel si se proporcionan
        if level_bounds:
            min_x, min_y, max_x, max_y = level_bounds
            new_x = max(min_x + self.radius, min(new_x, max_x - self.radius))
            new_y = max(min_y + self.radius, min(new_y, max_y - self.radius))
        else:
            # Limitar movimiento dentro de la pantalla
            new_x = max(self.radius, min(new_x, WIDTH - self.radius))
            new_y = max(self.radius, min(new_y, HEIGHT - self.radius))
        
        # Verificar colisiones con obstáculos
        if obstacles:
            # Verificar si la nueva posición colisiona con algún obstáculo
            new_rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
            new_rect.center = (new_x, new_y)
            
            for obstacle in obstacles:
                if new_rect.colliderect(obstacle.rect):
                    # Ajustar posición para evitar la colisión
                    # Intentar mover solo en X si es posible
                    x_only_rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
                    x_only_rect.center = (new_x, self.y)
                    
                    if not x_only_rect.colliderect(obstacle.rect):
                        new_y = self.y
                    else:
                        # Intentar mover solo en Y si es posible
                        y_only_rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
                        y_only_rect.center = (self.x, new_y)
                        
                        if not y_only_rect.colliderect(obstacle.rect):
                            new_x = self.x
                        else:
                            # Si no se puede mover en ninguna dirección, mantener posición actual
                            new_x = self.x
                            new_y = self.y
        
        # Actualizar posición
        self.x = new_x
        self.y = new_y
        self.update_rect()
    
    def attack(self):
        if self.is_reloading or not self.can_shoot:
            return None, None
        
        weapon = self.weapons[self.current_weapon]
        if weapon["ammo"] <= 0:
            self.reload()
            return None, None
        
        weapon["ammo"] -= 1
        self.can_shoot = False
        weapon["fire_counter"] = weapon["fire_rate"]
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
        
        # Posición para el efecto de ataque (delante del arma)
        effect_distance = 30
        effect_x = self.x + math.cos(angle) * effect_distance
        effect_y = self.y + math.sin(angle) * effect_distance
        
        # Crear efectos
        try:
            from weapons import Projectile
            projectile = Projectile(self.x, self.y, angle, weapon["damage"] * self.damage_multiplier)
        except ImportError:
            # Clase Projectile básica si no se puede importar
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
                    
            projectile = Projectile(self.x, self.y, angle, weapon["damage"] * self.damage_multiplier)
        
        # Clase AttackEffect para efectos visuales
        class AttackEffect:
            def __init__(self, x, y, angle):
                self.x = x
                self.y = y
                self.angle = angle
                self.lifetime = 5  # Duración del efecto en frames
                try:
                    self.image = load_image("assets/images/items/attack_effect.png", (30, 15))
                    self.rotated_image = pygame.transform.rotate(self.image, -math.degrees(angle))
                    self.rect = self.rotated_image.get_rect(center=(x, y))
                except:
                    self.image = None
                    self.rotated_image = None
                    self.rect = pygame.Rect(x - 15, y - 7, 30, 15)
            
            def update(self):
                self.lifetime -= 1
            
            def draw(self, screen):
                if self.rotated_image:
                    screen.blit(self.rotated_image, self.rect.topleft)
                else:
                    # Dibujo de respaldo
                    pygame.draw.line(screen, (255, 200, 0), 
                                    (self.x, self.y),
                                    (self.x + math.cos(self.angle) * 30, self.y + math.sin(self.angle) * 30),
                                    3)
            
            def is_finished(self):
                return self.lifetime <= 0
                
        attack_effect = AttackEffect(effect_x, effect_y, angle)
        
        # Reproducir sonido de ataque
        try:
            weapon_sound_path = f"assets/sounds/sfx/{weapon['name'].lower()}_attack.wav"
            attack_sound = pygame.mixer.Sound(weapon_sound_path)
            attack_sound.play()
        except:
            pass
            
        return projectile, attack_effect
    
    def reload(self):
        weapon = self.weapons[self.current_weapon]
        if weapon["ammo"] == weapon["max_ammo"] or self.is_reloading:
            return
        
        self.is_reloading = True
        weapon["reload_counter"] = weapon["reload_time"]
        
        # Reproducir sonido de recarga
        try:
            reload_sound = pygame.mixer.Sound("assets/sounds/sfx/reload.wav")
            reload_sound.play()
        except:
            pass
    
    def update(self):
        weapon = self.weapons[self.current_weapon]
        
        # Actualizar recarga
        if self.is_reloading:
            weapon["reload_counter"] -= 1
            if weapon["reload_counter"] <= 0:
                weapon["ammo"] = weapon["max_ammo"]
                self.is_reloading = False
        
        # Actualizar cadencia de disparo
        if not self.can_shoot:
            weapon["fire_counter"] -= 1
            if weapon["fire_counter"] <= 0:
                self.can_shoot = True
    
    def switch_weapon(self, direction):
        self.current_weapon = (self.current_weapon + direction) % len(self.weapons)
        self.is_reloading = False
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        
        # Reproducir sonido de daño
        try:
            hurt_sound = pygame.mixer.Sound("assets/sounds/sfx/player_hurt.wav")
            hurt_sound.play()
        except:
            pass
    
    def draw_hud(self, screen, enemies_to_spawn=0, enemies_count=0):
        # Barra de vida
        screen.blit(self.health_bar, (20, 20))
        health_text = pygame.font.SysFont('Arial', 24).render(f"SALUD", True, WHITE)
        screen.blit(health_text, (30, 25))
        
        # Dibujar barra de salud
        health_width = 150 * (self.health / self.max_health)
        health_rect = pygame.Rect(70, 50, health_width, 25)
        
        # Color según porcentaje de vida
        if self.health > self.max_health * 0.7:
            health_color = GREEN
        elif self.health > self.max_health * 0.3:
            health_color = (255, 255, 0)  # Amarillo
        else:
            health_color = RED
            
        pygame.draw.rect(screen, health_color, health_rect)
        
        # Información de arma y munición
        weapon = self.weapons[self.current_weapon]
        screen.blit(self.ammo_bar, (20, 100))
        
        # Dibujar icono del arma actual en el HUD
        screen.blit(weapon["hud_image"], (30, 110))
        
        # Mostrar munición
        ammo_text = pygame.font.SysFont('Arial', 24).render(f"{weapon['ammo']}/{weapon['max_ammo']}", True, WHITE)
        screen.blit(ammo_text, (150, 125))
        
        if self.is_reloading:
            reload_text = pygame.font.SysFont('Arial', 24).render("RECARGANDO", True, WHITE)
            screen.blit(reload_text, (150, 100))
        
        # Puntuación
        screen.blit(self.score_display, (WIDTH - 170, 20))
        score_text = pygame.font.SysFont('Arial', 24).render(f"{self.score}", True, DARK_RED)
        screen.blit(score_text, (WIDTH - 110, 35))
        
        # Información de nivel
        level_text = pygame.font.SysFont('Arial', 24).render(f"NIVEL: {self.level}", True, WHITE)
        screen.blit(level_text, (WIDTH - 150, 80))
        
        # Mostrar contador de enemigos
        if enemies_count > 0 or enemies_to_spawn > 0:
            enemies_left = enemies_to_spawn + enemies_count
            progress = int(100 - (enemies_left / (enemies_left + 1) * 100))
            enemies_text = pygame.font.SysFont('Arial', 24).render(f"ENEMIGOS: {enemies_left} - PROGRESO: {progress}%", True, WHITE)
            screen.blit(enemies_text, (WIDTH - 350, 110))