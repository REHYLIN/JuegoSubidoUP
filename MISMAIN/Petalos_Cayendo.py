# petalos_cayendo.py (versión mejorada y corregida)
import pygame
import math
import random

class PetalosCayendo:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.tiempo = 0
        self.activo = False
        
        # Colores más suaves y pastel
        self.color_rosa = (255, 200, 220)      # rosa muy claro
        self.color_rosa_oscuro = (240, 160, 190)
        self.color_rosa_brillo = (255, 230, 240)
        
        self.petalos = []
        self.crear_petalos_iniciales(cantidad=25)  # ✅ Aumentado a 25 para mejor visibilidad

    def crear_petalos_iniciales(self, cantidad=25):
        for _ in range(cantidad):
            self._crear_un_petalo(inicial=True)

    def _crear_un_petalo(self, inicial=False):
        tamano = random.randint(8, 14)  # ✅ Un poco más grandes para verse mejor
        
        if inicial:
            x = random.uniform(0, self.ancho)
            y = random.uniform(-self.alto * 1.5, self.alto)
        else:
            x = random.uniform(-50, self.ancho + 50)
            y = random.uniform(-80, -20)
        
        self.petalos.append({
            'x': x,
            'y': y,
            'tamano': tamano,
            'vel_y': random.uniform(0.6, 1.5),      # ✅ Caída más lenta
            'vel_x': random.uniform(-0.6, 0.6),
            'rotacion': random.uniform(0, 360),
            'vel_rotacion': random.uniform(-1.5, 1.5),
            'alpha': random.randint(120, 200),      # ✅ Más visibles (120-200 en lugar de 90-160)
            'oscilacion_fase': random.uniform(0, 2 * math.pi)  # Fase para la onda
        })

    def update(self, escena_actual):
        """✅ CORREGIDO: Solo funciona en tutorial"""
        if escena_actual != "tutorial":
            self.activo = False
            return
        
        self.activo = True
        self.tiempo += 0.016
        nuevos_petalos = []
        
        for p in self.petalos:
            # Movimiento vertical
            p['y'] += p['vel_y']
            
            # Movimiento horizontal con onda suave
            onda = math.sin(self.tiempo * 1.2 + p['oscilacion_fase']) * 0.7
            p['x'] += p['vel_x'] + onda
            
            # Rotación
            p['rotacion'] += p['vel_rotacion']
            
            # Reciclar pétalo si sale de pantalla
            if p['y'] > self.alto + 50:
                p['y'] = random.uniform(-80, -20)
                p['x'] = random.uniform(0, self.ancho)
                p['vel_y'] = random.uniform(0.6, 1.5)
                p['vel_x'] = random.uniform(-0.6, 0.6)
                p['alpha'] = random.randint(120, 200)
                p['oscilacion_fase'] = random.uniform(0, 2 * math.pi)
            
            nuevos_petalos.append(p)
        
        self.petalos = nuevos_petalos
        
        # ✅ Mantener cantidad estable (20-30 pétalos)
        while len(self.petalos) < 20:
            self._crear_un_petalo()

    def draw(self, pantalla, escena_actual):
        """✅ CORREGIDO: Solo dibuja en tutorial y con mejor visualización"""
        if escena_actual != "tutorial":
            return
        
        for p in self.petalos:
            # Crear superficie para el pétalo
            tamano_surf = int(p['tamano'] * 2.5)
            sup = pygame.Surface((tamano_surf, tamano_surf), pygame.SRCALPHA)
            
            # Dibujar pétalo base (forma ovalada)
            radio_x = int(p['tamano'] * 1.2)
            radio_y = int(p['tamano'] * 0.6)
            pygame.draw.ellipse(sup, 
                              self.color_rosa + (p['alpha'],), 
                              (tamano_surf // 2 - radio_x, 
                               tamano_surf // 2 - radio_y, 
                               radio_x * 2, 
                               radio_y * 2))
            
            # Sombra más visible
            pygame.draw.ellipse(sup, 
                              self.color_rosa_oscuro + (int(p['alpha'] * 0.5),), 
                              (tamano_surf // 2 - int(radio_x * 0.7), 
                               tamano_surf // 2 - int(radio_y * 0.3), 
                               int(radio_x * 1.4), 
                               int(radio_y * 0.6)))
            
            # Brillo central
            pygame.draw.circle(sup, 
                             self.color_rosa_brillo + (int(p['alpha'] * 0.6),), 
                             (tamano_surf // 2, tamano_surf // 2 - int(radio_y * 0.3)), 
                             int(p['tamano'] * 0.4))
            
            # Rotar superficie
            sup_rot = pygame.transform.rotate(sup, p['rotacion'])
            rect = sup_rot.get_rect(center=(int(p['x']), int(p['y'])))
            
            # Dibujar pétalo rotado
            pantalla.blit(sup_rot, rect)
