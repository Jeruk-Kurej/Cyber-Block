"""Menulis teks: font sistem dengan titik jangkar, dan font pixel bercahaya."""

import pygame

from ui import pixel_font, theme


def draw_text(surface, text, role, color, pos, anchor="topleft"):
    """Tulis teks dengan font sistem, posisi mengikuti anchor."""
    rendered = theme.font(role).render(text, True, color)
    rect = rendered.get_rect(**{anchor: pos})
    surface.blit(rendered, rect)
    return rect


def draw_pixel_text(surface, text, scale, color, anchor_pos, anchor="center"):
    """Tulis teks dengan font pixel bercahaya."""
    rendered = pixel_font.render(text, scale, color)
    rect = rendered.get_rect(**{anchor: anchor_pos})
    halo = pixel_font.render_glow(text, scale, color)
    surface.blit(halo, halo.get_rect(center=rect.center), special_flags=pygame.BLEND_RGB_ADD)
    surface.blit(rendered, rect)
    return rect
