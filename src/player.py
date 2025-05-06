"""
Módulo de jugador para Killer Potato
Contiene la clase del jugador y sus funcionalidades
"""

import pygame
import math
import random
from pygame.locals import *

# Inicializar pygame si no está inicializado
if not pygame.get_init():
    pygame.init()

# Configuración de pantalla (tomar de config o usar valores por defecto)
try:
    from config.settings import WIDTH, HEIGHT
except ImportError:
    WIDTH, HEIGHT = 800, 600

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
        self.score = 0
        self.level = 1
        self.current_weapon = 0
        self.facing_right = True
        
        # Stats del jugador
        self.attack_power = 1.0  # Multiplicador de daño
        self.defense = 1.0  # Reducción de daño recibido
        self.critical_chance = 0.05  # 5% probabilidad de crítico
        self.pickup_range = 50  # Rango para recoger ítems
        
        # Sistema de experiencia
        self.experience = 0
        self.level_threshold = 100  # XP necesaria para subir de nivel
        self.skill_points = 0  # Puntos para mejorar habilidades
        
        # Efectos de estado
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.speed_boost = False
        self.speed_boost_timer = 0
        self.damage_boost = False
        self.damage_boost_timer = 0
        
        # Cargar imágenes del jugador
        self.image_right = load_image("assets/images/characters/killer_potato_right.png", (50, 50))
        self.image_left = load_image("assets/images/characters/killer_potato_left.png", (50, 50))
        self.image_hurt_right = load_image("assets/images/characters/killer_potato_hurt_right.png", (50, 50))
        self.image_hurt_left = load_image("assets/images/characters/killer_potato_hurt_left.png", (50, 50))
        
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
                "hud_image": load_image("assets/images/ui/fork_hud.png", (80, 40)),
                "sound": "assets/sounds/sfx/fork_attack.wav"
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
                "hud_image": load_image("assets/images/ui/spoon_hud.png", (80, 40)),
                "sound": "assets/sounds/sfx/spoon_attack.wav"
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
                "hud_image": load_image("assets/images/ui/knife_hud.png", (80, 40)),
                "sound": "assets/sounds/sfx/knife_attack.wav"
            },
        ]
        self.is_reloading = False
        self.can_shoot = True
        
        # Cargar HUD
        self.health_bar = load_image("assets/images/ui/health_bar.png", (250, 70))
        self.ammo_bar = load_image("assets/images/ui/ammo_bar.png", (250, 70))
        self.score_display = load_image("assets/images/ui/score_display.png", (150, 50))
        self.xp_bar = load_image("assets/images/ui/xp_bar.png", (250, 20))
        
        # Cargar sonidos
        self.sounds = {
            "hurt": None,
            "death": None,
            "level_up": None,
            "reload": None,
            "no_ammo": None,
            "pickup": None
        }
        
        try:
            self.sounds["hurt"] = pygame.mixer.Sound("assets/sounds/sfx/player_hurt.wav")
            self.sounds["death"] = pygame.mixer.Sound("assets/sounds/sfx/player_death.wav")
            self.sounds["level_up"] = pygame.mixer.Sound("assets/sounds/sfx/level_up.wav")
            self.sounds["reload"] = pygame.mixer.Sound("assets/sounds/sfx/reload.wav")
            self.sounds["no_ammo"] = pygame.mixer.Sound("assets/sounds/sfx/no_ammo.wav")
            self.sounds["pickup"] = pygame.mixer.Sound("assets/sounds/sfx/pickup.wav")
        except:
            print("No se pudieron cargar algunos sonidos")
        
        # Cargar efectos de partículas
        self.particles = []
        
        # Obtener rectángulo para colisiones
        self.rect = self.image_right.get_rect()
        self.update_rect()
        
        # Historial de movimiento para inercia/suavizado
        self.movement_history = [(self.x, self.y)] * 5
        self.trail_counter = 0

    def update_rect(self):
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        # Determinar qué imagen del jugador usar según la dirección y estado
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.facing_right = mouse_x >= self.x
        
        if self.invulnerable and pygame.time.get_ticks() % 200 < 100:
            # Parpadeo cuando es invulnerable
            return
            
        if self.health < self.max_health * 0.3:  # Menos del 30% de salud
            player_image = self.image_hurt_right if self.facing_right else self.image_hurt_left
        else:
            player_image = self.image_right if self.facing_right else self.image_left
        
        # Dibujar rastro/estela del jugador si tiene mejoras de velocidad
        if self.speed_boost:
            self.trail_counter += 1
            if self.trail_counter % 3 == 0:  # Controlar frecuencia de la estela
                for i, pos in enumerate(self.movement_history):
                    alpha = 120 - i * 20  # Desvanecer con la distancia
                    if alpha > 0:
                        trail_size = self.radius - i * 3
                        if trail_size > 0:
                            trail_surface = pygame.Surface((trail_size*2, trail_size*2), pygame.SRCALPHA)
                            pygame.draw.circle(trail_surface, (0, 200, 255, alpha), (trail_size, trail_size), trail_size)
                            screen.blit(trail_surface, (pos[0] - trail_size, pos[1] - trail_size))
        
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
        
        # Efectos visuales para mejoras activas
        if self.damage_boost:
            # Aura roja para daño mejorado
            boost_radius = self.radius + 10
            boost_surface = pygame.Surface((boost_radius*2, boost_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(boost_surface, (255, 0, 0, 70), (boost_radius, boost_radius), boost_radius)
            screen.blit(boost_surface, (self.x - boost_radius, self.y - boost_radius))
        
        # Dibujar partículas
        for particle in self.particles[:]:
            particle["lifetime"] -= 1
            if particle["lifetime"] <= 0:
                self.particles.remove(particle)
                continue
                
            # Actualizar posición
            particle["x"] += particle["dx"]
            particle["y"] += particle["dy"]
            
            # Actualizar tamaño/opacidad según vida restante
            size = particle["size"] * (particle["lifetime"] / particle["max_lifetime"])
            alpha = 255 * (particle["lifetime"] / particle["max_lifetime"])
            
            # Dibujar
            particle_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, 
                              (particle["color"][0], particle["color"][1], particle["color"][2], int(alpha)), 
                              (size, size), size)
            screen.blit(particle_surface, (particle["x"] - size, particle["y"] - size))
    
    def move(self, dx, dy, obstacles=None):
        # Aplicar velocidad base
        speed = self.speed
        
        # Aplicar mejora de velocidad si está activa
        if self.speed_boost:
            speed *= 1.5
        
        # Calcular nueva posición
        new_x = self.x + dx * speed
        new_y = self.y + dy * speed
        
        # Actualizar historial de movimiento para la estela
        self.movement_history.pop(0)
        self.movement_history.append((self.x, self.y))
        
        # Verificar colisiones con obstáculos
        can_move_x = True
        can_move_y = True
        
        if obstacles:
            # Crear rects para probar movimiento en X e Y por separado
            test_rect_x = pygame.Rect(self.rect)
            test_rect_x.centerx = new_x
            
            test_rect_y = pygame.Rect(self.rect)
            test_rect_y.centery = new_y
            
            # Probar colisiones para cada eje
            for obstacle in obstacles:
                if test_rect_x.colliderect(obstacle.rect):
                    can_move_x = False
                if test_rect_y.colliderect(obstacle.rect):
                    can_move_y = False
        
        # Actualizar posición si es posible
        if can_move_x:
            self.x = new_x
        if can_move_y:
            self.y = new_y
            
        # Limitar movimiento dentro de la pantalla
        self.x = max(self.radius, min(self.x, WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, HEIGHT - self.radius))
            
        self.update_rect()
    
    def attack(self):
        if self.is_reloading or not self.can_shoot:
            return None, None
        
        weapon = self.weapons[self.current_weapon]
        if weapon["ammo"] <= 0:
            # Sin munición
            if self.sounds["no_ammo"]:
                self.sounds["no_ammo"].play()
            self.reload()
            return None, None
        
        weapon["ammo"] -= 1
        self.can_shoot = False
        weapon["fire_counter"] = weapon["fire_rate"]
        
        # Obtener posición del mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
        
        # Calcular daño (incluyendo mejoras y críticos)
        damage = weapon["damage"] * self.attack_power
        
        # Verificar golpe crítico
        critical = random.random() < self.critical_chance
        if critical:
            damage *= 2
            
        # Posición para el efecto de ataque (delante del arma)
        effect_distance = 30
        effect_x = self.x + math.cos(angle) * effect_distance
        effect_y = self.y + math.sin(angle) * effect_distance
        
        # Crear efecto
        attack_effect = {
            "x": effect_x,
            "y": effect_y,
            "angle": angle,
            "critical": critical
        }
        
        # Reproducir sonido de ataque
        try:
            attack_sound = pygame.mixer.Sound(weapon["sound"])
            attack_sound.play()
        except:
            pass
        
        # Importar Projectile desde weapons para evitar ciclos de importación
        try:
            from weapons import Projectile
            projectile = Projectile(self.x, self.y, angle, damage, "player", is_critical=critical)
            return projectile, attack_effect
        except ImportError:
            print("No se pudo importar la clase Projectile")
            return None, attack_effect
    
    def reload(self):
        weapon = self.weapons[self.current_weapon]
        if weapon["ammo"] == weapon["max_ammo"] or self.is_reloading:
            return
        
        self.is_reloading = True
        weapon["reload_counter"] = weapon["reload_time"]
        
        # Reproducir sonido de recarga
        if self.sounds["reload"]:
            self.sounds["reload"].play()
    
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
        
        # Actualizar temporizadores de efectos
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
                
        if self.speed_boost:
            self.speed_boost_timer -= 1
            if self.speed_boost_timer <= 0:
                self.speed_boost = False
                
        if self.damage_boost:
            self.damage_boost_timer -= 1
            if self.damage_boost_timer <= 0:
                self.damage_boost = False
                self.attack_power /= 1.5  # Eliminar bonus temporal
    
    def switch_weapon(self, direction):
        self.current_weapon = (self.current_weapon + direction) % len(self.weapons)
        self.is_reloading = False
    
    def take_damage(self, damage):
        # No recibir daño si es invulnerable
        if self.invulnerable:
            return False
            
        # Aplicar reducción por defensa
        actual_damage = damage / self.defense
        self.health -= actual_damage
        
        # Efecto visual
        self.add_damage_particles()
        
        # Reproducir sonido de daño
        if self.sounds["hurt"]:
            self.sounds["hurt"].play()
        
        # Activar invulnerabilidad temporal
        self.invulnerable = True
        self.invulnerable_timer = 30  # 0.5 segundos a 60 FPS
        
        # Comprobar si ha muerto
        if self.health <= 0:
            self.health = 0
            self.die()
            return True
            
        return False
    
    def heal(self, amount):
        """Restaurar salud"""
        self.health = min(self.max_health, self.health + amount)
        
        # Efecto visual
        self.add_healing_particles()
    
    def add_damage_particles(self):
        """Añadir partículas cuando recibe daño"""
        for _ in range(10):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            self.particles.append({
                "x": self.x,
                "y": self.y,
                "dx": math.cos(angle) * speed,
                "dy": math.sin(angle) * speed,
                "size": random.uniform(2, 5),
                "color": (255, 0, 0),  # Rojo
                "lifetime": random.randint(20, 40),
                "max_lifetime": 40
            })
    
    def add_healing_particles(self):
        """Añadir partículas cuando se cura"""
        for _ in range(8):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2)
            self.particles.append({
                "x": self.x,
                "y": self.y,
                "dx": math.cos(angle) * speed,
                "dy": math.sin(angle) * speed - 0.2,  # Añadir componente hacia arriba
                "size": random.uniform(2, 4),
                "color": (0, 255, 0),  # Verde
                "lifetime": random.randint(30, 50),
                "max_lifetime": 50
            })
    
    def add_experience(self, amount):
        """Añadir experiencia y comprobar si sube de nivel"""
        self.experience += amount
        
        # Comprobar si sube de nivel
        if self.experience >= self.level_threshold:
            self.level_up()
            return True
            
        return False
    
    def level_up(self):
        """Subir de nivel y mejorar estadísticas"""
        self.level += 1
        self.skill_points += 1
        self.experience -= self.level_threshold
        
        # Aumentar umbral para el próximo nivel
        self.level_threshold = int(self.level_threshold * 1.5)
        
        # Mejorar estadísticas base
        self.max_health += 10
        self.health = self.max_health
        
        # Reproducir sonido y efectos visuales
        if self.sounds["level_up"]:
            self.sounds["level_up"].play()
            
        # Añadir partículas de nivel
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            self.particles.append({
                "x": self.x,
                "y": self.y,
                "dx": math.cos(angle) * speed,
                "dy": math.sin(angle) * speed,
                "size": random.uniform(3, 6),
                "color": (255, 215, 0),  # Dorado
                "lifetime": random.randint(40, 60),
                "max_lifetime": 60
            })
    
    def upgrade_stat(self, stat):
        """Mejorar una estadística usando puntos de habilidad"""
        if self.skill_points <= 0:
            return False
            
        if stat == "health":
            self.max_health += 20
            self.health += 20
        elif stat == "attack":
            self.attack_power += 0.1
        elif stat == "defense":
            self.defense += 0.1
        elif stat == "speed":
            self.speed += 0.5
        elif stat == "critical":
            self.critical_chance += 0.02
        else:
            return False
            
        self.skill_points -= 1
        return True
    
    def apply_speed_boost(self, duration=300):
        """Aplicar mejora temporal de velocidad"""
        self.speed_boost = True
        self.speed_boost_timer = duration  # 5 segundos a 60 FPS
    
    def apply_damage_boost(self, duration=300):
        """Aplicar mejora temporal de daño"""
        if not self.damage_boost:
            self.attack_power *= 1.5  # Añadir bonus temporal
            
        self.damage_boost = True
        self.damage_boost_timer = duration  # 5 segundos a 60 FPS
    
    def die(self):
        """Manejar muerte del jugador"""
        # Reproducir sonido de muerte
        if self.sounds["death"]:
            self.sounds["death"].play()
            
        # Crear muchas partículas al morir
        for _ in range(40):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 6)
            self.particles.append({
                "x": self.x,
                "y": self.y,
                "dx": math.cos(angle) * speed,
                "dy": math.sin(angle) * speed,
                "size": random.uniform(3, 8),
                "color": (random.randint(200, 255), random.randint(0, 50), 0),  # Naranjas y rojos
                "lifetime": random.randint(40, 80),
                "max_lifetime": 80
            })
    
    def draw_hud(self, screen):
        # Barra de vida
        screen.blit(self.health_bar, (20, 20))
        health_text = pygame.font.SysFont('Arial', 18).render(f"SALUD: {int(self.health)}/{self.max_health}", True, (255, 255, 255))
        screen.blit(health_text, (30, 30))
        
        # Dibujar barra de salud
        health_width = 150 * (self.health / self.max_health)
        health_rect = pygame.Rect(70, 55, health_width, 25)
        
        # Color de la barra de salud según porcentaje
        if self.health > self.max_health * 0.6:
            health_color = (0, 200, 0)  # Verde
        elif self.health > self.max_health * 0.3:
            health_color = (200, 200, 0)  # Amarillo
        else:
            health_color = (200, 0, 0)  # Rojo
            
        pygame.draw.rect(screen, health_color, health_rect)
        
        # Información de arma y munición
        weapon = self.weapons[self.current_weapon]
        screen.blit(self.ammo_bar, (20, 100))
        
        # Dibujar icono del arma actual en el HUD
        screen.blit(weapon["hud_image"], (30, 110))
        
        # Mostrar nombre del arma
        weapon_name_text = pygame.font.SysFont('Arial', 16).render(weapon["name"], True, (255, 255, 255))
        screen.blit(weapon_name_text, (120, 105))
        
        # Mostrar munición
        ammo_text = pygame.font.SysFont('Arial', 18).render(f"{weapon['ammo']}/{weapon['max_ammo']}", True, (255, 255, 255))
        screen.blit(ammo_text, (120, 130))
        
        if self.is_reloading:
            reload_text = pygame.font.SysFont('Arial', 16).render("RECARGANDO", True, (255, 255, 255))
            screen.blit(reload_text, (180, 130))
        
        # Puntuación
        screen.blit(self.score_display, (WIDTH - 170, 20))
        score_text = pygame.font.SysFont('Arial', 18).render(f"{self.score}", True, (200, 0, 0))
        screen.blit(score_text, (WIDTH - 110, 35))
        
        # Nivel
        level_text = pygame.font.SysFont('Arial', 18).render(f"NIVEL: {self.level}", True, (255, 255, 255))
        screen.blit(level_text, (WIDTH - 150, 70))
        
        # Barra de experiencia
        if self.xp_bar:
            screen.blit(self.xp_bar, (WIDTH - 170, 100))
            
        xp_width = 120 * (self.experience / self.level_threshold)
        xp_rect = pygame.Rect(WIDTH - 150, 105, xp_width, 10)
        pygame.draw.rect(screen, (0, 150, 255), xp_rect)  # Azul para XP
        
        xp_text = pygame.font.SysFont('Arial', 14).render(f"XP: {self.experience}/{self.level_threshold}", True, (255, 255, 255))
        screen.blit(xp_text, (WIDTH - 150, 120))
        
        # Mostrar mejoras activas
        y_offset = 150
        if self.speed_boost:
            boost_text = pygame.font.SysFont('Arial', 14).render(f"Velocidad + ({self.speed_boost_timer//60}s)", True, (0, 200, 255))
            screen.blit(boost_text, (WIDTH - 150, y_offset))
            y_offset += 20
            
        if self.damage_boost:
            boost_text = pygame.font.SysFont('Arial', 14).render(f"Daño + ({self.damage_boost_timer//60}s)", True, (255, 100, 100))
            screen.blit(boost_text, (WIDTH - 150, y_offset))
            y_offset += 20
            
        if self.skill_points > 0:
            points_text = pygame.font.SysFont('Arial', 16).render(f"¡Puntos de habilidad: {self.skill_points}!", True, (255, 215, 0))
            screen.blit(points_text, (WIDTH - 250, y_offset))

# Ejemplo de uso
if __name__ == "__main__":
    # Inicializar pygame y crear ventana
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Prueba de Jugador")
    
    # Crear jugador
    player = Player()
    
    # Bucle principal
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    player.reload()
                    
                if event.key == pygame.K_h:
                    player.heal(10)
                    
                if event.key == pygame.K_x:
                    player.take_damage(10)
                    
                if event.key == pygame.K_e:
                    player.add_experience(20)
                    
                if event.key == pygame.K_1:
                    player.upgrade_stat("health")
                elif event.key == pygame.K_2:
                    player.upgrade_stat("attack")
                elif event.key == pygame.K_3:
                    player.upgrade_stat("speed")
                    
                if event.key == pygame.K_s:
                    player.apply_speed_boost()
                elif event.key == pygame.K_d:
                    player.apply_damage_boost()
            
            if event.type == pygame.MOUSEWHEEL:
                player.switch_weapon(event.y)
        
        # Mover jugador
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
        
        # Normalizar movimiento diagonal
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
            
        player.move(dx, dy)
        
        # Disparar con clic del ratón
        if pygame.mouse.get_pressed()[0]:
            player.attack()
        
        # Actualizar jugador
        player.update()
        
        # Dibujar
        screen.fill((50, 40, 30))  # Fondo marrón oscuro
        player.draw(screen)
        player.draw_hud(screen)
        
        # Mostrar instrucciones
        instructions = [
            "WASD / Flechas: Mover",
            "R: Recargar",
            "Rueda del ratón: Cambiar arma",
            "Clic izquierdo: Atacar",
            "H: Curar (+10)",
            "X: Daño (-10)",
            "E: Experiencia (+20)",
            "1,2,3: Mejorar stats",
            "S: Boost velocidad",
            "D: Boost daño"
        ]
        
        font = pygame.font.SysFont('Arial', 14)
        for i, text in enumerate(instructions):
            txt_surface = font.render(text, True, (255, 255, 255))
            screen.blit(txt_surface, (10, HEIGHT - 180 + i*18))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
"""
Módulo de jugador para Killer Potato
Contiene la clase del jugador y sus funcionalidades
"""

import pygame
import math
import random
from pygame.locals import *

# Inicializar pygame si no está inicializado
if not pygame.get_init():
    pygame.init()