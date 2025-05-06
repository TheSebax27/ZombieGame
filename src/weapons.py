"""
Módulo de armas para Killer Potato
Contiene las clases para proyectiles, ataques y el sistema de armas
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
    from config.settings import WIDTH, HEIGHT, WEAPONS, DEBUG_MODE, UNLIMITED_AMMO
except ImportError:
    WIDTH, HEIGHT = 800, 600
    DEBUG_MODE = False
    UNLIMITED_AMMO = False
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
        }
    }

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

# Clase base para proyectiles
class Projectile:
    def __init__(self, x, y, angle, damage, owner="player", speed=12, is_critical=False):
        self.x = x
        self.y = y
        self.speed = speed
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.radius = 5
        self.damage = damage
        self.angle = angle
        self.owner = owner  # "player" o "enemy"
        self.is_critical = is_critical
        self.lifetime = 120  # Tiempo de vida en frames (2 segundos a 60 FPS)
        self.explosive = False  # Por defecto no es explosivo
        
        # Cargar imagen según propietario
        if owner == "player":
            self.image = load_image("assets/images/items/player_projectile.png", (12, 6))
        else:
            self.image = load_image("assets/images/items/enemy_projectile.png", (12, 6))
            
        # Rotar imagen según ángulo
        self.angle_degrees = math.degrees(angle)
        self.rotated_image = pygame.transform.rotate(self.image, -self.angle_degrees)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))
        
        # Efecto para golpes críticos
        self.critical_effect = None
        if is_critical:
            try:
                self.critical_effect = load_image("assets/images/effects/critical.png", (20, 20))
            except:
                self.critical_effect = None
    
    def update(self):
        """Actualizar posición y estado del proyectil"""
        self.x += self.dx
        self.y += self.dy
        self.rect.center = (self.x, self.y)
        
        # Reducir tiempo de vida
        self.lifetime -= 1
    
    def draw(self, screen):
        """Dibujar proyectil en pantalla"""
        # Dibujar proyectil
        screen.blit(self.rotated_image, self.rect.topleft)
        
        # Dibujar efecto de golpe crítico si corresponde
        if self.is_critical and self.critical_effect:
            # Posición con offset para que el efecto siga al proyectil
            effect_x = self.x - self.critical_effect.get_width() // 2
            effect_y = self.y - self.critical_effect.get_height() // 2
            
            # Efecto de rotación para el crítico
            critical_angle = pygame.time.get_ticks() % 360
            rotated_effect = pygame.transform.rotate(self.critical_effect, critical_angle)
            effect_rect = rotated_effect.get_rect(center=(self.x, self.y))
            
            screen.blit(rotated_effect, effect_rect.topleft)
        
        # Efecto de estela
        if self.owner == "player":
            trail_length = 3
            trail_color = (255, 200, 0, 150)  # Amarillo para jugador
        else:
            trail_length = 2
            trail_color = (200, 0, 0, 150)  # Rojo para enemigos
            
        for i in range(1, trail_length + 1):
            alpha = 200 - i * 60  # La estela se desvanece
            if alpha > 0:
                trail_pos = (int(self.x - self.dx * i * 0.5), int(self.y - self.dy * i * 0.5))
                
                # Crear superficie para partícula con alpha
                trail_size = self.radius - i
                if trail_size > 0:
                    trail_surf = pygame.Surface((trail_size*2, trail_size*2), pygame.SRCALPHA)
                    pygame.draw.circle(
                        trail_surf, 
                        (trail_color[0], trail_color[1], trail_color[2], alpha), 
                        (trail_size, trail_size), 
                        trail_size
                    )
                    screen.blit(trail_surf, (trail_pos[0]-trail_size, trail_pos[1]-trail_size))
    
    def is_offscreen(self):
        """Comprobar si el proyectil está fuera de la pantalla"""
        return (self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT)
    
    def is_expired(self):
        """Comprobar si el proyectil ha expirado"""
        return self.lifetime <= 0
    
    def explode(self):
        """Método para proyectiles explosivos"""
        if self.explosive:
            return ShockWave(self.x, self.y, self.damage * 0.8, 80, (255, 100, 0))
        return None

# Clase para proyectiles lanzados por el chef
class ThrownUtensil(Projectile):
    def __init__(self, x, y, angle, damage, utensil_type):
        super().__init__(x, y, angle, damage, "enemy", 8)
        self.utensil_type = utensil_type  # "cuchillo", "tenedor", "sartén"
        self.rotation_speed = random.uniform(-5, 5)  # Velocidad de rotación aleatoria
        self.current_rotation = 0
        
        # Cargar imagen según tipo
        if utensil_type == "cuchillo":
            self.base_image = load_image("assets/images/items/thrown_knife.png", (24, 8))
        elif utensil_type == "tenedor":
            self.base_image = load_image("assets/images/items/thrown_fork.png", (24, 8))
        elif utensil_type == "sartén":
            self.base_image = load_image("assets/images/items/thrown_pan.png", (30, 30))
            self.rotation_speed *= 2  # La sartén gira más rápido
        else:
            self.base_image = load_image("assets/images/items/thrown_generic.png", (20, 10))
    
    def update(self):
        """Actualizar posición, rotación y estado"""
        super().update()
        
        # Actualizar rotación
        self.current_rotation += self.rotation_speed
        
        # Recalcular imagen rotada
        total_rotation = self.angle_degrees + self.current_rotation
        self.rotated_image = pygame.transform.rotate(self.base_image, -total_rotation)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))

# Clase para proyectiles teledirigidos (misiles, etc)
class HomingMissile(Projectile):
    def __init__(self, x, y, damage, speed=6, target=None):
        # Ángulo inicial aleatorio si no hay objetivo
        if target:
            dx = target[0] - x
            dy = target[1] - y
            angle = math.atan2(dy, dx)
        else:
            angle = random.uniform(0, math.pi * 2)
            
        super().__init__(x, y, angle, damage, "enemy", speed)
        
        self.target = target  # Coordenadas del objetivo o None
        self.turning_speed = 0.04  # Velocidad de giro en radianes
        self.acceleration = 0.1  # Aceleración
        self.max_speed = speed + 2  # Velocidad máxima
        self.smoke_timer = 0  # Temporizador para efectos de humo
        self.smoke_particles = []  # Partículas de humo
        self.explosive = True  # Es explosivo
        
        # Cargar imagen
        self.base_image = load_image("assets/images/items/missile.png", (20, 8))
    
    def update(self):
        """Actualizar posición, dirección y efectos"""
        # Actualizar humo
        self.smoke_timer += 1
        if self.smoke_timer >= 3:  # Generar humo cada 3 frames
            self.smoke_timer = 0
            
            # Añadir partícula de humo
            self.smoke_particles.append({
                'x': self.x - self.dx * 0.8,  # Posición detrás del misil
                'y': self.y - self.dy * 0.8,
                'size': random.uniform(3, 6),
                'lifetime': random.randint(20, 30),
                'max_lifetime': 30,
                'color': (200, 200, 200)  # Gris
            })
        
        # Actualizar partículas de humo
        for particle in self.smoke_particles[:]:
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0:
                self.smoke_particles.remove(particle)
        
        # Seguir al objetivo si existe
        if self.target:
            # Calcular dirección al objetivo
            dx = self.target[0] - self.x
            dy = self.target[1] - self.y
            target_angle = math.atan2(dy, dx)
            
            # Calcular diferencia de ángulo (menor camino)
            angle_diff = target_angle - self.angle
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            # Girar hacia el objetivo
            if abs(angle_diff) < self.turning_speed:
                self.angle = target_angle
            elif angle_diff > 0:
                self.angle += self.turning_speed
            else:
                self.angle -= self.turning_speed
            
            # Actualizar dirección
            self.dx = math.cos(self.angle) * self.speed
            self.dy = math.sin(self.angle) * self.speed
            
            # Aplicar aceleración
            if self.speed < self.max_speed:
                self.speed += self.acceleration
        
        # Posición
        self.x += self.dx
        self.y += self.dy
        
        # Actualizar imagen rotada
        self.angle_degrees = math.degrees(self.angle)
        self.rotated_image = pygame.transform.rotate(self.base_image, -self.angle_degrees)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))
        
        # Reducir tiempo de vida
        self.lifetime -= 1
    
    def draw(self, screen):
        """Dibujar misil y efectos de humo"""
        # Dibujar partículas de humo
        for particle in self.smoke_particles:
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            size = particle['size'] * (particle['lifetime'] / particle['max_lifetime'])
            
            particle_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface, 
                (*particle['color'], alpha), 
                (size, size), 
                size
            )
            screen.blit(particle_surface, (particle['x'] - size, particle['y'] - size))
        
        # Dibujar misil
        screen.blit(self.rotated_image, self.rect.topleft)
        
        # Dibujar fuego de propulsión
        exhaust_length = random.randint(5, 15)
        exhaust_width = 3
        
        # Calcular posición trasera del misil
        back_x = self.x - math.cos(self.angle) * (self.rotated_image.get_width() // 2)
        back_y = self.y - math.sin(self.angle) * (self.rotated_image.get_height() // 2)
        
        # Dibujar fuego
        exhaust_points = [
            (back_x, back_y),
            (back_x - math.cos(self.angle - 0.2) * exhaust_width, back_y - math.sin(self.angle - 0.2) * exhaust_width),
            (back_x - math.cos(self.angle) * exhaust_length, back_y - math.sin(self.angle) * exhaust_length),
            (back_x - math.cos(self.angle + 0.2) * exhaust_width, back_y - math.sin(self.angle + 0.2) * exhaust_width)
        ]
        
        # Colores del fuego
        colors = [(255, 200, 0), (255, 100, 0), (200, 0, 0)]
        for i, color in enumerate(colors):
            if i == 0:
                points = exhaust_points
            else:
                # Hacer el fuego más corto para cada color
                shorter = exhaust_length * (1 - i * 0.3)
                points = [
                    exhaust_points[0],
                    exhaust_points[1],
                    (back_x - math.cos(self.angle) * shorter, back_y - math.sin(self.angle) * shorter),
                    exhaust_points[3]
                ]
                
            pygame.draw.polygon(screen, color, points)
    
    def set_target(self, target_x, target_y):
        """Establecer nuevo objetivo"""
        self.target = (target_x, target_y)
    
    def explode(self):
        """Crear explosión al impactar"""
        return ShockWave(self.x, self.y, self.damage, 100, (255, 100, 0))

# Clase para ondas expansivas o ataques en área
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
        self.hits = set()  # Conjunto para registrar qué ya ha sido golpeado
        
        # Color de la onda
        if wave_color:
            self.color = wave_color
        else:
            self.color = (50, 50, 200)  # Azul por defecto
    
    def update(self):
        """Actualizar tamaño y transparencia de la onda"""
        self.current_radius += self.growth_speed
        
        # Reducir velocidad de crecimiento y transparencia cuando se acerca al máximo
        if self.current_radius > self.max_radius * 0.5:
            self.growth_speed = max(1, self.growth_speed * 0.95)
            self.alpha -= self.fade_speed
            self.fade_speed *= 1.05
        
        return self.is_finished()
    
    def draw(self, screen):
        """Dibujar onda expansiva"""
        # Crear superficie con transparencia
        wave_surface = pygame.Surface((self.current_radius*2, self.current_radius*2), pygame.SRCALPHA)
        
        # Dibujar círculo con degradado
        for i in range(5):
            size_factor = 1 - i * 0.15
            alpha_factor = 1 - i * 0.25
            
            radius = int(self.current_radius * size_factor)
            alpha = int(self.alpha * alpha_factor)
            
            if radius > 0 and alpha > 0:
                pygame.draw.circle(
                    wave_surface, 
                    (*self.color, alpha), 
                    (self.current_radius, self.current_radius), 
                    radius, 
                    2
                )
        
        # Dibujar en pantalla
        screen.blit(wave_surface, (self.x - self.current_radius, self.y - self.current_radius))
    
    def check_collision(self, entity_rect):
        """Comprobar si un rectángulo está dentro de la onda y no ha sido golpeado antes"""
        # Calcular distancia al centro
        entity_center_x = entity_rect.centerx
        entity_center_y = entity_rect.centery
        
        distance = math.sqrt((entity_center_x - self.x)**2 + (entity_center_y - self.y)**2)
        
        # Comprobar si está dentro del radio de daño
        wave_front_width = 30  # Ancho del frente de onda que causa daño
        in_damage_zone = self.current_radius - wave_front_width <= distance <= self.current_radius
        
        if in_damage_zone:
            # Convertir rect a tupla para poder añadirlo al conjunto
            entity_key = (entity_rect.x, entity_rect.y, entity_rect.width, entity_rect.height)
            
            # Si no ha sido golpeado antes, marcar como golpeado y devolver True
            if entity_key not in self.hits:
                self.hits.add(entity_key)
                return True
        
        return False
    
    def is_finished(self):
        """Comprobar si la onda ha terminado su efecto"""
        return self.current_radius >= self.max_radius or self.alpha <= 0

# Clase para efectos de área persistentes (como fuego, ácido, etc)
class AreaEffect:
    def __init__(self, x, y, damage, duration, effect_type="fire"):
        self.x = x
        self.y = y
        self.radius = 50
        self.damage = damage
        self.duration = duration
        self.effect_type = effect_type
        self.damage_timer = 0
        self.damage_interval = 30  # Aplicar daño cada 30 frames (0.5 segundos)
        self.particles = []
        self.max_particles = 20
        
        # Valores según tipo de efecto
        if effect_type == "fire":
            self.color = (255, 100, 0)
            self.generate_particles = self.generate_fire_particles
        elif effect_type == "acid":
            self.color = (0, 255, 0)
            self.generate_particles = self.generate_acid_particles
        elif effect_type == "electric":
            self.color = (50, 50, 255)
            self.generate_particles = self.generate_electric_particles
        else:
            self.color = (200, 200, 200)
            self.generate_particles = self.generate_generic_particles
            
        # Generar partículas iniciales
        self.generate_particles(self.max_particles)
    
    def update(self):
        """Actualizar estado y partículas"""
        # Reducir duración
        self.duration -= 1
        
        # Actualizar timer de daño
        self.damage_timer += 1
        
        # Actualizar partículas
        for particle in self.particles[:]:
            particle['lifetime'] -= 1
            
            # Actualizar posición
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            
            # Eliminar partículas muertas
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
        
        # Generar nuevas partículas si se necesitan
        if len(self.particles) < self.max_particles:
            self.generate_particles(self.max_particles - len(self.particles))
            
        # Devolver si el efecto ha terminado
        return self.is_finished()
    
    def draw(self, screen):
        """Dibujar efecto de área y partículas"""
        # Dibujar área de efecto como círculo semitransparente
        area_surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        alpha = min(100, int(self.duration * 0.5))
        pygame.draw.circle(area_surface, (*self.color, alpha), (self.radius, self.radius), self.radius)
        screen.blit(area_surface, (self.x - self.radius, self.y - self.radius))
        
        # Dibujar partículas
        for particle in self.particles:
            # Calcular tamaño y opacidad según tiempo de vida
            size = particle['size'] * (particle['lifetime'] / particle['max_lifetime'])
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            
            particle_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface, 
                (*particle['color'], alpha), 
                (size, size), 
                size
            )
            screen.blit(particle_surface, (particle['x'] - size, particle['y'] - size))
    
    def generate_fire_particles(self, count):
        """Generar partículas de fuego"""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.2, 1.0)
            distance = random.uniform(0, self.radius * 0.8)
            
            # Posición dentro del área
            px = self.x + math.cos(angle) * distance
            py = self.y + math.sin(angle) * distance
            
            # Movimiento (siempre hacia arriba con variación)
            dx = random.uniform(-0.5, 0.5)
            dy = -random.uniform(0.5, 1.5)  # Negativo = hacia arriba
            
            # Color (variaciones de naranja/rojo)
            r = random.randint(200, 255)
            g = random.randint(50, 150)
            b = 0
            
            self.particles.append({
                'x': px,
                'y': py,
                'dx': dx,
                'dy': dy,
                'size': random.uniform(2, 5),
                'color': (r, g, b),
                'lifetime': random.randint(20, 40),
                'max_lifetime': 40
            })
    
    def generate_acid_particles(self, count):
        """Generar partículas de ácido"""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.1, 0.5)
            distance = random.uniform(0, self.radius * 0.9)
            
            # Posición dentro del área
            px = self.x + math.cos(angle) * distance
            py = self.y + math.sin(angle) * distance
            
            # Movimiento (burbujeo aleatorio)
            dx = random.uniform(-0.3, 0.3)
            dy = random.uniform(-0.3, 0.3)
            
            # Color (variaciones de verde)
            r = random.randint(0, 50)
            g = random.randint(180, 255)
            b = random.randint(0, 100)
            
            self.particles.append({
                'x': px,
                'y': py,
                'dx': dx,
                'dy': dy,
                'size': random.uniform(2, 6),
                'color': (r, g, b),
                'lifetime': random.randint(30, 60),
                'max_lifetime': 60
            })
    
    def generate_electric_particles(self, count):
        """Generar partículas eléctricas"""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.0, 3.0)
            distance = random.uniform(0, self.radius * 0.9)
            
            # Posición dentro del área
            px = self.x + math.cos(angle) * distance
            py = self.y + math.sin(angle) * distance
            
            # Movimiento (rápido y errático)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            
            # Color (azul eléctrico/blanco)
            intensity = random.randint(150, 255)
            r = random.randint(0, 50)
            g = random.randint(50, 150)
            b = intensity
            
            self.particles.append({
                'x': px,
                'y': py,
                'dx': dx,
                'dy': dy,
                'size': random.uniform(1, 3),
                'color': (r, g, b),
                'lifetime': random.randint(5, 15),
                'max_lifetime': 15
            })
    
    def generate_generic_particles(self, count):
        """Generar partículas genéricas"""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.3, 0.8)
            distance = random.uniform(0, self.radius * 0.8)
            
            # Posición dentro del área
            px = self.x + math.cos(angle) * distance
            py = self.y + math.sin(angle) * distance
            
            # Movimiento aleatorio
            dx = random.uniform(-0.5, 0.5)
            dy = random.uniform(-0.5, 0.5)
            
            # Color (gris/blanco)
            intensity = random.randint(100, 200)
            
            self.particles.append({
                'x': px,
                'y': py,
                'dx': dx,
                'dy': dy,
                'size': random.uniform(2, 4),
                'color': (intensity, intensity, intensity),
                'lifetime': random.randint(20, 40),
                'max_lifetime': 40
            })
    
    def check_collision(self, entity_rect):
        """Comprobar si un rectángulo está dentro del área de efecto"""
        # Calcular distancia al centro
        entity_center_x = entity_rect.centerx
        entity_center_y = entity_rect.centery
        
        distance = math.sqrt((entity_center_x - self.x)**2 + (entity_center_y - self.y)**2)
        
        # Comprobar si está dentro del radio y si es momento de aplicar daño
        return distance <= self.radius and self.damage_timer >= self.damage_interval
    
    def apply_damage(self):
        """Aplicar daño y reiniciar timer"""
        self.damage_timer = 0
        return self.damage
    
    def is_finished(self):
        """Comprobar si el efecto ha terminado"""
        return self.duration <= 0

# Clase especial para crear explosivo dirigido
class ExplosiveProjectile(Projectile):
    def __init__(self, x, y, angle, damage, owner="player", speed=10, is_critical=False):
        super().__init__(x, y, angle, damage, owner, speed, is_critical)
        self.explosive = True
        self.explosion_radius = 80
        self.explosion_damage = damage * 0.8
    
    def explode(self):
        """Crear explosión al impactar"""
        return ShockWave(self.x, self.y, self.explosion_damage, self.explosion_radius, (255, 100, 0))

# Clase para rayos/láseres
class BeamProjectile(Projectile):
    def __init__(self, x, y, angle, damage, owner="player", is_critical=False):
        super().__init__(x, y, angle, damage, owner, 30, is_critical)
        # Radio más grande para simular un rayo
        self.radius = 8
        # Tiempo de vida más corto
        self.lifetime = 10
        # Longitud del rayo
        self.length = 1000
        
    def draw(self, screen):
        """Dibujar como línea en lugar de imagen"""
        start_pos = (self.x, self.y)
        end_x = self.x + math.cos(self.angle) * self.length
        end_y = self.y + math.sin(self.angle) * self.length
        end_pos = (end_x, end_y)
        
        # Color según propietario y crítico
        if self.owner == "player":
            if self.is_critical:
                color = (255, 255, 0)  # Amarillo brillante
            else:
                color = (0, 200, 255)  # Azul cian
        else:
            color = (255, 0, 0)  # Rojo
            
        # Dibujar línea principal
        pygame.draw.line(screen, color, start_pos, end_pos, 4)
        
        # Dibujar halo
        halo_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(halo_surf, (*color, 128), start_pos, end_pos, 8)
        screen.blit(halo_surf, (0, 0))
        
        # Añadir efecto de partículas
        for _ in range(2):
            # Posición aleatoria a lo largo del rayo
            t = random.random()
            particle_x = self.x + t * (end_x - self.x)
            particle_y = self.y + t * (end_y - self.y)
            
            # Tamaño aleatorio
            size = random.uniform(2, 5)
            
            # Dibujar partícula
            particle_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (*color, 200), (size, size), size)
            screen.blit(particle_surf, (particle_x - size, particle_y - size))

# Clase para gestionar armas y mejoras
class WeaponManager:
    def __init__(self):
        self.weapons = []
        self.current_weapon = 0
        
        # Cargar armas predeterminadas
        self.load_default_weapons()
    
    def load_default_weapons(self):
        """Cargar armas predeterminadas desde configuración"""
        try:
            from config.settings import WEAPONS
            
            # Convertir diccionario de armas a lista con imágenes cargadas
            for key, weapon_data in WEAPONS.items():
                weapon = weapon_data.copy()
                
                # Añadir contadores internos
                weapon["reload_counter"] = 0
                weapon["fire_counter"] = 0
                
                # Cargar imágenes
                weapon["image_right"] = load_image(f"assets/images/items/{key}_right.png", (40, 20))
                weapon["image_left"] = load_image(f"assets/images/items/{key}_left.png", (40, 20))
                weapon["hud_image"] = load_image(f"assets/images/ui/{key}_hud.png", (80, 40))
                
                self.weapons.append(weapon)
                
        except (ImportError, AttributeError):
            # Usar armas por defecto si no se puede cargar la configuración
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
                    "sound": "assets/sounds/sfx/fork_attack.wav",
                    "projectile_type": "normal",
                    "projectile_count": 1,
                    "projectile_speed": 12
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
                    "sound": "assets/sounds/sfx/spoon_attack.wav",
                    "projectile_type": "explosive",
                    "projectile_count": 1,
                    "projectile_speed": 10
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
                    "sound": "assets/sounds/sfx/knife_attack.wav",
                    "projectile_type": "rapid",
                    "projectile_count": 1,
                    "projectile_speed": 15
                },
            ]
    
    def get_current_weapon(self):
        """Obtener arma actual"""
        if 0 <= self.current_weapon < len(self.weapons):
            return self.weapons[self.current_weapon]
        return None
    
    def switch_weapon(self, direction):
        """Cambiar de arma"""
        self.current_weapon = (self.current_weapon + direction) % len(self.weapons)
    
    def add_weapon(self, weapon_data):
        """Añadir una nueva arma"""
        self.weapons.append(weapon_data)
    
    def upgrade_weapon(self, index, attribute, amount):
        """Mejorar un atributo de un arma"""
        if 0 <= index < len(self.weapons):
            weapon = self.weapons[index]
            
            if attribute == "damage":
                weapon["damage"] += amount
            elif attribute == "max_ammo":
                weapon["max_ammo"] += amount
                weapon["ammo"] += amount
            elif attribute == "reload_time":
                weapon["reload_time"] = max(5, weapon["reload_time"] - amount)
            elif attribute == "fire_rate":
                weapon["fire_rate"] = max(5, weapon["fire_rate"] - amount)
            elif attribute == "projectile_count":
                weapon["projectile_count"] += amount
            elif attribute == "projectile_speed":
                weapon["projectile_speed"] += amount
    
    def create_projectiles(self, x, y, angle, owner="player", is_critical=False):
        """Crear proyectiles según el arma actual"""
        weapon = self.get_current_weapon()
        if not weapon:
            return []
            
        projectiles = []
        
        # Si está activado el modo de munición ilimitada
        unlimited_ammo = False
        try:
            from config.settings import UNLIMITED_AMMO
            unlimited_ammo = UNLIMITED_AMMO
        except ImportError:
            pass
        
        # Comprobar munición
        if not unlimited_ammo and weapon["ammo"] <= 0:
            return []
            
        # Restar munición si no es ilimitada
        if not unlimited_ammo:
            weapon["ammo"] -= 1
        
        # Aplicar tipo de proyectil y cantidad
        if weapon["projectile_type"] == "normal":
            # Proyectil estándar
            projectiles.append(Projectile(x, y, angle, weapon["damage"], owner, weapon["projectile_speed"], is_critical))
            
        elif weapon["projectile_type"] == "rapid":
            # Disparo rápido (un solo proyectil más veloz)
            projectiles.append(Projectile(x, y, angle, weapon["damage"], owner, weapon["projectile_speed"], is_critical))
            
        elif weapon["projectile_type"] == "explosive":
            # Proyectil explosivo (más lento pero con área de efecto)
            projectiles.append(ExplosiveProjectile(x, y, angle, weapon["damage"], owner, weapon["projectile_speed"] * 0.8, is_critical))
            
        elif weapon["projectile_type"] == "spread":
            # Disparo en abanico (múltiples proyectiles en ángulo)
            spread_count = weapon["projectile_count"]
            spread_angle = 0.3  # En radianes (aproximadamente 17 grados)
            
            for i in range(spread_count):
                # Calcular ángulo para cada proyectil
                if spread_count == 1:
                    proj_angle = angle
                else:
                    proj_angle = angle - spread_angle/2 + (spread_angle * i / (spread_count - 1))
                    
                projectiles.append(Projectile(x, y, proj_angle, weapon["damage"], owner, weapon["projectile_speed"], is_critical))
                
        elif weapon["projectile_type"] == "beam":
            # Rayo continuo
            projectiles.append(BeamProjectile(x, y, angle, weapon["damage"] / 5, owner, is_critical))
        
        else:
            # Proyectil por defecto como fallback
            projectiles.append(Projectile(x, y, angle, weapon["damage"], owner, weapon["projectile_speed"], is_critical))
        
        return projectiles

# Ejemplo de uso del sistema de armas
if __name__ == "__main__":
    # Inicializar pygame y crear ventana
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Prueba de Armas")
    
    # Crear instancias de prueba
    weapon_manager = WeaponManager()
    projectiles = []
    effects = []
    
    # Bucle principal
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic izquierdo
                    # Obtener posición del mouse y calcular ángulo
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    center_x, center_y = WIDTH // 2, HEIGHT // 2
                    angle = math.atan2(mouse_y - center_y, mouse_x - center_x)
                    
                    # Crear proyectiles
                    new_projectiles = weapon_manager.create_projectiles(center_x, center_y, angle)
                    projectiles.extend(new_projectiles)
                    
                if event.button == 3:  # Clic derecho
                    # Crear efecto de área
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                        # Crear onda expansiva
                        effects.append(ShockWave(mouse_x, mouse_y, 20, 150))
                    else:
                        # Crear efecto persistente
                        effect_types = ["fire", "acid", "electric"]
                        selected_type = effect_types[random.randint(0, len(effect_types)-1)]
                        effects.append(AreaEffect(mouse_x, mouse_y, 5, 180, selected_type))
            
            if event.type == pygame.MOUSEWHEEL:
                weapon_manager.switch_weapon(event.y)
        
        # Actualizar
        for projectile in projectiles[:]:
            projectile.update()
            
            # Eliminar proyectiles expirados o fuera de pantalla
            if projectile.is_expired() or projectile.is_offscreen():
                projectiles.remove(projectile)
        
        for effect in effects[:]:
            if effect.update():
                effects.remove(effect)
        
        # Dibujar
        screen.fill((30, 30, 30))  # Fondo gris oscuro
        
        # Dibujar puntero central
        pygame.draw.circle(screen, (0, 255, 0), (WIDTH // 2, HEIGHT // 2), 10, 2)
        
        # Dibujar efectos
        for effect in effects:
            effect.draw(screen)
            
        # Dibujar proyectiles
        for projectile in projectiles:
            projectile.draw(screen)
        
        # Mostrar arma actual
        current_weapon = weapon_manager.get_current_weapon()
        if current_weapon:
            text = f"Arma: {current_weapon['name']} - Daño: {current_weapon['damage']} - Tipo: {current_weapon['projectile_type']}"
            font = pygame.font.SysFont('Arial', 20)
            text_surf = font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, (10, 10))
            
            # Instrucciones
            instructions = [
                "Clic izquierdo: Disparar arma actual",
                "Clic derecho: Crear efecto de área",
                "Shift + Clic derecho: Crear onda expansiva",
                "Rueda del ratón: Cambiar de arma"
            ]
            
            for i, text in enumerate(instructions):
                inst_surf = font.render(text, True, (200, 200, 200))
                screen.blit(inst_surf, (10, HEIGHT - 100 + i * 22))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()