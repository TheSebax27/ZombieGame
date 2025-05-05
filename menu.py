import pygame
import sys
import os
from pygame.locals import *
import random
import math

# Importar el juego principal
import Zombies

# Inicializar Pygame
pygame.init()
pygame.font.init()

# Configuración de pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Survival - Menu")

# Cargar fuentes
try:
    # Intentar cargar fuentes más atractivas para un juego de zombies
    font_small = pygame.font.Font("fonts/zombie.ttf", 20)
    font_medium = pygame.font.Font("fonts/zombie.ttf", 32)
    font_large = pygame.font.Font("fonts/zombie.ttf", 60)
    font_title = pygame.font.Font("fonts/zombie.ttf", 72)
except:
    # Fallback a fuentes del sistema
    print("No se pudieron cargar las fuentes personalizadas")
    font_small = pygame.font.SysFont('Arial', 20)
    font_medium = pygame.font.SysFont('Impact', 32)
    font_large = pygame.font.SysFont('Impact', 60)
    font_title = pygame.font.SysFont('Impact', 72)

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLOOD_RED = (180, 0, 0)
DARK_RED = (120, 0, 0)
GREEN = (50, 200, 50)
BLUE = (0, 0, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
TRANSPARENT_BLACK = (0, 0, 0, 180)

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
        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 0, 0), surface.get_rect(), 1)
        pygame.draw.line(surface, (255, 0, 0), (0, 0), (100, 100), 2)
        pygame.draw.line(surface, (255, 0, 0), (100, 0), (0, 100), 2)
        return surface

# Cargar imágenes
try:
    background = load_image("icons/menu_background.png", (WIDTH, HEIGHT))
    logo = load_image("icons/game_logo.png", (550, 200))
    zombie_icon = load_image("icons/zombie_icon.png", (64, 64))
    blood_splatter = load_image("icons/blood_splatter.png", (100, 100))
except:
    # Si no se pueden cargar las imágenes, usar fondos de color
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(BLACK)
    
    # Crear un logo de fallback
    logo = pygame.Surface((550, 200), pygame.SRCALPHA)
    zombie_icon = None
    blood_splatter = None

# Clase para los botones del menú con estilo mejorado
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False
        self.alpha = 230  # Transparencia inicial
        self.pulse_value = 0
        self.pulse_speed = 0.05
        self.pulse_direction = 1
        
    def draw(self, surface):
        # Efecto de pulsación para el botón seleccionado
        if self.is_hovered:
            self.pulse_value += self.pulse_speed * self.pulse_direction
            if self.pulse_value >= 1.0:
                self.pulse_value = 1.0
                self.pulse_direction = -1
            elif self.pulse_value <= 0.0:
                self.pulse_value = 0.0
                self.pulse_direction = 1
                
            pulse_offset = int(self.pulse_value * 5)
            color = self.hover_color
        else:
            pulse_offset = 0
            color = self.color
            
        # Crear superficie para el botón con transparencia
        button_surface = pygame.Surface((self.rect.width + pulse_offset*2, self.rect.height + pulse_offset*2), pygame.SRCALPHA)
        
        # Dibujar forma de botón con borde más interesante
        pygame.draw.rect(button_surface, (*color, self.alpha), 
                         (0, 0, self.rect.width + pulse_offset*2, self.rect.height + pulse_offset*2), 0, 8)
        
        # Borde sangriento
        if self.is_hovered:
            border_color = RED
            border_width = 3
        else:
            border_color = DARK_RED
            border_width = 2
            
        pygame.draw.rect(button_surface, (*border_color, 255), 
                         (0, 0, self.rect.width + pulse_offset*2, self.rect.height + pulse_offset*2), border_width, 8)
        
        # Dibujar el texto con efecto de sombra
        if self.is_hovered:
            text_surf = font_medium.render(self.text, True, WHITE)
        else:
            text_surf = font_medium.render(self.text, True, LIGHT_GRAY)
            
        # Sombra del texto
        shadow_surf = font_medium.render(self.text, True, BLACK)
        shadow_rect = shadow_surf.get_rect(center=(button_surface.get_width()//2 + 2, button_surface.get_height()//2 + 2))
        button_surface.blit(shadow_surf, shadow_rect)
        
        # Texto principal
        text_rect = text_surf.get_rect(center=(button_surface.get_width()//2, button_surface.get_height()//2))
        button_surface.blit(text_surf, text_rect)
        
        # Dibujar manchas de sangre en los botones (solo si está cargada la imagen)
        if blood_splatter and self.is_hovered:
            splatter_pos = [(random.randint(0, self.rect.width), random.randint(0, self.rect.height)) for _ in range(2)]
            for pos in splatter_pos:
                button_surface.blit(blood_splatter, pos)
        
        # Dibujar el botón en la superficie principal
        surface.blit(button_surface, (self.rect.x - pulse_offset, self.rect.y - pulse_offset))
        
        # Dibujar ícono zombie al lado del botón cuando está seleccionado
        if self.is_hovered and zombie_icon:
            icon_offset = int(math.sin(pygame.time.get_ticks() / 200) * 5)  # Movimiento oscilante
            surface.blit(zombie_icon, (self.rect.x - 80, self.rect.y - 10 + icon_offset))
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            # Efecto de sonido al hacer clic
            try:
                click_sound = pygame.mixer.Sound("sounds/button_click.wav")
                click_sound.play()
            except:
                pass
                
            if self.action:
                self.action()
            return True
        return False

# Funciones para las acciones de los botones
def start_game():
    print("Iniciando juego...")
    # Transición de pantalla antes de comenzar
    fade_transition()
    # Llamar al juego principal
    Zombies.main()
    
def show_instructions():
    print("Mostrando instrucciones...")
    # Cambiar a la pantalla de instrucciones
    instructions_screen()
    
def show_credits():
    print("Mostrando créditos...")
    # Cambiar a la pantalla de créditos
    credits_screen()
    
def quit_game():
    print("Saliendo del juego...")
    fade_transition(fade_in=False)
    pygame.quit()
    sys.exit()

# Efectos de transición
def fade_transition(fade_in=True):
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill(BLACK)
    
    for alpha in range(0, 300, 5):
        if fade_in:
            alpha_value = 255 - alpha
        else:
            alpha_value = alpha
            
        if alpha_value < 0:
            alpha_value = 0
        if alpha_value > 255:
            alpha_value = 255
            
        fade_surface.set_alpha(alpha_value)
        screen.blit(background, (0, 0))
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)

# Función para la pantalla de instrucciones con diseño mejorado
def instructions_screen():
    running = True
    
    instructions = [
        "CONTROLES:",
        "- Movimiento: WASD o flechas",
        "- Disparar: Clic izquierdo",
        "- Recargar: R",
        "- Cambiar arma: 1-3 o rueda del ratón",
        "- Pausar: P",
        "",
        "OBJETIVO:",
        "- Sobrevive a todas las oleadas de zombis",
        "- Cada oleada trae más zombis, más fuertes y rápidos",
        "- Gana puntos por cada zombi eliminado"
    ]
    
    back_button = Button(WIDTH//2 - 75, HEIGHT - 80, 150, 50, "VOLVER", DARK_RED, RED, None)
    
    # Efecto de sangre goteando
    blood_drops = []
    for _ in range(15):
        drop = {
            'x': random.randint(0, WIDTH),
            'y': random.randint(-500, -50),
            'speed': random.uniform(0.5, 2.0),
            'size': random.randint(2, 6),
            'color': (random.randint(150, 200), 0, 0)
        }
        blood_drops.append(drop)
    
    fade_transition()
    
    while running:
        screen.blit(background, (0, 0))
        
        # Crear panel semi-transparente para el contenido
        panel = pygame.Surface((WIDTH - 100, HEIGHT - 150), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        screen.blit(panel, (50, 120))
        
        # Título con efecto de sangre
        title_text = "INSTRUCCIONES"
        title_shadow = font_large.render(title_text, True, BLACK)
        title = font_large.render(title_text, True, RED)
        screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 3, 53))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Línea divisoria con degradado
        pygame.draw.line(screen, DARK_RED, (100, 110), (WIDTH - 100, 110), 2)
        
        # Instrucciones con mejor formato
        for i, line in enumerate(instructions):
            if ":" in line:  # Es un título de sección
                text = font_medium.render(line, True, RED)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, 150 + i * 35))
            else:
                text = font_small.render(line, True, WHITE)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, 150 + i * 35))
        
        # Actualizar y dibujar gotas de sangre
        for drop in blood_drops:
            drop['y'] += drop['speed']
            if drop['y'] > HEIGHT:
                drop['y'] = random.randint(-200, -50)
                drop['x'] = random.randint(0, WIDTH)
            
            pygame.draw.circle(screen, drop['color'], (int(drop['x']), int(drop['y'])), drop['size'])
            # Rastro de la gota
            pygame.draw.circle(screen, (drop['color'][0]-50, 0, 0), 
                              (int(drop['x']), int(drop['y']) - 5), drop['size'] - 1)
        
        # Botón de volver
        mouse_pos = pygame.mouse.get_pos()
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)
        
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == QUIT:
                fade_transition(fade_in=False)
                pygame.quit()
                sys.exit()
                
            if back_button.handle_event(event):
                running = False
                
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        
        pygame.display.flip()
        pygame.time.delay(10)
    
    fade_transition()

# Función para la pantalla de créditos con diseño mejorado
def credits_screen():
    running = True
    
    credits = [
        "DESARROLLO:",
        "Juan Sebastian Silva Piñeros",
        "",
        "ARTE:",
        "Icons designed by various artists",
        "",
        "MÚSICA:",
        "Sound effects by various artists",
        "",
        "AGRADECIMIENTOS:",
        "Gracias por jugar a Zombie Survival!"
    ]
    
    back_button = Button(WIDTH//2 - 75, HEIGHT - 80, 150, 50, "VOLVER", DARK_RED, RED, None)
    
    # Zombies animados para los créditos
    class ZombieAnimation:
        def __init__(self):
            self.zombies = []
            for _ in range(5):
                zombie = {
                    'x': random.choice([-50, WIDTH + 50]),
                    'y': random.randint(HEIGHT - 150, HEIGHT - 50),
                    'speed': random.uniform(0.3, 0.8),
                    'size': random.randint(30, 50),
                    'color': (random.randint(50, 100), random.randint(100, 150), random.randint(50, 100)),
                    'direction': 1 if random.random() > 0.5 else -1
                }
                if zombie['x'] > WIDTH:
                    zombie['direction'] = -1
                self.zombies.append(zombie)
                
        def update(self):
            for zombie in self.zombies:
                zombie['x'] += zombie['speed'] * zombie['direction']
                
                # Cambiar de dirección al llegar a los bordes
                if zombie['x'] < -100 or zombie['x'] > WIDTH + 100:
                    zombie['direction'] *= -1
                    
        def draw(self, surface):
            for zombie in self.zombies:
                # Dibujar una silueta simple de zombie
                color = zombie['color']
                x, y = int(zombie['x']), int(zombie['y'])
                size = zombie['size']
                
                # Cuerpo
                pygame.draw.ellipse(surface, color, (x-size//2, y-size, size, size*2))
                
                # Cabeza
                head_size = size * 0.8
                pygame.draw.circle(surface, color, (x, y-size-head_size//2), head_size//2)
                
                # Brazos extendidos
                arm_length = size * 0.7
                pygame.draw.line(surface, color, (x, y-size//2), 
                                (x + arm_length * zombie['direction'], y-size//2 + random.randint(-10, 10)), 
                                max(3, size//10))
                pygame.draw.line(surface, color, (x, y-size//3), 
                                (x + arm_length * zombie['direction'], y-size//3 + random.randint(-10, 10)), 
                                max(3, size//10))
    
    zombie_anim = ZombieAnimation()
    scroll_offset = 0
    scroll_speed = 0.5
    
    fade_transition()
    
    while running:
        screen.blit(background, (0, 0))
        
        # Crear panel semi-transparente para el contenido
        panel = pygame.Surface((WIDTH - 100, HEIGHT - 150), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        screen.blit(panel, (50, 120))
        
        # Título con efecto de sangre
        title_text = "CRÉDITOS"
        title_shadow = font_large.render(title_text, True, BLACK)
        title = font_large.render(title_text, True, RED)
        screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 3, 53))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Línea divisoria con degradado
        pygame.draw.line(screen, DARK_RED, (100, 110), (WIDTH - 100, 110), 2)
        
        # Créditos con animación de desplazamiento
        for i, line in enumerate(credits):
            if ":" in line:  # Es un título de sección
                text = font_medium.render(line, True, RED)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, 150 + i * 35 - scroll_offset))
            else:
                text = font_small.render(line, True, WHITE)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, 150 + i * 35 - scroll_offset))
        
        # Incrementar desplazamiento y reiniciar cuando sea necesario
        scroll_offset += scroll_speed
        if scroll_offset > (len(credits) * 35) - 200:
            scroll_offset = 0
            
        # Actualizar y dibujar zombies
        zombie_anim.update()
        zombie_anim.draw(screen)
        
        # Botón de volver
        mouse_pos = pygame.mouse.get_pos()
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)
        
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == QUIT:
                fade_transition(fade_in=False)
                pygame.quit()
                sys.exit()
                
            if back_button.handle_event(event):
                running = False
                
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        
        pygame.display.flip()
        pygame.time.delay(10)
    
    fade_transition()

# Animación de fondo para el menú principal mejorada
class BackgroundEffect:
    def __init__(self):
        self.particles = []
        self.fog_particles = []
        self.max_particles = 30
        self.max_fog = 15
        self.generate_particles()
        self.generate_fog()
        
    def generate_particles(self):
        for _ in range(self.max_particles):
            particle = {
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'size': random.randint(1, 4),
                'speed': random.uniform(0.5, 2.0),
                'color': (random.randint(150, 255), 0, 0, random.randint(50, 200))
            }
            self.particles.append(particle)
    
    def generate_fog(self):
        for _ in range(self.max_fog):
            fog = {
                'x': random.randint(-200, WIDTH),
                'y': random.randint(0, HEIGHT),
                'width': random.randint(100, 300),
                'height': random.randint(50, 150),
                'speed': random.uniform(0.2, 0.5),
                'alpha': random.randint(5, 20)
            }
            self.fog_particles.append(fog)
            
    def update(self):
        # Actualizar partículas de sangre
        for particle in self.particles:
            particle['y'] += particle['speed']
            
            # Si la partícula sale de la pantalla, reiniciarla
            if particle['y'] > HEIGHT:
                particle['y'] = random.randint(-50, 0)
                particle['x'] = random.randint(0, WIDTH)
                
        # Actualizar niebla
        for fog in self.fog_particles:
            fog['x'] += fog['speed']
            
            # Si la niebla sale de la pantalla, reiniciarla
            if fog['x'] > WIDTH + 100:
                fog['x'] = random.randint(-300, -100)
                fog['y'] = random.randint(0, HEIGHT)
                
    def draw(self, surface):
        # Dibujar niebla
        for fog in self.fog_particles:
            fog_surface = pygame.Surface((fog['width'], fog['height']), pygame.SRCALPHA)
            fog_surface.fill((100, 100, 100, fog['alpha']))
            surface.blit(fog_surface, (int(fog['x']), int(fog['y'])))
            
        # Dibujar partículas de sangre
        for particle in self.particles:
            pygame.draw.circle(
                surface, 
                particle['color'], 
                (int(particle['x']), int(particle['y'])), 
                particle['size']
            )
            # Efecto de goteo
            if particle['size'] > 2 and random.random() > 0.8:
                drip_height = random.randint(5, 15)
                drip_color = (particle['color'][0], particle['color'][1], particle['color'][2], 
                              particle['color'][3] // 2)
                pygame.draw.line(
                    surface,
                    drip_color,
                    (int(particle['x']), int(particle['y'])),
                    (int(particle['x']), int(particle['y']) + drip_height),
                    1
                )

# Función principal para el menú con diseño mejorado
def main():
    clock = pygame.time.Clock()
    
    # Crear botones
    button_width, button_height = 220, 60
    button_x = WIDTH // 2 - button_width // 2
    button_spacing = 80
    
    play_button = Button(button_x, 200, button_width, button_height, "JUGAR", DARK_RED, RED, start_game)
    instructions_button = Button(button_x, 200 + button_spacing, button_width, button_height, "INSTRUCCIONES", DARK_RED, RED, show_instructions)
    credits_button = Button(button_x, 200 + button_spacing * 2, button_width, button_height, "CRÉDITOS", DARK_RED, RED, show_credits)
    quit_button = Button(button_x, 200 + button_spacing * 3, button_width, button_height, "SALIR", DARK_RED, RED, quit_game)
    
    # Efecto de fondo
    bg_effect = BackgroundEffect()
    
    # Animación del título
    title_y = -150
    title_target_y = 60
    title_speed = 2
    title_scale = 1.0
    title_scale_direction = 0.001
    title_angle = 0
    
    # Música de fondo
    try:
        pygame.mixer.music.load("music/menu_music.mp3")
        pygame.mixer.music.play(-1)  # Reproducir en bucle
        pygame.mixer.music.set_volume(0.7)
    except:
        print("No se pudo cargar la música de fondo")
    
    # Transición inicial
    fade_transition()
    
    running = True
    while running:
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == QUIT:
                fade_transition(fade_in=False)
                running = False
                
            # Comprobar clics en botones
            play_button.handle_event(event)
            instructions_button.handle_event(event)
            credits_button.handle_event(event)
            quit_button.handle_event(event)
                
        # Actualizar posición del ratón
        mouse_pos = pygame.mouse.get_pos()
        play_button.check_hover(mouse_pos)
        instructions_button.check_hover(mouse_pos)
        credits_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
        
        # Actualizar efecto de fondo
        bg_effect.update()
        
        # Actualizar animación del título
        if title_y < title_target_y:
            title_y += title_speed
            if title_y > title_target_y:
                title_y = title_target_y
        
        # Efecto de pulso para el título
        title_scale += title_scale_direction
        if title_scale > 1.03:
            title_scale = 1.03
            title_scale_direction = -0.001
        elif title_scale < 0.97:
            title_scale = 0.97
            title_scale_direction = 0.001
            
        # Efecto de oscilación suave
        title_angle = math.sin(pygame.time.get_ticks() / 1000) * 2
        
        # Dibujar
        screen.blit(background, (0, 0))
        
        # Panel semi-transparente para el fondo
        panel = pygame.Surface((WIDTH - 80, HEIGHT - 80), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 150))
        screen.blit(panel, (40, 40))
        
        # Marco de sangre alrededor de la pantalla
        border_width = 10
        for i in range(border_width):
            alpha = 255 - (i * 255 // border_width)
            pygame.draw.rect(screen, (DARK_RED[0], DARK_RED[1], DARK_RED[2], alpha), 
                            (40-i, 40-i, WIDTH-80+i*2, HEIGHT-80+i*2), 1)
        
        # Dibujar efecto de fondo
        bg_effect.draw(screen)
        
        # Dibujar logo o título con efectos
        if logo:
            # Rotar y escalar el logo
            rotated_logo = pygame.transform.rotozoom(logo, title_angle, title_scale)
            logo_rect = rotated_logo.get_rect(center=(WIDTH//2, title_y + logo.get_height()//2))
            screen.blit(rotated_logo, logo_rect.topleft)
            
            # Añadir un resplandor bajo el logo
            glow_surf = pygame.Surface((logo.get_width()+40, 20), pygame.SRCALPHA)
            for i in range(10):
                alpha = 150 - i * 15
                if alpha < 0:
                    alpha = 0
                pygame.draw.ellipse(glow_surf, (RED[0], 0, 0, alpha), 
                                  (i*2, i, logo.get_width()+40-i*4, 20-i*2))
            screen.blit(glow_surf, (WIDTH//2 - glow_surf.get_width()//2, title_y + logo.get_height() + 5))
        else:
            # Título texto con efectos
            title_text = "ZOMBIE SURVIVAL"
            
            # Sombra del título
            shadow_surf = font_title.render(title_text, True, BLACK)
            shadow_rect = shadow_surf.get_rect(center=(WIDTH//2 + 3, title_y + 3))
            screen.blit(shadow_surf, shadow_rect)
            
            # Título principal con degradado
            for i in range(len(title_text)):
                char = title_text[i]
                char_color = (max(100, 200 - i*10), 0, 0)
                char_surf = font_title.render(char, True, char_color)
                char_pos = (WIDTH//2 - font_title.size(title_text)[0]//2 + font_title.size(title_text[:i])[0], 
                           title_y)
                screen.blit(char_surf, char_pos)
        
        # Dibujar botones
        play_button.draw(screen)
        instructions_button.draw(screen)
        credits_button.draw(screen)
        quit_button.draw(screen)
        
        # Dibujar versión con estilo
        version_text = font_small.render("v1.0", True, LIGHT_GRAY)
        version_shadow = font_small.render("v1.0", True, BLACK)
        screen.blit(version_shadow, (WIDTH - version_shadow.get_width() - 9, HEIGHT - version_shadow.get_height() - 9))
        screen.blit(version_text, (WIDTH - version_text.get_width() - 10, HEIGHT - version_text.get_height() - 10))
        
        # Dibujar nombre del creador
        creator_text = font_small.render("© Juan Sebastian Silva P.", True, LIGHT_GRAY)
        creator_shadow = font_small.render("© Juan Sebastian Silva P.", True, BLACK)
        screen.blit(creator_shadow, (11, HEIGHT - creator_shadow.get_height() - 9))
        screen.blit(creator_text, (10, HEIGHT - creator_text.get_height() - 10))
        
        # Agregar efecto de flash aleatorio para ambiente de terror
        if random.random() < 0.005:  # Probabilidad baja para que no sea molesto
            flash = pygame.Surface((WIDTH, HEIGHT))
            flash.fill(WHITE)
            flash.set_alpha(random.randint(5, 20))
            screen.blit(flash, (0, 0))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()