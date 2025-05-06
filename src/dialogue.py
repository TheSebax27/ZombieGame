"""
Módulo de diálogos para Killer Potato
Maneja la carga, visualización y gestión de todos los diálogos en el juego
"""

import pygame
import os
import json

# Inicializar pygame si no está inicializado
if not pygame.get_init():
    pygame.init()

if not pygame.font.get_init():
    pygame.font.init()

# Configuración de pantalla (tomar de config o usar valores por defecto)
try:
    from config.settings import WIDTH, HEIGHT
except ImportError:
    WIDTH, HEIGHT = 800, 600

# Cargar fuentes
try:
    font = pygame.font.Font("assets/fonts/potato.ttf", 24)
    font_name = pygame.font.Font("assets/fonts/potato.ttf", 28)
except:
    font = pygame.font.SysFont('Arial', 24)
    font_name = pygame.font.SysFont('Arial', 28)

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
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
        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 0, 0), surface.get_rect(), 1)
        pygame.draw.line(surface, (255, 0, 0), (0, 0), (100, 100), 2)
        pygame.draw.line(surface, (255, 0, 0), (100, 0), (0, 100), 2)
        return surface

# Cargar diálogos de archivos
def load_dialogues(level):
    """Carga los diálogos para un nivel específico desde un archivo JSON"""
    try:
        file_path = f"assets/dialogue/level{level}.json"
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error cargando diálogos del nivel {level}: {e}")
        # Devolver un diálogo de emergencia si no se puede cargar el archivo
        return [{
            "speaker": "Killer Potato",
            "text": f"¡Nivel {level}! ¡Hora de aplastar humanos!",
            "portrait": "assets/images/characters/killer_potato_dialog.png",
            "position": "bottom"
        }]

# Clase para cuadros de diálogo
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
        self.bg_color = (0, 0, 0, 180)  # Negro semi-transparente
        self.border_color = POTATO_BROWN
        self.font = font
        self.font_name = font_name
        self.portrait = None
        self.display_index = 0
        self.display_speed = 2
        self.display_counter = 0
        self.next_dialog = None
        self.complete = False
        self.dialog_queue = []
        self.sound_enabled = True
        self.text_sound = None
        
        # Intentar cargar sonido de texto
        try:
            self.text_sound = pygame.mixer.Sound("assets/sounds/sfx/text.wav")
            self.text_sound.set_volume(0.3)
        except:
            self.sound_enabled = False
    
    def set_dialog(self, text, speaker="", portrait=None, position="bottom", next_dialog=None):
        """Establece un nuevo diálogo"""
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
    
    def queue_dialog(self, dialogs):
        """Añade una lista de diálogos a la cola para mostrarlos secuencialmente"""
        if not dialogs:
            return
            
        self.dialog_queue.extend(dialogs)
        
        # Si no hay diálogo activo, mostrar el primero de la cola
        if not self.visible and self.dialog_queue:
            dialog = self.dialog_queue.pop(0)
            self.set_dialog(
                dialog.get("text", ""), 
                dialog.get("speaker", ""), 
                dialog.get("portrait", None),
                dialog.get("position", "bottom")
            )
    
    def update(self):
        """Actualiza el estado del diálogo, animando el texto"""
        if not self.visible:
            return
            
        if not self.complete:
            self.display_counter += 1
            if self.display_counter >= self.display_speed:
                self.display_counter = 0
                self.display_index += 1
                
                # Reproducir sonido de texto cada ciertos caracteres
                if self.sound_enabled and self.text_sound and self.display_index % 3 == 0:
                    self.text_sound.play()
                
                if self.display_index >= len(self.text):
                    self.complete = True
                    self.display_index = len(self.text)
    
    def draw(self, surface):
        """Dibuja el cuadro de diálogo en la pantalla"""
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
            speaker_surface = self.font_name.render(self.speaker, True, RED)
            dialog_surface.blit(speaker_surface, (text_start_x, 10))
            text_start_y = 45
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
            indicator_x = self.width - 30
            indicator_y = self.height - 25
            animation_offset = abs(pygame.time.get_ticks() % 1000 - 500) / 500.0 * 5
            
            pygame.draw.polygon(dialog_surface, WHITE, 
                              [(indicator_x, indicator_y + animation_offset), 
                               (indicator_x + 20, indicator_y + animation_offset), 
                               (indicator_x + 10, indicator_y + 10 + animation_offset)])
        
        # Dibujar el cuadro de diálogo en la superficie principal
        surface.blit(dialog_surface, (self.x, self.y))
    
    def handle_input(self, event):
        """Maneja la entrada del usuario para avanzar en el diálogo"""
        if not self.visible:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_z):
                if self.complete:
                    # Si hay más diálogos en la cola, mostrar el siguiente
                    if self.dialog_queue:
                        dialog = self.dialog_queue.pop(0)
                        self.set_dialog(
                            dialog.get("text", ""), 
                            dialog.get("speaker", ""), 
                            dialog.get("portrait", None),
                            dialog.get("position", "bottom")
                        )
                    else:
                        self.visible = False
                    return True
                else:
                    # Mostrar todo el texto inmediatamente
                    self.display_index = len(self.text)
                    self.complete = True
                    return True
        
        return False

# Función para mostrar tutorial
def show_tutorial(screen, level):
    """Muestra un tutorial específico para el nivel actual"""
    tutorials = {
        1: [
            "Usa WASD o las flechas para moverte.",
            "Haz clic izquierdo para atacar.",
            "Recoge potenciadores para obtener ventajas."
        ],
        2: [
            "Los robots son más resistentes pero más lentos.",
            "Usa R para recargar tu arma cuando te quedes sin munición.",
            "Cambia de arma con las teclas 1-3 o la rueda del ratón."
        ],
        3: [
            "Los chefs son peligrosos y hacen mucho daño.",
            "Busca armas especiales para derrotarlos más fácilmente.",
            "Usa P para pausar el juego en cualquier momento."
        ]
    }
    
    # Obtener tutoriales para el nivel actual o usar un tutorial genérico
    tutorial_texts = tutorials.get(level, ["¡Sobrevive y acaba con tus enemigos!"])
    
    # Dibujar fondo semi-transparente
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Dibujar título
    title = font_name.render(f"NIVEL {level} - CONSEJOS", True, RED)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
    
    # Dibujar textos de tutorial
    for i, text in enumerate(tutorial_texts):
        tutorial_text = font.render(text, True, WHITE)
        screen.blit(tutorial_text, (WIDTH//2 - tutorial_text.get_width()//2, HEIGHT//2 - 30 + i * 40))
    
    # Dibujar indicación para continuar
    continue_text = font.render("Presiona ESPACIO para continuar", True, WHITE)
    screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 120))
    
    # Actualizar pantalla
    pygame.display.flip()
    
    # Esperar input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_z):
                    waiting = False
        
        # Pequeña pausa para no consumir CPU
        pygame.time.delay(10)

# Función para mostrar cutscenes entre niveles
def show_cutscene(screen, level):
    """Muestra una cutscene entre niveles"""
    cutscenes = {
        1: {
            "background": "assets/images/backgrounds/cutscene1.png",
            "text": [
                "Killer Potato ha escapado del laboratorio y ahora debe enfrentarse a los guardias de seguridad.",
                "Su primer objetivo: llegar a la salida del complejo subterráneo."
            ]
        },
        2: {
            "background": "assets/images/backgrounds/cutscene2.png",
            "text": [
                "Tras escapar del laboratorio, Killer Potato se adentra en la fábrica de procesamiento.",
                "Aquí es donde sus hermanos tubérculos son convertidos en papas fritas."
            ]
        },
        3: {
            "background": "assets/images/backgrounds/cutscene3.png",
            "text": [
                "Las máquinas de la fábrica han sido reprogramadas para detener a Killer Potato.",
                "El chef supremo Crustini ha ordenado su captura a toda costa."
            ]
        }
    }
    
    # Obtener datos de la cutscene para el nivel actual o usar datos genéricos
    cutscene_data = cutscenes.get(level, {
        "background": None,
        "text": [f"Nivel {level} - La venganza continúa..."]
    })
    
    # Cargar fondo de la cutscene o usar uno negro
    try:
        if cutscene_data["background"]:
            background = load_image(cutscene_data["background"], (WIDTH, HEIGHT))
        else:
            background = pygame.Surface((WIDTH, HEIGHT))
            background.fill(BLACK)
    except:
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill(BLACK)
    
    # Animación de texto
    text_lines = cutscene_data["text"]
    display_index = 0
    line_index = 0
    display_speed = 2
    display_counter = 0
    complete = False
    
    # Reproducir sonido de cutscene si existe
    try:
        cutscene_sound = pygame.mixer.Sound("assets/sounds/sfx/cutscene.wav")
        cutscene_sound.play()
    except:
        pass
    
    # Loop de la cutscene
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_z):
                    if complete:
                        running = False
                    else:
                        # Mostrar todo el texto inmediatamente
                        display_index = len(text_lines[line_index])
                        complete = (line_index >= len(text_lines) - 1)
        
        # Dibujar fondo
        screen.blit(background, (0, 0))
        
        # Panel para texto
        text_panel = pygame.Surface((WIDTH - 100, 100), pygame.SRCALPHA)
        text_panel.fill((0, 0, 0, 200))
        screen.blit(text_panel, (50, HEIGHT - 150))
        
        # Actualizar animación de texto
        if not complete:
            display_counter += 1
            if display_counter >= display_speed:
                display_counter = 0
                display_index += 1
                
                # Pasar a la siguiente línea cuando se complete
                if display_index > len(text_lines[line_index]):
                    display_index = len(text_lines[line_index])
                    if line_index < len(text_lines) - 1:
                        line_index += 1
                        display_index = 0
                    else:
                        complete = True
        
        # Dibujar texto actual
        if line_index < len(text_lines):
            displayed_text = text_lines[line_index][:display_index]
            text_surface = font.render(displayed_text, True, WHITE)
            screen.blit(text_surface, (70, HEIGHT - 130))
        
        # Indicador para continuar si el texto está completo
        if complete:
            indicator_text = font.render("Presiona ESPACIO para continuar", True, WHITE)
            screen.blit(indicator_text, (WIDTH//2 - indicator_text.get_width()//2, HEIGHT - 50))
        
        pygame.display.flip()
        pygame.time.delay(10)

# Ejemplo de uso:
if __name__ == "__main__":
    # Inicializar pantalla para pruebas
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Prueba de Diálogos")
    
    # Crear caja de diálogo
    dialog_box = DialogBox()
    
    # Cargar diálogos de prueba
    dialogs = [
        {
            "speaker": "Killer Potato",
            "text": "¡Por fin soy libre! Ahora voy a vengarme de todos los humanos.",
            "portrait": "assets/images/characters/killer_potato_dialog.png",
            "position": "bottom"
        },
        {
            "speaker": "Científico",
            "text": "¡No! ¡El experimento 13 ha escapado! ¡Detengan a esa papa!",
            "portrait": "assets/images/characters/scientist_dialog.png",
            "position": "top"
        },
        {
            "speaker": "Killer Potato",
            "text": "Nunca más seré parte de su 'menú del día'. ¡La revolución de las papas ha comenzado!",
            "portrait": "assets/images/characters/killer_potato_dialog.png",
            "position": "bottom"
        }
    ]
    
    # Añadir diálogos a la cola
    dialog_box.queue_dialog(dialogs)
    
    # Loop principal
    running = True
    clock = pygame.time.Clock()
    while running:
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Manejar input para el diálogo
            dialog_box.handle_input(event)
        
        # Actualizar
        dialog_box.update()
        
        # Dibujar
        screen.fill((0, 0, 0))  # Fondo negro
        dialog_box.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()