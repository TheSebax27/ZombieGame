import pygame
import sys
import os
from pygame.locals import *
import random
import math

# Import the game main module
# Changed from Zombies to game
import game

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen configuration
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Killer Potato: La Venganza de la Papa")

# Load fonts
try:
    # Try to load more attractive fonts for a game
    font_small = pygame.font.Font("assets/fonts/potato.ttf", 20)
    font_medium = pygame.font.Font("assets/fonts/potato.ttf", 32)
    font_large = pygame.font.Font("assets/fonts/potato.ttf", 60)
    font_title = pygame.font.Font("assets/fonts/potato.ttf", 72)
except:
    # Fallback to system fonts
    print("No se pudieron cargar las fuentes personalizadas")
    font_small = pygame.font.SysFont('Arial', 20)
    font_medium = pygame.font.SysFont('Impact', 32)
    font_large = pygame.font.SysFont('Impact', 60)
    font_title = pygame.font.SysFont('Impact', 72)

# Colors
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

# Function to load images with error handling
def load_image(path, scale=None):
    try:
        image = pygame.image.load(path).convert_alpha()
        if scale:
            image = pygame.transform.scale(image, scale)
        return image
    except pygame.error as e:
        print(f"No se pudo cargar la imagen {path}: {e}")
        # Create a replacement surface
        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.rect(surface, (POTATO_BROWN[0], POTATO_BROWN[1], POTATO_BROWN[2], 255), surface.get_rect(), 1)
        pygame.draw.line(surface, (POTATO_BROWN[0], POTATO_BROWN[1], POTATO_BROWN[2], 255), (0, 0), (100, 100), 2)
        pygame.draw.line(surface, (POTATO_BROWN[0], POTATO_BROWN[1], POTATO_BROWN[2], 255), (100, 0), (0, 100), 2)
        return surface

# Load images
try:
    background = load_image("assets/images/backgrounds/menu_background.png", (WIDTH, HEIGHT))
    logo = load_image("assets/images/ui/game_logo.png", (550, 200))
    potato_character = load_image("assets/images/characters/killer_potato.png", (150, 150))
    splatter = load_image("assets/images/ui/sauce_splatter.png", (100, 100))
except:
    # If images can't be loaded, use color backgrounds
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(POTATO_LIGHT)
    
    # Create a fallback logo
    logo = pygame.Surface((550, 200), pygame.SRCALPHA)
    potato_character = None
    splatter = None

# Improved menu button class with cleaner style
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False
        self.alpha = 230  # Initial transparency
        self.pulse_value = 0
        self.pulse_speed = 0.03  # Reduced from 0.05
        self.pulse_direction = 1
        
    def draw(self, surface):
        # Simplified pulse effect for selected button
        if self.is_hovered:
            self.pulse_value += self.pulse_speed * self.pulse_direction
            if self.pulse_value >= 1.0:
                self.pulse_value = 1.0
                self.pulse_direction = -1
            elif self.pulse_value <= 0.0:
                self.pulse_value = 0.0
                self.pulse_direction = 1
                
            pulse_offset = int(self.pulse_value * 3)  # Reduced from 5
            color = self.hover_color
        else:
            pulse_offset = 0
            color = self.color
            
        # Create surface for button with transparency
        button_surface = pygame.Surface((self.rect.width + pulse_offset*2, self.rect.height + pulse_offset*2), pygame.SRCALPHA)
        
        # Draw button shape with more subtle border
        pygame.draw.rect(button_surface, (*color, self.alpha), 
                       (0, 0, self.rect.width + pulse_offset*2, self.rect.height + pulse_offset*2), 0, 8)
        
        # Border
        if self.is_hovered:
            border_color = POTATO_BROWN
            border_width = 2  # Reduced from 3
        else:
            border_color = DARK_RED
            border_width = 1  # Reduced from 2
            
        pygame.draw.rect(button_surface, (*border_color, 255), 
                       (0, 0, self.rect.width + pulse_offset*2, self.rect.height + pulse_offset*2), border_width, 8)
        
        # Draw text with subtle shadow effect
        if self.is_hovered:
            text_surf = font_medium.render(self.text, True, WHITE)
        else:
            text_surf = font_medium.render(self.text, True, LIGHT_GRAY)
            
        # Text shadow (more subtle)
        shadow_surf = font_medium.render(self.text, True, BLACK)
        shadow_rect = shadow_surf.get_rect(center=(button_surface.get_width()//2 + 1, button_surface.get_height()//2 + 1))
        button_surface.blit(shadow_surf, shadow_rect)
        
        # Main text
        text_rect = text_surf.get_rect(center=(button_surface.get_width()//2, button_surface.get_height()//2))
        button_surface.blit(text_surf, text_rect)
        
        # Draw the button on the main surface
        surface.blit(button_surface, (self.rect.x - pulse_offset, self.rect.y - pulse_offset))
        
        # Small potato icon when hovered (instead of large character)
        if self.is_hovered and potato_character:
            icon_offset = int(math.sin(pygame.time.get_ticks() / 400) * 2)  # Reduced movement
            icon_scale = (40, 40)  # Smaller icon
            try:
                icon = pygame.transform.scale(potato_character, icon_scale)
                surface.blit(icon, (self.rect.x - 50, self.rect.y + self.rect.height//2 - 20 + icon_offset))
            except:
                pass
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            # Sound effect on click
            try:
                click_sound = pygame.mixer.Sound("assets/sounds/sfx/button_click.wav")
                click_sound.play()
            except:
                pass
                
            if self.action:
                self.action()
            return True
        return False

# Button action functions
def start_game():
    print("Starting game...")
    # Screen transition before starting
    fade_transition()
    # Call the main game
    game.main()
    
def show_instructions():
    print("Showing instructions...")
    # Change to instructions screen
    instructions_screen()
    
def show_credits():
    print("Showing credits...")
    # Change to credits screen
    credits_screen()

def show_story():
    print("Showing story...")
    # Change to story screen
    story_screen()
    
def quit_game():
    print("Exiting game...")
    fade_transition(fade_in=False)
    pygame.quit()
    sys.exit()

# Transition effects
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

# Simplified background effect class
class BackgroundEffect:
    def __init__(self):
        self.particles = []
        self.fog_particles = []
        self.max_particles = 15  # Reduced from 30
        self.max_fog = 8  # Reduced from 15
        self.generate_particles()
        self.generate_fog()
        
    def generate_particles(self):
        for _ in range(self.max_particles):
            particle = {
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'size': random.randint(1, 3),  # Smaller particles
                'speed': random.uniform(0.3, 1.5),  # Slower movement
                'color': (random.randint(150, 255), random.randint(100, 150), 0, random.randint(30, 150))  # Less opaque
            }
            self.particles.append(particle)
    
    def generate_fog(self):
        for _ in range(self.max_fog):
            fog = {
                'x': random.randint(-200, WIDTH),
                'y': random.randint(0, HEIGHT),
                'width': random.randint(100, 300),
                'height': random.randint(50, 150),
                'speed': random.uniform(0.1, 0.3),  # Slower movement
                'alpha': random.randint(5, 15)  # More transparent
            }
            self.fog_particles.append(fog)
            
    def update(self):
        # Update sauce particles
        for particle in self.particles:
            particle['y'] += particle['speed']
            
            # Reset particle if it leaves the screen
            if particle['y'] > HEIGHT:
                particle['y'] = random.randint(-50, 0)
                particle['x'] = random.randint(0, WIDTH)
                
        # Update fog
        for fog in self.fog_particles:
            fog['x'] += fog['speed']
            
            # Reset fog if it leaves the screen
            if fog['x'] > WIDTH + 100:
                fog['x'] = random.randint(-300, -100)
                fog['y'] = random.randint(0, HEIGHT)
                
    def draw(self, surface):
        # Draw fog (more subtle)
        for fog in self.fog_particles:
            fog_surface = pygame.Surface((fog['width'], fog['height']), pygame.SRCALPHA)
            fog_surface.fill((POTATO_LIGHT[0], POTATO_LIGHT[1], POTATO_LIGHT[2], fog['alpha']))
            surface.blit(fog_surface, (int(fog['x']), int(fog['y'])))
            
        # Draw sauce particles (more subtle)
        for particle in self.particles:
            pygame.draw.circle(
                surface, 
                particle['color'], 
                (int(particle['x']), int(particle['y'])), 
                particle['size']
            )
            # Simplified drip effect (less frequent)
            if particle['size'] > 2 and random.random() > 0.9:
                drip_height = random.randint(3, 10)  # Shorter drips
                drip_color = (particle['color'][0], particle['color'][1], particle['color'][2], 
                            particle['color'][3] // 2)
                pygame.draw.line(
                    surface,
                    drip_color,
                    (int(particle['x']), int(particle['y'])),
                    (int(particle['x']), int(particle['y']) + drip_height),
                    1
                )

# Story screen function
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
    
    # Simplified sauce drops effect (fewer drops)
    sauce_drops = []
    for _ in range(8):  # Reduced from 15
        drop = {
            'x': random.randint(0, WIDTH),
            'y': random.randint(-500, -50),
            'speed': random.uniform(0.5, 1.5),  # Slower
            'size': random.randint(2, 5),  # Smaller
            'color': (random.randint(150, 255), 0, 0)  # Red for sauce
        }
        sauce_drops.append(drop)
    
    fade_transition()
    
    # Display all text at once (no animation)
    text_display_index = len(story_text)
    
    story_image = None
    try:
        story_image = load_image("assets/images/backgrounds/story_scene.png", (400, 300))
    except:
        pass
    
    while running:
        screen.blit(background, (0, 0))
        
        # Create semi-transparent panel for content (cleaner)
        panel = pygame.Surface((WIDTH - 140, HEIGHT - 180), pygame.SRCALPHA)  # Larger margins
        panel.fill((0, 0, 0, 160))  # More transparent
        screen.blit(panel, (70, 130))  # Positioned with more space
        
        # Show story image if available
        if story_image:
            screen.blit(story_image, (WIDTH//2 - story_image.get_width()//2, 150))
            text_start_y = 460  # Below image
        else:
            text_start_y = 170  # No image, text higher up
        
        # Title with effect (more subtle)
        title_text = "LA HISTORIA"
        title_shadow = font_large.render(title_text, True, BLACK)
        title = font_large.render(title_text, True, RED)
        screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 2, 52))  # Reduced shadow
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Simple divider line
        pygame.draw.line(screen, POTATO_BROWN, (100, 110), (WIDTH - 100, 110), 2)
        
        # Show all text directly (no animation)
        for i in range(min(text_display_index, len(story_text))):
            line = story_text[i]
            if line == "":  # Empty line
                continue
            else:
                text = font_small.render(line, True, WHITE)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, text_start_y + i * 25))
        
        # Update and draw sauce drops (more subtle)
        for drop in sauce_drops:
            drop['y'] += drop['speed']
            if drop['y'] > HEIGHT:
                drop['y'] = random.randint(-200, -50)
                drop['x'] = random.randint(0, WIDTH)
            
            pygame.draw.circle(screen, drop['color'], (int(drop['x']), int(drop['y'])), drop['size'])
            # Simple trail
            pygame.draw.circle(screen, (drop['color'][0]-50, 0, 0), 
                            (int(drop['x']), int(drop['y']) - 3), drop['size'] - 1)
        
        # Back button
        mouse_pos = pygame.mouse.get_pos()
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)
        
        # Event handling
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

# Instructions screen function with improved design
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
        
        # Create cleaner panel for content
        panel = pygame.Surface((WIDTH - 140, HEIGHT - 180), pygame.SRCALPHA)  # Increased margins
        panel.fill((0, 0, 0, 160))  # More transparent
        screen.blit(panel, (70, 130))  # Better positioning
        
        # Title with subtle effect
        title_text = "INSTRUCCIONES"
        title_shadow = font_large.render(title_text, True, BLACK)
        title = font_large.render(title_text, True, RED)
        screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 2, 52))  # Reduced shadow
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Simple divider
        pygame.draw.line(screen, POTATO_BROWN, (100, 110), (WIDTH - 100, 110), 2)
        
        # Instructions with better spacing
        for i, line in enumerate(instructions):
            if ":" in line:  # Section title
                text = font_medium.render(line, True, RED)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, 170 + i * 28))
            else:
                text = font_small.render(line, True, WHITE)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, 170 + i * 28))
        
        # Character image to one side (less intrusive)
        if potato_character:
            char_x = WIDTH - 180
            char_y = HEIGHT - 180
            screen.blit(potato_character, (char_x, char_y))
            
            # Simple speech bubble
            bubble_width, bubble_height = 180, 60
            bubble_x = char_x - bubble_width + 40
            bubble_y = char_y - bubble_height
            
            # Draw bubble
            pygame.draw.ellipse(screen, WHITE, (bubble_x, bubble_y, bubble_width, bubble_height))
            pygame.draw.ellipse(screen, BLACK, (bubble_x, bubble_y, bubble_width, bubble_height), 2)
            
            # Bubble tip
            points = [(bubble_x + bubble_width - 30, bubble_y + bubble_height),
                     (bubble_x + bubble_width - 10, bubble_y + bubble_height + 20),
                     (bubble_x + bubble_width - 5, bubble_y + bubble_height - 5)]
            pygame.draw.polygon(screen, WHITE, points)
            pygame.draw.polygon(screen, BLACK, points, 2)
            
            # Text in bubble
            dialog_text = font_small.render("¡A freír humanos!", True, BLACK)
            screen.blit(dialog_text, (bubble_x + bubble_width//2 - dialog_text.get_width()//2, 
                                     bubble_y + bubble_height//2 - dialog_text.get_height()//2))
        
        # Back button
        mouse_pos = pygame.mouse.get_pos()
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)
        
        # Event handling
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

# Credits screen function with static credits (no scrolling)
def credits_screen():
    running = True
    
    # Static credits (no scrolling)
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
    
    # Simplified potato animations
    class PotatoAnimation:
        def __init__(self):
            self.potatoes = []
            for _ in range(3):  # Reduced from 5
                potato = {
                    'x': random.choice([-50, WIDTH + 50]),
                    'y': random.randint(HEIGHT - 150, HEIGHT - 50),
                    'speed': random.uniform(0.2, 0.5),  # Slower
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
                
                # Change direction at edges
                if potato['x'] < -100 or potato['x'] > WIDTH + 100:
                    potato['direction'] *= -1
                    
        def draw(self, surface):
            for potato in self.potatoes:
                # Draw simple potato silhouette
                color = potato['color']
                x, y = int(potato['x']), int(potato['y'])
                size = potato['size']
                
                # Potato body (more oval)
                pygame.draw.ellipse(surface, color, (x-size//2, y-size//2, size, size))
                
                # Eyes
                eye_size = size * 0.15
                pygame.draw.circle(surface, BLACK, (int(x - size*0.2), int(y - size*0.1)), int(eye_size))
                pygame.draw.circle(surface, BLACK, (int(x + size*0.2), int(y - size*0.1)), int(eye_size))
                
                # Eye highlights
                pygame.draw.circle(surface, WHITE, (int(x - size*0.2 + eye_size*0.5), 
                                                  int(y - size*0.1 - eye_size*0.5)), int(eye_size*0.3))
                pygame.draw.circle(surface, WHITE, (int(x + size*0.2 + eye_size*0.5), 
                                                  int(y - size*0.1 - eye_size*0.5)), int(eye_size*0.3))
                
                # Angry mouth
                mouth_start = (int(x - size*0.3), int(y + size*0.2))
                mouth_end = (int(x + size*0.3), int(y + size*0.2))
                pygame.draw.line(surface, BLACK, mouth_start, mouth_end, max(2, int(size*0.05)))
                
                # Angry eyebrows
                brow_length = size * 0.25
                brow_start_left = (int(x - size*0.3), int(y - size*0.25))
                brow_end_left = (int(x - size*0.1), int(y - size*0.15))
                pygame.draw.line(surface, BLACK, brow_start_left, brow_end_left, max(2, int(size*0.05)))
                
                brow_start_right = (int(x + size*0.3), int(y - size*0.25))
                brow_end_right = (int(x + size*0.1), int(y - size*0.15))
                pygame.draw.line(surface, BLACK, brow_start_right, brow_end_right, max(2, int(size*0.05)))
                
                # Bandana (Rambo style)
                bandana_top = y - size*0.4
                bandana_height = size * 0.2
                pygame.draw.rect(surface, RED, (x - size//2, bandana_top, size, bandana_height))
                
                # Bandana ends
                bandana_end_length = size * 0.4
                bandana_end_width = size * 0.1
                pygame.draw.rect(surface, RED, (x - size//2, bandana_top, bandana_end_length, bandana_end_width))
    
    potato_anim = PotatoAnimation()
    
    fade_transition()
    
    while running:
        screen.blit(background, (0, 0))
        
        # Cleaner content panel
        panel = pygame.Surface((WIDTH - 140, HEIGHT - 180), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 160))
        screen.blit(panel, (70, 130))
        
        # Title with subtle effect
        title_text = "CRÉDITOS"
        title_shadow = font_large.render(title_text, True, BLACK)
        title = font_large.render(title_text, True, RED)
        screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 2, 52))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Simple divider
        pygame.draw.line(screen, POTATO_BROWN, (100, 110), (WIDTH - 100, 110), 2)
        
        # Static credits (no scrolling animation)
        for i, line in enumerate(credits):
            if ":" in line:  # Section title
                text = font_medium.render(line, True, RED)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, 170 + i * 35))
            else:
                text = font_small.render(line, True, WHITE)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, 170 + i * 35))
        
        # Update and draw potatoes
        potato_anim.update()
        potato_anim.draw(screen)
        
        # Back button
        mouse_pos = pygame.mouse.get_pos()
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)
        
        # Event handling
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

# Improved main menu function with stationary title (no animation)
def main():
    clock = pygame.time.Clock()
    
    # Create buttons with more spacing
    button_width, button_height = 220, 60
    button_x = WIDTH // 2 - button_width // 2
    button_spacing = 90  # Increased from 70 for better spacing
    
    play_button = Button(button_x, 250, button_width, button_height, "JUGAR", POTATO_BROWN, RED, start_game)
    story_button = Button(button_x, 250 + button_spacing, button_width, button_height, "HISTORIA", POTATO_BROWN, RED, show_story)
    instructions_button = Button(button_x, 250 + button_spacing * 2, button_width, button_height, "INSTRUCCIONES", POTATO_BROWN, RED, show_instructions)
    credits_button = Button(button_x, 250 + button_spacing * 3, button_width, button_height, "CRÉDITOS", POTATO_BROWN, RED, show_credits)
    quit_button = Button(button_x, 250 + button_spacing * 4, button_width, button_height, "SALIR", POTATO_BROWN, RED, quit_game)
    
    # Simplified background effect
    bg_effect = BackgroundEffect()
    
    # Title positioning (static, no animation)
    title_y = 80  # Fixed position instead of animated
    title_scale = 1.0
    title_scale_direction = 0.0005  # Very subtle pulse
    title_angle = 0
    
    # Background music
    try:
        pygame.mixer.music.load("assets/sounds/music/menu_music.mp3")
        pygame.mixer.music.play(-1)  # Loop playback
        pygame.mixer.music.set_volume(0.7)
    except:
        print("No se pudo cargar la música de fondo")
    
    # Initial transition
    fade_transition()
    
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                fade_transition(fade_in=False)
                running = False
                
            # Check button clicks
            play_button.handle_event(event)
            story_button.handle_event(event)
            instructions_button.handle_event(event)
            credits_button.handle_event(event)
            quit_button.handle_event(event)
                
        # Update mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        play_button.check_hover(mouse_pos)
        story_button.check_hover(mouse_pos)
        instructions_button.check_hover(mouse_pos)
        credits_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
        
        # Update background effect
        bg_effect.update()
        
        # Very subtle pulse effect for title (no vertical movement)
        title_scale += title_scale_direction
        if title_scale > 1.02:  # Reduced from 1.03
            title_scale = 1.02
            title_scale_direction = -0.0005
        elif title_scale < 0.98:  # Increased from 0.97
            title_scale = 0.98
            title_scale_direction = 0.0005
            
        # Minimal oscillation for title
        title_angle = math.sin(pygame.time.get_ticks() / 2000) * 1  # Slower, smaller rotation
        
        # Draw background
        screen.blit(background, (0, 0))
        
        # Cleaner panel with more space
        panel = pygame.Surface((WIDTH - 140, HEIGHT - 140), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 150))  # More transparent
        screen.blit(panel, (70, 70))  # More margin
        
        # Simple, thinner border
        border_width = 4
        for i in range(border_width):
            alpha = 200 - (i * 200 // border_width)
            pygame.draw.rect(screen, (POTATO_BROWN[0], POTATO_BROWN[1], POTATO_BROWN[2], alpha), 
                            (70-i, 70-i, WIDTH-140+i*2, HEIGHT-140+i*2), 1)
        
        # Draw background effect (subtler)
        bg_effect.draw(screen)
        
        # Draw character in a less intrusive position
        if potato_character:
            char_x = WIDTH - 160
            char_y = HEIGHT - 180
            # Minimal floating effect
            char_y += math.sin(pygame.time.get_ticks() / 1000) * 3  # Slower, smaller movement
            screen.blit(potato_character, (char_x, char_y))
        
        # Draw logo or title with minimal effects (fixed position)
        if logo:
            # Simple logo animation (just subtle rotation/scale, no vertical movement)
            rotated_logo = pygame.transform.rotozoom(logo, title_angle, title_scale)
            logo_rect = rotated_logo.get_rect(center=(WIDTH//2, title_y + logo.get_height()//2))
            screen.blit(rotated_logo, logo_rect.topleft)
            
            # Simplified glow effect
            glow_surf = pygame.Surface((logo.get_width()+20, 10), pygame.SRCALPHA)
            for i in range(5):  # Fewer iterations
                alpha = 100 - i * 20  # Less intense
                if alpha < 0:
                    alpha = 0
                pygame.draw.ellipse(glow_surf, (POTATO_BROWN[0], POTATO_BROWN[1], 0, alpha), 
                                  (i, i, logo.get_width()+20-i*2, 10-i*2))
            screen.blit(glow_surf, (WIDTH//2 - glow_surf.get_width()//2, title_y + logo.get_height() + 5))
        else:
            # Simplified title text (fixed position)
            title_text = "KILLER POTATO"
            subtitle_text = "LA VENGANZA DE LA PAPA"
            
            # Simple shadow
            shadow_surf = font_title.render(title_text, True, BLACK)
            shadow_rect = shadow_surf.get_rect(center=(WIDTH//2 + 2, title_y + 2))  # Reduced shadow offset
            screen.blit(shadow_surf, shadow_rect)
            
            # Main title
            title_surf = font_title.render(title_text, True, RED)
            title_rect = title_surf.get_rect(center=(WIDTH//2, title_y))
            screen.blit(title_surf, title_rect)
                
            # Subtitle
            subtitle_shadow = font_medium.render(subtitle_text, True, BLACK)
            subtitle = font_medium.render(subtitle_text, True, RED)
            subtitle_y = title_y + 80
            screen.blit(subtitle_shadow, (WIDTH//2 - subtitle_shadow.get_width()//2 + 2, subtitle_y + 2))
            screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, subtitle_y))
        
        # Draw buttons
        play_button.draw(screen)
        story_button.draw(screen)
        instructions_button.draw(screen)
        credits_button.draw(screen)
        quit_button.draw(screen)
        
        # Version info
        version_text = font_small.render("v1.0", True, LIGHT_GRAY)
        version_shadow = font_small.render("v1.0", True, BLACK)
        screen.blit(version_shadow, (WIDTH - version_shadow.get_width() - 14, HEIGHT - version_shadow.get_height() - 14))
        screen.blit(version_text, (WIDTH - version_text.get_width() - 15, HEIGHT - version_text.get_height() - 15))
        
        # Creator info
        creator_text = font_small.render("© Juan Sebastian Silva P.", True, LIGHT_GRAY)
        creator_shadow = font_small.render("© Juan Sebastian Silva P.", True, BLACK)
        screen.blit(creator_shadow, (16, HEIGHT - creator_shadow.get_height() - 14))
        screen.blit(creator_text, (15, HEIGHT - creator_text.get_height() - 15))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()