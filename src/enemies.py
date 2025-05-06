"""
Módulo de enemigos para Killer Potato
Contiene todas las clases y lógica relacionada con los enemigos del juego
"""

import pygame
import random
import math
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

# Clase base de enemigo
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
        self.level = level
        self.value = 10  # Puntos base que da al ser eliminado
        self.drop_chance = 0.3  # Probabilidad de soltar un ítem
        self.knockback_resistance = 1.0  # Resistencia al retroceso
        
        # Sonidos
        self.hit_sound = None
        self.death_sound = None
        self.attack_sound = None
        
        try:
            self.hit_sound = pygame.mixer.Sound("assets/sounds/sfx/enemy_hit.wav")
            self.death_sound = pygame.mixer.Sound("assets/sounds/sfx/enemy_death.wav")
            self.attack_sound = pygame.mixer.Sound("assets/sounds/sfx/enemy_attack.wav")
        except:
            pass
        
        # Cargar imágenes del enemigo según tipo
        if enemy_type == "human":
            self.image_right = load_image("assets/images/characters/human_right.png", (50, 50))
            self.image_left = load_image("assets/images/characters/human_left.png", (50, 50))
        elif enemy_type == "robot":
            self.image_right = load_image("assets/images/characters/robot_right.png", (60, 60))
            self.image_left = load_image("assets/images/characters/robot_left.png", (60, 60))
            self.health += 30  # Robots más resistentes
            self.speed -= 0.3  # Robots más lentos
            self.value = 20  # Más puntos
            self.knockback_resistance = 2.0  # Más resistentes al retroceso
        elif enemy_type == "chef":
            self.image_right = load_image("assets/images/characters/chef_right.png", (55, 55))
            self.image_left = load_image("assets/images/characters/chef_left.png", (55, 55))
            self.damage += 10  # Chef hace más daño
            self.value = 30  # Aún más puntos
            self.drop_chance = 0.5  # Mayor probabilidad de soltar ítems
        
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
        pygame.draw.rect(screen, (255, 0, 0), (self.x - bar_width//2, bar_y, bar_width, bar_height))
        # Parte de salud (verde)
        pygame.draw.rect(screen, (0, 255, 0), (self.x - bar_width//2, bar_y, bar_width * health_percentage, bar_height))
        # Borde de la barra
        pygame.draw.rect(screen, (0, 0, 0), (self.x - bar_width//2, bar_y, bar_width, bar_height), 1)
    
    def take_damage(self, damage, knockback_x=0, knockback_y=0):
        self.health -= damage
        self.hit_effect = 5  # Duración del efecto de daño en frames
        
        # Aplicar retroceso (knockback)
        if knockback_x != 0 or knockback_y != 0:
            knockback_strength = 5.0 / self.knockback_resistance
            self.x += knockback_x * knockback_strength
            self.y += knockback_y * knockback_strength
            self.update_rect()
        
        # Reproducir sonido de golpe
        if self.hit_sound:
            self.hit_sound.play()
            
        return self.is_dead()
    
    def is_dead(self):
        if self.health <= 0:
            # Reproducir sonido de muerte
            if self.death_sound:
                self.death_sound.play()
            return True
        return False
    
    def can_attack(self):
        return self.attack_counter <= 0
    
    def attack(self, player):
        if self.can_attack():
            player.take_damage(self.damage)
            self.attack_counter = self.attack_cooldown
            
            # Reproducir sonido de ataque
            if self.attack_sound:
                self.attack_sound.play()
                
            return True
        return False
    
    def get_drop_type(self):
        """Determina el tipo de ítem que puede soltar el enemigo"""
        if random.random() < self.drop_chance:
            # Determinar tipo de drop
            roll = random.random()
            if roll < 0.5:  # 50% probabilidad
                return "health"
            elif roll < 0.8:  # 30% probabilidad
                return "ammo"
            else:  # 20% probabilidad
                return "speed"
        return None

# Clase de enemigo: Guardia
class Guard(Enemy):
    def __init__(self, level):
        super().__init__(level, "human")
        self.value = 10  # Puntos base
        
        # Guardias armados en niveles superiores
        if level >= 2:
            self.has_gun = True
            self.shoot_cooldown = 90
            self.shoot_counter = 0
            self.shoot_range = 300
        else:
            self.has_gun = False
    
    def update(self, player_x, player_y):
        dist = math.sqrt((player_x - self.x)**2 + (player_y - self.y)**2)
        
        # Si tiene arma y está en rango, intentar disparar
        if self.has_gun and dist < self.shoot_range:
            if self.shoot_counter <= 0:
                self.shoot_counter = self.shoot_cooldown
                return self.shoot(player_x, player_y)
            else:
                self.shoot_counter -= 1
                
            # Si está en rango para disparar, moverse menos (mantener distancia)
            if dist > self.shoot_range * 0.5:
                super().update(player_x, player_y)
            else:
                # Mantener distancia
                dx = -(player_x - self.x) * 0.5
                dy = -(player_y - self.y) * 0.5
                dist = max(1, math.sqrt(dx**2 + dy**2))
                dx /= dist
                dy /= dist
                
                self.x += dx * self.speed * 0.5
                self.y += dy * self.speed * 0.5
                
                # Actualizar dirección de vista y rectángulo
                self.facing_right = player_x > self.x
                self.update_rect()
        else:
            # Comportamiento estándar
            super().update(player_x, player_y)
            
    def shoot(self, player_x, player_y):
        """El guardia dispara al jugador"""
        from weapons import Projectile  # Importación local para evitar ciclos
        
        # Calcular dirección del disparo
        dx = player_x - self.x
        dy = player_y - self.y
        dist = max(1, math.sqrt(dx**2 + dy**2))
        dx /= dist
        dy /= dist
        
        # Crear proyectil
        angle = math.atan2(dy, dx)
        projectile = Projectile(self.x, self.y, angle, 10, "enemy")
        
        # Reproducir sonido de disparo
        try:
            shoot_sound = pygame.mixer.Sound("assets/sounds/sfx/enemy_shoot.wav")
            shoot_sound.play()
        except:
            pass
            
        return projectile
        
    def draw(self, screen):
        super().draw(screen)
        
        # Dibujar indicador de guardia armado
        if self.has_gun:
            indicator_color = (255, 100, 100)  # Rojo claro
            pygame.draw.circle(screen, indicator_color, (int(self.x), int(self.y - self.radius - 15)), 3)

# Clase de enemigo: Robot
class Robot(Enemy):
    def __init__(self, level):
        super().__init__(level, "robot")
        self.value = 20
        self.special_attack_cooldown = 150
        self.special_attack_counter = 0
        self.special_attack_range = 200
        self.special_attack_damage = 15 + level * 2
    
    def update(self, player_x, player_y):
        super().update(player_x, player_y)
        
        # Actualizar contador de ataque especial
        if self.special_attack_counter > 0:
            self.special_attack_counter -= 1
            
    def special_attack(self, player):
        """Ataque especial del robot: daño en área"""
        if self.special_attack_counter <= 0:
            dist = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
            
            if dist < self.special_attack_range:
                # El robot realiza un ataque de área
                player.take_damage(self.special_attack_damage)
                self.special_attack_counter = self.special_attack_cooldown
                
                # Efecto visual del ataque especial
                return True
        return False
        
    def draw(self, screen):
        super().draw(screen)
        
        # Mostrar indicador de ataque especial cargado
        if self.special_attack_counter <= 0:
            indicator_color = (0, 255, 255)  # Cian
            pygame.draw.circle(screen, indicator_color, (int(self.x), int(self.y - self.radius - 15)), 3)

# Clase de enemigo: Chef
class Chef(Enemy):
    def __init__(self, level):
        super().__init__(level, "chef")
        self.value = 30
        self.throw_cooldown = 80
        self.throw_counter = 0
        self.throw_range = 250
        self.throw_speed = 8
        self.weapon_types = ["cuchillo", "tenedor", "sartén"]
        self.current_weapon = random.choice(self.weapon_types)
        
    def update(self, player_x, player_y):
        dist = math.sqrt((player_x - self.x)**2 + (player_y - self.y)**2)
        
        # Si está en rango, intentar lanzar un utensilio
        if dist < self.throw_range:
            if self.throw_counter <= 0:
                self.throw_counter = self.throw_cooldown
                return self.throw_utensil(player_x, player_y)
            else:
                self.throw_counter -= 1
            
            # Mantener distancia si está en rango
            if dist < self.throw_range * 0.6:
                dx = -(player_x - self.x)
                dy = -(player_y - self.y)
                dist = max(1, math.sqrt(dx**2 + dy**2))
                dx /= dist
                dy /= dist
                
                self.x += dx * self.speed
                self.y += dy * self.speed
                
                # Actualizar dirección y rectángulo
                self.facing_right = player_x > self.x
                self.update_rect()
                return None
                
        # Comportamiento estándar
        super().update(player_x, player_y)
        return None
        
    def throw_utensil(self, player_x, player_y):
        """El chef lanza un utensilio de cocina"""
        from weapons import ThrownUtensil  # Importación local para evitar ciclos
        
        # Calcular dirección del lanzamiento
        dx = player_x - self.x
        dy = player_y - self.y
        dist = max(1, math.sqrt(dx**2 + dy**2))
        dx /= dist
        dy /= dist
        
        # Elegir un utensilio aleatorio para lanzar
        utensil_type = random.choice(self.weapon_types)
        
        # Crear el proyectil
        angle = math.atan2(dy, dx)
        utensil = ThrownUtensil(self.x, self.y, angle, 15, utensil_type)
        
        # Reproducir sonido de lanzamiento
        try:
            throw_sound = pygame.mixer.Sound("assets/sounds/sfx/throw.wav")
            throw_sound.play()
        except:
            pass
            
        return utensil
        
    def draw(self, screen):
        super().draw(screen)
        
        # Mostrar indicador de lanzamiento listo
        if self.throw_counter <= 0:
            indicator_color = (255, 165, 0)  # Naranja
            pygame.draw.circle(screen, indicator_color, (int(self.x), int(self.y - self.radius - 15)), 3)

# Clase de enemigo: Jefe (Boss)
class Boss(Enemy):
    def __init__(self, level, boss_type):
        self.boss_type = boss_type
        
        # Configuración según tipo de jefe
        if boss_type == "chef_supremo":
            super().__init__(level, "chef")
            self.name = "Chef Supremo Crustini"
            self.health = 300 + level * 30
            self.max_health = self.health
            self.speed = 1.2
            self.value = 200
            self.damage = 15 + level * 2
            self.phase = 1
            self.max_phases = 3
            self.attack_patterns = [
                self.attack_pattern_1,
                self.attack_pattern_2,
                self.attack_pattern_3
            ]
            
            # Cargar imágenes específicas del jefe
            try:
                self.image_right = load_image("assets/images/characters/chef_boss_right.png", (80, 80))
                self.image_left = load_image("assets/images/characters/chef_boss_left.png", (80, 80))
            except:
                pass
                
            # Sonidos específicos
            try:
                self.boss_music = pygame.mixer.Sound("assets/sounds/music/boss_music.mp3")
                self.phase_change_sound = pygame.mixer.Sound("assets/sounds/sfx/boss_phase.wav")
                self.victory_sound = pygame.mixer.Sound("assets/sounds/sfx/victory.wav")
            except:
                pass
                
        elif boss_type == "robot_jefe":
            super().__init__(level, "robot")
            self.name = "Exprimidor-9000"
            self.health = 400 + level * 25
            self.max_health = self.health
            self.speed = 0.8
            self.value = 250
            self.damage = 20 + level * 3
            self.phase = 1
            self.max_phases = 3
            self.attack_patterns = [
                self.attack_pattern_1,
                self.attack_pattern_2,
                self.attack_pattern_3
            ]
            
            # Cargar imágenes específicas del jefe
            try:
                self.image_right = load_image("assets/images/characters/robot_boss_right.png", (90, 90))
                self.image_left = load_image("assets/images/characters/robot_boss_left.png", (90, 90))
            except:
                pass
        
        # Timers y contadores
        self.phase_health_thresholds = [self.max_health * 0.6, self.max_health * 0.3]
        self.attack_cooldown = 60
        self.attack_counter = 0
        self.special_cooldown = 150
        self.special_counter = 0
        self.invulnerable = False
        self.invulnerable_counter = 0
        
        # Llamar a la animación de entrada
        self.entrance_animation = True
        self.entrance_counter = 180  # 3 segundos a 60 FPS
        
        # Iniciar música de jefe si existe
        if hasattr(self, 'boss_music'):
            try:
                pygame.mixer.music.stop()
                self.boss_music.play(-1)
            except:
                pass
    
    def update(self, player_x, player_y):
        # Animación de entrada
        if self.entrance_animation:
            self.entrance_counter -= 1
            if self.entrance_counter <= 0:
                self.entrance_animation = False
            return None
            
        # Verificar cambio de fase
        for i, threshold in enumerate(self.phase_health_thresholds):
            if self.health <= threshold and self.phase == i + 1:
                self.change_phase()
        
        # Si es invulnerable, no procesar más allá
        if self.invulnerable:
            self.invulnerable_counter -= 1
            if self.invulnerable_counter <= 0:
                self.invulnerable = False
            return None
            
        # Actualizar contadores
        if self.attack_counter > 0:
            self.attack_counter -= 1
            
        if self.special_counter > 0:
            self.special_counter -= 1
            
        # Elegir patrón de ataque según fase actual
        if self.attack_counter <= 0 and self.special_counter <= 0:
            attack_result = self.attack_patterns[self.phase - 1](player_x, player_y)
            if attack_result:
                return attack_result
        
        # Movimiento básico
        super().update(player_x, player_y)
        return None
        
    def change_phase(self):
        """Cambiar a la siguiente fase del jefe"""
        self.phase += 1
        self.invulnerable = True
        self.invulnerable_counter = 60  # 1 segundo de invulnerabilidad
        
        # Reproducir sonido de cambio de fase
        if hasattr(self, 'phase_change_sound'):
            try:
                self.phase_change_sound.play()
            except:
                pass
                
        # Efecto visual de cambio de fase
        return "phase_change"
        
    def attack_pattern_1(self, player_x, player_y):
        """Patrón de ataque de la fase 1 - Básico"""
        self.attack_counter = self.attack_cooldown
        
        # Patrón específico según el tipo de jefe
        if self.boss_type == "chef_supremo":
            # Lanzar 3 proyectiles en forma de abanico
            projectiles = []
            
            base_angle = math.atan2(player_y - self.y, player_x - self.x)
            for i in range(-1, 2):
                from weapons import ThrownUtensil
                angle = base_angle + i * 0.2  # Separación de 0.2 radianes
                utensil = ThrownUtensil(self.x, self.y, angle, 15, random.choice(["cuchillo", "tenedor", "sartén"]))
                projectiles.append(utensil)
                
            return projectiles
            
        elif self.boss_type == "robot_jefe":
            # Generar una onda expansiva
            from weapons import ShockWave
            wave = ShockWave(self.x, self.y, 15, 200)
            return wave
            
        return None
        
    def attack_pattern_2(self, player_x, player_y):
        """Patrón de ataque de la fase 2 - Intermedio"""
        self.special_counter = self.special_cooldown
        
        # Patrón específico según el tipo de jefe
        if self.boss_type == "chef_supremo":
            # Salto hacia el jugador con daño en área
            self.x = player_x
            self.y = player_y
            self.update_rect()
            
            # Efecto visual
            from weapons import AreaEffect
            effect = AreaEffect(self.x, self.y, 30, 100)
            return effect
            
        elif self.boss_type == "robot_jefe":
            # Lanzar misiles teledirigidos
            from weapons import HomingMissile
            missiles = []
            for _ in range(3):
                missile = HomingMissile(self.x, self.y, 20, 8)
                missiles.append(missile)
            return missiles
            
        return None
        
    def attack_pattern_3(self, player_x, player_y):
        """Patrón de ataque de la fase 3 - Avanzado (solo disponible en fase 3)"""
        if self.phase < 3:
            return None
            
        self.special_counter = self.special_cooldown * 2
        
        # Patrón específico según el tipo de jefe
        if self.boss_type == "chef_supremo":
            # Invocar ayudantes (chefs menores)
            helpers = []
            for _ in range(2):
                chef = Chef(self.level)
                # Posicionar cerca del jefe
                chef.x = self.x + random.randint(-100, 100)
                chef.y = self.y + random.randint(-100, 100)
                chef.update_rect()
                helpers.append(chef)
            return {"type": "summon", "enemies": helpers}
            
        elif self.boss_type == "robot_jefe":
            # Modo berserk: disparos rápidos en todas direcciones
            from weapons import Projectile
            projectiles = []
            for i in range(8):
                angle = i * math.pi / 4  # 8 direcciones equidistantes
                projectile = Projectile(self.x, self.y, angle, 15, "enemy", speed=12)
                projectiles.append(projectile)
            return projectiles
            
        return None
        
    def take_damage(self, damage, knockback_x=0, knockback_y=0):
        # Si es invulnerable, no recibe daño
        if self.invulnerable:
            return False
            
        return super().take_damage(damage, knockback_x, knockback_y)
    
    def draw(self, screen):
        # Dibujar el enemigo base
        super().draw(screen)
        
        # Dibujar nombre del jefe
        if hasattr(self, 'name'):
            # Cargar fuente
            try:
                boss_font = pygame.font.Font("assets/fonts/potato.ttf", 16)
            except:
                boss_font = pygame.font.SysFont('Arial', 16)
                
            name_text = boss_font.render(self.name, True, (255, 50, 50))
            screen.blit(name_text, (self.x - name_text.get_width() // 2, self.y - self.radius - 25))
        
        # Mostrar fase actual con estrellas
        for i in range(self.phase):
            star_color = (255, 215, 0)  # Dorado
            star_pos = (int(self.x - 15 + i * 15), int(self.y - self.radius - 40))
            
            # Dibujar una estrella simple
            pygame.draw.polygon(screen, star_color, [
                (star_pos[0], star_pos[1] - 5),
                (star_pos[0] + 2, star_pos[1] - 2),
                (star_pos[0] + 5, star_pos[1] - 2),
                (star_pos[0] + 3, star_pos[1] + 1),
                (star_pos[0] + 4, star_pos[1] + 4),
                (star_pos[0], star_pos[1] + 2),
                (star_pos[0] - 4, star_pos[1] + 4),
                (star_pos[0] - 3, star_pos[1] + 1),
                (star_pos[0] - 5, star_pos[1] - 2),
                (star_pos[0] - 2, star_pos[1] - 2)
            ])
        
        # Efecto visual para invulnerabilidad
        if self.invulnerable:
            shield_radius = self.radius + 5
            shield_color = (100, 100, 255, 128)  # Azul semi-transparente
            
            shield_surface = pygame.Surface((shield_radius*2, shield_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, shield_color, (shield_radius, shield_radius), shield_radius)
            
            # Dibujar escudo pulsante
            pulse = math.sin(pygame.time.get_ticks() / 200) * 5
            scaled_radius = int(shield_radius + pulse)
            scaled_shield = pygame.transform.scale(shield_surface, (scaled_radius*2, scaled_radius*2))
            
            screen.blit(scaled_shield, (self.x - scaled_radius, self.y - scaled_radius))

# Clase de enemigo: Minion (enemigos más débiles)
class Minion(Enemy):
    def __init__(self, level, spawn_x=None, spawn_y=None):
        super().__init__(level, "human")
        self.health = 30 + level * 5
        self.max_health = self.health
        self.damage = 3 + level
        self.speed = 1.5 + level * 0.1
        self.value = 5
        
        # Si se especifica posición, usarla
        if spawn_x is not None and spawn_y is not None:
            self.x = spawn_x
            self.y = spawn_y
            self.update_rect()
            
        # Cargar imágenes más pequeñas
        try:
            self.image_right = load_image("assets/images/characters/minion_right.png", (40, 40))
            self.image_left = load_image("assets/images/characters/minion_left.png", (40, 40))
        except:
            pass

# Función para crear enemigo aleatorio según nivel
def create_random_enemy(level):
    """Crea un enemigo aleatorio apropiado para el nivel actual"""
    roll = random.random()
    
    if level <= 2:
        # Niveles iniciales: mayoría de guardias
        if roll < 0.8:
            return Guard(level)
        else:
            return Minion(level)
    elif level <= 5:
        # Niveles intermedios: guardias y robots
        if roll < 0.5:
            return Guard(level)
        elif roll < 0.8:
            return Robot(level)
        else:
            return Minion(level)
    else:
        # Niveles avanzados: todos los tipos
        if roll < 0.4:
            return Guard(level)
        elif roll < 0.7:
            return Robot(level)
        elif roll < 0.9:
            return Chef(level)
        else:
            return Minion(level)

# Función para crear jefe según nivel
def create_boss(level):
    """Crea un jefe apropiado para el nivel actual"""
    if level % 5 == 0:  # Cada 5 niveles
        if level % 10 == 0:  # Niveles 10, 20, etc.
            return Boss(level, "robot_jefe")
        else:  # Niveles 5, 15, etc.
            return Boss(level, "chef_supremo")
    return None

# Ejemplo de uso:
if __name__ == "__main__":
    # Prueba simple
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Prueba de Enemigos")
    
    enemies = [
        Guard(1),
        Robot(2),
        Chef(3),
        Minion(1),
        Boss(5, "chef_supremo")
    ]
    
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Simulación de posición de jugador (centro de pantalla)
        player_x, player_y = WIDTH // 2, HEIGHT // 2
        
        # Actualizar enemigos
        for enemy in enemies:
            enemy.update(player_x, player_y)
        
        # Dibujar
        screen.fill((0, 0, 0))
        for enemy in enemies:
            enemy.draw(screen)
            
        # Dibujar posición del jugador
        pygame.draw.circle(screen, (0, 255, 0), (player_x, player_y), 10)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()