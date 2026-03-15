# HojasCayendo.py
import pygame
import math
import random

class HojasCayendo:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.tiempo = 0.0
        self.activo = False
        
        # Colores de hojas verdes (variaciones naturales)
        self.color_verde_claro = (140, 220, 100)     # verde brillante
        self.color_verde_medio = (100, 180, 70)      # verde bosque
        self.color_verde_oscuro = (80, 140, 50)      # verde oscuro
        self.color_verde_brillo = (180, 255, 140)    # highlight
        
        self.hojas = []
        self.crear_hojas_iniciales(cantidad=15)  # menos que pétalos para no saturar

    def crear_hojas_iniciales(self, cantidad=15):
        for _ in range(cantidad):
            self._crear_una_hoja(inicial=True)

    def _crear_una_hoja(self, inicial=False):
        tamano = random.randint(8, 16)
        
        if inicial:
            x = random.uniform(0, self.ancho)
            y = random.uniform(-self.alto * 1.5, self.alto)
        else:
            x = random.uniform(-50, self.ancho + 50)
            y = random.uniform(-80, -20)
        
        self.hojas.append({
            'x': x,
            'y': y,
            'tamano': tamano,
            'vel_y': random.uniform(0.7, 1.6),
            'vel_x': random.uniform(-0.7, 0.7),
            'rotacion': random.uniform(0, 360),
            'vel_rotacion': random.uniform(-1.8, 1.8),
            'alpha': random.randint(140, 220),
            'oscilacion_fase': random.uniform(0, 2 * math.pi)
        })

    def update(self, escena_actual):
        if escena_actual != "bosque":
            self.activo = False
            return
        
        self.activo = True
        self.tiempo += 0.016  # tiempo avanza CADA FRAME, siempre
        
        nuevos_hojas = []
        
        for h in self.hojas:
            # Caída vertical constante
            h['y'] += h['vel_y']
            
            # Onda lateral suave (usando tiempo absoluto)
            onda = math.sin(self.tiempo * 1.2 + h['oscilacion_fase']) * 0.8
            h['x'] += h['vel_x'] + onda
            
            # Rotación constante
            h['rotacion'] += h['vel_rotacion']
            
            # Reciclar si sale de pantalla
            if h['y'] > self.alto + 50:
                h['y'] = random.uniform(-80, -20)
                h['x'] = random.uniform(0, self.ancho)
                h['vel_y'] = random.uniform(0.7, 1.6)
                h['vel_x'] = random.uniform(-0.7, 0.7)
                h['alpha'] = random.randint(140, 220)
                h['oscilacion_fase'] = random.uniform(0, 2 * math.pi)
            
            nuevos_hojas.append(h)
        
        self.hojas = nuevos_hojas
        
        # Mantener siempre 10–20 hojas visibles
        while len(self.hojas) < 10:
            self._crear_una_hoja()

    def draw(self, pantalla, escena_actual):
        if escena_actual != "bosque":
            return
        
        for h in self.hojas:
            tamano_surf = int(h['tamano'] * 2.5)
            sup = pygame.Surface((tamano_surf, tamano_surf), pygame.SRCALPHA)
            
            radio_x = int(h['tamano'] * 1.4)
            radio_y = int(h['tamano'] * 0.5)
            pygame.draw.ellipse(sup, 
                              self.color_verde_medio + (h['alpha'],), 
                              (tamano_surf // 2 - radio_x, 
                               tamano_surf // 2 - radio_y, 
                               radio_x * 2, 
                               radio_y * 2))
            
            pygame.draw.ellipse(sup, 
                              self.color_verde_oscuro + (int(h['alpha'] * 0.6),), 
                              (tamano_surf // 2 - int(radio_x * 0.7), 
                               tamano_surf // 2 - int(radio_y * 0.3), 
                               int(radio_x * 1.4), 
                               int(radio_y * 0.6)))
            
            pygame.draw.circle(sup, 
                             self.color_verde_brillo + (int(h['alpha'] * 0.7),), 
                             (tamano_surf // 2, tamano_surf // 2 - int(radio_y * 0.4)), 
                             int(h['tamano'] * 0.5))
            
            sup_rot = pygame.transform.rotate(sup, h['rotacion'])
            rect = sup_rot.get_rect(center=(int(h['x']), int(h['y'])))
            
            pantalla.blit(sup_rot, rect)