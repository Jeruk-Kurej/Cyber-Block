"""Layar judul: cara main, syarat menang, pilihan level, dan tombol mulai."""

import pygame

from config import LEVELS, HUMAN_CLOCK_SECONDS, SCORE_PER_SECOND_LEFT, SCORE_PER_TURN, SCORE_WIN_BONUS
import rules
from ui import theme
from ui.effects import blit_glowing, lerp_color, pulse
from ui.text import draw_pixel_text, draw_text

RULES_HEADER = "Setiap giliran (kamu dan AI): GERAK dulu, lalu pasang TEMBOK."
RULES = (
    ("1. GERAK", "klik tile biru: pindah 1 kotak ke 8 arah."),
    ("2. TEMBOK", "klik tile kosong mana saja: jadi tembok."),
    ("MENANG", "AI terkurung, tidak ada kotak untuk dituju."),
    ("KALAH", f"kamu terkurung, atau waktumu {HUMAN_CLOCK_SECONDS:.0f} detik habis."),
    ("SKOR", f"menang +{SCORE_WIN_BONUS} · sisa waktu x{SCORE_PER_SECOND_LEFT} · tiap giliran +{SCORE_PER_TURN}"),
)
CONTROLS = "Pilih level: 1 / 2 / 3   ·   Batal gerak: Esc / klik kanan   ·   Tab: lihat cara AI berpikir"


class TitleScreen:
    """Layar judul sebelum game dimulai."""

    def __init__(self, sprites):
        """Simpan sprite untuk token KAMU vs AI."""
        self.sprites = sprites

    def draw(self, surface, level, t):
        """Gambar layar judul. level = indeks level yang dipilih."""
        cx = theme.WINDOW_SIZE[0] // 2
        draw_pixel_text(surface, "CYBER-BLOCK", theme.PIXEL_TEXT_SCALE["title_logo"], theme.WALL, (cx, 110))
        draw_text(surface, "Kurung AI sebelum kamu yang terkurung.", "title", theme.TEXT, (cx, 188), anchor="center")
        self.draw_versus(surface, cx, 244)
        self.draw_rules(surface, cx, 290)
        self.draw_levels(surface, cx, level, 556)
        color = lerp_color(theme.HUMAN_DARK, theme.HUMAN_LIGHT, pulse(t))
        draw_text(surface, "TEKAN SPASI UNTUK MULAI", "banner", color, (cx, 690), anchor="center")

    def draw_versus(self, surface, cx, y):
        """Token KAMU vs AI."""
        for player, name, color, side in ((rules.HUMAN, "KAMU", theme.HUMAN, -1), (rules.AI, "AI", theme.AI, 1)):
            center = (cx + side * 150, y)
            blit_glowing(surface, self.sprites.title_token[player], self.sprites.title_token_glow[player], center)
            draw_text(surface, name, "title", color, (center[0] + side * 60, y), anchor="midright" if side < 0 else "midleft")
        draw_text(surface, "VS", "banner", theme.TEXT_DIM, (cx, y), anchor="center")

    def draw_rules(self, surface, cx, y):
        """Kotak aturan singkat."""
        box = pygame.Rect(0, 0, 780, 244)
        box.midtop = (cx, y)
        pygame.draw.rect(surface, theme.PANEL_BG, box)
        pygame.draw.rect(surface, theme.PANEL_EDGE, box, 2)
        draw_text(surface, RULES_HEADER, "body", theme.HUMAN, (cx, box.y + 30), anchor="center")
        line_y = box.y + 62
        for label, text in RULES:
            draw_text(surface, label, "body", theme.WALL, (box.x + 28, line_y))
            draw_text(surface, text, "body", theme.TEXT, (box.x + 190, line_y))
            line_y += 34

    def draw_levels(self, surface, cx, selected_index, y):
        """Tiga tombol level, yang dipilih berwarna kuning."""
        width, gap = 210, 24
        start = cx - (len(LEVELS) * width + (len(LEVELS) - 1) * gap) // 2
        for i, level in enumerate(LEVELS):
            box = pygame.Rect(start + i * (width + gap), y, width, 52)
            selected = i == selected_index
            pygame.draw.rect(surface, theme.PANEL_BG, box)
            pygame.draw.rect(surface, theme.WALL if selected else theme.PANEL_EDGE, box, 3 if selected else 2)
            color = theme.WALL if selected else theme.TEXT_DIM
            draw_text(surface, f"[{i + 1}] {level['name'].upper()}", "title", color, box.center, anchor="center")
        draw_text(surface, CONTROLS, "small", theme.TEXT_DIM, (cx, y + 74), anchor="center")
