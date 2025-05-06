"""
Módulo de UI para Killer Potato
Contiene elementos de interfaz de usuario y menús en el juego
"""

import pygame
import math
import random
from pygame.locals import *

# Inicializar pygame si no está inicializado
if not pygame.get_init():
    pygame.init()

# Configuración de pantalla
try:
    from config.settings import WIDTH, HEIGHT
except ImportError:
    WIDTH, HEIGHT = 800, 600

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
        pygame.draw.rect(surface, (255, 0, 0), surface.get_rect(), 1)
        pygame.draw.line(surface, (255, 0, 0), (0, 0), (50, 50), 2)
        pygame.draw.line(surface, (255, 0, 0), (50, 0), (0, 50), 2)
        return surface

# Clase para botones
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None, font=None):
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
        
        # Fuente
        if font:
            self.font = font
        else:
            try:
                self.font = pygame.font.Font("assets/fonts/potato.ttf", 24)
            except:
                self.font = pygame.font.SysFont('Arial', 24)
        
        # Sonido
        self.click_sound = None
        try:
            self.click_sound = pygame.mixer.Sound("assets/sounds/sfx/button_click.wav")
        except:
            pass
        
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
        
        # Borde
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
            text_surf = self.font.render(self.text, True, WHITE)
        else:
            text_surf = self.font.render(self.text, True, (200, 200, 200))
            
        # Sombra del texto
        shadow_surf = self.font.render(self.text, True, BLACK)
        shadow_rect = shadow_surf.get_rect(center=(button_surface.get_width()//2 + 2, button_surface.get_height()//2 + 2))
        button_surface.blit(shadow_surf, shadow_rect)
        
        # Texto principal
        text_rect = text_surf.get_rect(center=(button_surface.get_width()//2, button_surface.get_height()//2))
        button_surface.blit(text_surf, text_rect)
        
        # Dibujar el botón en la superficie principal
        surface.blit(button_surface, (self.rect.x - pulse_offset, self.rect.y - pulse_offset))
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            # Efecto de sonido al hacer clic
            if self.click_sound:
                self.click_sound.play()
                
            if self.action:
                self.action()
            return True
        return False

# Clase para barras de progreso
class ProgressBar:
    def __init__(self, x, y, width, height, progress=0, max_value=100, color=GREEN, bg_color=GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.progress = progress
        self.max_value = max_value
        self.color = color
        self.bg_color = bg_color
        self.border_color = BLACK
        self.border_width = 2
        self.text_color = WHITE
        self.show_text = True
        self.font = None
        
        try:
            self.font = pygame.font.Font("assets/fonts/potato.ttf", 16)
        except:
            self.font = pygame.font.SysFont('Arial', 16)
    
    def update(self, new_value):
        self.progress = new_value
        
    def draw(self, surface):
        # Dibujar fondo
        pygame.draw.rect(surface, self.bg_color, self.rect)
        
        # Calcular ancho de la barra
        progress_width = int(self.rect.width * (self.progress / self.max_value))
        progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
        
        # Dibujar barra de progreso
        pygame.draw.rect(surface, self.color, progress_rect)
        
        # Dibujar borde
        pygame.draw.rect(surface, self.border_color, self.rect, self.border_width)
        
        # Mostrar texto si está activado
        if self.show_text:
            if self.max_value == 100:
                text = f"{int(self.progress)}%"
            else:
                text = f"{int(self.progress)}/{self.max_value}"
                
            text_surf = self.font.render(text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

# Clase para el menú de pausa
class PauseMenu:
    def __init__(self):
        self.visible = False
        self.buttons = []
        self.title_font = None
        self.background = None
        
        # Cargar fuentes
        try:
            self.title_font = pygame.font.Font("assets/fonts/potato.ttf", 36)
            self.text_font = pygame.font.Font("assets/fonts/potato.ttf", 24)
        except:
            self.title_font = pygame.font.SysFont('Arial', 36)
            self.text_font = pygame.font.SysFont('Arial', 24)
            
        # Cargar fondo
        try:
            self.background = load_image("assets/images/ui/pause_background.png", (WIDTH, HEIGHT))
        except:
            # Crear fondo semitransparente
            self.background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            self.background.fill((0, 0, 0, 180))
            
        # Crear botones
        button_width, button_height = 200, 50
        button_x = WIDTH // 2 - button_width // 2
        
        self.buttons.append(Button(
            button_x, 
            HEIGHT // 2 - 25, 
            button_width, 
            button_height, 
            "CONTINUAR", 
            DARK_RED, 
            RED, 
            self.resume,
            self.text_font
        ))
        
        self.buttons.append(Button(
            button_x, 
            HEIGHT // 2 + 50, 
            button_width, 
            button_height, 
            "REINICIAR", 
            DARK_RED, 
            RED, 
            self.restart,
            self.text_font
        ))
        
        self.buttons.append(Button(
            button_x, 
            HEIGHT // 2 + 125, 
            button_width, 
            button_height, 
            "SALIR", 
            DARK_RED, 
            RED, 
            self.quit,
            self.text_font
        ))
        
        # Callbacks
        self.resume_callback = None
        self.restart_callback = None
        self.quit_callback = None
    
    def set_callbacks(self, resume_func, restart_func, quit_func):
        self.resume_callback = resume_func
        self.restart_callback = restart_func
        self.quit_callback = quit_func
    
    def resume(self):
        self.visible = False
        if self.resume_callback:
            self.resume_callback()
    
    def restart(self):
        self.visible = False
        if self.restart_callback:
            self.restart_callback()
    
    def quit(self):
        if self.quit_callback:
            self.quit_callback()
    
    def show(self):
        self.visible = True
    
    def hide(self):
        self.visible = False
    
    def handle_event(self, event):
        if not self.visible:
            return False
            
        for button in self.buttons:
            if button.handle_event(event):
                return True
                
        return False
    
    def update(self):
        if not self.visible:
            return
            
        # Actualizar botones
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.check_hover(mouse_pos)
    
    def draw(self, surface):
        if not self.visible:
            return
            
        # Dibujar fondo semitransparente
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            
        # Dibujar título
        title = self.title_font.render("PAUSA", True, WHITE)
        shadow = self.title_font.render("PAUSA", True, BLACK)
        shadow_rect = shadow.get_rect(center=(WIDTH//2 + 3, HEIGHT//2 - 100 + 3))
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
        
        surface.blit(shadow, shadow_rect)
        surface.blit(title, title_rect)
        
        # Dibujar botones
        for button in self.buttons:
            button.draw(surface)

# Clase para la pantalla de mejoras/habilidades
class UpgradeScreen:
    def __init__(self, player):
        self.visible = False
        self.player = player
        self.buttons = []
        self.title_font = None
        self.text_font = None
        self.detail_font = None
        self.background = None
        
        # Cargar fuentes
        try:
            self.title_font = pygame.font.Font("assets/fonts/potato.ttf", 36)
            self.text_font = pygame.font.Font("assets/fonts/potato.ttf", 24)
            self.detail_font = pygame.font.Font("assets/fonts/potato.ttf", 18)
        except:
            self.title_font = pygame.font.SysFont('Arial', 36)
            self.text_font = pygame.font.SysFont('Arial', 24)
            self.detail_font = pygame.font.SysFont('Arial', 18)
            
        # Cargar fondo
        try:
            self.background = load_image("assets/images/ui/upgrade_background.png", (WIDTH, HEIGHT))
        except:
            # Crear fondo semitransparente
            self.background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            self.background.fill((0, 0, 0, 180))
            
        # Crear botones de mejora
        self.create_buttons()
        
        # Botón de vuelta
        self.back_button = Button(
            WIDTH // 2 - 100, 
            HEIGHT - 80, 
            200, 
            50, 
            "VOLVER", 
            DARK_RED, 
            RED, 
            self.hide,
            self.text_font
        )
        
        # Callback
        self.on_upgrade = None
    
    def create_buttons(self):
        self.buttons = []
        
        # Definir mejoras disponibles
        upgrades = [
            {"stat": "health", "name": "SALUD", "desc": "Aumenta tu salud máxima", "icon": "assets/images/ui/health_icon.png"},
            {"stat": "attack", "name": "ATAQUE", "desc": "Aumenta tu daño", "icon": "assets/images/ui/attack_icon.png"},
            {"stat": "defense", "name": "DEFENSA", "desc": "Reduce el daño recibido", "icon": "assets/images/ui/defense_icon.png"},
            {"stat": "speed", "name": "VELOCIDAD", "desc": "Aumenta tu velocidad de movimiento", "icon": "assets/images/ui/speed_icon.png"},
            {"stat": "critical", "name": "CRÍTICO", "desc": "Aumenta la probabilidad de golpes críticos", "icon": "assets/images/ui/critical_icon.png"}
        ]
        
        # Crear botones
        button_width, button_height = 180, 60
        
        for i, upgrade in enumerate(upgrades):
            # Posición en cuadrícula 3x2
            row = i // 3
            col = i % 3
            
            x = WIDTH // 4 + col * 200
            y = HEIGHT // 4 + row * 120
            
            # Función de mejora específica para este botón
            def make_upgrade_func(stat=upgrade["stat"]):
                return lambda: self.upgrade_stat(stat)
                
            # Crear botón
            button = Button(
                x, 
                y, 
                button_width, 
                button_height, 
                upgrade["name"], 
                DARK_RED, 
                RED, 
                make_upgrade_func(),
                self.text_font
            )
            
            # Añadir información adicional al botón
            button.description = upgrade["desc"]
            button.stat = upgrade["stat"]
            
            # Cargar icono si existe
            try:
                button.icon = load_image(upgrade["icon"], (32, 32))
            except:
                button.icon = None
                
            self.buttons.append(button)
    
    def set_callback(self, upgrade_func):
        self.on_upgrade = upgrade_func
    
    def upgrade_stat(self, stat):
        if self.player.skill_points <= 0:
            return False
            
        if self.player.upgrade_stat(stat):
            if self.on_upgrade:
                self.on_upgrade(stat)
            
            # Efecto de sonido
            try:
                upgrade_sound = pygame.mixer.Sound("assets/sounds/sfx/upgrade.wav")
                upgrade_sound.play()
            except:
                pass
                
            return True
            
        return False
    
    def show(self):
        self.visible = True
    
    def hide(self):
        self.visible = False
    
    def handle_event(self, event):
        if not self.visible:
            return False
            
        for button in self.buttons:
            if button.handle_event(event):
                return True
                
        if self.back_button.handle_event(event):
            return True
                
        return False
    
    def update(self):
        if not self.visible:
            return
            
        # Actualizar botones
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.check_hover(mouse_pos)
            
        self.back_button.check_hover(mouse_pos)
    
    def draw(self, surface):
        if not self.visible:
            return
            
        # Dibujar fondo semitransparente
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            
        # Dibujar título
        title = self.title_font.render("MEJORAS", True, WHITE)
        shadow = self.title_font.render("MEJORAS", True, BLACK)
        shadow_rect = shadow.get_rect(center=(WIDTH//2 + 3, 60 + 3))
        title_rect = title.get_rect(center=(WIDTH//2, 60))
        
        surface.blit(shadow, shadow_rect)
        surface.blit(title, title_rect)
        
        # Mostrar puntos disponibles
        points_text = self.text_font.render(f"Puntos disponibles: {self.player.skill_points}", True, (255, 215, 0))
        points_rect = points_text.get_rect(center=(WIDTH//2, 110))
        surface.blit(points_text, points_rect)
        
        # Dibujar botones
        for button in self.buttons:
            button.draw(surface)
            
            # Dibujar icono junto al botón
            if hasattr(button, 'icon') and button.icon:
                icon_x = button.rect.x - 40
                icon_y = button.rect.y + button.rect.height // 2 - button.icon.get_height() // 2
                surface.blit(button.icon, (icon_x, icon_y))
            
            # Mostrar descripción si está seleccionado
            if button.is_hovered:
                desc_text = self.detail_font.render(button.description, True, WHITE)
                desc_rect = desc_text.get_rect(center=(WIDTH//2, HEIGHT - 150))
                surface.blit(desc_text, desc_rect)
                
                # Mostrar valor actual de la estadística
                current_value = ""
                if button.stat == "health":
                    current_value = f"Valor actual: {self.player.max_health}"
                elif button.stat == "attack":
                    current_value = f"Valor actual: {self.player.attack_power:.1f}x"
                elif button.stat == "defense":
                    current_value = f"Valor actual: {self.player.defense:.1f}x"
                elif button.stat == "speed":
                    current_value = f"Valor actual: {self.player.speed:.1f}"
                elif button.stat == "critical":
                    current_value = f"Valor actual: {int(self.player.critical_chance * 100)}%"
                    
                value_text = self.detail_font.render(current_value, True, WHITE)
                value_rect = value_text.get_rect(center=(WIDTH//2, HEIGHT - 120))
                surface.blit(value_text, value_rect)
        
        # Dibujar botón de volver
        self.back_button.draw(surface)

# Clase para la pantalla de game over
class GameOverScreen:
    def __init__(self):
        self.visible = False
        self.text_font = None
        self.title_font = None
        self.background = None
        self.score = 0
        self.level = 1
        self.time_played = 0
        
        # Cargar fuentes
        try:
            self.title_font = pygame.font.Font("assets/fonts/potato.ttf", 48)
            self.text_font = pygame.font.Font("assets/fonts/potato.ttf", 24)
        except:
            self.title_font = pygame.font.SysFont('Arial', 48)
            self.text_font = pygame.font.SysFont('Arial', 24)
        
        # Cargar fondo
        try:
            self.background = load_image("assets/images/ui/gameover_background.png", (WIDTH, HEIGHT))
        except:
            # Fondo negro como fallback
            self.background = None
        
        # Crear botones
        self.restart_button = Button(
            WIDTH // 2 - 100, 
            HEIGHT // 2 + 50, 
            200, 
            50, 
            "REINTENTAR", 
            DARK_RED, 
            RED, 
            self.restart,
            self.text_font
        )
        
        self.quit_button = Button(
            WIDTH // 2 - 100, 
            HEIGHT // 2 + 120, 
            200, 
            50, 
            "SALIR", 
            DARK_RED, 
            RED, 
            self.quit,
            self.text_font
        )
        
        # Callbacks
        self.restart_callback = None
        self.quit_callback = None
    
    def set_callbacks(self, restart_func, quit_func):
        self.restart_callback = restart_func
        self.quit_callback = quit_func
    
    def restart(self):
        self.visible = False
        if self.restart_callback:
            self.restart_callback()
    
    def quit(self):
        if self.quit_callback:
            self.quit_callback()
    
    def show(self, score, level, time_played):
        self.visible = True
        self.score = score
        self.level = level
        self.time_played = time_played
    
    def hide(self):
        self.visible = False
    
    def handle_event(self, event):
        if not self.visible:
            return False
            
        if self.restart_button.handle_event(event):
            return True
            
        if self.quit_button.handle_event(event):
            return True
                
        return False
    
    def update(self):
        if not self.visible:
            return
            
        # Actualizar botones
        mouse_pos = pygame.mouse.get_pos()
        self.restart_button.check_hover(mouse_pos)
        self.quit_button.check_hover(mouse_pos)
    
    def draw(self, surface):
        if not self.visible:
            return
            
        # Dibujar fondo
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            # Fondo negro como fallback
            surface.fill(BLACK)
            
        # Dibujar overlay semitransparente
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
            
        # Dibujar título
        title = self.title_font.render("GAME OVER", True, RED)
        shadow = self.title_font.render("GAME OVER", True, BLACK)
        shadow_rect = shadow.get_rect(center=(WIDTH//2 + 4, HEIGHT//2 - 150 + 4))
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 150))
        
        surface.blit(shadow, shadow_rect)
        surface.blit(title, title_rect)
        
        # Mostrar estadísticas
        score_text = self.text_font.render(f"Puntuación: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 80))
        surface.blit(score_text, score_rect)
        
        level_text = self.text_font.render(f"Nivel alcanzado: {self.level}", True, WHITE)
        level_rect = level_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 40))
        surface.blit(level_text, level_rect)
        
        # Formatear tiempo jugado
        minutes = self.time_played // 60
        seconds = self.time_played % 60
        time_text = self.text_font.render(f"Tiempo jugado: {minutes}m {seconds}s", True, WHITE)
        time_rect = time_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        surface.blit(time_text, time_rect)
        
        # Dibujar botones
        self.restart_button.draw(surface)
        self.quit_button.draw(surface)

# Clase para notificaciones y mensajes emergentes
class NotificationSystem:
    def __init__(self):
        self.notifications = []
        self.font = None
        
        # Cargar fuente
        try:
            self.font = pygame.font.Font("assets/fonts/potato.ttf", 20)
        except:
            self.font = pygame.font.SysFont('Arial', 20)
    
    def add_notification(self, text, duration=180, color=WHITE, size=20):
        """Añadir una nueva notificación"""
        # Ajustar fuente según tamaño
        try:
            font = pygame.font.Font("assets/fonts/potato.ttf", size)
        except:
            font = pygame.font.SysFont('Arial', size)
            
        # Crear superficie de texto
        text_surf = font.render(text, True, color)
        
        # Añadir notificación
        self.notifications.append({
            "text": text,
            "surface": text_surf,
            "duration": duration,
            "alpha": 255,
            "y_offset": 0,
            "color": color
        })
    
    def update(self):
        # Actualizar todas las notificaciones
        for notif in self.notifications[:]:
            notif["duration"] -= 1
            
            # Animación de desvanecimiento al final
            if notif["duration"] < 60:
                notif["alpha"] = max(0, int(notif["alpha"] * 0.95))
                
            # Animación de movimiento hacia arriba
            notif["y_offset"] += 0.5
            
            # Eliminar notificaciones expiradas
            if notif["duration"] <= 0:
                self.notifications.remove(notif)
    
    def draw(self, surface):
        # Dibujar todas las notificaciones desde abajo hacia arriba
        y_pos = HEIGHT - 100
        
        for i, notif in enumerate(reversed(self.notifications)):
            text_surf = notif["surface"].copy()
            
            # Aplicar transparencia
            text_surf.set_alpha(notif["alpha"])
            
            # Posición
            y = y_pos - i * 30 - notif["y_offset"]
            
            # Calcular posición x para centrar
            x = WIDTH // 2 - text_surf.get_width() // 2
            
            # Dibujar
            surface.blit(text_surf, (x, y))

# Clase para mostrar mensajes de diálogo en pantalla
class MessageBox:
    def __init__(self):
        self.visible = False
        self.messages = []
        self.current_message = 0
        self.font = None
        self.background = None
        self.continue_text = "Presiona ESPACIO para continuar"
        self.continue_alpha = 255
        self.continue_direction = -5
        
        # Cargar fuente
        try:
            self.font = pygame.font.Font("assets/fonts/potato.ttf", 22)
            self.name_font = pygame.font.Font("assets/fonts/potato.ttf", 26)
        except:
            self.font = pygame.font.SysFont('Arial', 22)
            self.name_font = pygame.font.SysFont('Arial', 26)
            
        # Cargar fondo para la caja
        try:
            self.background = load_image("assets/images/ui/message_box.png", (WIDTH - 100, 150))
        except:
            self.background = None
    
    def set_messages(self, messages):
        """Establecer una lista de mensajes para mostrar secuencialmente"""
        self.messages = messages
        self.current_message = 0
        self.visible = len(messages) > 0
    
    def next_message(self):
        """Avanzar al siguiente mensaje"""
        if self.current_message < len(self.messages) - 1:
            self.current_message += 1
            return True
        else:
            self.visible = False
            return False
    
    def handle_event(self, event):
        """Manejar eventos para avanzar entre mensajes"""
        if not self.visible:
            return False
            
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_z):
            return self.next_message()
                
        return False
    
    def update(self):
        """Actualizar animaciones"""
        if not self.visible:
            return
            
        # Animación pulsante del texto de continuar
        self.continue_alpha += self.continue_direction
        if self.continue_alpha > 255:
            self.continue_alpha = 255
            self.continue_direction = -5
        elif self.continue_alpha < 100:
            self.continue_alpha = 100
            self.continue_direction = 5
    
    def draw(self, surface):
        """Dibujar el cuadro de mensaje actual"""
        if not self.visible or self.current_message >= len(self.messages):
            return
            
        # Obtener mensaje actual
        message = self.messages[self.current_message]
        
        # Dibujar fondo de la caja
        if self.background:
            # Posicionar en la parte inferior de la pantalla
            box_x = 50
            box_y = HEIGHT - 200
            surface.blit(self.background, (box_x, box_y))
        else:
            # Fondo alternativo
            box_rect = pygame.Rect(50, HEIGHT - 200, WIDTH - 100, 150)
            pygame.draw.rect(surface, (0, 0, 0, 200), box_rect)
            pygame.draw.rect(surface, POTATO_BROWN, box_rect, 3)
        
        # Verificar si hay nombre del hablante
        if "name" in message and message["name"]:
            name_text = self.name_font.render(message["name"], True, RED)
            surface.blit(name_text, (70, HEIGHT - 190))
            text_y = HEIGHT - 150
        else:
            text_y = HEIGHT - 170
        
        # Dibujar avatar si existe
        if "avatar" in message and message["avatar"]:
            try:
                avatar = load_image(message["avatar"], (80, 80))
                surface.blit(avatar, (WIDTH - 150, HEIGHT - 190))
            except:
                pass
        
        # Dibujar texto del mensaje
        if "text" in message:
            # Dividir el texto en líneas para que quepa
            words = message["text"].split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + word + " "
                if self.font.size(test_line)[0] < WIDTH - 200:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            
            if current_line:
                lines.append(current_line)
            
            # Dibujar cada línea
            for i, line in enumerate(lines):
                text_surf = self.font.render(line, True, WHITE)
                surface.blit(text_surf, (70, text_y + i * 30))
        
        # Dibujar indicador de continuar
        continue_surf = self.font.render(self.continue_text, True, WHITE)
        continue_surf.set_alpha(self.continue_alpha)
        surface.blit(continue_surf, (WIDTH - 300, HEIGHT - 70))

# Clase para el HUD principal
class GameHUD:
    def __init__(self, player):
        self.player = player
        self.font = None
        self.small_font = None
        
        # Cargar fuentes
        try:
            self.font = pygame.font.Font("assets/fonts/potato.ttf", 20)
            self.small_font = pygame.font.Font("assets/fonts/potato.ttf", 16)
        except:
            self.font = pygame.font.SysFont('Arial', 20)
            self.small_font = pygame.font.SysFont('Arial', 16)
        
        # Cargar imágenes del HUD
        try:
            self.health_bar = load_image("assets/images/ui/health_bar.png", (250, 70))
            self.ammo_bar = load_image("assets/images/ui/ammo_bar.png", (250, 70))
            self.score_display = load_image("assets/images/ui/score_display.png", (150, 50))
            self.xp_bar = load_image("assets/images/ui/xp_bar.png", (250, 20))
            self.weapon_slot = load_image("assets/images/ui/weapon_slot.png", (100, 50))
            self.minimap = load_image("assets/images/ui/minimap.png", (150, 150))
        except:
            self.health_bar = None
            self.ammo_bar = None
            self.score_display = None
            self.xp_bar = None
            self.weapon_slot = None
            self.minimap = None
        
        # Crear barras de progreso
        self.health_progress = ProgressBar(70, 55, 150, 25, self.player.health, self.player.max_health, GREEN, DARK_RED)
        self.xp_progress = ProgressBar(WIDTH - 150, 105, 120, 10, self.player.experience, self.player.level_threshold, BLUE, GRAY)
    
    def update(self):
        """Actualizar elementos del HUD"""
        # Actualizar barras de progreso
        self.health_progress.update(self.player.health)
        self.health_progress.max_value = self.player.max_health
        
        self.xp_progress.update(self.player.experience)
        self.xp_progress.max_value = self.player.level_threshold
    
    def draw(self, surface):
        """Dibujar HUD completo"""
        # Barra de vida
        if self.health_bar:
            surface.blit(self.health_bar, (20, 20))
        else:
            pygame.draw.rect(surface, DARK_RED, (20, 20, 250, 70), 0, 10)
            pygame.draw.rect(surface, BLACK, (20, 20, 250, 70), 2, 10)
            
        health_text = self.font.render(f"SALUD: {int(self.player.health)}/{self.player.max_health}", True, WHITE)
        surface.blit(health_text, (30, 30))
        
        # Dibujar barra de salud
        self.health_progress.draw(surface)
        
        # Información de arma y munición
        weapon = self.player.weapons[self.player.current_weapon]
        
        if self.ammo_bar:
            surface.blit(self.ammo_bar, (20, 100))
        else:
            pygame.draw.rect(surface, DARK_RED, (20, 100, 250, 70), 0, 10)
            pygame.draw.rect(surface, BLACK, (20, 100, 250, 70), 2, 10)
        
        # Dibujar icono del arma actual en el HUD
        if "hud_image" in weapon and weapon["hud_image"]:
            surface.blit(weapon["hud_image"], (30, 110))
        
        # Mostrar nombre del arma
        weapon_name_text = self.small_font.render(weapon["name"], True, WHITE)
        surface.blit(weapon_name_text, (120, 105))
        
        # Mostrar munición
        ammo_text = self.font.render(f"{weapon['ammo']}/{weapon['max_ammo']}", True, WHITE)
        surface.blit(ammo_text, (120, 130))
        
        if self.player.is_reloading:
            reload_text = self.small_font.render("RECARGANDO", True, WHITE)
            surface.blit(reload_text, (180, 130))
        
        # Puntuación
        if self.score_display:
            surface.blit(self.score_display, (WIDTH - 170, 20))
        else:
            pygame.draw.rect(surface, DARK_RED, (WIDTH - 170, 20, 150, 50), 0, 10)
            pygame.draw.rect(surface, BLACK, (WIDTH - 170, 20, 150, 50), 2, 10)
            
        score_text = self.font.render(f"{self.player.score}", True, RED)
        surface.blit(score_text, (WIDTH - 110, 35))
        
        # Nivel
        level_text = self.font.render(f"NIVEL: {self.player.level}", True, WHITE)
        surface.blit(level_text, (WIDTH - 150, 70))
        
        # Barra de experiencia
        if self.xp_bar:
            surface.blit(self.xp_bar, (WIDTH - 170, 100))
        else:
            pygame.draw.rect(surface, DARK_RED, (WIDTH - 170, 100, 150, 20), 0, 5)
            pygame.draw.rect(surface, BLACK, (WIDTH - 170, 100, 150, 20), 2, 5)
        
        # Dibujar barra de XP
        self.xp_progress.draw(surface)
        
        # Mostrar mejoras activas
        y_offset = 150
        if self.player.speed_boost:
            boost_text = self.small_font.render(f"Velocidad + ({self.player.speed_boost_timer//60}s)", True, (0, 200, 255))
            surface.blit(boost_text, (WIDTH - 150, y_offset))
            y_offset += 20
            
        if self.player.damage_boost:
            boost_text = self.small_font.render(f"Daño + ({self.player.damage_boost_timer//60}s)", True, (255, 100, 100))
            surface.blit(boost_text, (WIDTH - 150, y_offset))
            y_offset += 20
            
        if self.player.skill_points > 0:
            points_text = self.font.render(f"¡Puntos de habilidad: {self.player.skill_points}!", True, (255, 215, 0))
            surface.blit(points_text, (WIDTH - 250, y_offset))

# Clase para el minimapa
class Minimap:
    def __init__(self, level, player):
        self.level = level
        self.player = player
        self.width = 150
        self.height = 150
        self.x = WIDTH - self.width - 20
        self.y = HEIGHT - self.height - 20
        self.scale_x = 0.1  # Escala para mapear coordenadas del nivel
        self.scale_y = 0.1
        self.background = None
        
        # Cargar fondo del minimapa
        try:
            self.background = load_image("assets/images/ui/minimap_bg.png", (self.width, self.height))
        except:
            self.background = None
    
    def update(self, level, player):
        """Actualizar referencias"""
        self.level = level
        self.player = player
        
        # Ajustar escala según tamaño del nivel
        if level.linear:
            self.scale_x = self.width / level.scroll_width
            self.scale_y = self.height / HEIGHT
    
    def draw(self, surface):
        """Dibujar minimapa"""
        # Dibujar fondo
        if self.background:
            surface.blit(self.background, (self.x, self.y))
        else:
            map_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            pygame.draw.rect(surface, (0, 0, 0, 150), map_rect)
            pygame.draw.rect(surface, POTATO_BROWN, map_rect, 2)
        
        # Dibujar elementos del nivel si hay nivel
        if self.level:
            # Obstáculos
            for obstacle in self.level.obstacles:
                # Convertir coordenadas del nivel a coordenadas del minimapa
                if self.level.linear:
                    map_x = self.x + (obstacle.x - self.level.scroll_offset_x) * self.scale_x
                    map_y = self.y + obstacle.y * self.scale_y
                else:
                    map_x = self.x + obstacle.x * self.scale_x
                    map_y = self.y + obstacle.y * self.scale_y
                
                # Dibujar punto para el obstáculo
                map_width = max(2, obstacle.width * self.scale_x)
                map_height = max(2, obstacle.height * self.scale_y)
                
                # Seleccionar color según tipo
                if obstacle.type == "wall":
                    color = GRAY
                elif obstacle.type == "table":
                    color = POTATO_BROWN
                else:
                    color = DARK_RED
                    
                pygame.draw.rect(surface, color, (map_x, map_y, map_width, map_height))
            
            # Checkpoints
            for checkpoint in self.level.checkpoints:
                if self.level.linear:
                    map_x = self.x + (checkpoint.x - self.level.scroll_offset_x) * self.scale_x
                    map_y = self.y + checkpoint.y * self.scale_y
                else:
                    map_x = self.x + checkpoint.x * self.scale_x
                    map_y = self.y + checkpoint.y * self.scale_y
                
                # Usar color según estado
                color = GREEN if checkpoint.active else WHITE
                pygame.draw.circle(surface, color, (int(map_x), int(map_y)), 3)
            
            # Punto de salida
            exit_x, exit_y = self.level.get_exit_point()
            if self.level.linear:
                map_exit_x = self.x + (exit_x) * self.scale_x
                map_exit_y = self.y + exit_y * self.scale_y
            else:
                map_exit_x = self.x + exit_x * self.scale_x
                map_exit_y = self.y + exit_y * self.scale_y
            
            pygame.draw.circle(surface, BLUE, (int(map_exit_x), int(map_exit_y)), 4)
        
        # Dibujar jugador en el minimapa
        if self.player:
            if self.level and self.level.linear:
                # En niveles lineales, el jugador se mueve relativo al nivel
                map_player_x = self.x + (self.player.x + self.level.scroll_offset_x) * self.scale_x
                map_player_y = self.y + self.player.y * self.scale_y
            else:
                # En niveles normales, posición directa
                map_player_x = self.x + self.player.x * self.scale_x
                map_player_y = self.y + self.player.y * self.scale_y
            
            # Dibujar jugador como punto más grande
            pygame.draw.circle(surface, RED, (int(map_player_x), int(map_player_y)), 5)

# Ejemplo de uso
if __name__ == "__main__":
    # Inicializar pygame y crear ventana
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Prueba de UI")
    
    # Crear elementos de UI para prueba
    buttons = [
        Button(WIDTH//2 - 100, 100, 200, 50, "JUGAR", DARK_RED, RED),
        Button(WIDTH//2 - 100, 170, 200, 50, "OPCIONES", DARK_RED, RED),
        Button(WIDTH//2 - 100, 240, 200, 50, "SALIR", DARK_RED, RED)
    ]
    
    progress_bar = ProgressBar(WIDTH//2 - 100, 350, 200, 30, 75)
    
    notifications = NotificationSystem()
    
    messages = [
        {"name": "Killer Potato", "text": "¡Por fin soy libre! Ahora voy a vengarme de todos los humanos.", "avatar": "assets/images/characters/killer_potato_dialog.png"},
        {"name": "Científico", "text": "¡No! ¡El experimento 13 ha escapado! ¡Detengan a esa papa!", "avatar": "assets/images/characters/scientist_dialog.png"},
        {"text": "Los guardias comienzan a acercarse..."}
    ]
    
    message_box = MessageBox()
    message_box.set_messages(messages)
    
    # Bucle principal
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Manejar eventos de botones
            for button in buttons:
                button.handle_event(event)
                
            # Manejar eventos de caja de mensajes
            message_box.handle_event(event)
                
            # Añadir notificación al presionar N
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    notifications.add_notification("¡Notificación de prueba!", 180, GREEN)
                elif event.key == pygame.K_m:
                    notifications.add_notification("¡Has subido de nivel!", 240, (255, 215, 0), 24)
                    
            # Cambiar progreso con rueda del ratón
            if event.type == pygame.MOUSEWHEEL:
                progress_bar.update(progress_bar.progress + event.y * 5)
                
        # Actualizar
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.check_hover(mouse_pos)
            
        notifications.update()
        message_box.update()
        
        # Dibujar
        screen.fill((50, 40, 30))  # Fondo marrón oscuro
        
        for button in buttons:
            button.draw(screen)
            
        progress_bar.draw(screen)
        
        notifications.draw(screen)
        message_box.draw(screen)
        
        # Instrucciones
        font = pygame.font.SysFont('Arial', 14)
        inst1 = font.render("Presiona N para añadir notificación normal", True, WHITE)
        inst2 = font.render("Presiona M para añadir notificación importante", True, WHITE)
        inst3 = font.render("Usa la rueda del ratón para cambiar el progreso", True, WHITE)
        inst4 = font.render("Presiona ESPACIO para avanzar en el diálogo", True, WHITE)
        
        screen.blit(inst1, (10, HEIGHT - 100))
        screen.blit(inst2, (10, HEIGHT - 80))
        screen.blit(inst3, (10, HEIGHT - 60))
        screen.blit(inst4, (10, HEIGHT - 40))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()