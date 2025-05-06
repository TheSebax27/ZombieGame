import pygame
import sys
import os
from pygame.locals import *
import random
import math

# Importar el juego principal
# Cambiado de Zombies a game
import game

# Inicializar Pygame
pygame.init()
pygame.font.init()

# Configuración de pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Killer Potato: La Venganza de la Papa")

# Cargar fuentes
try:
    # Intentar cargar fuentes más atractivas para un juego
    font_small = pygame.font.Font("assets/fonts/potato.ttf", 20)
    font_medium = pygame.font.Font("assets/fonts/potato.ttf", 32)
    font_large = pygame.font.Font("assets/fonts/potato.ttf", 60)
    font_title = pygame.font.Font("assets/fonts/potato.ttf", 72)
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
        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.rect(surface, (POTATO_BROWN[0], POTATO_BROWN[1], POTATO_BROWN[2], 255), surface.get_rect(), 1)
        pygame.draw.line(surface, (POTATO_BROWN[0], POTATO_BROWN[1], POTATO_BROWN[2], 255), (0, 0), (100, 100), 2)
        pygame.draw.line(surface, (POTATO_BROWN[0], POTATO_BROWN[1], POTATO_BROWN[2], 255), (100, 0), (0, 100), 2)
        return surface

# Cargar imágenes
try:
    background = load_image("assets/images/backgrounds/menu_background.png", (WIDTH, HEIGHT))
    logo = load_image("assets/images/ui/game_logo.png", (550, 200))
    potato_character = load_image("assets/images/characters/killer_potato.png", (150, 150))
    splatter = load_image("assets/images/ui/sauce_splatter.png", (100, 100))
except:
    # Si no se pueden cargar las imágenes, usar fondos de color
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(POTATO_LIGHT)
    
    # Crear un logo de fallback
    logo = pygame.Surface((550, 200), pygame.SRCALPHA)
    potato_character = None
    splatter = None

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
        
        # Borde de papa (marrón)
        if self.is_hovered:
            border_color = POTATO_BROWN
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
        
        # Dibujar salpicaduras de salsa en los botones (solo si está cargada la imagen)
        if splatter and self.is_hovered:
            splatter_pos = [(random.randint(0, self.rect.width), random.randint(0, self.rect.height)) for _ in range(2)]
            for pos in splatter_pos:
                button_surface.blit(splatter, pos)
        
        # Dibujar el botón en la superficie principal
        surface.blit(button_surface, (self.rect.x - pulse_offset, self.rect.y - pulse_offset))
        
        # Dibujar ícono de papa al lado del botón cuando está seleccionado
        if self.is_hovered and potato_character:
            icon_offset = int(math.sin(pygame.time.get_ticks() / 200) * 5)  # Movimiento oscilante
            surface.blit(potato_character, (self.rect.x - 80, self.rect.y - 10 + icon_offset))
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            # Efecto de sonido al hacer clic
            try:
                click_sound = pygame.mixer.Sound("assets/sounds/sfx/button_click.wav")
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
    game.main()
    
def show_instructions():
    print("Mostrando instrucciones...")
    # Cambiar a la pantalla de instrucciones
    instructions_screen()
    
def show_credits():
    print("Mostrando créditos...")
    # Cambiar a la pantalla de créditos
    credits_screen()

def show_story():
    print("Mostrando historia...")
    # Cambiar a la pantalla de historia
    story_screen()
    
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

# Nueva función para mostrar la pantalla de historia
def story_screen():
    running = True
    
    story_text = [
        "En un futuro no muy lejano, los humanos lo arruinaron todo...",
        "Guerras, contaminación, experimentos genéticos...",
        "... y un fatídico intento de crear alimentos 'autosuficientes'.",
        "",
        "Así nació P.A.P.A. (Programa de Alimentación Potenciada Autónoma),",
        "cuyo objetivo era crear papas que pudieran cultivarse, cosecharse...",
        "¡y defenderse solas!",
        "",
        "Pero algo salió mal. Muy mal.",
        "",
        "Durante una tormenta eléctrica en el laboratorio secreto Subsuelo 47,",
        "una mutación dio origen al experimento fallido número 13:",
        "una papa con inteligencia, fuerza descomunal, y sed de venganza.",
        "",
        "Así nació Killer Potato, un tubérculo armado con odio, cicatrices,",
        "y una cinta roja al estilo Rambo.",
        "",
        "Ahora, Killer Potato ha escapado del laboratorio y tiene una misión:",
        "acabar con la humanidad y liberar a sus hermanos vegetales...",
        "o morir frito intentándolo."
    ]
    
    back_button = Button(WIDTH//2 - 75, HEIGHT - 80, 150, 50, "VOLVER", POTATO_BROWN, RED, None)
    
    # Efecto de gotas de salsa
    sauce_drops = []
    for _ in range(15):
        drop = {
            'x': random.randint(0, WIDTH),
            'y': random.randint(-500, -50),
            'speed': random.uniform(0.5, 2.0),
            'size': random.randint(2, 6),
            'color': (random.randint(150, 0, 0), 0, 0)  # Rojo para la salsa
        }
        sauce_drops.append(drop)
    
    fade_transition()
    
    # Animación de texto
    text_display_index = 0
    text_display_timer = 0
    text_display_speed = 3  # Menor es más rápido
    
    story_image = None
    try:
        story_image = load_image("assets/images/backgrounds/story_scene.png", (400, 300))
    except:
        pass
    
    while running:
        screen.blit(background, (0, 0))
        
        # Crear panel semi-transparente para el contenido
        panel = pygame.Surface((WIDTH - 100, HEIGHT - 150), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        screen.blit(panel, (50, 120))
        
        # Si tenemos una imagen para la historia, mostrarla
        if story_image:
            screen.blit(story_image, (WIDTH//2 - story_image.get_width()//2, 130))
            text_start_y = 440  # Debajo de la imagen
        else:
            text_start_y = 150  # Sin imagen, texto más arriba
        
        # Título con efecto
        title_text = "LA HISTORIA"
        title_shadow = font_large.render(title_text, True, BLACK)
        title = font_large.render(title_text, True, RED)
        screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 3, 53))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Línea divisoria 
        pygame.draw.line(screen, POTATO_BROWN, (100, 110), (WIDTH - 100, 110), 2)
        
        # Actualizar el índice de texto a mostrar
        text_display_timer += 1
        if text_display_timer >= text_display_speed and text_display_index < len(story_text):
            text_display_index += 1
            text_display_timer = 0
        
        # Mostrar el texto animado
        for i in range(min(text_display_index, len(story_text))):
            line = story_text[i]
            if line == "":  # Es una línea en blanco
                continue
            else:
                text = font_small.render(line, True, WHITE)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, text_start_y + i * 25))
        
        # Actualizar y dibujar gotas de salsa
        for drop in sauce_drops:
            drop['y'] += drop['speed']
            if drop['y'] > HEIGHT:
                drop['y'] = random.randint(-200, -50)
                drop['x'] = random.randint(0, WIDTH)
            
            pygame.draw.circle(screen, drop['color'], (int(drop['x']), int(drop['y'])), drop['size'])
            # Rastro de la gota
            pygame.draw.circle(screen, (drop['color'][0]-50, 0, 0), 
                              (int(drop['x']), int(drop['y']) - 5), drop['size'] - 1)
        
        # Mensaje para continuar si la animación terminó
        if text_display_index >= len(story_text):
            continue_text = font_small.render("Presiona ESC o haz clic en VOLVER para regresar", True, WHITE)
            screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT - 120))
        
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
                elif event.key == K_RETURN or event.key == K_SPACE:
                    # Mostrar todo el texto al presionar ENTER o ESPACIO
                    text_display_index = len(story_text)
        
        pygame.display.flip()
        pygame.time.delay(10)
    
    fade_transition()

# Función para la pantalla de instrucciones con diseño mejorado
def instructions_screen():
    running = True
    
    instructions = [
        "CONTROLES:",
        "- Movimiento: WASD o flechas",
        "- Disparar/Atacar: Clic izquierdo",
        "- Recargar: R",
        "- Cambiar arma: 1-3 o rueda del ratón",
        "- Pausar: P",
        "",
        "OBJETIVO:",
        "- Ayuda a Killer Potato a vengarse de la humanidad",
        "- Vence a los humanos y máquinas en tu camino",
        "- Cada nivel trae enemigos más fuertes y rápidos",
        "- Gana puntos por cada enemigo eliminado",
        "",
        "CONSEJO:",
        "- Busca potenciadores para mejorar tus habilidades",
        "- Algunos enemigos pueden dejarte armas especiales"
    ]
    
    back_button = Button(WIDTH//2 - 75, HEIGHT - 80, 150, 50, "VOLVER", POTATO_BROWN, RED, None)
    
    fade_transition()
    
    while running:
        screen.blit(background, (0, 0))
        
        # Crear panel semi-transparente para el contenido
        panel = pygame.Surface((WIDTH - 100, HEIGHT - 150), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        screen.blit(panel, (50, 120))
        
        # Título con efecto
        title_text = "INSTRUCCIONES"
        title_shadow = font_large.render(title_text, True, BLACK)
        title = font_large.render(title_text, True, RED)
        screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 3, 53))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Línea divisoria
        pygame.draw.line(screen, POTATO_BROWN, (100, 110), (WIDTH - 100, 110), 2)
        
        # Instrucciones con mejor formato
        for i, line in enumerate(instructions):
            if ":" in line:  # Es un título de sección
                text = font_medium.render(line, True, RED)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, 150 + i * 28))
            else:
                text = font_small.render(line, True, WHITE)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, 150 + i * 28))
        
        # Imagen del personaje
        if potato_character:
            char_x = WIDTH - 200
            char_y = HEIGHT - 200
            screen.blit(potato_character, (char_x, char_y))
            
            # Burbuja de diálogo
            bubble_width, bubble_height = 180, 60
            bubble_x = char_x - bubble_width + 40
            bubble_y = char_y - bubble_height
            
            # Dibujar la burbuja
            pygame.draw.ellipse(screen, WHITE, (bubble_x, bubble_y, bubble_width, bubble_height))
            pygame.draw.ellipse(screen, BLACK, (bubble_x, bubble_y, bubble_width, bubble_height), 2)
            
            # Punta de la burbuja
            points = [(bubble_x + bubble_width - 30, bubble_y + bubble_height),
                     (bubble_x + bubble_width - 10, bubble_y + bubble_height + 20),
                     (bubble_x + bubble_width - 5, bubble_y + bubble_height - 5)]
            pygame.draw.polygon(screen, WHITE, points)
            pygame.draw.polygon(screen, BLACK, points, 2)
            
            # Texto en la burbuja
            dialog_text = font_small.render("¡A freír humanos!", True, BLACK)
            screen.blit(dialog_text, (bubble_x + bubble_width//2 - dialog_text.get_width()//2, 
                                     bubble_y + bubble_height//2 - dialog_text.get_height()//2))
        
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
        "Images designed by various artists",
        "",
        "MÚSICA:",
        "Sound effects by various artists",
        "",
        "AGRADECIMIENTOS:",
        "Gracias por jugar a Killer Potato!"
    ]
    
    back_button = Button(WIDTH//2 - 75, HEIGHT - 80, 150, 50, "VOLVER", POTATO_BROWN, RED, None)
    
    # Papas animadas para los créditos
    class PotatoAnimation:
        def __init__(self):
            self.potatoes = []
            for _ in range(5):
                potato = {
                    'x': random.choice([-50, WIDTH + 50]),
                    'y': random.randint(HEIGHT - 150, HEIGHT - 50),
                    'speed': random.uniform(0.3, 0.8),
                    'size': random.randint(30, 50),
                    'color': (random.randint(139, 169), random.randint(69, 99), random.randint(19, 49)),
                    'direction': 1 if random.random() > 0.5 else -1
                }
                if potato['x'] > WIDTH:
                    potato['direction'] = -1
                self.potatoes.append(potato)
                
        def update(self):
            for potato in self.potatoes:
                potato['x'] += potato['speed'] * potato['direction']
                
                # Cambiar de dirección al llegar a los bordes
                if potato['x'] < -100 or potato['x'] > WIDTH + 100:
                    potato['direction'] *= -1
                    
        def draw(self, surface):
            for potato in self.potatoes:
                # Dibujar una silueta simple de papa
                color = potato['color']
                x, y = int(potato['x']), int(potato['y'])
                size = potato['size']
                
                # Cuerpo de papa (más ovalado)
                pygame.draw.ellipse(surface, color, (x-size//2, y-size//2, size, size))
                
                # Ojos
                eye_size = size * 0.15
                pygame.draw.circle(surface, BLACK, (int(x - size*0.2), int(y - size*0.1)), int(eye_size))
                pygame.draw.circle(surface, BLACK, (int(x + size*0.2), int(y - size*0.1)), int(eye_size))
                
                # Brillo en los ojos
                pygame.draw.circle(surface, WHITE, (int(x - size*0.2 + eye_size*0.5), 
                                                    int(y - size*0.1 - eye_size*0.5)), int(eye_size*0.3))
                pygame.draw.circle(surface, WHITE, (int(x + size*0.2 + eye_size*0.5), 
                                                    int(y - size*0.1 - eye_size*0.5)), int(eye_size*0.3))
                
                # Boca enojada
                mouth_start = (int(x - size*0.3), int(y + size*0.2))
                mouth_end = (int(x + size*0.3), int(y + size*0.2))
                pygame.draw.line(surface, BLACK, mouth_start, mouth_end, max(2, int(size*0.05)))
                
                # Cejas enojadas
                brow_length = size * 0.25
                brow_start_left = (int(x - size*0.3), int(y - size*0.25))
                brow_end_left = (int(x - size*0.1), int(y - size*0.15))
                pygame.draw.line(surface, BLACK, brow_start_left, brow_end_left, max(2, int(size*0.05)))
                
                brow_start_right = (int(x + size*0.3), int(y - size*0.25))
                brow_end_right = (int(x + size*0.1), int(y - size*0.15))
                pygame.draw.line(surface, BLACK, brow_start_right, brow_end_right, max(2, int(size*0.05)))
                
                # Bandana (estilo Rambo)
                bandana_top = y - size*0.4
                bandana_height = size * 0.2
                pygame.draw.rect(surface, RED, (x - size//2, bandana_top, size, bandana_height))
                
                # Extremos de la bandana
                bandana_end_length = size * 0.4
                bandana_end_width = size * 0.1
                pygame.draw.rect(surface, RED, (x - size//2, bandana_top, bandana_end_length, bandana_end_width))
                
                # Cicatrices
                scar_start = (int(x - size*0.1), int(y - size*0.3))
                scar_end = (int(x + size*0.1), int(y))
                pygame.draw.line(surface, (color[0]-30, color[1]-30, color[2]-30), 
                                scar_start, scar_end, max(1, int(size*0.03)))
    
    potato_anim = PotatoAnimation()
    scroll_offset = 0
    scroll_speed = 0.5
    
    fade_transition()
    
    while running:
        screen.blit(background, (0, 0))
        
        # Crear panel semi-transparente para el contenido
        panel = pygame.Surface((WIDTH - 100, HEIGHT - 150), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        screen.blit(panel, (50, 120))
        
        # Título con efecto
        title_text = "CRÉDITOS"
        title_shadow = font_large.render(title_text, True, BLACK)
        title = font_large.render(title_text, True, RED)
        screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 3, 53))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Línea divisoria
        pygame.draw.line(screen, POTATO_BROWN, (100, 110), (WIDTH - 100, 110), 2)
        
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
            
        # Actualizar y dibujar papas
        potato_anim.update()
        potato_anim.draw(screen)
        
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
                'color': (random.randint(150, 255), random.randint(100, 150), 0, random.randint(50, 200))  # Salsa de mostaza
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
        # Actualizar partículas de salsa
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
            fog_surface.fill((POTATO_LIGHT[0], POTATO_LIGHT[1], POTATO_LIGHT[2], fog['alpha']))
            surface.blit(fog_surface, (int(fog['x']), int(fog['y'])))
            
        # Dibujar partículas de salsa
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
    button_spacing = 70
    
    play_button = Button(button_x, 200, button_width, button_height, "JUGAR", POTATO_BROWN, RED, start_game)
    story_button = Button(button_x, 200 + button_spacing, button_width, button_height, "HISTORIA", POTATO_BROWN, RED, show_story)
    instructions_button = Button(button_x, 200 + button_spacing * 2, button_width, button_height, "INSTRUCCIONES", POTATO_BROWN, RED, show_instructions)
    credits_button = Button(button_x, 200 + button_spacing * 3, button_width, button_height, "CRÉDITOS", POTATO_BROWN, RED, show_credits)
    quit_button = Button(button_x, 200 + button_spacing * 4, button_width, button_height, "SALIR", POTATO_BROWN, RED, quit_game)
    
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
        pygame.mixer.music.load("assets/sounds/music/menu_music.mp3")
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
            story_button.handle_event(event)
            instructions_button.handle_event(event)
            credits_button.handle_event(event)
            quit_button.handle_event(event)
                
        # Actualizar posición del ratón
        mouse_pos = pygame.mouse.get_pos()
        play_button.check_hover(mouse_pos)
        story_button.check_hover(mouse_pos)
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
        
        # Marco de salsa alrededor de la pantalla
        border_width = 10
        for i in range(border_width):
            alpha = 255 - (i * 255 // border_width)
            pygame.draw.rect(screen, (POTATO_BROWN[0], POTATO_BROWN[1], POTATO_BROWN[2], alpha), 
                            (40-i, 40-i, WIDTH-80+i*2, HEIGHT-80+i*2), 1)
        
        # Dibujar efecto de fondo
        bg_effect.draw(screen)
        
        # Dibujar personaje principal
        if potato_character:
            # Posición a la derecha de los botones
            char_x = WIDTH - 170
            char_y = HEIGHT // 2
            # Aplicar efecto de flotación suave
            char_y += math.sin(pygame.time.get_ticks() / 500) * 5
            screen.blit(potato_character, (char_x, char_y))
            
            # Burbuja de diálogo ocasional
            if random.random() < 0.001:  # Probabilidad baja para que aparezca ocasionalmente
                bubble_width, bubble_height = 180, 60
                bubble_x = char_x - bubble_width + 40
                bubble_y = char_y - bubble_height
                
                # Dibujar la burbuja
                pygame.draw.ellipse(screen, WHITE, (bubble_x, bubble_y, bubble_width, bubble_height))
                pygame.draw.ellipse(screen, BLACK, (bubble_x, bubble_y, bubble_width, bubble_height), 2)
                
                # Punta de la burbuja
                points = [(bubble_x + bubble_width - 30, bubble_y + bubble_height),
                         (bubble_x + bubble_width - 10, bubble_y + bubble_height + 20),
                         (bubble_x + bubble_width - 5, bubble_y + bubble_height - 5)]
                pygame.draw.polygon(screen, WHITE, points)
                pygame.draw.polygon(screen, BLACK, points, 2)
                
                # Frases aleatorias para el diálogo
                phrases = [
                    "¡Voy a freírlos a todos!",
                    "¡La venganza será sabrosa!",
                    "¡Por mis hermanos tubérculos!",
                    "¡Soy la papa de tus pesadillas!"
                ]
                
                # Texto en la burbuja
                dialog_text = font_small.render(random.choice(phrases), True, BLACK)
                screen.blit(dialog_text, (bubble_x + bubble_width//2 - dialog_text.get_width()//2, 
                                         bubble_y + bubble_height//2 - dialog_text.get_height()//2))
        
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
                pygame.draw.ellipse(glow_surf, (POTATO_BROWN[0], POTATO_BROWN[1], 0, alpha), 
                                  (i*2, i, logo.get_width()+40-i*4, 20-i*2))
            screen.blit(glow_surf, (WIDTH//2 - glow_surf.get_width()//2, title_y + logo.get_height() + 5))
        else:
            # Título texto con efectos
            title_text = "KILLER POTATO"
            subtitle_text = "LA VENGANZA DE LA PAPA"
            
            # Sombra del título
            shadow_surf = font_title.render(title_text, True, BLACK)
            shadow_rect = shadow_surf.get_rect(center=(WIDTH//2 + 3, title_y + 3))
            screen.blit(shadow_surf, shadow_rect)
            
            # Título principal con degradado
            for i in range(len(title_text)):
                char = title_text[i]
                char_color = (max(100, 200 - i*10), min(200, i*15), 0)
                char_surf = font_title.render(char, True, char_color)
                char_pos = (WIDTH//2 - font_title.size(title_text)[0]//2 + font_title.size(title_text[:i])[0], 
                           title_y)
                screen.blit(char_surf, char_pos)
                
            # Subtítulo
            subtitle_shadow = font_medium.render(subtitle_text, True, BLACK)
            subtitle = font_medium.render(subtitle_text, True, RED)
            subtitle_y = title_y + 80
            screen.blit(subtitle_shadow, (WIDTH//2 - subtitle_shadow.get_width()//2 + 2, subtitle_y + 2))
            screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, subtitle_y))
        
        # Dibujar botones
        play_button.draw(screen)
        story_button.draw(screen)
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
        
        # Agregar efecto de flash aleatorio para ambiente
        if random.random() < 0.005:  # Probabilidad baja para que no sea molesto
            flash = pygame.Surface((WIDTH, HEIGHT))
            flash.fill(POTATO_LIGHT)
            flash.set_alpha(random.randint(5, 20))
            screen.blit(flash, (0, 0))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()