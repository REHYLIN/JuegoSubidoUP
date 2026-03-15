# ================================================================
#  BolaMusical.py  v2  –  Discoteca para Tierra Musical
#  Uso standalone : python BolaMusical.py
#  Uso en main.py : from BolaMusical import BolaMusical
#                   sistema = BolaMusical()
#                   sistema.update()
#                   sistema.draw(pantalla)
# ================================================================

import pygame
import sys
import math
import random

ANCHO, ALTO = 1200, 640
PISO_Y      = 510
BPM         = 128
BEAT_MS     = int(60_000 / BPM)

COLORES = [
    (255,  50, 210),
    ( 50, 200, 255),
    (255, 215,   0),
    (100, 255, 100),
    (255, 100,  50),
    (160,  50, 255),
    (255, 255, 100),
    ( 50, 255, 200),
    (255,  70, 120),
    (210,  80, 255),
]

def _cidx(t_ms: int, vel: float = 1.0) -> int:
    return int(t_ms * vel / 500) % len(COLORES)


class SistemaBeat:
    def __init__(self):
        self._beat_num   = -1
        self._pulso      = 0.0
        self._nuevo_beat = False

    def update(self) -> bool:
        ahora       = pygame.time.get_ticks()
        beat_actual = ahora // BEAT_MS
        self._nuevo_beat = False
        if beat_actual != self._beat_num:
            self._beat_num   = beat_actual
            self._pulso      = 1.0
            self._nuevo_beat = True
        else:
            self._pulso = max(0.0, self._pulso * 0.87)
        return self._nuevo_beat

    @property
    def pulso(self)      -> float: return self._pulso
    @property
    def beat_num(self)   -> int:   return self._beat_num
    @property
    def nuevo_beat(self) -> bool:  return self._nuevo_beat


class HacesLuz:
    _POS_X = [70, 220, 390, 600, 810, 980, 1130]

    def __init__(self):
        self._surf = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        self.focos = [
            dict(
                x    = x,
                ang  = random.uniform(-0.55, 0.55),
                vel  = random.uniform(0.007, 0.020) * random.choice([-1, 1]),
                lon  = random.randint(370, 570),
                aper = random.uniform(0.07, 0.16),
                cfas = float(i * 1.1),
                cvel = random.uniform(0.002, 0.006),
                cidx = i % len(COLORES),
                alph = random.randint(28, 52),
            )
            for i, x in enumerate(self._POS_X)
        ]

    def update(self, beat: SistemaBeat):
        for f in self.focos:
            f['ang'] += f['vel']
            if abs(f['ang']) > 0.85:
                f['vel'] *= -1.0
            f['cfas'] += f['cvel']
            f['cidx']  = int(f['cfas']) % len(COLORES)
            if beat.nuevo_beat and random.random() < 0.40:
                f['vel'] = random.uniform(0.008, 0.024) * random.choice([-1, 1])

    def draw(self, pantalla: pygame.Surface):
        self._surf.fill((0, 0, 0, 0))
        for f in self.focos:
            ang, lon, aper = f['ang'], f['lon'], f['aper']
            px = f['x']
            p0 = (px, 0)
            p1 = (int(px + math.sin(ang - aper) * lon),
                  int(math.cos(ang - aper) * lon))
            p2 = (int(px + math.sin(ang + aper) * lon),
                  int(math.cos(ang + aper) * lon))
            c = COLORES[f['cidx']]
            pygame.draw.polygon(self._surf, (*c, f['alph']), [p0, p1, p2])
            pygame.draw.circle(self._surf, (*c, 200), (px, 4), 7)
        pantalla.blit(self._surf, (0, 0))


# ──────────────────────────────────────────────────────────────
#  BOLA DISCO — Pixel Art + Spots de luz reales
# ──────────────────────────────────────────────────────────────
class BolaDisco:
    TILES_X = 7
    TILES_Y = 7

    def __init__(self, x: int = ANCHO // 2, y: int = 72, radio: int = 60):
        self.x       = x
        self.y       = y
        self.radio   = radio
        self.rot     = 0.0
        self.vel_rot = 0.55

        self.spots = self._generar_spots()
        self._surf_spots = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        self._surf_bola  = pygame.Surface((radio*2+4, radio*2+4), pygame.SRCALPHA)

    def _generar_spots(self) -> list:
        spots = []
        n = 20
        for i in range(n):
            ang_base = (i / n) * math.tau
            spots.append(dict(
                ang_base      = ang_base,
                radio_barrido = random.randint(130, 400),
                altura        = random.uniform(290, PISO_Y - 20),
                cidx          = i % len(COLORES),
                tam           = random.randint(10, 20),
                vel_propia    = random.uniform(0.4, 1.1) * random.choice([-1, 1]),
                fase_propia   = random.uniform(0, math.tau),
                cx            = 0.0,
                cy            = 0.0,
            ))
        return spots

    def update(self, beat: SistemaBeat):
        self.rot = (self.rot + self.vel_rot) % 360.0
        rot_rad  = math.radians(self.rot)

        for s in self.spots:
            s['fase_propia'] += 0.018
            ang = s['ang_base'] + rot_rad * s['vel_propia']
            s['cx'] = self.x + math.cos(ang) * s['radio_barrido']
            s['cy'] = s['altura'] + math.sin(s['fase_propia']) * 38
            if beat.nuevo_beat and random.random() < 0.25:
                s['cidx'] = (s['cidx'] + random.randint(1, 3)) % len(COLORES)

    def _dibujar_bola(self):
        s   = self._surf_bola
        s.fill((0, 0, 0, 0))
        r   = self.radio
        cx  = r + 2
        cy  = r + 2
        t_ms = pygame.time.get_ticks()

        # Base gris oscuro
        pygame.draw.circle(s, (35, 38, 48), (cx, cy), r)

        tw = (r * 2) // self.TILES_X
        th = (r * 2) // self.TILES_Y
        rot_off = int(self.rot / 8)
        t_cycle = int(t_ms / 380)
        r2_limit = (r - 4) ** 2

        for ty in range(self.TILES_Y):
            for tx in range(self.TILES_X):
                px  = cx - r + tx * tw
                py  = cy - r + ty * th
                tcx = px + tw // 2
                tcy = py + th // 2
                if (tcx - cx)**2 + (tcy - cy)**2 < r2_limit:
                    fase = (tx + ty + rot_off + t_cycle) % len(COLORES)
                    bf   = abs(math.sin(math.radians(
                        self.rot * 4 + tx * 30 + ty * 25
                    )))
                    br  = int(bf * 180 + 75)
                    mod = (tx + ty + rot_off) % 4

                    if mod == 0:
                        c   = COLORES[fase]
                        col = (
                            min(255, int(c[0] * bf * 0.8 + 50)),
                            min(255, int(c[1] * bf * 0.8 + 40)),
                            min(255, int(c[2] * bf * 0.8 + 60)),
                        )
                    elif mod == 2:
                        c   = COLORES[(fase + 5) % len(COLORES)]
                        col = (
                            min(255, int(c[0] * 0.5 + 80)),
                            min(255, int(c[1] * 0.5 + 70)),
                            min(255, int(c[2] * 0.5 + 90)),
                        )
                    else:
                        col = (min(255, br+20), min(255, br+15), min(255, br+30))

                    # Tile con borde negro duro (pixel art)
                    pygame.draw.rect(s, col,
                                     (int(px+1), int(py+1), tw-2, th-2))
                    pygame.draw.rect(s, (12, 12, 18),
                                     (int(px), int(py), tw, th), 1)

        # Brillo especular
        bsurf = pygame.Surface((tw*2, th), pygame.SRCALPHA)
        pygame.draw.ellipse(bsurf, (255, 255, 255, 190), (0, 0, tw*2, th))
        s.blit(bsurf, (cx - tw, cy - r + th))

        # Borde exterior
        pygame.draw.circle(s, (10, 10, 16), (cx, cy), r, 3)

    def draw(self, pantalla: pygame.Surface, beat: SistemaBeat):
        base_alpha = 55 + int(beat.pulso * 80)

        # 1) Spots de luz proyectados
        self._surf_spots.fill((0, 0, 0, 0))
        for sp in self.spots:
            cx, cy = int(sp['cx']), int(sp['cy'])
            tam = sp['tam']
            c   = COLORES[sp['cidx']]
            for layer in range(3):
                pad = (layer + 1) * 4
                a   = max(0, base_alpha // (layer + 2))
                gs  = pygame.Surface((tam + pad*2, tam + pad*2), pygame.SRCALPHA)
                pygame.draw.rect(gs, (*c, a), (0, 0, tam + pad*2, tam + pad*2))
                self._surf_spots.blit(gs, (cx - tam//2 - pad, cy - tam//2 - pad))
            pygame.draw.rect(self._surf_spots, (*c, min(255, base_alpha + 60)),
                             (cx - tam//2, cy - tam//2, tam, tam))
        pantalla.blit(self._surf_spots, (0, 0))

        # 2) Halo glow
        t_ms   = pygame.time.get_ticks()
        halo_c = COLORES[_cidx(t_ms)]
        r_halo = self.radio + 8 + int(beat.pulso * 18)
        hd     = r_halo * 2 + 40
        hsurf  = pygame.Surface((hd, hd), pygame.SRCALPHA)
        for i in range(4):
            ri = r_halo - i * 5
            if ri < 1:
                break
            a = max(0, int((15 + beat.pulso * 30) / (i + 1)))
            pygame.draw.circle(hsurf, (*halo_c, a), (hd//2, hd//2), ri)
        pantalla.blit(hsurf, (self.x - hd//2, self.y - hd//2))

        # 3) Bola pixel art
        self._dibujar_bola()
        pantalla.blit(self._surf_bola,
                      (self.x - self.radio - 2, self.y - self.radio - 2))

        # 4) Cable
        pygame.draw.line(pantalla, (70, 80, 100),
                         (self.x, 0), (self.x, self.y - self.radio), 2)


# ──────────────────────────────────────────────────────────────
#  SPEAKERS — posiciones sobre los orificios azules del mapa
# ──────────────────────────────────────────────────────────────
class EfectoSpeaker:
    """
    Posiciones medidas sobre TierraMusical.png 1200x640.
    Cada tupla = centro del orificio/luz azul de una bocina.

    Col izq exterior (x≈62) : 4 bocinas en y 175,282,388,478
    Col izq interior (x≈158): 3 bocinas en y 215,328,432
    Col der interior (x≈1042): 3 bocinas en y 215,328,432
    Col der exterior (x≈1138): 4 bocinas en y 175,282,388,478
    """
    POS = [
        # Columna izq exterior
        ( 62, 175), ( 62, 282), ( 62, 388), ( 62, 478),
        # Columna izq interior
        (158, 215), (158, 328), (158, 432),
        # Columna der interior
        (1042, 215), (1042, 328), (1042, 432),
        # Columna der exterior
        (1138, 175), (1138, 282), (1138, 388), (1138, 478),
    ]

    def __init__(self):
        self._surf  = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        self.ondas: list[dict] = []

    def _activar(self, beat_num: int):
        cidx = beat_num % len(COLORES)
        c1   = COLORES[cidx]
        c2   = COLORES[(cidx + 3) % len(COLORES)]
        for px, py in self.POS:
            self.ondas.append(dict(x=px, y=py, r=10, vida=22, vmax=22,
                                   color=c1, gros=3))
            self.ondas.append(dict(x=px, y=py, r=4,  vida=14, vmax=14,
                                   color=c2, gros=2))

    def update(self, beat: SistemaBeat):
        if beat.nuevo_beat:
            self._activar(beat.beat_num)
        nuevas = []
        for o in self.ondas:
            o['r']    += 6
            o['vida'] -= 1
            if o['vida'] > 0:
                nuevas.append(o)
        self.ondas = nuevas

    def draw(self, pantalla: pygame.Surface, beat: SistemaBeat):
        self._surf.fill((0, 0, 0, 0))

        # Ondas expansivas
        for o in self.ondas:
            a = int(200 * o['vida'] / o['vmax'])
            pygame.draw.circle(self._surf, (*o['color'], a),
                               (o['x'], o['y']), o['r'], o['gros'])

        # Glow fijo pulsante
        t_ms = pygame.time.get_ticks()
        pr   = int(14 + beat.pulso * 12)
        for i, (px, py) in enumerate(self.POS):
            gc = COLORES[_cidx(t_ms + i * 80)]
            for layer in range(3):
                ri = pr - layer * 4
                if ri < 1:
                    continue
                a = int((22 + beat.pulso * 50) / (layer + 1))
                pygame.draw.circle(self._surf, (*gc, a), (px, py), ri)

        pantalla.blit(self._surf, (0, 0))


class PisoMusical:
    Y0     = 478
    TILE_W = 80
    TILE_H = 42
    FILAS  = 5

    def __init__(self):
        cols       = ANCHO // self.TILE_W + 1
        self._surf = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        self.tiles = [
            dict(
                col  = c,
                fila = f,
                cidx = (c + f * 3) % len(COLORES),
                fase = random.uniform(0, math.tau),
                vel  = random.uniform(0.04, 0.10),
            )
            for f in range(self.FILAS)
            for c in range(cols)
        ]

    def update(self, beat: SistemaBeat):
        for t in self.tiles:
            t['fase'] += t['vel']
            if beat.nuevo_beat and random.random() < 0.14:
                t['cidx'] = (t['cidx'] + 1) % len(COLORES)

    def draw(self, pantalla: pygame.Surface, beat: SistemaBeat):
        self._surf.fill((0, 0, 0, 0))
        for t in self.tiles:
            x  = t['col']  * self.TILE_W
            y  = self.Y0   + t['fila'] * self.TILE_H
            bf = (math.sin(t['fase']) * 0.28 + 0.72) * (1.0 + beat.pulso * 0.38)
            bf = min(1.0, bf)
            c  = COLORES[t['cidx']]
            a  = int(min(255, 65 * bf + beat.pulso * 55))
            col = tuple(min(255, int(ch * bf * 0.75)) for ch in c)
            pygame.draw.rect(self._surf, (*col, a),
                             (x + 1, y + 1, self.TILE_W - 2, self.TILE_H - 2))
        pantalla.blit(self._surf, (0, 0))


class ParticulasDiscotek:
    MAX = 120

    def __init__(self):
        self.pts: list[dict] = []

    def _emitir(self, n: int = 10):
        for _ in range(n):
            self.pts.append(dict(
                x    = random.uniform(60, ANCHO - 60),
                y    = random.uniform(60, 460),
                vx   = random.uniform(-2.0, 2.0),
                vy   = random.uniform(-3.0, -0.4),
                vida = random.randint(50, 95),
                vmax = 95,
                cidx = random.randrange(len(COLORES)),
                tam  = random.randint(3, 8),
            ))
        if len(self.pts) > self.MAX:
            self.pts = self.pts[-self.MAX:]

    def update(self, beat: SistemaBeat):
        if beat.nuevo_beat:
            self._emitir(random.randint(8, 14))
        nuevas = []
        for p in self.pts:
            p['x']   += p['vx']
            p['y']   += p['vy']
            p['vy']  += 0.045
            p['vida'] -= 1
            if p['vida'] > 0:
                nuevas.append(p)
        self.pts = nuevas

    def draw(self, pantalla: pygame.Surface):
        for p in self.pts:
            a  = int(240 * p['vida'] / p['vmax'])
            t  = p['tam']
            ps = pygame.Surface((t, t), pygame.SRCALPHA)
            pygame.draw.rect(ps, (*COLORES[p['cidx']], a), (0, 0, t, t))
            pantalla.blit(ps, (int(p['x']), int(p['y'])))


class EstrellasBrillo:
    def __init__(self):
        self.estrellas: list[dict] = []
        for _ in range(30):
            self._nueva()

    def _nueva(self):
        self.estrellas.append(dict(
            x     = random.uniform(0, ANCHO),
            y     = random.uniform(0, PISO_Y),
            vida  = random.randint(20, 60),
            vmax  = 60,
            cidx  = random.randrange(len(COLORES)),
            tam   = random.randint(2, 6),
            fase  = random.uniform(0, math.tau),
        ))

    def update(self, beat: SistemaBeat):
        if beat.nuevo_beat:
            for _ in range(random.randint(4, 8)):
                self._nueva()
        nuevas = []
        for e in self.estrellas:
            e['vida'] -= 1
            e['fase'] += 0.25
            if e['vida'] > 0:
                nuevas.append(e)
        self.estrellas = nuevas

    def draw(self, pantalla: pygame.Surface):
        for e in self.estrellas:
            a  = int(255 * abs(math.sin(e['fase'])) * e['vida'] / e['vmax'])
            t  = e['tam']
            c  = COLORES[e['cidx']]
            cx = int(e['x'])
            cy = int(e['y'])
            pygame.draw.line(pantalla, c, (cx - t, cy), (cx + t, cy), 1)
            pygame.draw.line(pantalla, c, (cx, cy - t), (cx, cy + t), 1)
            if t >= 3:
                pygame.draw.rect(pantalla, c, (cx - 1, cy - 1, 2, 2))


# ──────────────────────────────────────────────────────────────
#  FACHADA PÚBLICA
# ──────────────────────────────────────────────────────────────
class BolaMusical:
    def __init__(self, bola_x: int = ANCHO // 2, bola_y: int = 72):
        self.beat       = SistemaBeat()
        self.focos      = HacesLuz()
        self.bola       = BolaDisco(bola_x, bola_y, radio=60)
        self.speakers   = EfectoSpeaker()
        self.piso       = PisoMusical()
        self.particulas = ParticulasDiscotek()
        self.estrellas  = EstrellasBrillo()

    def update(self):
        self.beat.update()
        self.focos.update(self.beat)
        self.bola.update(self.beat)
        self.speakers.update(self.beat)
        self.piso.update(self.beat)
        self.particulas.update(self.beat)
        self.estrellas.update(self.beat)

    def draw(self, pantalla: pygame.Surface):
        self.focos.draw(pantalla)
        self.piso.draw(pantalla, self.beat)
        self.speakers.draw(pantalla, self.beat)
        self.estrellas.draw(pantalla)
        self.particulas.draw(pantalla)
        self.bola.draw(pantalla, self.beat)


# ──────────────────────────────────────────────────────────────
#  STANDALONE
# ──────────────────────────────────────────────────────────────
def _cargar_fondo(ruta, ancho, alto):
    try:
        img  = pygame.image.load(ruta).convert()
        iw, ih = img.get_size()
        ratio  = max(ancho / iw, alto / ih) * 1.02
        nw, nh = int(iw * ratio), int(ih * ratio)
        esc    = pygame.transform.smoothscale(img, (nw, nh))
        surf   = pygame.Surface((ancho, alto))
        surf.fill((5, 0, 18))
        surf.blit(esc, ((ancho - nw) // 2, (alto - nh) // 2))
        return surf
    except Exception as e:
        print(f"⚠️ {e}")
        surf = pygame.Surface((ancho, alto))
        for y in range(alto):
            pygame.draw.line(surf, (8, 0, 28 + int(y/alto*55)), (0, y), (ancho, y))
        return surf


if __name__ == "__main__":
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Tierra Musical – Bola Disco v2")
    clock = pygame.time.Clock()

    fondo   = _cargar_fondo("img/TierraMusical.png", ANCHO, ALTO)
    sistema = BolaMusical()

    running = True
    while running:
        clock.tick(60)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                running = False
        sistema.update()
        pantalla.blit(fondo, (0, 0))
        sistema.draw(pantalla)
        pygame.display.flip()

    pygame.quit()
    sys.exit()