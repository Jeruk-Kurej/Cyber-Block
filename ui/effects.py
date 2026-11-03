"""Efek visual: sprite dari matriks karakter, glow neon, scanline, dan pulse."""

import math

import pygame

from ui import theme


# --- Matriks karakter -> Surface ---
def matrix_surface(rows, palette, pixel):
    """Ubah matriks karakter jadi gambar pixel art."""
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("Semua baris matriks harus sama panjang")
    surface = pygame.Surface((width * pixel, len(rows) * pixel), pygame.SRCALPHA)
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char in palette:
                surface.fill(palette[char], (x * pixel, y * pixel, pixel, pixel))
    return surface


# --- Glow neon ---
def glow(surface, color, radius=theme.GLOW_RADIUS, strength=1.0):
    """Cahaya neon buram di sekeliling gambar."""
    pad = radius * 2
    tinted = color if strength >= 1 else tuple(int(c * strength) for c in color)
    silhouette = pygame.mask.from_surface(surface).to_surface(setcolor=(*tinted, 255), unsetcolor=(0, 0, 0, 0))
    canvas = pygame.Surface((surface.get_width() + pad * 2, surface.get_height() + pad * 2), pygame.SRCALPHA)
    canvas.blit(silhouette, (pad, pad))
    return pygame.transform.gaussian_blur(canvas, radius)


def blit_glowing(target, sprite, halo, center):
    """Gambar sprite beserta cahayanya di titik tengah."""
    target.blit(halo, halo.get_rect(center=center), special_flags=pygame.BLEND_RGB_ADD)
    target.blit(sprite, sprite.get_rect(center=center))


# --- Latar ---
def scanlines(size):
    """Garis horizontal tipis ala layar CRT."""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    for y in range(0, size[1], 3):
        surface.fill((0, 0, 0, theme.SCANLINE_ALPHA), (0, y, size[0], 1))
    return surface


def grid_background(size, spacing=28):
    """Latar gelap dengan garis kotak-kotak."""
    surface = pygame.Surface(size)
    surface.fill(theme.BACKGROUND)
    for x in range(0, size[0], spacing):
        surface.fill(theme.GRID_LINE, (x, 0, 1, size[1]))
    for y in range(0, size[1], spacing):
        surface.fill(theme.GRID_LINE, (0, y, size[0], 1))
    return surface


# --- Animasi ---
def pulse(t, speed=theme.PULSE_SPEED):
    """Nilai naik-turun 0 sampai 1 mengikuti waktu."""
    return 0.5 + 0.5 * math.sin(t * speed)


def blink(t):
    """True/False bergantian, untuk teks berkedip."""
    return math.sin(t * theme.BLINK_SPEED * math.pi) > -0.3


def lerp_color(a, b, amount):
    """Warna di antara a dan b (amount 0 sampai 1)."""
    return tuple(int(x + (y - x) * amount) for x, y in zip(a, b))
