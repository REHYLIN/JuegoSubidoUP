import pygame
import math
import random

class CespedMovil:
    def __init__(self, ancho, alto, y_base):
        self.ancho = ancho
        self.alto = alto
        self.y_base = y_base
        self.blades = []
        self.brotando = []
        self.dientes_leon = []
        self.num_blades = 1200
        self.tiempo = 0.0
        self.offset_x = 0.0
        self.wind_global = 0.0
        self.gusts = []
        
        # ✅ VARIABLES PARA ANIMACIÓN CONTINUA
        self.tiempo_total = 0.0  # Tiempo GLOBAL (siempre aumenta)
        
        self.generate_all()
        print("🌿 CespedMovil listo - ANIMA SIEMPRE (sin necesidad de movimiento)")

    def generate_all(self):
        """Generar césped"""
        for _ in range(self.num_blades):
            x = random.uniform(-self.ancho * 0.6, self.ancho * 1.6)
            height = random.gauss(24, 11)
            height = max(12, min(48, height))
            phase = random.uniform(0, math.tau * 5)
            sway_amp = random.uniform(0.85, 1.8)
            thickness = random.uniform(1.4, 3.0)
            green_base = random.randint(90, 165)
            self.blades.append({
                'x': x,
                'height': height,
                'phase': phase,
                'sway_amp': sway_amp,
                'thickness': thickness,
                'green_base': green_base
            })

        # Briznas que brotan
        for _ in range(50):
            x = random.uniform(0, self.ancho)
            self.brotando.append({
                'x': x,
                'progress': random.uniform(0, 1),
                'speed': random.uniform(0.01, 0.022),
                'max_height': random.uniform(20, 42),
                'phase': random.uniform(0, math.tau),
                'active': True
            })

    def update(self):
        """✅ ACTUALIZACIÓN CONTINUA - Anima SIEMPRE"""
        dt = 1 / 60.0
        self.tiempo += dt * 1.45
        self.tiempo_total += dt * 1.45  # ✅ TIEMPO GLOBAL - SIEMPRE AVANZA

        # Viento constante
        self.wind_global = (
            0.48 +
            math.sin(self.tiempo * 2.4) * 0.8 +
            math.cos(self.tiempo * 1.1) * 0.55 +
            math.sin(self.tiempo * 5.2 + 2.0) * 0.35
        )

        # Offset se mueve SIEMPRE
        self.offset_x += self.wind_global * 2.6 * dt * 60

        # Ráfagas aleatorias
        if random.random() < 0.05:
            x_start = random.uniform(-100, self.ancho + 100)
            strength = random.uniform(-1.8, 2.8)
            duration = random.randint(80, 200)
            self.gusts.append([x_start, strength, duration])

        new_gusts = []
        for g in self.gusts:
            g[2] -= 1
            if g[2] > 0:
                new_gusts.append(g)
        self.gusts = new_gusts

        # Actualizar briznas que brotan
        for b in self.brotando:
            if b['active']:
                b['progress'] += b['speed']
                if b['progress'] >= 1.0:
                    self.blades.append({
                        'x': b['x'],
                        'height': b['max_height'],
                        'phase': b['phase'],
                        'sway_amp': random.uniform(0.9, 1.7),
                        'thickness': random.uniform(1.5, 2.8),
                        'green_base': random.randint(100, 170)
                    })
                    b['progress'] = 0.0
                    b['max_height'] = random.uniform(20, 42)
                    b['phase'] = random.uniform(0, math.tau)
                    b['active'] = random.random() < 0.4

        # Generar dientes de león
        if random.random() < 0.03:
            x = random.uniform(self.ancho * 0.1, self.ancho * 0.9)
            self.dientes_leon.append({
                'x': x,
                'y': self.y_base + random.uniform(-10, 20),
                'vy': random.uniform(-2.2, -1.0),
                'vx': random.uniform(-0.8, 0.8),
                'size': random.uniform(2.8, 5.0),
                'lifetime': random.randint(140, 340),
                'alpha': 255
            })

        # Actualizar semillas
        new_dientes = []
        for d in self.dientes_leon:
            d['x'] += d['vx'] + self.wind_global * 0.9
            d['y'] += d['vy']
            d['vy'] += 0.025
            d['lifetime'] -= 1
            d['alpha'] = int(255 * (d['lifetime'] / 340))
            if d['lifetime'] > 0:
                new_dientes.append(d)
        self.dientes_leon = new_dientes

    def get_wind_at_x(self, x):
        """Obtener viento en posición"""
        wind = self.wind_global
        for g in self.gusts:
            gx, gs, rem = g
            if gx - 80 <= x <= gx + 320:
                fade = max(0, 1 - abs(x - (gx + 120)) / 200)
                wind += gs * fade * (rem / 150)
        return max(-3.5, min(3.5, wind))

    def draw(self, surface):
        """Dibujar céspedmovil"""
        # Briznas que brotan
        for b in self.brotando:
            if b['active'] and b['progress'] > 0:
                h = b['max_height'] * b['progress']
                base_x = b['x'] + self.offset_x * 0.35
                tip_y = self.y_base - h
                tip_x = base_x + math.sin(self.tiempo_total * 6 + b['phase']) * 8 * b['progress']

                g = int(80 + 140 * b['progress'])
                color = (30 + int(60 * b['progress']), g, 20 + int(50 * b['progress']))
                w = int(2.5 + 2.5 * b['progress'])

                pygame.draw.line(surface, color,
                                 (base_x, self.y_base),
                                 (tip_x, tip_y), w)

                if b['progress'] > 0.5:
                    pygame.draw.circle(surface, (230, 255, 190),
                                       (int(tip_x), int(tip_y)), 2)

        # Césped principal
        for blade in self.blades:
            base_x = (blade['x'] + self.offset_x) % (self.ancho * 2.2) - self.ancho * 0.6
            wind = self.get_wind_at_x(base_x)

            # ✅ USAR TIEMPO_TOTAL PARA ANIMACIÓN CONTINUA
            osc = math.sin(self.tiempo_total * 7.0 + blade['phase']) * 0.72
            sway = (osc + wind * 0.95) * blade['sway_amp'] * blade['height'] * 0.26

            tip_x = base_x + sway
            tip_y = self.y_base - blade['height']

            g = blade['green_base']
            color_base = (25, max(85, g), 15)
            color_mid  = (45, min(235, g + 90), 35)
            color_tip  = (70, 250, 50)

            w_base = int(blade['thickness'] + abs(wind) * 0.8)
            w_tip = max(1, int(w_base * 0.45))

            mid_x = base_x + sway * 0.52
            mid_y = self.y_base - blade['height'] * 0.52

            pygame.draw.line(surface, color_base, (base_x, self.y_base), (mid_x, mid_y), w_base)
            pygame.draw.line(surface, color_mid,  (mid_x, mid_y),  (tip_x, tip_y), (w_base + w_tip)//2)
            pygame.draw.line(surface, color_tip,  (tip_x - sway*0.18, tip_y-5), (tip_x, tip_y), w_tip)

            if abs(wind) > 1.7:
                pygame.draw.circle(surface, (220, 255, 180),
                                   (int(tip_x), int(tip_y)), 3)

        # Dientes de león
        for d in self.dientes_leon:
            alpha = d['alpha']
            color_head = (255, 245, 190)
            color_stem = (30, 130, 20)

            stem_y = d['y'] + 10
            stem_x_offset = math.sin(self.tiempo_total * 4 + d['x']*0.08) * 4  # ✅ USAR TIEMPO_TOTAL
            pygame.draw.line(surface, color_stem,
                             (d['x'], d['y']),
                             (d['x'] + stem_x_offset, stem_y), 2)

            pygame.draw.circle(surface, color_head, (int(d['x'] + stem_x_offset), int(stem_y)), int(d['size']))

            for i in range(10):
                angle = i * (math.tau / 10) + self.tiempo_total * 2.5  # ✅ USAR TIEMPO_TOTAL
                ex = d['x'] + stem_x_offset + math.cos(angle) * d['size'] * 1.6
                ey = stem_y + math.sin(angle) * d['size'] * 1.6
                pygame.draw.line(surface, color_head,
                                 (d['x'] + stem_x_offset, stem_y), (ex, ey), 1)