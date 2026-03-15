import pygame
import sys
import math
import random
from Petalos_Cayendo import PetalosCayendo
from cesped import CespedMovil
from HojasCayendo import HojasCayendo
from BolaMusical import BolaMusical
print("Clase importada correctamente:", PetalosCayendo)

pygame.init()
ANCHO, ALTO = 1200, 640

RESOLUCION_BASE = (1200, 640)
ANCHO, ALTO = RESOLUCION_BASE
PISO_Y = 510
PISO_Y_POZO = 550
PISO_Y_BOSQUE = 520

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Foxes Adventure")
clock = pygame.time.Clock()

def escalar_imagen_proporcional(img, tamano_destino):
    img_ancho, img_alto = img.get_size()
    ratio = max(tamano_destino[0] / img_ancho, tamano_destino[1] / img_alto) * 1.05
    nuevo_ancho = int(img_ancho * ratio)
    nuevo_alto = int(img_alto * ratio)
    escalada = pygame.transform.smoothscale(img, (nuevo_ancho, nuevo_alto))
    superficie = pygame.Surface(tamano_destino)
    superficie.fill((0, 0, 0))
    offset_x = (tamano_destino[0] - nuevo_ancho) // 2
    offset_y = (tamano_destino[1] - nuevo_alto) // 2
    superficie.blit(escalada, (offset_x, offset_y))
    return superficie

def cargar_fondo(ruta):
    try:
        img = pygame.image.load(ruta).convert()
        print(f"✅ Fondo cargado: {ruta}")
        return escalar_imagen_proporcional(img, (ANCHO, ALTO))
    except Exception as e:
        print(f"⚠️ No se pudo cargar {ruta}: {e}")
        s = pygame.Surface((ANCHO, ALTO))
        for y in range(ALTO):
            r = int(30 + (y / ALTO) * 50)
            g = int(20 + (y / ALTO) * 40)
            b = int(50 + (y / ALTO) * 80)
            pygame.draw.line(s, (r, g, b), (0, y), (ANCHO, y))
        return s

print("📸 Cargando fondos...")
fondo_tutorial = cargar_fondo("img/FondoDeTutorial.png")
fondo_interior = cargar_fondo("img/FondoInterior.png")
fondo_aldea = cargar_fondo("img/AldeaPixelada.png")
fondo_bosque = cargar_fondo("img/ArbolesDeLolibo.png")
fondo_tierra_musical = cargar_fondo("img/TierraMusical.png")

try:
    fondo_menu = cargar_fondo("img/FondoMenu.png")
except:
    fondo_menu = pygame.Surface((ANCHO, ALTO))
    fondo_menu.fill((50, 30, 70))

fondo_fnf = pygame.Surface((ANCHO, ALTO))
for y in range(ALTO):
    r = int(40)
    g = int(20 + (y / ALTO) * 40)
    b = int(80 + (y / ALTO) * 60)
    pygame.draw.line(fondo_fnf, (r, g, b), (0, y), (ANCHO, y))

fondo_actual = fondo_menu

print("🌸 Inicializando pétalos...")
petalos = PetalosCayendo(ANCHO, ALTO)
fondo_animado_tutorial = petalos

print("🎵 Inicializando sistema FNF...")

COLOR_MAGICO = (191, 94, 45)
MenuInicio_Activo = True

GRAVEDAD_POR_MAPA = {
    "tutorial": 1.05,
    "aldea": 1.0,
    "bosque": 0.96,
    "tierra_musical": 0.96
}

def obtener_gravedad(escena):
    return GRAVEDAD_POR_MAPA.get(escena, 1.0)

POZO_CENTRO_X = 530
POZO_ANCHO = 200
POZO_X_MIN = POZO_CENTRO_X - POZO_ANCHO // 2
POZO_X_MAX = POZO_CENTRO_X + POZO_ANCHO // 2

MESA_X = 400
MESA_Y = 280
MESA_ANCHO = 150
MESA_ALTO = 80
MESA_X_MIN = MESA_X - MESA_ANCHO // 2
MESA_X_MAX = MESA_X + MESA_ANCHO // 2
MESA_Y_MIN = MESA_Y - MESA_ALTO // 2
MESA_Y_MAX = MESA_Y + MESA_ALTO // 2

ALFOMBRA_X_MIN = 200
ALFOMBRA_X_MAX = 1000
ALFOMBRA_Y_BASE = 525
ALFOMBRA_Y_BAJA = 560
MESA_PLATAFORMA_X_MIN = 350
MESA_PLATAFORMA_X_MAX = 450
MESA_PLATAFORMA_Y = 250

pygame.mixer.music.set_volume(0.5)
musica_actual = None

def cargar_musica(escena):
    global musica_actual
    rutas_musica = {
        "tutorial": "music\\001. Once Upon a Time (UNDERTALE Soundtrack) - Toby Fox (1).mp3",
        "interior": "music\\snowy---undertale-ost-made-with-Voicemod.mp3",
        "aldea": "music\\AldeaMusic.mp3",
        "bosque": "music\\AldeaMusic.mp3",
        "tierra_caramelo": "music\\AldeaMusic.mp3",
        "menu": "music\\byte-storm-rampage.mp3"
    }
    if escena in rutas_musica and musica_actual != escena:
        try:
            pygame.mixer.music.load(rutas_musica[escena])
            pygame.mixer.music.play(-1)
            musica_actual = escena
        except pygame.error as e:
            print(f"⚠️ No se pudo cargar la música: {e}")

def cambiar_volumen(incremento):
    volumen_actual = pygame.mixer.music.get_volume()
    nuevo_volumen = max(0.0, min(1.0, volumen_actual + incremento))
    pygame.mixer.music.set_volume(nuevo_volumen)

def pausar_reanudar_musica():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()

class shaders:
    @staticmethod
    def aplicar(pantalla, escena, tiempo):
        if escena == "bosque":
            for y in range(ALTO):
                r = int(30 + (y / ALTO) * 50)
                g = int(20 + (y / ALTO) * 40)
                b = int(50 + (y / ALTO) * 80)
                pygame.draw.line(pantalla, (r, g, b), (0, y), (ANCHO, y))
        elif escena == "tierra_musical":
            for y in range(ALTO):
                r = int(40 + 10 * math.sin(tiempo / 500))
                g = int(20 + (y / ALTO) * 40 + 10 * math.cos(tiempo / 700))
                b = int(80 + (y / ALTO) * 60 + 10 * math.sin(tiempo / 900))
                pygame.draw.line(pantalla, (r, g, b), (0, y), (ANCHO, y))

class shaders2:
    @staticmethod
    def aplicar(pantalla, escena, tiempo):
        if escena == "AldeaPixelada":
            for y in range(ALTO):
                r = int(30 + (y / ALTO) * 50)
                g = int(20 + (y / ALTO) * 40)
                b = int(50 + (y / ALTO) * 80)
                pygame.draw.line(pantalla, (r, g, b), (0, y), (ANCHO, y))
        elif escena == "FondoInterior":
            for y in range(ALTO):
                r = int(40 + 10 * math.sin(tiempo / 500))
                g = int(20 + (y / ALTO) * 40 + 10 * math.cos(tiempo / 700))
                b = int(80 + (y / ALTO) * 60 + 10 * math.sin(tiempo / 900))
                pygame.draw.line(pantalla, (r, g, b), (0, y), (ANCHO, y))

# ============================================================
# TRANSICIÓN FADE NEGRO - Estilo Golden Sun
# ============================================================
class TransicionPantalla:
    def __init__(self):
        self.activa    = False
        self.fase      = "ninguna"
        self.alpha     = 0
        self.velocidad = 12
        self.sup       = pygame.Surface((ANCHO, ALTO))
        self.sup.fill((0, 0, 0))
        self.callback  = None

    def iniciar(self, callback=None):
        self.activa   = True
        self.fase     = "oscurecer"
        self.alpha    = 0
        self.callback = callback

    def update(self):
        if not self.activa:
            return
        if self.fase == "oscurecer":
            self.alpha = min(255, self.alpha + self.velocidad)
            if self.alpha >= 255:
                self.fase = "aclarar"
                if self.callback:
                    self.callback()
        elif self.fase == "aclarar":
            self.alpha = max(0, self.alpha - self.velocidad)
            if self.alpha <= 0:
                self.activa = False
                self.fase   = "ninguna"

    def draw(self, pantalla):
        if self.activa and self.alpha > 0:
            self.sup.set_alpha(self.alpha)
            pantalla.blit(self.sup, (0, 0))


# ============================================================
# LETRERO PIXEL ART - Nombre del mapa
# ============================================================
class NombreMapa:
    NOMBRES = {
        "tutorial":       "PUEBLO INICIO",
        "aldea":          "LA ALDEA",
        "bosque":         "BOSQUE SOMBRIO",
        "interior":       "INTERIOR",
        "tierra_musical": "TIERRA MUSICAL",
    }

    def __init__(self):
        self.activo     = False
        self.fase       = "caer"
        self.y          = -120.0
        self.y_objetivo = 55
        self.tiempo_esp = 0
        self.dur_espera = 3000
        self.alpha      = 255
        self.vel_caida  = 14
        self.sup        = None

    def _construir(self, nombre):
        ESCALA = 3
        fuente  = pygame.font.Font(None, 13)
        txt_p   = fuente.render(nombre, True, (255, 255, 220))
        txt_big = pygame.transform.scale(
            txt_p,
            (txt_p.get_width() * ESCALA, txt_p.get_height() * ESCALA)
        )
        pad  = 18
        pw   = txt_big.get_width()  + pad * 2
        ph   = txt_big.get_height() + pad * 2
        surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(surf, (10, 10, 30, 220),  (0, 0, pw, ph))
        pygame.draw.rect(surf, (255, 215, 0, 255),  (0, 0, pw, ph), 4)
        pygame.draw.rect(surf, (180, 140, 0, 180),  (4, 4, pw-8, ph-8), 2)
        sombra = fuente.render(nombre, True, (0, 0, 0))
        sombra = pygame.transform.scale(
            sombra,
            (sombra.get_width() * ESCALA, sombra.get_height() * ESCALA)
        )
        surf.blit(sombra,  (pad + 2, pad + 2))
        surf.blit(txt_big, (pad,     pad))
        self.sup = surf

    def mostrar(self, escena):
        nombre = self.NOMBRES.get(escena, escena.upper().replace("_", " "))
        self._construir(nombre)
        self.activo     = True
        self.fase       = "caer"
        self.y          = float(-self.sup.get_height() - 20)
        self.alpha      = 255

    def update(self):
        if not self.activo:
            return
        if self.fase == "caer":
            self.y += self.vel_caida
            if self.y >= self.y_objetivo:
                self.y    = float(self.y_objetivo)
                self.fase = "esperar"
                self.tiempo_esp = pygame.time.get_ticks()
        elif self.fase == "esperar":
            if pygame.time.get_ticks() - self.tiempo_esp >= self.dur_espera:
                self.fase = "desaparecer"
        elif self.fase == "desaparecer":
            self.alpha = max(0, self.alpha - 7)
            self.y    -= 1.5
            if self.alpha <= 0:
                self.activo = False

    def draw(self, pantalla):
        if not self.activo or self.sup is None:
            return
        s = self.sup.copy()
        s.set_alpha(self.alpha)
        x = (ANCHO - s.get_width()) // 2
        pantalla.blit(s, (int(x), int(self.y)))


class Plataforma:
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.mostrar_debug = False

    def draw_debug(self, pantalla):
        if self.mostrar_debug:
            pygame.draw.rect(pantalla, (255, 0, 0, 100), self.rect, 2)


class PuntuacionFlotante:
    def __init__(self):
        self.puntuaciones = []
        self.fuente = pygame.font.Font(None, 36)
        self.fuente_grande = pygame.font.Font(None, 48)
        self.puntuacion_total = 0

    def agregar(self, x, y, puntos, color=(255, 255, 0)):
        self.puntuaciones.append({
            'x': x, 'y': y, 'puntos': puntos,
            'tiempo_inicio': pygame.time.get_ticks(),
            'duracion': 1500, 'velocidad_y': -2,
            'color': color, 'alpha': 255
        })
        self.puntuacion_total += puntos

    def update(self):
        tiempo_actual = pygame.time.get_ticks()
        activas = []
        for p in self.puntuaciones:
            t = tiempo_actual - p['tiempo_inicio']
            if t < p['duracion']:
                p['y'] += p['velocidad_y']
                if t > p['duracion'] - 500:
                    p['alpha'] = int(255 * (1 - (t - (p['duracion'] - 500)) / 500))
                activas.append(p)
        self.puntuaciones = activas

    def draw(self, pantalla):
        for p in self.puntuaciones:
            texto = self.fuente.render(f"+{p['puntos']}", True, p['color'])
            texto.set_alpha(p['alpha'])
            t = pygame.time.get_ticks() - p['tiempo_inicio']
            if t < 200:
                escala = 1.0 + (0.3 * (1 - t / 200))
                texto = pygame.transform.scale(texto, (int(texto.get_width() * escala), int(texto.get_height() * escala)))
            rect = texto.get_rect(center=(p['x'], p['y']))
            sombra = self.fuente.render(f"+{p['puntos']}", True, (0, 0, 0))
            sombra.set_alpha(p['alpha'] // 2)
            pantalla.blit(sombra, sombra.get_rect(center=(p['x'] + 2, p['y'] + 2)))
            pantalla.blit(texto, rect)

    def draw_total(self, pantalla):
        texto = pygame.font.Font(None, 48).render(f"SCORE: {self.puntuacion_total}", True, (255, 255, 0))
        rect = texto.get_rect(topright=(ANCHO - 20, 10))
        fondo = pygame.Surface((rect.width + 20, rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(fondo, (0, 0, 0, 150), fondo.get_rect(), border_radius=8)
        pantalla.blit(fondo, (rect.x - 10, rect.y - 5))
        pantalla.blit(texto, rect)


class SistemaVidas:
    def __init__(self):
        self.vidas_totales   = 3
        self.vidas_actuales  = 3
        self.imagen_corazon  = None
        self.imagen_corazon_negro = None
        self.tamanio_corazon = 45
        self._cargar_sprites()
        self.game_over = False
        self.fuente    = pygame.font.Font(None, 24)

    def _cargar_sprites(self):
        try:
            img = pygame.image.load("img/Vidas.PNG").convert_alpha()
            self.imagen_corazon = pygame.transform.scale(img, (self.tamanio_corazon, self.tamanio_corazon))
            self._crear_corazon_negro_simple()
        except FileNotFoundError:
            self._crear_placeholder()

    def _crear_corazon_negro_simple(self):
        try:
            self.imagen_corazon_negro = self.imagen_corazon.copy()
            oscura = pygame.Surface((self.tamanio_corazon, self.tamanio_corazon), pygame.SRCALPHA)
            oscura.fill((30, 30, 30, 200))
            self.imagen_corazon_negro.blit(oscura, (0, 0))
        except:
            self._crear_placeholder()

    def _crear_placeholder(self):
        t = self.tamanio_corazon
        self.imagen_corazon = pygame.Surface((t, t), pygame.SRCALPHA)
        pygame.draw.polygon(self.imagen_corazon, (255, 0, 0),
                            [(t//2, t), (t, t//3), (t, 0), (t//2, t//3)])
        pygame.draw.polygon(self.imagen_corazon, (255, 0, 0),
                            [(t//2, t), (0, t//3), (0, 0), (t//2, t//3)])
        self.imagen_corazon_negro = pygame.Surface((t, t), pygame.SRCALPHA)
        pygame.draw.polygon(self.imagen_corazon_negro, (40, 40, 40),
                            [(t//2, t), (t, t//3), (t, 0), (t//2, t//3)])
        pygame.draw.polygon(self.imagen_corazon_negro, (40, 40, 40),
                            [(t//2, t), (0, t//3), (0, 0), (t//2, t//3)])

    def perder_vida(self):
        if self.vidas_actuales > 0:
            self.vidas_actuales -= 1
            if self.vidas_actuales <= 0:
                self.game_over = True
            return True
        return False

    def tiene_vidas(self):
        return self.vidas_actuales > 0 and not self.game_over

    def draw(self, pantalla):
        x_inicio, y_inicio = 15, 50
        for i in range(self.vidas_totales):
            x = x_inicio + (i * 55)
            img = self.imagen_corazon if i < self.vidas_actuales else self.imagen_corazon_negro
            pantalla.blit(img, (x, y_inicio))
        texto = self.fuente.render(f"VIDAS: {self.vidas_actuales}/3", True, (255, 255, 255))
        pantalla.blit(texto, (x_inicio + 170, y_inicio + 8))


class JoystickVirtual:
    def __init__(self, x, y, radio_fondo=60, radio_boton=35):
        self.x = x; self.y = y
        self.radio_fondo = radio_fondo; self.radio_boton = radio_boton
        self.boton_x = x; self.boton_y = y
        self.touch_id = None; self.activo = False; self.alpha = 100

    def handle_touch(self, eventos):
        teclas = {"izquierda": False, "derecha": False, "salto": False}
        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN:
                dist = math.sqrt((evento.pos[0]-self.x)**2 + (evento.pos[1]-self.y)**2)
                if dist <= self.radio_fondo + 20:
                    self.touch_id = 0; self.activo = True
            elif evento.type == pygame.MOUSEBUTTONUP:
                if self.touch_id == 0:
                    self.boton_x = self.x; self.boton_y = self.y
                    self.touch_id = None; self.activo = False
            elif evento.type == pygame.MOUSEMOTION and self.touch_id == 0:
                dx = evento.pos[0] - self.x; dy = evento.pos[1] - self.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist <= self.radio_fondo:
                    self.boton_x = evento.pos[0]; self.boton_y = evento.pos[1]
                else:
                    ang = math.atan2(dy, dx)
                    self.boton_x = self.x + math.cos(ang) * self.radio_fondo
                    self.boton_y = self.y + math.sin(ang) * self.radio_fondo
        if self.activo:
            dx = self.boton_x - self.x; dy = self.boton_y - self.y
            if dx < -20: teclas["izquierda"] = True
            elif dx > 20: teclas["derecha"] = True
            if dy < -25: teclas["salto"] = True
        return teclas

    def verificar_toque(self, pos):
        return math.sqrt((pos[0]-self.x)**2 + (pos[1]-self.y)**2) <= self.radio_fondo + 20

    def draw(self, pantalla):
        pygame.draw.circle(pantalla, (100, 100, 150), (int(self.x), int(self.y)), self.radio_fondo, 3)
        pygame.draw.circle(pantalla, (150, 150, 200), (int(self.boton_x), int(self.boton_y)), self.radio_boton)


class BotonAccion:
    def __init__(self, x, y, radio=40, letra="W", color=(200, 100, 100), es_pausa=False):
        self.x = x; self.y = y; self.radio = radio; self.letra = letra
        self.color = color; self.color_hover = tuple(min(c+50,255) for c in color)
        self.presionado = False; self.es_pausa = es_pausa
        self.fuente = pygame.font.Font(None, 36)

    def handle_touch(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            dist = math.sqrt((evento.pos[0]-self.x)**2 + (evento.pos[1]-self.y)**2)
            if dist <= self.radio:
                self.presionado = True; return True
        elif evento.type == pygame.MOUSEBUTTONUP:
            self.presionado = False
        return False

    def verificar_hover(self, mp):
        return math.sqrt((mp[0]-self.x)**2 + (mp[1]-self.y)**2) <= self.radio

    def verificar_toque(self, pos):
        return math.sqrt((pos[0]-self.x)**2 + (pos[1]-self.y)**2) <= self.radio

    def draw(self, pantalla, hover=False):
        color_actual = self.color_hover if hover or self.presionado else self.color
        if self.es_pausa:
            t = int(self.radio * 1.8)
            xi = int(self.x - t//2); yi = int(self.y - t//2)
            pygame.draw.rect(pantalla, color_actual, (xi, yi, t, t), border_radius=8)
            pygame.draw.rect(pantalla, (255,255,255), (xi, yi, t, t), 2, border_radius=8)
            bw = max(3, t//6); bh = t//2; sp = t//4
            yb = yi + (t - bh) // 2
            pygame.draw.rect(pantalla, (255,255,255), (xi+sp, yb, bw, bh))
            pygame.draw.rect(pantalla, (255,255,255), (xi+t-sp-bw, yb, bw, bh))
        else:
            pygame.draw.circle(pantalla, color_actual, (int(self.x), int(self.y)), self.radio)
            pygame.draw.circle(pantalla, (255,255,255), (int(self.x), int(self.y)), self.radio, 2)
        txt = self.fuente.render(self.letra, True, (255,255,255))
        pantalla.blit(txt, txt.get_rect(center=(int(self.x), int(self.y))))


class Enemigo:
    def __init__(self, x, y):
        self.sprites = []
        for ruta in ["img/Robot1 (1).png","img/Robot1 (2).png","img/Robot1 (3).png",
                     "img/Robot1 (4).png","img/Robot1 (5).png","img/Robot1 (6).png"]:
            try:
                img = pygame.image.load(ruta).convert_alpha()
                aw, ah = img.get_size()
                escala = 110 / max(aw, ah)
                nw, nh = int(aw*escala), int(ah*escala)
                img = pygame.transform.scale(img, (nw, nh))
                surf = pygame.Surface((127,127), pygame.SRCALPHA)
                surf.blit(img, ((127-nw)//2, (127-nh)//2))
                self.sprites.append(surf)
            except FileNotFoundError:
                pass
        if not self.sprites:
            self.sprites = self._crear_placeholder()
        self.image = self.sprites[0]
        self.rect  = self.image.get_rect(midbottom=(x, y))
        self.x = float(x); self.y = float(y)
        self.piso_y = PISO_Y_BOSQUE
        self.hitbox_offset_x = 20; self.hitbox_offset_y = 25
        self.hitbox_ancho = 87;    self.hitbox_alto = 70
        self.hitbox = pygame.Rect(0,0,self.hitbox_ancho,self.hitbox_alto)
        self._actualizar_hitbox()
        self.frame_actual = 0; self.contador_frame = 0
        self.velocidad_animacion = 8
        self.activo = False; self.primera_aparicion = True
        self.tiempo_aparicion = 0; self.duracion_mensaje = 3000
        self.mensaje_mostrado = False
        self.velocidad = 3; self.direccion = -1; self.vel_y = 0
        self.gravedad = 1; self.salto = -15; self.velocidad_juego = 1.0
        self.vidas = 3; self.danado = False; self.tiempo_dano = 0
        self.explosionando = False; self.tiempo_explosion = 0; self.frame_explosion = 0
        self.mirando_derecha = False; self.puntos_valor = 100
        self.muerto = False; self.tiempo_muerte = 0; self.visible = True
        self.mostrar_hitbox_debug = False

    def _actualizar_hitbox(self):
        self.hitbox.x = self.rect.x + self.hitbox_offset_x
        self.hitbox.y = self.rect.y + self.hitbox_offset_y

    def _crear_placeholder(self):
        sprites = []
        for _ in range(6):
            surf = pygame.Surface((120,120), pygame.SRCALPHA)
            pygame.draw.rect(surf, (255,140,0), (0,0,120,120), border_radius=20)
            pygame.draw.circle(surf, (255,100,0), (60,60), 30)
            sprites.append(surf)
        return sprites

    def activar(self):
        if self.primera_aparicion:
            self.activo = True; self.primera_aparicion = False
            self.tiempo_aparicion = pygame.time.get_ticks()
            self.mensaje_mostrado = False; self.velocidad_juego = 0.3
            self.muerto = False; self.visible = True
            return True
        return False

    def recibir_dano(self, puntuacion_flotante=None):
        if not self.danado and not self.muerto:
            self.vidas -= 1; self.danado = True
            self.tiempo_dano = pygame.time.get_ticks()
            if self.vidas <= 0:
                self.morir(puntuacion_flotante); return True
        return False

    def morir(self, puntuacion_flotante=None):
        self.muerto = True; self.tiempo_muerte = pygame.time.get_ticks()
        self.activo = False; self.visible = False
        if puntuacion_flotante:
            puntuacion_flotante.agregar(self.rect.centerx, self.rect.top-20, self.puntos_valor, (255,255,0))

    def muerte_por_contraataque(self, puntuacion_flotante=None):
        self.muerto = True; self.tiempo_muerte = pygame.time.get_ticks()
        self.activo = False; self.visible = False
        puntos_bonus = self.puntos_valor * 2
        if puntuacion_flotante:
            puntuacion_flotante.agregar(self.rect.centerx, self.rect.top-20, puntos_bonus, (255,100,100))

    def respawnear(self):
        self.muerto = False; self.visible = True; self.activo = True
        self.explosionando = False; self.frame_actual = 0; self.contador_frame = 0
        self.vidas = 3; self.danado = False
        if random.choice([True, False]):
            self.x = 50.0; self.direccion = 1; self.mirando_derecha = True
        else:
            self.x = float(ANCHO-50); self.direccion = -1; self.mirando_derecha = False
        self.y = float(self.piso_y); self.vel_y = 0
        self.image = self.sprites[0].copy(); self._actualizar_hitbox()

    def update(self, escena_actual="bosque"):
        if not self.activo or self.muerto: return
        if self.danado:
            if pygame.time.get_ticks() - self.tiempo_dano > 500:
                self.danado = False
        t = pygame.time.get_ticks() - self.tiempo_aparicion
        if t > self.duracion_mensaje:
            self.x += self.velocidad * self.direccion
            if self.x <= 50:   self.x = 50;          self.direccion = 1;  self.mirando_derecha = True
            elif self.x >= ANCHO-50: self.x = ANCHO-50; self.direccion = -1; self.mirando_derecha = False
        self.vel_y += obtener_gravedad(escena_actual)
        self.y += self.vel_y
        if self.y >= self.piso_y: self.y = self.piso_y; self.vel_y = 0
        self.rect.x = int(self.x); self.rect.y = int(self.y) - self.rect.height
        self._actualizar_hitbox()
        self.contador_frame += 1
        if self.contador_frame >= self.velocidad_animacion:
            self.contador_frame = 0
            self.frame_actual = (self.frame_actual + 1) % len(self.sprites)
            self.image = self.sprites[self.frame_actual].copy()
            if self.mirando_derecha:
                self.image = pygame.transform.flip(self.image, True, False)

    def verificar_colision(self, otro_rect):
        if self.muerto or not self.visible: return False
        return self.hitbox.colliderect(otro_rect)

    def draw(self, pantalla):
        if self.activo and self.visible and not self.muerto:
            pantalla.blit(self.image, self.rect)

    def draw_mensaje(self, pantalla):
        if not self.activo or self.mensaje_mostrado or self.muerto: return
        t = pygame.time.get_ticks() - self.tiempo_aparicion
        if t > self.duracion_mensaje: self.mensaje_mostrado = True; return
        if t < 500:       alpha = int((t/500)*255)
        elif t > self.duracion_mensaje-500: alpha = int(((self.duracion_mensaje-t)/500)*255)
        else: alpha = 255
        fuente = pygame.font.Font(None, 48)
        texto = fuente.render("¡ATACALO CON LA Q!!", True, (255,100,100))
        texto.set_alpha(alpha)
        rect = texto.get_rect(center=(ANCHO//2, 60))
        fondo = pygame.Surface((rect.width+40, rect.height+20), pygame.SRCALPHA)
        pygame.draw.rect(fondo, (0,0,0,150), fondo.get_rect(), border_radius=10)
        pantalla.blit(fondo, (rect.x-20, rect.y-10))
        pantalla.blit(texto, rect)


class Cinematica:
    def __init__(self):
        self.imagenes_originales = []; self.imagenes_escaladas = []
        self.activa = False; self.imagen_actual = 0
        self.tiempo_inicio_imagen = 0; self.duracion_por_imagen = 4000
        self.terminada = False; self.esperando_continuar = False
        self.fuente = pygame.font.Font(None, 36)
        self.tiempo_parpadeo = 0; self.alpha_texto = 255
        self._cargar_imagenes()

    def _cargar_imagenes(self):
        for i, ruta in enumerate(["img/cinematica1.PNG","img/cinematica2.PNG"], 1):
            try:
                self.imagenes_originales.append(pygame.image.load(ruta).convert())
            except:
                surf = pygame.Surface(RESOLUCION_BASE); surf.fill((0,0,0))
                txt = pygame.font.Font(None,72).render(f"CINEMATICA {i}", True, (220,220,255))
                surf.blit(txt, txt.get_rect(center=(RESOLUCION_BASE[0]//2, RESOLUCION_BASE[1]//2)))
                self.imagenes_originales.append(surf)
        self.reescalar_imagenes()

    def _escalar_imagen_adaptada(self, img, pw, ph):
        iw, ih = img.get_size()
        ai = iw/ih; ap = pw/ph
        if ai > ap: nw=pw; nh=int(pw/ai)
        else: nh=ph; nw=int(ph*ai)
        esc = pygame.transform.smoothscale(img, (nw, nh))
        surf = pygame.Surface((pw,ph)); surf.fill((0,0,0))
        surf.blit(esc, ((pw-nw)//2, (ph-nh)//2))
        return surf

    def reescalar_imagenes(self):
        self.imagenes_escaladas = [self._escalar_imagen_adaptada(i, ANCHO, ALTO) for i in self.imagenes_originales]

    def iniciar(self):
        self.activa = True; self.imagen_actual = 0
        self.tiempo_inicio_imagen = pygame.time.get_ticks()
        self.terminada = False; self.esperando_continuar = False
        self.reescalar_imagenes()

    def update(self):
        if not self.activa or self.esperando_continuar: return
        if pygame.time.get_ticks() - self.tiempo_inicio_imagen >= self.duracion_por_imagen:
            self.imagen_actual += 1
            self.tiempo_inicio_imagen = pygame.time.get_ticks()
            if self.imagen_actual >= len(self.imagenes_escaladas):
                self.esperando_continuar = True
                self.imagen_actual = len(self.imagenes_escaladas) - 1
        self.tiempo_parpadeo += 0.1
        self.alpha_texto = int(155 + abs(math.sin(self.tiempo_parpadeo)) * 100)

    def verificar_continuar(self, evento):
        if self.esperando_continuar:
            if (evento.type == pygame.KEYDOWN and evento.key == pygame.K_e) or evento.type == pygame.MOUSEBUTTONDOWN:
                self.terminar(); return True
        return False

    def terminar(self):
        self.activa = False; self.terminada = True; self.esperando_continuar = False

    def draw(self, pantalla):
        if not self.activa: return
        if self.imagen_actual < len(self.imagenes_escaladas):
            pantalla.blit(self.imagenes_escaladas[self.imagen_actual], (0,0))
        if self.esperando_continuar:
            texto = self.fuente.render("E para continuar", True, (255,255,255))
            texto.set_alpha(self.alpha_texto)
            rect = texto.get_rect(bottomright=(ANCHO-20, ALTO-20))
            fondo = pygame.Surface((rect.width+20, rect.height+10), pygame.SRCALPHA)
            pygame.draw.rect(fondo, (0,0,0,180), fondo.get_rect(), border_radius=8)
            pantalla.blit(fondo, (rect.x-10, rect.y-5))
            pantalla.blit(texto, rect)


class CinematicaTierraMusical:
    def __init__(self):
        self.imagen = None; self.activa = False
        self.tiempo_inicio = 0; self.duracion = 4000
        self.terminada = False; self.fnf_iniciado = False
        self._cargar_imagen()

    def _cargar_imagen(self):
        try:
            img = pygame.image.load("CinematicasParaBosses/Cutscene1.png").convert()
            iw, ih = img.get_size(); ai = iw/ih; ap = ANCHO/ALTO
            if ai > ap: nw=ANCHO; nh=int(ANCHO/ai)
            else: nh=ALTO; nw=int(ALTO*ai)
            esc = pygame.transform.smoothscale(img, (nw, nh))
            self.imagen = pygame.Surface((ANCHO, ALTO)); self.imagen.fill((0,0,0))
            self.imagen.blit(esc, ((ANCHO-nw)//2, (ALTO-nh)//2))
        except:
            self.imagen = pygame.Surface((ANCHO, ALTO)); self.imagen.fill((0,0,0))
            txt = pygame.font.Font(None,72).render("TIERRA MUSICAL", True, (255,215,0))
            self.imagen.blit(txt, txt.get_rect(center=(ANCHO//2, ALTO//2)))

    def iniciar(self):
        self.activa = True; self.tiempo_inicio = pygame.time.get_ticks()
        self.terminada = False; self.fnf_iniciado = False

    def update(self):
        if not self.activa: return
        if pygame.time.get_ticks() - self.tiempo_inicio >= self.duracion:
            self.activa = False; self.terminada = True

    def draw(self, pantalla):
        if self.activa and self.imagen:
            pantalla.blit(self.imagen, (0,0))


class MenuInicio:
    def __init__(self):
        self.fuente_titulo = pygame.font.Font(None, 80)
        self.fuente_boton  = pygame.font.Font(None, 48)
        self.boton_jugar    = pygame.Rect(ANCHO//2-150, ALTO//2-80,  300, 80)
        self.boton_tutorial = pygame.Rect(ANCHO//2-150, ALTO//2+40,  300, 80)
        self.hover_jugar = False; self.hover_tutorial = False
        self.tiempo_pulsacion = 0; self.escala_pulsacion = 1.0

    def update(self, mouse_pos):
        self.hover_jugar    = self.boton_jugar.collidepoint(mouse_pos)
        self.hover_tutorial = self.boton_tutorial.collidepoint(mouse_pos)
        self.tiempo_pulsacion += 0.08
        self.escala_pulsacion = 0.95 + abs(math.sin(self.tiempo_pulsacion)) * 0.05

    def verificar_click(self, mouse_pos, mouse_pressed):
        if mouse_pressed[0]:
            if self.boton_jugar.collidepoint(mouse_pos):    return "jugar"
            if self.boton_tutorial.collidepoint(mouse_pos): return "tutorial"
        return None

    def draw(self, pantalla):
        pantalla.blit(fondo_menu, (0,0))
        titulo = self.fuente_titulo.render("FOXES ADVENTURE", True, (255,215,100))
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO//2, 80)))
        for (rect, hover, color_h, color_n, label) in [
            (self.boton_jugar,    self.hover_jugar,    (100,200,100),(80,150,80),   "JUGAR"),
            (self.boton_tutorial, self.hover_tutorial, (100,150,200),(80,120,180),  "TUTORIAL"),
        ]:
            color  = color_h if hover else color_n
            escala = self.escala_pulsacion if hover else 1.0
            r = rect.copy()
            r.width  = int(rect.width  * escala)
            r.height = int(rect.height * escala)
            r.center = rect.center
            pygame.draw.rect(pantalla, color, r, border_radius=15)
            pygame.draw.rect(pantalla, (255,255,255), r, 3, border_radius=15)
            txt = self.fuente_boton.render(label, True, (255,255,255))
            pantalla.blit(txt, txt.get_rect(center=r.center))


class PantallaControles:
    def __init__(self):
        self.fuente_titulo  = pygame.font.Font(None, 60)
        self.fuente_texto   = pygame.font.Font(None, 32)
        self.fuente_pequena = pygame.font.Font(None, 24)
        self.tiempo_parpadeo = 0; self.alpha_parpadeo = 255

    def update(self):
        self.tiempo_parpadeo += 0.08
        self.alpha_parpadeo = int(200 + abs(math.sin(self.tiempo_parpadeo)) * 55)

    def draw(self, pantalla):
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0,0,0,200), overlay.get_rect(), border_radius=15)
        pantalla.blit(overlay, (0,0))
        pw, ph = 700, 550
        px, py = (ANCHO-pw)//2, (ALTO-ph)//2
        panel = pygame.Surface((pw,ph), pygame.SRCALPHA)
        pygame.draw.rect(panel, (30,20,50,220), panel.get_rect(), border_radius=20)
        pygame.draw.rect(panel, (255,215,100,255), panel.get_rect(), 4, border_radius=20)
        pantalla.blit(panel, (px, py))
        titulo = self.fuente_titulo.render("CONTROLES", True, (255,215,100))
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO//2, py+30)))
        pygame.draw.line(pantalla, (255,215,100), (px+30,py+80), (px+pw-30,py+80), 2)
        controles = [
            ("MOVIMIENTO", "← → Izquierda/Derecha"),
            ("SALTAR", "↑ Arriba (2 veces rápido = DOBLE SALTO)"),
            ("ATACAR", "Q Ataque (frames 3-6 = invencible)"),
            ("HABLAR CON NPCs", "W"),
            ("RECOGER OBJETOS", "T"),
            ("ABRIR/CERRAR PUERTAS", "E"),
            ("VOLVER ATRÁS", "R"),
            ("MÚSICA", "M Pausar/Reanudar"),
        ]
        yo = py + 110
        for t1, t2 in controles:
            pantalla.blit(self.fuente_texto.render(f"• {t1}:", True, (255,255,200)), (px+50, yo))
            pantalla.blit(self.fuente_pequena.render(t2, True, (200,200,200)), (px+70, yo+30))
            yo += 50
        tc = self.fuente_pequena.render("Toca la pantalla o presiona cualquier tecla para continuar...", True, (255,215,100))
        tc.set_alpha(self.alpha_parpadeo)
        pantalla.blit(tc, tc.get_rect(center=(ANCHO//2, ALTO-70)))


class DialogoBox:
    def __init__(self):
        self.activo = False; self.texto = ""; self.nombre = ""
        self.fuente_nombre = pygame.font.Font(None, 28)
        self.fuente_texto  = pygame.font.Font(None, 24)
        self.ancho_box = 800; self.alto_box = 150
        self.x = (ANCHO-800)//2; self.y = ALTO-170
        self.padding = 20; self.alpha = 0; self.max_alpha = 240

    def mostrar(self, nombre, texto):
        self.activo = True; self.nombre = nombre; self.texto = texto; self.alpha = 0

    def cerrar(self):
        self.activo = False; self.alpha = 0

    def update(self):
        if self.activo and self.alpha < self.max_alpha: self.alpha = min(self.alpha+15, self.max_alpha)
        elif not self.activo and self.alpha > 0: self.alpha = max(self.alpha-15, 0)

    def draw(self, pantalla):
        if self.alpha <= 0: return
        box = pygame.Surface((self.ancho_box, self.alto_box), pygame.SRCALPHA)
        pygame.draw.rect(box, (20,20,40,self.alpha), (0,0,self.ancho_box,self.alto_box), border_radius=10)
        pygame.draw.rect(box, (255,215,100,self.alpha), (0,0,self.ancho_box,self.alto_box), 3, border_radius=10)
        pygame.draw.rect(box, (255,200,50,self.alpha), (0,0,self.ancho_box,40), border_radius=10)
        tn = self.fuente_nombre.render(self.nombre, True, (50,30,70)); tn.set_alpha(self.alpha)
        box.blit(tn, (self.padding, 8))
        yo = 50; mx = self.ancho_box - self.padding*2
        palabras = self.texto.split(' '); linea = ""
        for p in palabras:
            prueba = linea + p + " "
            if self.fuente_texto.size(prueba)[0] <= mx: linea = prueba
            else:
                if linea:
                    tl = self.fuente_texto.render(linea, True, (255,255,255)); tl.set_alpha(self.alpha)
                    box.blit(tl, (self.padding, yo)); yo += 30
                linea = p + " "
        if linea:
            tl = self.fuente_texto.render(linea, True, (255,255,255)); tl.set_alpha(self.alpha)
            box.blit(tl, (self.padding, yo))
        if self.activo:
            tc = self.fuente_texto.render("[W] Cerrar", True, (255,215,100))
            tc.set_alpha(int(self.alpha*0.8))
            box.blit(tc, (self.ancho_box-120, self.alto_box-35))
        pantalla.blit(box, (self.x, self.y))


class MensajeAdvertencia:
    def __init__(self):
        self.activo = False; self.texto = ""
        self.fuente = pygame.font.Font(None, 32)
        self.tiempo_aparicion = 0; self.duracion = 2000; self.alpha = 0

    def mostrar(self, texto):
        self.activo = True; self.texto = texto
        self.tiempo_aparicion = pygame.time.get_ticks(); self.alpha = 255

    def update(self):
        if self.activo:
            t = pygame.time.get_ticks() - self.tiempo_aparicion
            if t > self.duracion: self.activo = False; self.alpha = 0
            elif t > self.duracion - 500: self.alpha = int(255*(1-(t-(self.duracion-500))/500))

    def draw(self, pantalla):
        if self.activo and self.alpha > 0:
            txt = self.fuente.render(self.texto, True, (255,50,50)); txt.set_alpha(self.alpha)
            rect = txt.get_rect(center=(ANCHO//2, 50))
            fondo = pygame.Surface((rect.width+20, rect.height+10), pygame.SRCALPHA)
            pygame.draw.rect(fondo, (0,0,0,200), fondo.get_rect(), border_radius=5)
            pantalla.blit(fondo, (rect.x-10, rect.y-5)); pantalla.blit(txt, rect)


class HadaCompanera:
    def __init__(self):
        try:
            self.imagen_idle  = pygame.transform.smoothscale(pygame.image.load("img/Hada_luminosa_en_la_oscuridad-removebg-preview.png").convert_alpha(), (80,80))
            self.imagen_vuelo = pygame.transform.smoothscale(pygame.image.load("img/Hada_brillante_en_vuelo_pixelado-removebg-preview.png").convert_alpha(), (80,80))
        except:
            self.imagen_idle = pygame.Surface((80,80), pygame.SRCALPHA)
            pygame.draw.circle(self.imagen_idle, (255,255,150), (40,40), 30)
            self.imagen_vuelo = self.imagen_idle.copy()
        self.imagen_actual = self.imagen_idle
        self.rect = self.imagen_actual.get_rect()
        self.offset_x = -100; self.offset_y = -120; self.velocidad = 4.5
        self.esta_volando = False; self.tiempo_flotacion = 0
        self.amplitud_flotacion = 10; self.velocidad_flotacion = 0.12
        self.area_interaccion = 90; self.tiempo_brillo = 0; self.intensidad_brillo = 0
        self.fuente = pygame.font.Font(None, 16)
        self.activa = False; self.pos_x = 0.0; self.pos_y = 0.0
        self.conversaciones = 0; self.puede_hablar = True

    def activar(self, jugador_pos):
        self.activa = True
        self.pos_x = float(jugador_pos[0] + self.offset_x)
        self.pos_y = float(jugador_pos[1] + self.offset_y)
        self.rect.centerx = int(self.pos_x); self.rect.centery = int(self.pos_y)
        self.puede_hablar = True

    def update(self, jugador_pos):
        if not self.activa: return
        self.tiempo_flotacion += self.velocidad_flotacion
        fy = math.sin(self.tiempo_flotacion) * self.amplitud_flotacion
        self.tiempo_brillo += 0.1
        self.intensidad_brillo = abs(math.sin(self.tiempo_brillo)) * 100 + 155
        tx = jugador_pos[0] + self.offset_x; ty = jugador_pos[1] + self.offset_y + fy
        dx = tx - self.pos_x; dy = ty - self.pos_y
        dist = math.sqrt(dx**2 + dy**2)
        self.esta_volando = dist > 5
        self.imagen_actual = self.imagen_vuelo if self.esta_volando else self.imagen_idle
        if dist > 3:
            v = min(self.velocidad, dist*0.15)
            self.pos_x += (dx/dist)*v; self.pos_y += (dy/dist)*v
        else:
            self.pos_x = tx; self.pos_y = ty
        self.rect.centerx = int(self.pos_x); self.rect.centery = int(self.pos_y)

    def verificar_interaccion(self, jr):
        if not self.activa: return False
        return self.rect.inflate(self.area_interaccion, self.area_interaccion).colliderect(jr)

    def interactuar(self, dialogo_box):
        if self.conversaciones == 0:
            dialogo_box.mostrar("✨ Hada Luminosa", "¡Hola! Soy tu compañera mágica. Te protegeré en esta aventura. Usa W para hablar conmigo. ¡Buena suerte!")
        else:
            dialogos = ["¡Adelante, aventurero!","No te rindas, estoy aquí.","¡Tu coraje me inspira!","¡Sigue adelante!"]
            dialogo_box.mostrar("✨ Hada Luminosa", dialogos[self.conversaciones % len(dialogos)])
        self.conversaciones += 1

    def draw(self, pantalla, jugador_cerca=False):
        if not self.activa: return
        bs = self.rect.width + 40
        brillo = pygame.Surface((bs, bs), pygame.SRCALPHA)
        for i in range(3):
            radio = bs//2 - (i*8)
            alpha = int((self.intensidad_brillo*0.2)/(i+1))
            pygame.draw.circle(brillo, (255,240,180,alpha), (bs//2,bs//2), radio)
        pantalla.blit(brillo, (self.rect.centerx-bs//2, self.rect.centery-bs//2))
        pantalla.blit(self.imagen_actual, self.rect)
        if jugador_cerca:
            txt = self.fuente.render("HABLAR [W]", True, (255,255,200))
            rect = txt.get_rect(center=(self.rect.centerx, self.rect.top-18))
            fondo = pygame.Surface((rect.width+8, rect.height+3), pygame.SRCALPHA)
            pygame.draw.rect(fondo, (50,30,70,200), fondo.get_rect(), border_radius=4)
            pantalla.blit(fondo, (rect.x-4, rect.y-1)); pantalla.blit(txt, rect)


class ObjetoInteractivo:
    def __init__(self, x, y, ruta_imagen, ancho=80, alto=80):
        try:
            self.imagen = pygame.transform.scale(pygame.image.load(ruta_imagen).convert_alpha(), (ancho,alto))
        except:
            self.imagen = pygame.Surface((ancho,alto), pygame.SRCALPHA)
            pygame.draw.rect(self.imagen, (255,100,100), self.imagen.get_rect())
        self.rect = self.imagen.get_rect(center=(x,y))
        self.visible = True; self.area_interaccion = 80
        self.fuente = pygame.font.Font(None, 18)

    def verificar_colision(self, jr):
        if not self.visible: return False
        return self.rect.inflate(self.area_interaccion, self.area_interaccion).colliderect(jr)

    def recoger(self): self.visible = False

    def draw(self, pantalla, jugador_cerca=False):
        if not self.visible: return
        pantalla.blit(self.imagen, self.rect)
        if jugador_cerca:
            txt = self.fuente.render("RECOGER [T]", True, (255,255,200)); txt.set_alpha(200)
            rect = txt.get_rect(center=(self.rect.centerx, self.rect.top-20))
            fondo = pygame.Surface((rect.width+8, rect.height+3), pygame.SRCALPHA)
            pygame.draw.rect(fondo, (0,0,0,150), fondo.get_rect(), border_radius=4)
            pantalla.blit(fondo, (rect.x-4, rect.y-1)); pantalla.blit(txt, rect)


class Puerta:
    def __init__(self, x, y, ancho=60, alto=80, tipo="entrada"):
        self.x=x; self.y=y; self.ancho=ancho; self.alto=alto
        self.rect = pygame.Rect(x-ancho//2, y-alto, ancho, alto)
        self.tipo=tipo; self.tiempo=0; self.pulsacion=0
        self.ultimo_uso=0; self.cooldown=500
        self.fuente_pequena = pygame.font.Font(None, 18)
        self.fuente_normal  = pygame.font.Font(None, 20)

    def update(self):
        self.tiempo += 0.15
        self.pulsacion = abs(math.sin(self.tiempo)) * 0.6 + 0.9

    def verificar_colision(self, jr):
        return self.rect.inflate(60,60).colliderect(jr)

    def activar(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_uso >= self.cooldown:
            self.ultimo_uso = ahora; return True
        return False

    def draw_indicator(self, pantalla, jugador_cerca=False):
        if not jugador_cerca: return
        alpha = int(150 * self.pulsacion) + 80
        texto_accion = "ENTRAR [E]" if self.tipo == "entrada" else "SALIR [E]"
        simbolo      = "↑"          if self.tipo == "entrada" else "←"
        tf = self.fuente_normal.render(simbolo, True, (255,255,255)); tf.set_alpha(alpha)
        pantalla.blit(tf, tf.get_rect(center=(self.x, self.rect.y-12)))
        te = self.fuente_pequena.render(texto_accion, True, (255,255,255)); te.set_alpha(alpha)
        rect = te.get_rect(center=(self.x, self.rect.y-28))
        fondo = pygame.Surface((rect.width+8, rect.height+3), pygame.SRCALPHA)
        pygame.draw.rect(fondo, (0,0,0,150), fondo.get_rect(), border_radius=4)
        pantalla.blit(fondo, (rect.x-4, rect.y-1)); pantalla.blit(te, rect)


class PosterToyFreddy:
    def __init__(self):
        self.x=837; self.y=195; self.ancho=110; self.alto=170
        try:
            self.imagen = pygame.transform.scale(pygame.image.load("img/toyFreddyIsteregnumero1.jpg").convert_alpha(), (self.ancho,self.alto))
        except:
            self.imagen = pygame.Surface((self.ancho,self.alto), pygame.SRCALPHA)
            pygame.draw.rect(self.imagen, (180,100,80), (0,0,self.ancho,self.alto))
        try: self.sonido_nariz = pygame.mixer.Sound("music/fnaf-12-3-freddys-nose-sound.mp3")
        except: self.sonido_nariz = None
        self.rect_poster = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        self.rect_nariz  = pygame.Rect(self.x+50, self.y+80, 36, 28)

    def colision_nariz(self, pos): return self.rect_nariz.collidepoint(pos)
    def tocar_nariz(self):
        if self.sonido_nariz: self.sonido_nariz.play()

    def draw(self, pantalla):
        if self.imagen: pantalla.blit(self.imagen, self.rect_poster)


class ShadowBonnieInterior:
    def __init__(self):
        self.plush_x=295; self.plush_y=500; self.plush_ancho=70; self.plush_alto=70
        self.grande_x=1000; self.grande_y=200; self.grande_ancho=280; self.grande_alto=380
        try: self.imagen_plush = pygame.transform.scale(pygame.image.load("img/shadowbonnieIsteregNumber2.png").convert_alpha(), (self.plush_ancho,self.plush_alto))
        except:
            self.imagen_plush = pygame.Surface((self.plush_ancho,self.plush_alto), pygame.SRCALPHA)
            pygame.draw.ellipse(self.imagen_plush, (10,10,10), self.imagen_plush.get_rect())
        try: self.imagen_grande = pygame.transform.scale(pygame.image.load("img/ShadowBonnie.png").convert_alpha(), (self.grande_ancho,self.grande_alto))
        except:
            self.imagen_grande = pygame.Surface((self.grande_ancho,self.grande_alto), pygame.SRCALPHA)
            pygame.draw.ellipse(self.imagen_grande, (150,150,150), self.imagen_grande.get_rect())
        self.rect_plush = pygame.Rect(self.plush_x, self.plush_y, self.plush_ancho, self.plush_alto)
        self.mostrar_grande = False
        try: self.sonido_toreador = pygame.mixer.Sound("music/Carmen Overture _Toreador_ (Music Box).mp3")
        except: self.sonido_toreador = None
        self.tiempo_aparicion = 0; self.duracion_aparicion = 4000

    def colision_plush(self, pos): return self.rect_plush.collidepoint(pos)

    def activar_grande(self):
        self.mostrar_grande = True; self.tiempo_aparicion = pygame.time.get_ticks()
        pygame.mixer.music.pause()
        if self.sonido_toreador: self.sonido_toreador.play()

    def update(self):
        if not self.mostrar_grande: return
        if pygame.time.get_ticks() - self.tiempo_aparicion > self.duracion_aparicion:
            self.desaparecer()

    def desaparecer(self):
        self.mostrar_grande = False
        if self.sonido_toreador: self.sonido_toreador.stop()
        pygame.mixer.music.unpause()

    def draw(self, pantalla):
        if self.imagen_plush: pantalla.blit(self.imagen_plush, self.rect_plush)
        if self.mostrar_grande and self.imagen_grande:
            t = pygame.time.get_ticks() - self.tiempo_aparicion
            puls = abs(math.sin(t/200))*50+150
            brillo = pygame.Surface((self.grande_ancho+40, self.grande_alto+40), pygame.SRCALPHA)
            pygame.draw.ellipse(brillo, (200,50,50,int(puls*0.3)), (0,0,self.grande_ancho+40,self.grande_alto+40))
            pantalla.blit(brillo, (self.grande_x-20, self.grande_y-20))
            pantalla.blit(self.imagen_grande, (self.grande_x, self.grande_y))


class Jugador:
    def __init__(self):
        self.TAMANIO = 155
        self.TAMANIO_CORRER = 148
        self.sonido_ataque = None
        try: self.sonido_ataque = pygame.mixer.Sound("music/punch-140236.mp3")
        except Exception as e: print(f"⚠️ Sonido: {e}")
        self.idle = pygame.image.load("img/Fox.png").convert_alpha()
        self.idle = pygame.transform.scale(self.idle, (self.TAMANIO_CORRER, self.TAMANIO_CORRER))
        self.animaciones_salto = self._cargar_animaciones_salto()
        self.animaciones_correr = []
        for i in range(1, 14):
            ruta = f"img/corriendo1 ({i}).png"
            try:
                img = pygame.image.load(ruta).convert_alpha()
                img = pygame.transform.smoothscale(img, (self.TAMANIO_CORRER, self.TAMANIO_CORRER))
                self.animaciones_correr.append(img)
            except FileNotFoundError: pass
        if not self.animaciones_correr:
            self.animaciones_correr = self._crear_animaciones_correr_dinamicas()
        self.animaciones_quieto  = self._cargar_animaciones_quieto()
        self.animaciones_ataque  = self._cargar_animaciones_ataque()
        self.animaciones_mareado = self._cargar_animaciones_mareado()
        self.image = self.idle
        self.frame = 0
        self.rect  = self.image.get_rect(midbottom=(ANCHO//2, PISO_Y))
        self.velocidad            = 4
        self.multiplicador_base   = 1.3
        self.multiplicador_sprint = 1.5
        self.multiplicador_actual = self.multiplicador_base
        self.vel_y = 0; self.gravedad = 1
        # ✅ FIX: salto reducido de -26 a -18
        self.salto = -22
        self.en_suelo = True; self.mirando_derecha = True
        self.hitbox_offset_x = 33; self.hitbox_offset_y = 18
        self.hitbox_ancho = 78;    self.hitbox_alto = 128
        self.hitbox = pygame.Rect(0,0,self.hitbox_ancho,self.hitbox_alto)
        self._actualizar_hitbox()
        self.mostrar_hitbox_debug = False
        self.anim_delay = 50; self.last_update = pygame.time.get_ticks()
        self.estaba_corriendo = False; self.velocidad_desliz = 0; self.friccion_desliz = 0.85
        self.frame_quieto = 0
        self.tiempo_ultimo_frame_quieto = pygame.time.get_ticks()
        self.duracion_frame_quieto = 1800 // max(len(self.animaciones_quieto), 1)
        self.saltando = False; self.frame_salto = 0
        self.tiempo_inicio_salto = 0; self.velocidad_frames_salto = 40
        self.atacando = False; self.frame_ataque = 0; self.tiempo_ataque = 0
        self.duracion_ataque = 600; self.velocidad_frames_ataque = 80
        self.dano_aplicado = False; self.frames_invencibles_ataque = {2,3,4,5}
        self.invencible_durante_ataque = False; self.mata_al_contacto = False; self.golpe_conectado = False
        self.esta_mareado = False; self.tiempo_inicio_mareado = 0; self.duracion_mareado = 2000
        self.frame_mareado = 0; self.contador_frame_mareado = 0; self.velocidad_animacion_mareado = 3
        self.parpadeo_visible = True; self.contador_parpadeo = 0; self.velocidad_parpadeo = 4
        self.invencible = False; self.tiempo_invencibilidad = 0; self.duracion_invencibilidad = 1500
        self.doble_salto_desbloqueado = False; self.puede_doble_saltar = False
        self.tiempo_ultimo_salto = 0; self.cooldown_doble_salto = 300; self.saltando_doble = False
        self.tecla_arriba_presionada_anterior = False
        self.contador_saltos = 0; self.tiempo_reset_saltos = 0; self.joystick_salto_anterior = False
        print("✅ Jugador listo")

    def _cargar_animaciones_quieto(self):
        animaciones = []; T = self.TAMANIO; H = int(T*0.88)
        for i in range(1, 39):
            ruta = f"img/quieto{i}-removebg-preview.png"
            try:
                img = pygame.image.load(ruta).convert_alpha()
                rc  = img.get_bounding_rect()
                rec = pygame.Surface((rc.width,rc.height), pygame.SRCALPHA)
                rec.blit(img, (0,0), rc)
                prop  = H / rec.get_height()
                ancho = int(rec.get_width() * prop)
                esc   = pygame.transform.smoothscale(rec, (ancho, H))
                lienzo = pygame.Surface((T,T), pygame.SRCALPHA)
                lienzo.blit(esc, ((T-ancho)//2, T-H))
                animaciones.append(lienzo)
            except FileNotFoundError:
                animaciones.append(self.idle.copy())
        return animaciones

    def _cargar_animaciones_salto(self):
        T = self.TAMANIO; animaciones = []
        for i in range(1, 34):
            try:
                img = pygame.image.load(f"img/salto_6 ({i}).png").convert_alpha()
                img = pygame.transform.smoothscale(img, (T,T))
            except:
                img = pygame.Surface((T,T), pygame.SRCALPHA)
                pygame.draw.circle(img, (255,150,0), (T//2,T//2), T//4)
            animaciones.append(img)
        return animaciones

    def _cargar_animaciones_ataque(self):
        T = self.TAMANIO; animaciones = []
        for i in range(1, 7):
            try:
                img = pygame.image.load(f"img/atacando{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (T,T))
            except:
                img = pygame.Surface((T,T), pygame.SRCALPHA)
                pygame.draw.circle(img, (255,100,100), (T//2,T//2), T//3)
            animaciones.append(img)
        return animaciones

    def _cargar_animaciones_mareado(self):
        T = self.TAMANIO; animaciones = []
        for i in range(1, 29):
            try:
                img = pygame.image.load(f"img/mareado{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (T,T))
            except:
                img = pygame.Surface((T,T), pygame.SRCALPHA)
                pygame.draw.circle(img, (255,200,0), (T//2,T//2), T//3)
            animaciones.append(img)
        return animaciones

    def _crear_animaciones_correr_dinamicas(self):
        T = self.TAMANIO_CORRER; animaciones = []
        for i in range(13):
            frame = self.idle.copy(); e = 0.95 + (i%3)*0.03
            frame = pygame.transform.scale(frame, (int(T*e), int(T*e)))
            animaciones.append(frame)
        return animaciones

    def animar_quieto(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.tiempo_ultimo_frame_quieto >= self.duracion_frame_quieto:
            self.tiempo_ultimo_frame_quieto = ahora
            self.frame_quieto = (self.frame_quieto+1) % len(self.animaciones_quieto)
        mb = self.rect.midbottom
        self.image = self.animaciones_quieto[self.frame_quieto].copy()
        if not self.mirando_derecha:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(midbottom=mb)

    def _actualizar_hitbox(self):
        if self.mirando_derecha: self.hitbox.x = self.rect.x + self.hitbox_offset_x
        else: self.hitbox.x = self.rect.x + (self.rect.width - self.hitbox_offset_x - self.hitbox_ancho)
        self.hitbox.y = self.rect.y + self.hitbox_offset_y

    def iniciar_ataque(self):
        if not self.atacando and not self.esta_mareado:
            self.atacando=True; self.frame_ataque=0; self.tiempo_ataque=pygame.time.get_ticks()
            self.dano_aplicado=False; self.invencible_durante_ataque=False
            self.mata_al_contacto=False; self.golpe_conectado=False

    def actualizar_ataque(self):
        if not self.atacando: return
        t = pygame.time.get_ticks() - self.tiempo_ataque
        self.frame_ataque = min(int(t/self.velocidad_frames_ataque), len(self.animaciones_ataque)-1)
        mb = self.rect.midbottom
        self.image = self.animaciones_ataque[self.frame_ataque].copy()
        if not self.mirando_derecha: self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(midbottom=mb)
        self.invencible_durante_ataque = self.frame_ataque in self.frames_invencibles_ataque
        self.mata_al_contacto = self.invencible_durante_ataque
        if not self.dano_aplicado and self.frame_ataque >= 2: self.dano_aplicado = True
        if t > self.duracion_ataque:
            self.atacando=False; self.frame_ataque=0
            self.invencible_durante_ataque=False; self.mata_al_contacto=False

    def aplicar_golpe(self, enemigo):
        if self.golpe_conectado: return
        self.golpe_conectado = True
        if self.sonido_ataque:
            try: self.sonido_ataque.play()
            except Exception as e: print(f"⚠️ {e}")

    def actualizar_animacion_salto(self):
        if not self.saltando or not self.animaciones_salto: return
        mb = self.rect.midbottom
        t  = pygame.time.get_ticks() - self.tiempo_inicio_salto
        self.frame_salto = min(int(t/self.velocidad_frames_salto), len(self.animaciones_salto)-1)
        self.image = self.animaciones_salto[self.frame_salto].copy()
        if self.mirando_derecha: self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(midbottom=mb)
        if self.frame_salto >= len(self.animaciones_salto)-1:
            self.saltando=False; self.frame_salto=0

    def recibir_dano(self, cantidad, barra_vida):
        if self.invencible_durante_ataque or self.invencible: return False
        if not self.esta_mareado:
            self.esta_mareado=True; self.invencible=True
            self.tiempo_inicio_mareado=pygame.time.get_ticks()
            self.tiempo_invencibilidad=pygame.time.get_ticks()
            self.frame_mareado=0; self.contador_frame_mareado=0
            self.parpadeo_visible=True; self.contador_parpadeo=0
            barra_vida.recibir_dano(cantidad); return True
        return False

    def actualizar_mareado(self):
        if not self.esta_mareado: return
        t = pygame.time.get_ticks() - self.tiempo_inicio_mareado
        if t >= self.duracion_mareado:
            self.esta_mareado=False; self.frame_mareado=0; self.parpadeo_visible=True; return
        self.contador_parpadeo += 1
        if self.contador_parpadeo >= self.velocidad_parpadeo:
            self.contador_parpadeo=0; self.parpadeo_visible = not self.parpadeo_visible
        self.contador_frame_mareado += 1
        if self.contador_frame_mareado >= self.velocidad_animacion_mareado:
            self.contador_frame_mareado=0
            self.frame_mareado = (self.frame_mareado+1) % len(self.animaciones_mareado)
        mb = self.rect.midbottom
        self.image = self.animaciones_mareado[self.frame_mareado].copy()
        if not self.mirando_derecha: self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(midbottom=mb)

    def actualizar_invencibilidad(self):
        if self.invencible:
            if pygame.time.get_ticks() - self.tiempo_invencibilidad >= self.duracion_invencibilidad:
                self.invencible = False

    def verificar_colision_enemigo(self, enemigo):
        if enemigo.activo and not enemigo.muerto:
            if self.hitbox.colliderect(enemigo.hitbox):
                if self.mata_al_contacto: return "matar_enemigo"
                elif not self.invencible_durante_ataque and not self.esta_mareado and not self.invencible: return "dano"
        return None

    def update(self, escena_actual, velocidad_juego=1.0, teclas_joystick=None):
        self.actualizar_invencibilidad()
        if self.esta_mareado:
            self.actualizar_mareado(); self._actualizar_hitbox(); return
        keys = pygame.key.get_pressed()
        if self.atacando:
            self.actualizar_ataque(); self._actualizar_hitbox(); return
        self.multiplicador_actual = self.multiplicador_sprint if keys[pygame.K_z] else self.multiplicador_base
        self.vel_y += obtener_gravedad(escena_actual) * velocidad_juego
        self.rect.y += self.vel_y * velocidad_juego
        if escena_actual in ("bosque","tierra_caramelo"): piso_actual = PISO_Y_BOSQUE
        elif escena_actual == "interior": piso_actual = self.calcular_altura_interior(escena_actual)
        else: piso_actual = self.calcular_profundidad_pozo(escena_actual)
        if self.rect.bottom >= piso_actual:
            self.rect.bottom=piso_actual; self.vel_y=0; self.en_suelo=True; self.saltando=False
        else: self.en_suelo=False
        moviendo = False
        va = self.velocidad * self.multiplicador_actual * velocidad_juego
        if keys[pygame.K_LEFT]:  self.rect.x -= va; self.mirando_derecha=True;  moviendo=True; self.velocidad_desliz=0
        if keys[pygame.K_RIGHT]: self.rect.x += va; self.mirando_derecha=False; moviendo=True; self.velocidad_desliz=0
        if teclas_joystick:
            if teclas_joystick.get("izquierda"): self.rect.x -= va; self.mirando_derecha=True;  moviendo=True; self.velocidad_desliz=0
            if teclas_joystick.get("derecha"):   self.rect.x += va; self.mirando_derecha=False; moviendo=True; self.velocidad_desliz=0
            salto_ahora = teclas_joystick.get("salto", False)
            if salto_ahora and not self.joystick_salto_anterior:
                if self.en_suelo:
                    self.vel_y=self.salto; self.en_suelo=False; self.saltando=True
                    self.tiempo_inicio_salto=pygame.time.get_ticks()
                    self.contador_saltos=1; self.tiempo_reset_saltos=pygame.time.get_ticks()
                elif (self.doble_salto_desbloqueado and self.contador_saltos==1 and
                      pygame.time.get_ticks()-self.tiempo_reset_saltos < self.cooldown_doble_salto):
                    self.vel_y=self.salto; self.contador_saltos=2
            if pygame.time.get_ticks()-self.tiempo_reset_saltos > 500: self.contador_saltos=0
            self.joystick_salto_anterior = salto_ahora
        ta = keys[pygame.K_UP]
        if ta and not self.tecla_arriba_presionada_anterior:
            if self.en_suelo:
                self.vel_y=self.salto; self.en_suelo=False; self.saltando=True
                self.tiempo_inicio_salto=pygame.time.get_ticks()
                self.contador_saltos=1; self.tiempo_reset_saltos=pygame.time.get_ticks()
            elif (self.doble_salto_desbloqueado and self.contador_saltos==1 and
                  pygame.time.get_ticks()-self.tiempo_reset_saltos < self.cooldown_doble_salto):
                self.vel_y=self.salto; self.contador_saltos=2
        if pygame.time.get_ticks()-self.tiempo_reset_saltos > 500: self.contador_saltos=0
        self.tecla_arriba_presionada_anterior = ta
        if not moviendo and self.en_suelo and self.velocidad_desliz > 0.5:
            self.rect.x += self.velocidad_desliz * velocidad_juego * (1 if self.mirando_derecha else -1)
            self.velocidad_desliz *= self.friccion_desliz
        self.rect.left  = max(0, self.rect.left)
        self.rect.right = min(ANCHO, self.rect.right)
        ahora = pygame.time.get_ticks()
        if not self.en_suelo:
            if self.saltando and self.animaciones_salto: self.actualizar_animacion_salto()
            self.estaba_corriendo = False
        elif moviendo:
            if not self.estaba_corriendo: self.frame=0; self.last_update=ahora
            self.estaba_corriendo = True
            if ahora - self.last_update >= self.anim_delay:
                self.frame = (self.frame+1) % len(self.animaciones_correr); self.last_update=ahora
            mb = self.rect.midbottom
            self.image = self.animaciones_correr[self.frame].copy()
            self.rect  = self.image.get_rect(midbottom=mb)
            self.velocidad_desliz = self.velocidad * 0.6
            if not self.mirando_derecha: self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.animar_quieto(); self.estaba_corriendo=False
        self._actualizar_hitbox()

    def esta_en_area_pozo(self, escena):
        return escena=="aldea" and POZO_X_MIN <= self.rect.centerx <= POZO_X_MAX

    def calcular_profundidad_pozo(self, escena):
        if not self.esta_en_area_pozo(escena): return PISO_Y
        pos = (self.rect.centerx-POZO_X_MIN)/(POZO_X_MAX-POZO_X_MIN)
        return int(PISO_Y + (PISO_Y_POZO-PISO_Y)*math.sin(pos*math.pi))

    def calcular_altura_interior(self, escena):
        if escena != "interior": return PISO_Y
        return ALFOMBRA_Y_BAJA if ALFOMBRA_X_MIN <= self.rect.centerx <= ALFOMBRA_X_MAX else PISO_Y

    def draw(self, pantalla):
        if self.esta_mareado and not self.parpadeo_visible: return
        if self.invencible and not self.esta_mareado:
            if self.parpadeo_visible: pantalla.blit(self.image, self.rect)
        else: pantalla.blit(self.image, self.rect)
        if self.mostrar_hitbox_debug:
            pygame.draw.rect(pantalla, (0,255,0), self.hitbox, 2)


class BarraVida:
    def __init__(self):
        self.vida=100; self.vida_maxima=100
        self.x=10; self.y=10; self.ancho_barra=200; self.alto_barra=25
        self.fuente=pygame.font.Font(None,20); self.fuente_hp=pygame.font.Font(None,14)

    def recibir_dano(self, cantidad): self.vida = max(0, self.vida-cantidad)
    def curar(self, cantidad): self.vida = min(self.vida_maxima, self.vida+cantidad)

    def get_color(self):
        p = self.vida/self.vida_maxima
        if p > 0.5: return (76,175,80)
        elif p > 0.25: return (255,193,7)
        return (244,67,54)

    def draw(self, pantalla):
        pygame.draw.circle(pantalla, (255,140,0), (self.x+18,self.y+18), 15)
        pygame.draw.circle(pantalla, (255,100,0), (self.x+18,self.y+18), 15, 2)
        pygame.draw.rect(pantalla, (40,40,40), (self.x+38,self.y+5,self.ancho_barra,self.alto_barra))
        ancho_actual = (self.vida/self.vida_maxima)*self.ancho_barra
        pygame.draw.rect(pantalla, self.get_color(), (self.x+38,self.y+5,ancho_actual,self.alto_barra))
        pygame.draw.rect(pantalla, (255,140,0), (self.x+38,self.y+5,self.ancho_barra,self.alto_barra), 2)
        txt = self.fuente_hp.render(f"HP: {int(self.vida)}/{self.vida_maxima}", True, (255,255,255))
        pantalla.blit(txt, (self.x+43,self.y+10))


# ============================================================
# PARTÍCULAS - Efecto al hacer click en botones
# ============================================================
class SistemaParticulas:
    def __init__(self):
        self.particulas = []

    def emitir(self, x, y, color=(255, 215, 0), cantidad=18):
        for _ in range(cantidad):
            angulo = random.uniform(0, math.pi * 2)
            vel    = random.uniform(2, 7)
            vida   = random.randint(18, 35)
            tam    = random.randint(3, 7)
            colores_pixel = [
                (255, 215, 0), (255, 100, 50), (100, 220, 255),
                (255, 255, 255), (180, 100, 255), color
            ]
            self.particulas.append({
                'x': float(x), 'y': float(y),
                'vx': math.cos(angulo) * vel,
                'vy': math.sin(angulo) * vel,
                'vida': vida, 'vida_max': vida,
                'tam': tam,
                'color': random.choice(colores_pixel),
            })

    def update(self):
        vivas = []
        for p in self.particulas:
            p['x']  += p['vx']
            p['y']  += p['vy']
            p['vy'] += 0.25
            p['vida'] -= 1
            if p['vida'] > 0:
                vivas.append(p)
        self.particulas = vivas

    def draw(self, pantalla):
        for p in self.particulas:
            alpha_ratio = p['vida'] / p['vida_max']
            tam = max(1, int(p['tam'] * alpha_ratio))
            pygame.draw.rect(pantalla, p['color'],
                             (int(p['x']), int(p['y']), tam, tam))


# ============================================================
# BOTÓN OPCIONES - Pixel art, con partículas al click
# ============================================================
class BotonOpcionesPixel:
    def __init__(self, x, y, tam=50):
        self.x   = x
        self.y   = y
        self.tam = tam
        self.rect = pygame.Rect(x - tam//2, y - tam//2, tam, tam)
        self.presionado  = False
        self.tiempo_anim = 0
        self._construir_sprite()

    def _construir_sprite(self):
        S = 8
        ESCALA = self.tam // S
        self.sprite_normal  = self._dibujar_engranaje(S, ESCALA, (80,  60, 120))
        self.sprite_hover   = self._dibujar_engranaje(S, ESCALA, (120, 90, 200))
        self.sprite_pressed = self._dibujar_engranaje(S, ESCALA, (200,150, 255))

    def _dibujar_engranaje(self, S, ESCALA, color_fondo):
        mini = pygame.Surface((S, S), pygame.SRCALPHA)
        mini.fill((0, 0, 0, 0))
        pygame.draw.rect(mini, color_fondo, (0, 0, S, S))
        pygame.draw.rect(mini, (255, 215, 0), (0, 0, S, S), 1)
        cx, cy = S//2, S//2
        dientes = [(cx, 0),(cx, S-1),(0, cy),(S-1, cy),
                   (1,1),(S-2,1),(1,S-2),(S-2,S-2)]
        for dx, dy in dientes:
            mini.set_at((dx, dy), (255, 215, 0))
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx*dx + dy*dy <= 5:
                    mini.set_at((cx+dx, cy+dy), (255, 215, 0))
        mini.set_at((cx, cy), color_fondo)
        surf = pygame.transform.scale(mini, (S*ESCALA, S*ESCALA))
        return surf

    def verificar_hover(self, mp):
        return self.rect.collidepoint(mp)

    def handle_touch(self, evento, particulas):
        if evento.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(evento.pos):
            self.presionado = True
            particulas.emitir(self.x, self.y)
            return True
        if evento.type == pygame.MOUSEBUTTONUP:
            self.presionado = False
        return False

    def draw(self, pantalla, hover=False):
        self.tiempo_anim += 0.04
        if self.presionado:
            sprite = self.sprite_pressed
        elif hover:
            sprite = self.sprite_hover
        else:
            sprite = self.sprite_normal
        angulo_grados = int(math.degrees(self.tiempo_anim) % 360)
        rotado = pygame.transform.rotate(sprite, -angulo_grados)
        rect_r = rotado.get_rect(center=(self.x, self.y))
        pantalla.blit(rotado, rect_r)


# ============================================================
# PANEL DE OPCIONES
# ============================================================
class PanelOpciones:
    VEL_LENTA  = 0.5
    VEL_NORMAL = 1.0
    VEL_RAPIDA = 1.8

    def __init__(self):
        self.visible   = False
        self.alpha     = 0
        self.ancho     = 260
        self.alto      = 220
        self.x         = ANCHO - self.ancho - 10
        self.y         = 90
        self.vel_actual = self.VEL_NORMAL
        self.controles_visibles = True
        self.fuente_titulo = pygame.font.Font(None, 13)
        self.fuente_btn    = pygame.font.Font(None, 11)
        self._construir()

    def _pixel_text(self, fuente, texto, color):
        s = fuente.render(texto, True, color)
        return pygame.transform.scale(s, (s.get_width()*2, s.get_height()*2))

    def _construir(self):
        bw, bh = 220, 48
        bx = self.x + (self.ancho - bw) // 2
        self.btn_lenta  = pygame.Rect(bx, self.y + 50,  bw, bh)
        self.btn_rapida = pygame.Rect(bx, self.y + 108, bw, bh)
        self.btn_ctrl   = pygame.Rect(bx, self.y + 166, bw, bh - 8)

    def toggle(self):
        self.visible = not self.visible

    def handle_click(self, pos, particulas):
        if not self.visible: return
        if self.btn_lenta.collidepoint(pos):
            self.vel_actual = self.VEL_LENTA if self.vel_actual != self.VEL_LENTA else self.VEL_NORMAL
            particulas.emitir(*self.btn_lenta.center, color=(100,200,255))
        elif self.btn_rapida.collidepoint(pos):
            self.vel_actual = self.VEL_RAPIDA if self.vel_actual != self.VEL_RAPIDA else self.VEL_NORMAL
            particulas.emitir(*self.btn_rapida.center, color=(255,100,50))
        elif self.btn_ctrl.collidepoint(pos):
            self.controles_visibles = not self.controles_visibles
            particulas.emitir(*self.btn_ctrl.center, color=(100,255,150))

    def update(self):
        objetivo = 240 if self.visible else 0
        self.alpha += (objetivo - self.alpha) * 0.18
        if abs(self.alpha - objetivo) < 1: self.alpha = objetivo

    def _dibujar_boton(self, pantalla, rect, label, activo, color_act, color_inact):
        color = color_act if activo else color_inact
        pygame.draw.rect(pantalla, color, rect)
        pygame.draw.rect(pantalla, (255, 255, 255), rect, 2)
        pygame.draw.rect(pantalla, (0, 0, 0),       rect, 1)
        if activo:
            pygame.draw.rect(pantalla, (255, 255, 100),
                             (rect.right-14, rect.top+4, 10, 10))
            pygame.draw.rect(pantalla, (0,0,0),
                             (rect.right-14, rect.top+4, 10, 10), 1)
        mini = pygame.font.Font(None, 11).render(label, True, (255,255,255))
        txt  = pygame.transform.scale(mini, (mini.get_width()*2, mini.get_height()*2))
        pantalla.blit(txt, txt.get_rect(center=rect.center))

    def draw(self, pantalla):
        if self.alpha < 2: return
        a = int(self.alpha)
        panel = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        pygame.draw.rect(panel, (15, 10, 35, a),   (0, 0, self.ancho, self.alto))
        pygame.draw.rect(panel, (255, 215, 0, a),   (0, 0, self.ancho, self.alto), 3)
        pygame.draw.rect(panel, (80, 50, 140, a),   (3, 3, self.ancho-6, self.alto-6), 1)
        mini = pygame.font.Font(None, 13).render("OPCIONES", True, (255, 215, 0))
        titulo = pygame.transform.scale(mini, (mini.get_width()*2, mini.get_height()*2))
        titulo.set_alpha(a)
        panel.blit(titulo, titulo.get_rect(centerx=self.ancho//2, y=10))
        pantalla.blit(panel, (self.x, self.y))
        if a < 20: return
        surf_btn = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        surf_btn.set_alpha(a)
        self._dibujar_boton(surf_btn,
            self.btn_lenta.move(-self.x, -self.y),
            ">> CAMARA LENTA  (x0.5)",
            self.vel_actual == self.VEL_LENTA,
            (30, 80, 160), (40, 40, 80))
        self._dibujar_boton(surf_btn,
            self.btn_rapida.move(-self.x, -self.y),
            ">> CAMARA RAPIDA (x1.8)",
            self.vel_actual == self.VEL_RAPIDA,
            (160, 50, 30), (80, 40, 40))
        label_ctrl = ">> OCULTAR CONTROLES" if self.controles_visibles else ">> MOSTRAR CONTROLES"
        self._dibujar_boton(surf_btn,
            self.btn_ctrl.move(-self.x, -self.y),
            label_ctrl,
            not self.controles_visibles,
            (30, 120, 60), (40, 70, 50))
        pantalla.blit(surf_btn, (self.x, self.y))


# ============================================================
# INICIALIZACIÓN
# ============================================================
print("\n🎮 Inicializando juego...")
jugador   = Jugador()
fondo_actual = fondo_menu
hada      = HadaCompanera()
dialogo_box  = DialogoBox()
mensaje_advertencia = MensajeAdvertencia()
menu      = MenuInicio()
pantalla_controles = PantallaControles()
cinematica = Cinematica()
cinematica_tierra_musical = CinematicaTierraMusical()
enemigos  = []

transicion  = TransicionPantalla()
nombre_mapa = NombreMapa()
# ✅ FIX: BolaMusical integrada correctamente
sistema_disco = BolaMusical()

puerta_entrada = Puerta(x=947, y=375, ancho=45, alto=65, tipo="entrada")
puerta_salida  = Puerta(x=1000, y=400, ancho=50, alto=70, tipo="salida")
mapa2 = ObjetoInteractivo(x=1000, y=500, ruta_imagen="img/Mapa2.png", ancho=45, alto=45)
poster_toy_freddy       = PosterToyFreddy()
shadow_bonnie_interior  = ShadowBonnieInterior()
barra_vida        = BarraVida()
sistema_vidas     = SistemaVidas()
cesped            = CespedMovil(ANCHO, ALTO, 480)
hojas             = HojasCayendo(ANCHO, ALTO)
puntuacion_flotante = PuntuacionFlotante()

joystick    = JoystickVirtual(80, 560, radio_fondo=60, radio_boton=35)
boton_pausa = BotonAccion(ANCHO-50,  50,  radio=25, letra="⏸", color=(50,180,220), es_pausa=True)
boton_q     = BotonAccion(ANCHO-230, ALTO-100, radio=40, letra="Q", color=(200,100,150))
boton_w     = BotonAccion(ANCHO-130, ALTO-100, radio=40, letra="W", color=(150,100,200))
boton_t     = BotonAccion(ANCHO-30,  ALTO-100, radio=40, letra="T", color=(100,150,200))
boton_e     = BotonAccion(ANCHO-80,  ALTO-30,  radio=40, letra="E", color=(200,150,100))
boton_r     = BotonAccion(ANCHO-180, ALTO-30,  radio=40, letra="R", color=(100,200,150))

boton_opciones  = BotonOpcionesPixel(ANCHO-50, 95, tam=44)
panel_opciones  = PanelOpciones()
particulas      = SistemaParticulas()
velocidad_juego = 1.0

escena_actual     = "menu"
historial_escenas = []
cargar_musica(escena_actual)

cooldown_borde   = 0
tiempo_cooldown_borde = 4000
mostrando_controles = False
juego_pausado    = False
cooldown_retroceso = 0
tiempo_cooldown_retroceso = 4000

tiempo_ultimo_enemigo_muerto = 0
tiempo_respawn_enemigo = 3000
enemigos_matados  = 0
enemigos_necesarios = 50
oleada_actual     = 0
tamano_oleada     = 1
max_enemigos_por_oleada = 6
oleada_completada = True
tiempo_ultima_oleada = 0
cooldown_entre_oleadas = 2000
tierra_musical_desbloqueada = False

# ✅ FIX: plataformas_tierra_musical vaciada — eliminada la hitbox invisible
plataformas_tierra_musical = []

def spawn_oleada():
    global tamano_oleada
    for _ in range(tamano_oleada):
        if random.random() < 0.5: x=50;        dir=1;  mirando=True
        else:                      x=ANCHO-50;  dir=-1; mirando=False
        e = Enemigo(x, PISO_Y_BOSQUE)
        e.direccion=dir; e.mirando_derecha=mirando
        e.activo=True; e.visible=True; e.muerto=False; e.vidas=3
        e.primera_aparicion=False; e.mensaje_mostrado=True
        e.tiempo_aparicion=pygame.time.get_ticks()
        enemigos.append(e)

print("✅ Juego inicializado.\n")

# ============================================================
# LOOP PRINCIPAL
# ============================================================
running = True
while running:
    clock.tick(60)
    mouse_pos     = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()
    eventos       = pygame.event.get()

    for evento in eventos:
        if evento.type == pygame.QUIT:
            running = False

        if cinematica.activa:
            if cinematica.verificar_continuar(evento):
                escena_actual = "tutorial"
                fondo_actual  = fondo_tutorial
                jugador.rect.midbottom = (ANCHO//2, PISO_Y)
                cargar_musica(escena_actual)
                nombre_mapa.mostrar("tutorial")
            continue

        if mostrando_controles:
            if evento.type == pygame.KEYDOWN or evento.type == pygame.MOUSEBUTTONDOWN:
                mostrando_controles = False
            continue

        if evento.type == pygame.MOUSEBUTTONDOWN and escena_actual == "interior" and not transicion.activa:
            if poster_toy_freddy.colision_nariz(evento.pos): poster_toy_freddy.tocar_nariz()
            if shadow_bonnie_interior.colision_plush(evento.pos): shadow_bonnie_interior.activar_grande()

        if evento.type == pygame.MOUSEBUTTONDOWN and escena_actual == "menu":
            resultado = menu.verificar_click(mouse_pos, pygame.mouse.get_pressed())
            if resultado == "jugar":    cinematica.iniciar()
            elif resultado == "tutorial": mostrando_controles = True

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_q and not transicion.activa and not jugador.atacando:
                jugador.iniciar_ataque()

            if evento.key == pygame.K_w and not transicion.activa:
                if dialogo_box.activo: dialogo_box.cerrar(); continue
                if hada.activa and hada.verificar_interaccion(jugador.rect):
                    hada.interactuar(dialogo_box); continue

            if evento.key == pygame.K_e and not transicion.activa:
                if escena_actual == "tutorial":
                    if puerta_entrada.verificar_colision(jugador.rect) and puerta_entrada.activar():
                        def entrar_casa():
                            global escena_actual, fondo_actual
                            historial_escenas.append(("tutorial", jugador.rect.midbottom))
                            escena_actual = "interior"; fondo_actual = fondo_interior
                            jugador.rect.midbottom = (250, PISO_Y)
                            cargar_musica(escena_actual); nombre_mapa.mostrar(escena_actual)
                        transicion.iniciar(entrar_casa)
                elif escena_actual == "interior":
                    if puerta_salida.verificar_colision(jugador.rect) and puerta_salida.activar():
                        def salir_casa():
                            global escena_actual, fondo_actual
                            historial_escenas.append(("interior", jugador.rect.midbottom))
                            escena_actual = "tutorial"; fondo_actual = fondo_tutorial
                            jugador.rect.midbottom = (900, PISO_Y)
                            cargar_musica(escena_actual); nombre_mapa.mostrar(escena_actual)
                        transicion.iniciar(salir_casa)

            if evento.key == pygame.K_t and not transicion.activa:
                if escena_actual == "interior" and mapa2.verificar_colision(jugador.rect) and mapa2.visible:
                    mapa2.recoger()

            if evento.key == pygame.K_r and not transicion.activa and len(historial_escenas) > 0:
                tiempo_actual = pygame.time.get_ticks()
                if tiempo_actual - cooldown_retroceso >= tiempo_cooldown_retroceso:
                    def retroceder():
                        global escena_actual, fondo_actual
                        e, p = historial_escenas.pop()
                        fondos = {"tutorial": fondo_tutorial, "interior": fondo_interior,
                                  "aldea": fondo_aldea, "bosque": fondo_bosque,
                                  "tierra_musical": fondo_tierra_musical}
                        escena_actual = e; fondo_actual = fondos.get(e, fondo_tutorial)
                        jugador.rect.midbottom = p
                        cargar_musica(escena_actual); nombre_mapa.mostrar(escena_actual)
                    transicion.iniciar(retroceder)
                    cooldown_retroceso = tiempo_actual

            if evento.key == pygame.K_r and len(historial_escenas) == 0:
                jugador.rect.centerx = ANCHO//2; jugador.rect.bottom = PISO_Y

            if evento.key == pygame.K_m: pausar_reanudar_musica()
            if evento.key in (pygame.K_PLUS, pygame.K_EQUALS): cambiar_volumen(0.1)
            if evento.key == pygame.K_MINUS: cambiar_volumen(-0.1)

        if escena_actual != "menu" and not cinematica.activa:
            if boton_pausa.handle_touch(evento): juego_pausado = not juego_pausado
            if boton_opciones.handle_touch(evento, particulas):
                panel_opciones.toggle()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                panel_opciones.handle_click(evento.pos, particulas)
            if boton_q.handle_touch(evento):
                if not transicion.activa and not jugador.atacando: jugador.iniciar_ataque()
            if boton_w.handle_touch(evento):
                if not transicion.activa:
                    if dialogo_box.activo: dialogo_box.cerrar()
                    elif hada.activa and hada.verificar_interaccion(jugador.rect): hada.interactuar(dialogo_box)
            if boton_t.handle_touch(evento):
                if escena_actual=="interior" and not transicion.activa and mapa2.verificar_colision(jugador.rect) and mapa2.visible:
                    mapa2.recoger()
            if boton_e.handle_touch(evento):
                if not transicion.activa:
                    if escena_actual == "tutorial":
                        if puerta_entrada.verificar_colision(jugador.rect) and puerta_entrada.activar():
                            def entrar_casa_btn():
                                global escena_actual, fondo_actual
                                historial_escenas.append(("tutorial", jugador.rect.midbottom))
                                escena_actual="interior"; fondo_actual=fondo_interior
                                jugador.rect.midbottom=(250,PISO_Y)
                                cargar_musica(escena_actual); nombre_mapa.mostrar(escena_actual)
                            transicion.iniciar(entrar_casa_btn)
                    elif escena_actual == "interior":
                        if puerta_salida.verificar_colision(jugador.rect) and puerta_salida.activar():
                            def salir_casa_btn():
                                global escena_actual, fondo_actual
                                historial_escenas.append(("interior", jugador.rect.midbottom))
                                escena_actual="tutorial"; fondo_actual=fondo_tutorial
                                jugador.rect.midbottom=(900,PISO_Y)
                                cargar_musica(escena_actual); nombre_mapa.mostrar(escena_actual)
                            transicion.iniciar(salir_casa_btn)
            if boton_r.handle_touch(evento):
                if not transicion.activa and len(historial_escenas) > 0:
                    tiempo_actual = pygame.time.get_ticks()
                    if tiempo_actual - cooldown_retroceso >= tiempo_cooldown_retroceso:
                        def retroceder_btn():
                            global escena_actual, fondo_actual
                            e, p = historial_escenas.pop()
                            fondos = {"tutorial":fondo_tutorial,"interior":fondo_interior,
                                      "aldea":fondo_aldea,"bosque":fondo_bosque,"tierra_musical":fondo_tierra_musical}
                            escena_actual=e; fondo_actual=fondos.get(e,fondo_tutorial)
                            jugador.rect.midbottom=p
                            cargar_musica(escena_actual); nombre_mapa.mostrar(escena_actual)
                        transicion.iniciar(retroceder_btn)
                        cooldown_retroceso = tiempo_actual

    # ============================================================
    # UPDATE
    # ============================================================
    if cinematica.activa:
        cinematica.update()
    elif escena_actual == "menu":
        menu.update(mouse_pos)
        if mostrando_controles: pantalla_controles.update()
    else:
        teclas_joystick = joystick.handle_touch(eventos) if not mostrando_controles and panel_opciones.controles_visibles else None

        velocidad_juego = panel_opciones.vel_actual

        if not juego_pausado and not mostrando_controles:
            jugador.update(escena_actual, velocidad_juego=velocidad_juego, teclas_joystick=teclas_joystick)

        panel_opciones.update()
        particulas.update()

        if escena_actual == "tutorial": petalos.update(escena_actual)
        if hada.activa: hada.update(jugador.rect.midbottom)
        dialogo_box.update(); mensaje_advertencia.update(); puntuacion_flotante.update()
        if escena_actual == "tutorial": puerta_entrada.update()
        elif escena_actual == "interior": puerta_salida.update()
        shadow_bonnie_interior.update()
        if escena_actual == "tierra_musical":
            cinematica_tierra_musical.update()
            # ✅ FIX: update del sistema disco en tierra_musical
            sistema_disco.update()

        if not juego_pausado and escena_actual != "menu":
            if barra_vida.vida <= 0:
                if sistema_vidas.tiene_vidas():
                    barra_vida.vida = barra_vida.vida_maxima
                    sistema_vidas.perder_vida()
                    mensaje_advertencia.mostrar(f"❌ PERDISTE UNA VIDA - QUEDAN {sistema_vidas.vidas_actuales}")
                else:
                    juego_pausado = True
                    mensaje_advertencia.mostrar("💀 ¡GAME OVER!")

        if not transicion.activa:
            if escena_actual == "tutorial" and jugador.rect.right >= ANCHO-50:
                def ir_aldea():
                    global escena_actual, fondo_actual
                    historial_escenas.append(("tutorial", jugador.rect.midbottom))
                    escena_actual="aldea"; fondo_actual=fondo_aldea
                    jugador.rect.midbottom=(100,PISO_Y)
                    cargar_musica(escena_actual); nombre_mapa.mostrar(escena_actual)
                    if not hada.activa: hada.activar(jugador.rect.midbottom)
                transicion.iniciar(ir_aldea)

            elif escena_actual == "aldea" and jugador.rect.right >= ANCHO-50:
                def ir_bosque():
                    global escena_actual, fondo_actual, oleada_actual, oleada_completada, enemigos
                    historial_escenas.append(("aldea", jugador.rect.midbottom))
                    escena_actual="bosque"; fondo_actual=fondo_bosque
                    jugador.rect.midbottom=(100,PISO_Y_BOSQUE)
                    cargar_musica(escena_actual); nombre_mapa.mostrar(escena_actual)
                    oleada_actual=0; oleada_completada=True; enemigos=[]
                    spawn_oleada()
                transicion.iniciar(ir_bosque)

            elif escena_actual == "bosque" and jugador.rect.right >= ANCHO-50:
                if tierra_musical_desbloqueada:
                    def ir_tierra():
                        global escena_actual, fondo_actual
                        historial_escenas.append(("bosque", jugador.rect.midbottom))
                        escena_actual="tierra_musical"; fondo_actual=fondo_tierra_musical
                        jugador.rect.midbottom=(100,PISO_Y_BOSQUE)
                        cargar_musica(escena_actual); nombre_mapa.mostrar(escena_actual)
                        cinematica_tierra_musical.iniciar()
                    transicion.iniciar(ir_tierra)
                else:
                    mensaje_advertencia.mostrar(f"❌ DEBES MATAR {enemigos_necesarios-enemigos_matados} ENEMIGOS MÁS")

        transicion.update()
        nombre_mapa.update()

        # ✅ FIX: plataformas_tierra_musical está vacía, este loop no hace nada (sin hitbox oculta)
        if escena_actual == "tierra_musical":
            for plat in plataformas_tierra_musical:
                if (jugador.vel_y >= 0 and
                    jugador.rect.bottom <= plat.rect.top+10 and
                    jugador.rect.bottom+jugador.vel_y >= plat.rect.top and
                    jugador.rect.left < plat.rect.right and
                    jugador.rect.right > plat.rect.left):
                    jugador.rect.bottom=plat.rect.top; jugador.vel_y=0
                    jugador.en_suelo=True; jugador.saltando=False

        if escena_actual == "bosque" and not juego_pausado:
            if cesped: cesped.update()
            hojas.update(escena_actual)
            ev = len([e for e in enemigos if not e.muerto])
            if ev == 0 and oleada_completada: oleada_completada=False; tiempo_ultima_oleada=pygame.time.get_ticks()
            if not oleada_completada and pygame.time.get_ticks()-tiempo_ultima_oleada >= cooldown_entre_oleadas:
                oleada_actual += 1
                if oleada_actual==1: tamano_oleada=1
                elif oleada_actual==2: tamano_oleada=2
                elif oleada_actual==3: tamano_oleada=3
                else: tamano_oleada=max_enemigos_por_oleada
                spawn_oleada(); oleada_completada=True
            for enemigo in enemigos:
                enemigo.update(escena_actual)
                if not enemigo.activo or enemigo.muerto: continue
                resultado = jugador.verificar_colision_enemigo(enemigo)
                if resultado == "matar_enemigo":
                    enemigo.muerte_por_contraataque(puntuacion_flotante)
                    enemigos_matados += 1
                    if enemigos_matados >= enemigos_necesarios and not jugador.doble_salto_desbloqueado:
                        jugador.doble_salto_desbloqueado=True
                        mensaje_advertencia.mostrar("✨ ¡DOBLE SALTO ACTIVADO!")
                    if enemigos_matados >= enemigos_necesarios and not tierra_musical_desbloqueada:
                        tierra_musical_desbloqueada=True
                        mensaje_advertencia.mostrar("🍬 ¡TIERRA MUSICAL DESBLOQUEADA!")
                elif jugador.hitbox.colliderect(enemigo.hitbox):
                    if not jugador.invencible_durante_ataque and not jugador.esta_mareado and not jugador.invencible:
                        jugador.recibir_dano(20, barra_vida)

    # ============================================================
    # RENDERIZADO
    # ============================================================
    try:
        if cinematica_tierra_musical.activa:
            pantalla.fill((0,0,0))
            cinematica_tierra_musical.draw(pantalla)
        elif cinematica.activa:
            cinematica.draw(pantalla)
        elif escena_actual == "menu":
            menu.draw(pantalla)
            if mostrando_controles: pantalla_controles.draw(pantalla)
        else:
            pantalla.blit(fondo_actual, (0,0))

            if escena_actual == "bosque" and cesped: cesped.draw(pantalla); hojas.draw(pantalla, escena_actual)
            if escena_actual == "tutorial": petalos.draw(pantalla, escena_actual)
            # ✅ FIX: sin plataformas, draw_debug no dibuja nada (lista vacía)
            if escena_actual == "tierra_musical":
                for plat in plataformas_tierra_musical: plat.draw_debug(pantalla)
            if escena_actual == "interior":
                poster_toy_freddy.draw(pantalla)
                shadow_bonnie_interior.draw(pantalla)
                mapa2.draw(pantalla, mapa2.verificar_colision(jugador.rect))
            # ✅ FIX: sistema_disco.draw en su propio bloque correcto (fuera de "interior")
            if escena_actual == "tierra_musical":
                sistema_disco.draw(pantalla)

            if escena_actual == "tutorial":
                puerta_entrada.draw_indicator(pantalla, puerta_entrada.verificar_colision(jugador.rect))
            elif escena_actual == "interior":
                puerta_salida.draw_indicator(pantalla, puerta_salida.verificar_colision(jugador.rect))

            if hada.activa: hada.draw(pantalla, hada.verificar_interaccion(jugador.rect))

            jugador.draw(pantalla)

            if escena_actual == "bosque":
                for e in enemigos: e.draw(pantalla); e.draw_mensaje(pantalla)

            puntuacion_flotante.draw(pantalla)
            puntuacion_flotante.draw_total(pantalla)
            barra_vida.draw(pantalla)
            sistema_vidas.draw(pantalla)

            if escena_actual == "bosque":
                fuente_c = pygame.font.Font(None, 36)
                tc = fuente_c.render(f"ENEMIGOS: {enemigos_matados}/{enemigos_necesarios}", True, (255,255,0))
                rc = tc.get_rect(topleft=(20,60))
                fd = pygame.Surface((rc.width+20,rc.height+10), pygame.SRCALPHA)
                pygame.draw.rect(fd,(0,0,0,150),fd.get_rect(),border_radius=8)
                pantalla.blit(fd,(rc.x-10,rc.y-5)); pantalla.blit(tc,rc)
                if jugador.doble_salto_desbloqueado:
                    td = pygame.font.Font(None,24).render("✨ DOBLE SALTO ACTIVADO", True, (100,200,255))
                    rd = td.get_rect(topleft=(20,160))
                    fd2 = pygame.Surface((rd.width+20,rd.height+10),pygame.SRCALPHA)
                    pygame.draw.rect(fd2,(20,100,200,200),fd2.get_rect(),border_radius=8)
                    pantalla.blit(fd2,(rd.x-10,rd.y-5)); pantalla.blit(td,rd)
                if tierra_musical_desbloqueada:
                    tt = pygame.font.Font(None,24).render("🍬 ¡TIERRA MUSICAL DESBLOQUEADA!", True, (255,215,0))
                    rt = tt.get_rect(topleft=(20,110))
                    ft = pygame.Surface((rt.width+20,rt.height+10),pygame.SRCALPHA)
                    pygame.draw.rect(ft,(139,69,19,200),ft.get_rect(),border_radius=8)
                    pantalla.blit(ft,(rt.x-10,rt.y-5)); pantalla.blit(tt,rt)

            dialogo_box.draw(pantalla)
            mensaje_advertencia.draw(pantalla)

            if panel_opciones.controles_visibles:
                joystick.draw(pantalla)
            boton_pausa.draw(pantalla, boton_pausa.verificar_hover(mouse_pos))
            boton_opciones.draw(pantalla, boton_opciones.verificar_hover(mouse_pos))
            if panel_opciones.controles_visibles:
                boton_q.draw(pantalla, boton_q.verificar_hover(mouse_pos))
                boton_w.draw(pantalla, boton_w.verificar_hover(mouse_pos))
                boton_t.draw(pantalla, boton_t.verificar_hover(mouse_pos))
                boton_e.draw(pantalla, boton_e.verificar_hover(mouse_pos))
                boton_r.draw(pantalla, boton_r.verificar_hover(mouse_pos))

            if juego_pausado:
                ov = pygame.Surface((ANCHO,ALTO), pygame.SRCALPHA)
                ov.fill((0,0,0,140)); pantalla.blit(ov,(0,0))
                tp = pygame.font.Font(None,120).render("PAUSADO", True, (255,215,100))
                pantalla.blit(tp, tp.get_rect(center=(ANCHO//2,ALTO//2)))

            if mostrando_controles: pantalla_controles.draw(pantalla)

            panel_opciones.draw(pantalla)
            particulas.draw(pantalla)

            nombre_mapa.draw(pantalla)
            transicion.draw(pantalla)

    except Exception as e:
        print(f"❌ Error en renderizado: {e}")
        pantalla.fill((0,0,0))
        pantalla.blit(pygame.font.Font(None,48).render(f"ERROR: {str(e)[:40]}", True, (255,100,100)), (50,300))
    pygame.display.flip()

pygame.quit()
sys.exit()