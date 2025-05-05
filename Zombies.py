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
pygame.display.set_caption("Zombie Survival")

# Cargar fuentes
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

# Clase para efectos de disparo
class MuzzleFlash:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.lifetime = 5  # Duración del efecto en frames
        self.image = load_image("icons/muzzle_flash.png", (30, 15))
        self.rotated_image = pygame.transform.rotate(self.image, -math.degrees(angle))
        self.rect = self.rotated_image.get_rect(center=(x, y))
    
    def update(self):
        self.lifetime -= 1
    
    def draw(self, screen):
        screen.blit(self.rotated_image, self.rect.topleft)
    
    def is_finished(self):
        return self.lifetime <= 0

# Clase Jugador
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 20
        self.speed = 5
        self.health = 100
        self.score = 0
        self.current_weapon = 0
        self.facing_right = True
        
        # Cargar imágenes del jugador
        self.image_right = load_image("icons/player_right.png", (50, 50))
        self.image_left = load_image("icons/player_left.png", (50, 50))
        
        # Configurar armas
        self.weapons = [
            {
                "name": "Pistola", 
                "damage": 25, 
                "ammo": 30, 
                "max_ammo": 30, 
                "reload_time": 15, 
                "reload_counter": 0, 
                "fire_rate": 20, 
                "fire_counter": 0,
                "image_right": load_image("icons/pistol_right.png", (40, 20)),
                "image_left": load_image("icons/pistol_left.png", (40, 20)),
                "hud_image": load_image("icons/pistol_hud.png", (80, 40))
            },
            {
                "name": "Escopeta", 
                "damage": 75, 
                "ammo": 20, 
                "max_ammo": 20, 
                "reload_time": 40, 
                "reload_counter": 0, 
                "fire_rate": 50, 
                "fire_counter": 0,
                "image_right": load_image("icons/shotgun_right.png", (50, 20)),
                "image_left": load_image("icons/shotgun_left.png", (50, 20)),
                "hud_image": load_image("icons/shotgun_hud.png", (80, 40))
            },
            {
                "name": "Rifle", 
                "damage": 40, 
                "ammo": 30, 
                "max_ammo": 30, 
                "reload_time": 30, 
                "reload_counter": 0, 
                "fire_rate": 10, 
                "fire_counter": 0,
                "image_right": load_image("icons/rifle_right.png", (60, 20)),
                "image_left": load_image("icons/rifle_left.png", (60, 20)),
                "hud_image": load_image("icons/rifle_hud.png", (80, 40))
            },
        ]
        self.is_reloading = False
        self.can_shoot = True
        
        # Cargar HUD
        self.health_bar = load_image("icons/health_bar.png", (250, 70))
        self.ammo_bar = load_image("icons/ammo_bar.png", (250, 70))
        self.score_display = load_image("icons/score_display.png", (150, 50))
        
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
    
    def shoot(self):
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
        
        # Posición para el destello del disparo (delante del arma)
        muzzle_distance = 30
        flash_x = self.x + math.cos(angle) * muzzle_distance
        flash_y = self.y + math.sin(angle) * muzzle_distance
        
        # Crear efectos
        bullet = Bullet(self.x, self.y, angle, weapon["damage"])
        muzzle_flash = MuzzleFlash(flash_x, flash_y, angle)
        
        return bullet, muzzle_flash
    
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
        health_text = font.render(f"HEALTH", True, WHITE)
        screen.blit(health_text, (30, 25))
        
        # Dibujar barra roja de salud
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
            reload_text = font.render("RELOADING", True, WHITE)
            screen.blit(reload_text, (150, 100))
        
        # Puntuación
        screen.blit(self.score_display, (WIDTH - 170, 20))
        score_text = font.render(f"{self.score}", True, DARK_RED)
        screen.blit(score_text, (WIDTH - 110, 35))
        
        # Información de oleada
        wave_text = font.render(f"WAVE: {wave}", True, WHITE)
        screen.blit(wave_text, (WIDTH - 150, 80))
        
        zombies_left_text = font.render(f"ZOMBIES: {len(zombies) + zombies_to_spawn}", True, WHITE)
        screen.blit(zombies_left_text, (WIDTH - 200, 110))

# Clase Bala
class Bullet:
    def __init__(self, x, y, angle, damage):
        self.x = x
        self.y = y
        self.speed = 12
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.radius = 5
        self.damage = damage
        
        # Cargar imagen de bala
        self.image = load_image("icons/bullet.png", (12, 6))
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

# Clase Zombie
class Zombie:
    def __init__(self, wave):
        self.radius = 20
        self.speed = 1 + wave * 0.2  # Los zombis se vuelven más rápidos con cada oleada
        self.health = 50 + wave * 10  # Los zombis se vuelven más resistentes con cada oleada
        self.max_health = 50 + wave * 10  # Salud máxima para calcular porcentaje
        self.damage = 5 + wave  # Los zombis hacen más daño con cada oleada
        self.attack_cooldown = 50
        self.attack_counter = 0
        self.facing_right = True
        self.hit_effect = 0  # Contador para efecto de daño
        
        # Cargar imágenes del zombi
        self.image_right = load_image("icons/zombie_right.png", (50, 50))
        self.image_left = load_image("icons/zombie_left.png", (50, 50))
        
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
        zombie_image = self.image_right if self.facing_right else self.image_left
        
        # Aplicar efecto de daño (parpadeo rojo)
        if self.hit_effect > 0:
            # Crear una copia de la imagen para modificarla
            damaged_image = zombie_image.copy()
            damaged_image.fill((255, 0, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(damaged_image, (self.x - zombie_image.get_width() // 2, self.y - zombie_image.get_height() // 2))
        else:
            # Dibujar zombi normal
            screen.blit(zombie_image, (self.x - zombie_image.get_width() // 2, self.y - zombie_image.get_height() // 2))
        
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
    global wave, zombies, zombies_to_spawn  # Para acceso desde métodos de clase
    
    clock = pygame.time.Clock()
    
    # Cargar imágenes de fondo
    try:
        background = load_image("icons/background.png", (WIDTH, HEIGHT))
    except:
        # Si no se puede cargar la imagen, crear un fondo de color
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill(GRAY)
    
    player = Player()
    bullets = []
    muzzle_flashes = []
    zombies = []
    
    wave = 1
    zombies_in_wave = 5  # Inicial
    zombies_to_spawn = zombies_in_wave
    spawn_cooldown = 60  # frames entre spawn de zombis
    spawn_counter = 0
    
    wave_complete = False
    wave_timer = 180  # Pausa entre oleadas (3 segundos a 60 FPS)
    
    game_over = False
    paused = False
    
    running = True
    while running:
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            if event.type == KEYDOWN:
                if event.key == K_p:  # Tecla de pausa
                    paused = not paused
                
                if not paused and not game_over:
                    if event.key == K_r:
                        player.reload()
                    if event.key == K_1:
                        player.current_weapon = 0
                    if event.key == K_2 and len(player.weapons) > 1:
                        player.current_weapon = 1
                    if event.key == K_3 and len(player.weapons) > 2:
                        player.current_weapon = 2
                    if event.key == K_SPACE and wave_complete:
                        # Iniciar próxima oleada
                        wave += 1
                        zombies_in_wave = 5 + wave * 2
                        zombies_to_spawn = zombies_in_wave
                        wave_complete = False
                
                if game_over and event.key == K_RETURN:
                    # Reiniciar juego
                    player = Player()
                    bullets = []
                    muzzle_flashes = []
                    zombies = []
                    wave = 1
                    zombies_in_wave = 5
                    zombies_to_spawn = zombies_in_wave
                    spawn_cooldown = 60
                    spawn_counter = 0
                    wave_complete = False
                    game_over = False
            
            if not paused and not game_over:
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    bullet, flash = player.shoot()
                    if bullet:
                        bullets.append(bullet)
                    if flash:
                        muzzle_flashes.append(flash)
                
                if event.type == MOUSEWHEEL:
                    player.switch_weapon(event.y)
        
        if paused:
            draw_pause_screen(screen)
            pygame.display.flip()
            continue
            
        if game_over:
            # Pantalla de Game Over
            screen.fill(BLACK)
            game_over_text = big_font.render("GAME OVER", True, RED)
            score_text = font.render(f"Puntuación: {player.score}", True, WHITE)
            wave_text = font.render(f"Oleada alcanzada: {wave}", True, WHITE)
            restart_text = font.render("Presiona ENTER para reiniciar", True, WHITE)
            
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 60))
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
            screen.blit(wave_text, (WIDTH//2 - wave_text.get_width()//2, HEIGHT//2 + 30))
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
        
        # Actualizar efectos de disparo
        for flash in muzzle_flashes[:]:
            flash.update()
            if flash.is_finished():
                muzzle_flashes.remove(flash)
        
        # Actualizar balas
        for bullet in bullets[:]:
            bullet.update()
            if bullet.is_offscreen():
                bullets.remove(bullet)
        
        # Actualizar zombis y comprobar colisiones
        for zombie in zombies[:]:
            zombie.update(player.x, player.y)
            
            # Comprobar colisión con jugador
            if player.rect.colliderect(zombie.rect):
                zombie.attack(player)
            
            # Comprobar colisión con balas
            for bullet in bullets[:]:
                if zombie.rect.collidepoint(bullet.x, bullet.y):
                    zombie.take_damage(bullet.damage)
                    bullets.remove(bullet)
                    break
            
            # Eliminar zombis muertos
            if zombie.is_dead():
                player.score += 10
                zombies.remove(zombie)
        
        # Generar zombis
        if not wave_complete and zombies_to_spawn > 0:
            if spawn_counter <= 0:
                zombies.append(Zombie(wave))
                zombies_to_spawn -= 1
                spawn_counter = spawn_cooldown
            else:
                spawn_counter -= 1
        
        # Comprobar fin de oleada
        if not wave_complete and zombies_to_spawn <= 0 and len(zombies) == 0:
            wave_complete = True
            wave_timer = 180  # Reiniciar temporizador entre oleadas
        
        # Actualizar temporizador entre oleadas
        if wave_complete:
            wave_timer -= 1
        
        # Comprobar si el jugador ha muerto
        if player.health <= 0:
            game_over = True
        
        # Dibujar todo
        screen.blit(background, (0, 0))
        
        # Dibujar balas
        for bullet in bullets:
            bullet.draw(screen)
            
        # Dibujar zombis
        for zombie in zombies:
            zombie.draw(screen)
            
        # Dibujar jugador
        player.draw(screen)
        
        # Dibujar efectos de disparo
        for flash in muzzle_flashes:
            flash.draw(screen)
        
        # Dibujar HUD
        player.draw_hud(screen)
        
        # Mensaje de oleada completada
        if wave_complete:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))  # Semi-transparente
            screen.blit(overlay, (0, 0))
            
            complete_text = big_font.render(f"¡OLEADA {wave} COMPLETADA!", True, WHITE)
            next_text = font.render("Presiona ESPACIO para iniciar la siguiente oleada", True, WHITE)
            screen.blit(complete_text, (WIDTH//2 - complete_text.get_width()//2, HEIGHT//2 - 30))
            screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 + 20))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()