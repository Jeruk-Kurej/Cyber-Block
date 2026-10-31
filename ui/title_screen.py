"""Layar siap: aturan singkat, pilihan level (oleh panitia), dan tombol mulai."""

import pygame

from config import LEVELS, HUMAN_CLOCK_SECONDS, SCORE_PER_SECOND_LEFT, SCORE_PER_TURN, SCORE_WIN_BONUS
import rules
from ui import theme
from ui.effects import blit_glowing, lerp_color, pulse
from ui.sprites import Sprites
from ui.text import draw_pixel_text, draw_text

RULES = (
    ("1. GERAK", "pindah 1 tile ke 8 arah (bukan tembok, bukan lawan)."),
    ("2. PLACE", "ubah 1 tile kosong di mana saja jadi tembok permanen."),
    ("MENANG", "AI tidak bisa bergerak saat gilirannya."),
    ("KALAH", f"kamu terkurung, atau waktu {HUMAN_CLOCK_SECONDS:.0f} detik habis."),
    ("SKOR", f"menang +{SCORE_WIN_BONUS} · sisa waktu x{SCORE_PER_SECOND_LEFT} · tiap giliran +{SCORE_PER_TURN}"),
)


class TitleScreen:
    def __init__(self, sprites: Sprites):
        self.sprites = sprites

    def draw(self, surface: pygame.Surface, level: int, t: float) -> None:
        cx = theme.WINDOW_SIZE[0] // 2
        draw_pixel_text(surface, "CYBER-BLOCK", theme.PIXEL_TEXT_SCALE["title_logo"], theme.WALL, (cx, 110))
        draw_text(surface, "Kurung AI sebelum kamu yang terkurung.", "title", theme.TEXT, (cx, 188), anchor="center")
        self._draw_versus(surface, cx, 250)
        self._draw_rules(surface, cx, 312)
        self._draw_levels(surface, cx, level, 556)
        color = lerp_color(theme.HUMAN_DARK, theme.HUMAN_LIGHT, pulse(t))
        draw_text(surface, "TEKAN SPASI UNTUK MULAI", "banner", color, (cx, 690), anchor="center")

    def _draw_versus(self, surface, cx: int, y: int) -> None:
        for player, name, color, side in ((rules.HUMAN, "KAMU", theme.HUMAN, -1), (rules.AI, "AI", theme.AI, 1)):
            center = (cx + side * 150, y)
            blit_glowing(surface, self.sprites.title_token[player], self.sprites.title_token_glow[player], center)
            draw_text(surface, name, "title", color, (center[0] + side * 60, y), anchor="midright" if side < 0 else "midleft")
        draw_text(surface, "VS", "banner", theme.TEXT_DIM, (cx, y), anchor="center")

    def _draw_rules(self, surface, cx: int, y: int) -> None:
        box = pygame.Rect(0, 0, 780, 210)
        box.midtop = (cx, y)
        pygame.draw.rect(surface, theme.PANEL_BG, box)
        pygame.draw.rect(surface, theme.PANEL_EDGE, box, 2)
        line_y = box.y + 22
        for label, text in RULES:
            draw_text(surface, label, "body", theme.WALL, (box.x + 28, line_y))
            draw_text(surface, text, "body", theme.TEXT, (box.x + 190, line_y))
            line_y += 36

    def _draw_levels(self, surface, cx: int, level: int, y: int) -> None:
        width, gap = 210, 24
        start = cx - (len(LEVELS) * width + (len(LEVELS) - 1) * gap) // 2
        for i, level in enumerate(LEVELS):
            box = pygame.Rect(start + i * (width + gap), y, width, 52)
            selected = i == level
            pygame.draw.rect(surface, theme.PANEL_BG, box)
            pygame.draw.rect(surface, theme.WALL if selected else theme.PANEL_EDGE, box, 3 if selected else 2)
            color = theme.WALL if selected else theme.TEXT_DIM
            draw_text(surface, f"[{i + 1}] {level['name'].upper()}", "title", color, box.center, anchor="center")
        draw_text(surface, "Level diatur panitia dengan tombol 1 / 2 / 3", "small", theme.TEXT_DIM, (cx, y + 74), anchor="center")
