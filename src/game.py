import pygame
import sys
import random
import math
import os
from pygame.locals import *

# Inicializar Pygame
pygame.init()
pygame.font.init()

# Configuración de pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Killer Potato: La Venganza de la Papa")

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

# Clase para diálogos y textos narrativos
class DialogBox:
    def __init__(self):
        self.visible = False
        self.text = ""
        self.speaker = ""
        self.position = "bottom"  # bottom, top, left, right
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
        
    def set_dialog(self, text, speaker="", portrait=None, position="bottom", next_dialog=None):
        self.text = text
        self.speaker = speaker
        self.position = position
        self.display_index = 0
        self.display_counter = 0
        self.complete = False
        self.next_dialog = next_dialog
        
        if portrait:
            try:
                self.portrait = load_image(portrait, (100, 100))
            except:
                self.portrait = None
        
        # Ajustar posición según el parámetro
        if position == "bottom":
            self.x = 50
            self.y = HEIGHT - 200
            self.width = WIDTH - 100
        elif position == "top":
            self.x = 50
            self.y = 50
            self.width = WIDTH - 100
        elif position == "left":
            self.x = 50
            self.y = (HEIGHT - self.height) // 2
            self.width = WIDTH // 2 - 75
        elif position == "right":
            self.x = WIDTH // 2 + 25
            self.y = (HEIGHT - self.height) // 2
            self.width = WIDTH // 2 - 75
        
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

# Clase Jugador (Killer Potato)
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 20
        self.speed = 5
        self.health = 100
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
    
    def move(self, dx, dy):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        # Limitar movimiento dentro de la pantalla
        if 0 + self.radius <= new_x <= WIDTH - self.radius:
            self.x = new_x
        if 0 + self.radius <= new_y <= HEIGHT - self.radius:
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
        projectile = Projectile(self.x, self.y, angle, weapon["damage"])
        attack_effect = AttackEffect(effect_x, effect_y, angle)
        
        return projectile, attack_effect
    
    def reload(self):
        weapon = self.weapons[self.current_weapon]
        if weapon["ammo"] == weapon["max_ammo"] or self.is_reloading:
            return
        
        self.is_reloading = True
        weapon["reload_counter"] = weapon["reload_time"]
    
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
    
    def draw_hud(self, screen):
        # Barra de vida
        screen.blit(self.health_bar, (20, 20))
        health_text = font.render(f"SALUD", True, WHITE)
        screen.blit(health_text, (30, 25))
        
        # Dibujar barra de salud
        health_width = 150 * (self.health / 100)
        health_rect = pygame.Rect(70, 50, health_width, 25)
        pygame.draw.rect(screen, DARK_RED, health_rect)
        
        # Información de arma y munición
        weapon = self.weapons[self.current_weapon]
        screen.blit(self.ammo_bar, (20, 100))
        
        # Dibujar icono del arma actual en el HUD
        screen.blit(weapon["hud_image"], (30, 110))
        
        # Mostrar munición
        ammo_text = font.render(f"{weapon['ammo']}/{weapon['max_ammo']}", True, WHITE)
        screen.blit(ammo_text, (150, 125))
        
        if self.is_reloading:
            reload_text = font.render("RECARGANDO", True, WHITE)
            screen.blit(reload_text, (150, 100))
        
        # Puntuación
        screen.blit(self.score_display, (WIDTH - 170, 20))
        score_text = font.render(f"{self.score}", True, DARK_RED)
        screen.blit(score_text, (WIDTH - 110, 35))
        
        # Información de nivel
        level_text = font.render(f"NIVEL: {self.level}", True, WHITE)
        screen.blit(level_text, (WIDTH - 150, 80))
        
        enemies_left_text = font.render(f"ENEMIGOS: {len(enemies) + enemies_to_spawn}", True, WHITE)
        screen.blit(enemies_left_text, (WIDTH - 200, 110))

# Clase Proyectil
class Projectile:
    def __init__(self, x, y, angle, damage):
        self.x = x
        self.y = y
        self.speed = 12
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.radius = 5
        self.damage = damage
        
        # Cargar imagen de proyectil
        self.image = load_image("assets/images/items/projectile.png", (12, 6))
        self.angle = math.degrees(angle)
        self.rotated_image = pygame.transform.rotate(self.image, -self.angle)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.center = (self.x, self.y)
    
    def draw(self, screen):
        screen.blit(self.rotated_image, self.rect.topleft)
        
        # Efecto de estela (opcional)
        trail_length = 3
        for i in range(1, trail_length + 1):
            alpha = 200 - i * 60  # La estela se desvanece
            if alpha > 0:
                trail_pos = (int(self.x - self.dx * i * 0.5), int(self.y - self.dy * i * 0.5))
                pygame.draw.circle(screen, (255, 200, 0, alpha), trail_pos, self.radius - i)
    
    def is_offscreen(self):
        return (self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT)

# Clase Enemigo
class Enemy:
    def __init__(self, level, enemy_type="human"):
        self.radius = 20
        self.speed = 1 + level * 0.2  # Los enemigos se vuelven más rápidos con cada nivel
        self.health = 50 + level * 10  # Los enemigos se vuelven más resistentes con cada nivel
        self.max_health = 50 + level * 10  # Salud máxima para calcular porcentaje
        self.damage = 5 + level  # Los enemigos hacen más daño con cada nivel
        self.attack_cooldown = 50
        self.attack_counter = 0
        self.facing_right = True
        self.hit_effect = 0  # Contador para efecto de daño
        self.enemy_type = enemy_type
        
        # Cargar imágenes del enemigo según tipo
        if enemy_type == "human":
            self.image_right = load_image("assets/images/characters/human_right.png", (50, 50))
            self.image_left = load_image("assets/images/characters/human_left.png", (50, 50))
        elif enemy_type == "robot":
            self.image_right = load_image("assets/images/characters/robot_right.png", (60, 60))
            self.image_left = load_image("assets/images/characters/robot_left.png", (60, 60))
            self.health += 30  # Robots más resistentes
            self.speed -= 0.3  # Robots más lentos
        elif enemy_type == "chef":
            self.image_right = load_image("assets/images/characters/chef_right.png", (55, 55))
            self.image_left = load_image("assets/images/characters/chef_left.png", (55, 55))
            self.damage += 10  # Chef hace más daño
        
        # Posición inicial (fuera de la pantalla)
        side = random.randint(0, 3)
        if side == 0:  # Superior
            self.x = random.randint(0, WIDTH)
            self.y = -self.radius
        elif side == 1:  # Derecha
            self.x = WIDTH + self.radius
            self.y = random.randint(0, HEIGHT)
        elif side == 2:  # Inferior
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + self.radius
        else:  # Izquierda
            self.x = -self.radius
            self.y = random.randint(0, HEIGHT)
            
        # Obtener rectángulo para colisiones
        self.rect = self.image_right.get_rect()
        self.update_rect()
        
    def update_rect(self):
        self.rect.center = (self.x, self.y)
    
    def update(self, player_x, player_y):
        # Moverse hacia el jugador
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            dx /= dist
            dy /= dist
        
        self.x += dx * self.speed
        self.y += dy * self.speed
        
        # Actualizar dirección de vista
        self.facing_right = dx > 0
        
        # Actualizar rectángulo
        self.update_rect()
        
        # Actualizar contador de ataque
        if self.attack_counter > 0:
            self.attack_counter -= 1
            
        # Actualizar efecto de daño
        if self.hit_effect > 0:
            self.hit_effect -= 1
    
    def draw(self, screen):
        # Seleccionar imagen según dirección
        enemy_image = self.image_right if self.facing_right else self.image_left
        
        # Aplicar efecto de daño (parpadeo rojo)
        if self.hit_effect > 0:
            # Crear una copia de la imagen para modificarla
            damaged_image = enemy_image.copy()
            damaged_image.fill((255, 0, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(damaged_image, (self.x - enemy_image.get_width() // 2, self.y - enemy_image.get_height() // 2))
        else:
            # Dibujar enemigo normal
            screen.blit(enemy_image, (self.x - enemy_image.get_width() // 2, self.y - enemy_image.get_height() // 2))
        
        # Barra de vida (siempre visible)
        bar_width = 40
        health_percentage = max(0, self.health / self.max_health)
        bar_height = 5
        bar_y = self.y - self.radius - 10
        
        # Fondo de la barra (rojo)
        pygame.draw.rect(screen, RED, (self.x - bar_width//2, bar_y, bar_width, bar_height))
        # Parte de salud (verde)
        pygame.draw.rect(screen, GREEN, (self.x - bar_width//2, bar_y, bar_width * health_percentage, bar_height))
        # Borde de la barra
        pygame.draw.rect(screen, BLACK, (self.x - bar_width//2, bar_y, bar_width, bar_height), 1)
    
    def take_damage(self, damage):
        self.health -= damage
        self.hit_effect = 5  # Duración del efecto de daño en frames
    
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
        if pickup_type == "health":
            self.image = load_image("assets/images/items/health_pickup.png", (30, 30))
        elif pickup_type == "ammo":
            self.image = load_image("assets/images/items/ammo_pickup.png", (30, 30))
        elif pickup_type == "speed":
            self.image = load_image("assets/images/items/speed_pickup.png", (30, 30))
        else:
            self.image = load_image("assets/images/items/generic_pickup.png", (30, 30))
            
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        # Efecto de oscilación vertical
        self.bob_offset += self.bob_speed * self.bob_direction
        if abs(self.bob_offset) > 5:
            self.bob_direction *= -1
            
        # Efecto de rotación
        self.rotation = (self.rotation + self.rotation_speed) % 360
        
        # Actualizar rectángulo
        self.rect.center = (self.x, self.y + self.bob_offset)
        
        # Reducir tiempo de vida
        self.lifetime -= 1
    
    def draw(self, screen):
        # Rotar imagen
        rotated_image = pygame.transform.rotate(self.image, self.rotation)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        
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
    
    def is_collected(self, player):
        # Comprobar si el jugador toca el objeto
        distance = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
        return distance < self.radius + player.radius
    
    def is_expired(self):
        return self.lifetime <= 0
        
    def apply_effect(self, player):
        # Aplicar efecto según tipo
        if self.type == "health":
            player.health = min(100, player.health + 25)
            return "Salud +25"
        elif self.type == "ammo":
            weapon = player.weapons[player.current_weapon]
            weapon["ammo"] = weapon["max_ammo"]
            return f"{weapon['name']} recargada"
        elif self.type == "speed":
            player.speed += 0.5
            return "Velocidad +0.5"
        return "Objeto recogido"

# Función para dibujar la pantalla de pausa
def draw_pause_screen(screen):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))  # Semi-transparente negro
    screen.blit(overlay, (0, 0))
    
    pause_text = big_font.render("JUEGO PAUSADO", True, WHITE)
    continue_text = font.render("Presiona P para continuar", True, WHITE)
    
    screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 20))

# Función principal del juego
def main():
    global enemies, enemies_to_spawn  # Para acceso desde métodos de clase
    
    clock = pygame.time.Clock()
    
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
    enemies_in_level = 5  # Inicial
    enemies_to_spawn = enemies_in_level
    spawn_cooldown = 60  # frames entre spawn de enemigos
    spawn_counter = 0
    
    level_complete = False
    level_timer = 180  # Pausa entre niveles (3 segundos a 60 FPS)
    
    game_over = False
    paused = False
    
    # Diálogo inicial
    dialog = DialogBox()
    show_intro_dialog = True
    
    if show_intro_dialog:
        dialog.set_dialog(
            "¡Por fin he escapado! Ahora es hora de vengarme de los humanos que nos convirtieron en... esto.", 
            "Killer Potato", 
            "assets/images/characters/killer_potato_dialog.png",
            next_dialog=("Veo que hay guardias de seguridad adelante. ¡Tendré que abrirme paso a través de ellos!", 
                         "Killer Potato", 
                         "assets/images/characters/killer_potato_dialog.png")
        )
    
    running = True
    while running:
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
                    enemies_in_level = 5
                    enemies_to_spawn = enemies_in_level
                    spawn_cooldown = 60
                    spawn_counter = 0
                    level_complete = False
                    game_over = False
            
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
            screen.blit(background, (0, 0))
            
            # Dibujar jugador y enemigos
            player.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
                
            # Dibujar HUD
            player.draw_hud(screen)
            
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
            # Pantalla de Game Over
            screen.fill(BLACK)
            game_over_text = big_font.render("GAME OVER", True, RED)
            score_text = font.render(f"Puntuación: {player.score}", True, WHITE)
            level_text = font.render(f"Nivel alcanzado: {level}", True, WHITE)
            restart_text = font.render("Presiona ENTER para reiniciar", True, WHITE)
            
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 60))
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
            screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 + 30))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 80))
            
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
        
        # Actualizar jugador
        player.move(dx, dy)
        player.update()
        
        # Actualizar efectos de ataque
        for effect in attack_effects[:]:
            effect.update()
            if effect.is_finished():
                attack_effects.remove(effect)
        
        # Actualizar proyectiles
        for projectile in projectiles[:]:
            projectile.update()
            if projectile.is_offscreen():
                projectiles.remove(projectile)
        
        # Actualizar pickups
        for pickup in pickups[:]:
            pickup.update()
            
            # Comprobar si el jugador recoge el pickup
            if pickup.is_collected(player):
                message = pickup.apply_effect(player)
                pickups.remove(pickup)
            elif pickup.is_expired():
                pickups.remove(pickup)
        
        # Actualizar enemigos y comprobar colisiones
        for enemy in enemies[:]:
            enemy.update(player.x, player.y)
            
            # Comprobar colisión con jugador
            if player.rect.colliderect(enemy.rect):
                enemy.attack(player)
            
            # Comprobar colisión con proyectiles
            for projectile in projectiles[:]:
                if enemy.rect.collidepoint(projectile.x, projectile.y):
                    enemy.take_damage(projectile.damage)
                    projectiles.remove(projectile)
                    break
            
            # Eliminar enemigos muertos
            if enemy.is_dead():
                # Posibilidad de soltar pickup
                if random.random() < 0.3:  # 30% de probabilidad
                    pickup_type = random.choice(["health", "ammo", "speed"])
                    pickups.append(Pickup(enemy.x, enemy.y, pickup_type))
                
                player.score += 10
                enemies.remove(enemy)
        
        # Generar enemigos
        if not level_complete and enemies_to_spawn > 0:
            if spawn_counter <= 0:
                # Elegir tipo de enemigo basado en nivel
                if level >= 3 and random.random() < 0.3:
                    enemy_type = "robot"
                elif level >= 5 and random.random() < 0.2:
                    enemy_type = "chef"
                else:
                    enemy_type = "human"
                
                enemies.append(Enemy(level, enemy_type))
                enemies_to_spawn -= 1
                spawn_counter = spawn_cooldown
            else:
                spawn_counter -= 1
        
        # Comprobar fin de nivel
        if not level_complete and enemies_to_spawn <= 0 and len(enemies) == 0:
            level_complete = True
            level_timer = 180  # Reiniciar temporizador entre niveles
        
        # Actualizar temporizador entre niveles
        if level_complete:
            level_timer -= 1
        
        # Comprobar si el jugador ha muerto
        if player.health <= 0:
            game_over = True
        
        # Dibujar todo
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
        player.draw_hud(screen)
        
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