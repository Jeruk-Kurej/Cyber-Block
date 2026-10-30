"""Semua warna, ukuran, layout, durasi animasi, dan font Cyber-Block."""

from functools import cache

import pygame

from config import BOARD_SIZE

# --- Warna dasar ---
BACKGROUND = (6, 6, 11)
GRID_LINE = (14, 16, 26)
SCANLINE_ALPHA = 26
PANEL_BG = (11, 12, 21)
PANEL_EDGE = (38, 42, 64)
TEXT = (218, 226, 240)
TEXT_DIM = (112, 120, 146)
WHITE = (240, 250, 255)
OVERLAY_DIM = (2, 2, 6, 190)

# --- Warna papan & token ---
CELL_EMPTY = (26, 28, 38)
CELL_EDGE = (40, 43, 57)
CELL_TICK = (30, 70, 86)
WALL = (255, 228, 40)
WALL_DARK = (58, 50, 6)
WALL_BEVEL = (112, 96, 10)
HUMAN = (40, 180, 255)
HUMAN_DARK = (10, 62, 118)
HUMAN_LIGHT = (130, 245, 255)
AI = (255, 44, 86)
AI_DARK = (106, 12, 36)
AI_LIGHT = (255, 170, 120)
MOVE_HINT = (90, 220, 255)
PLACE_HINT = (255, 214, 40)
URGENT = (255, 50, 80)
DANGER = (255, 120, 60)

# --- Palet sprite (karakter matriks -> warna) ---
PALETTE = {
    "G": CELL_EDGE, "g": CELL_EMPTY, "c": CELL_TICK,
    "Y": WALL, "y": WALL_DARK, "h": WALL_BEVEL,
    "B": HUMAN, "b": HUMAN_DARK, "C": HUMAN_LIGHT,
    "R": AI, "r": AI_DARK, "O": AI_LIGHT,
    "W": WHITE,
}

# --- Ukuran & layout ---
WINDOW_SIZE = (1120, 760)
WINDOW_TITLE = "Cyber-Block"
FPS = 60
PIXEL = 4
CELL_GAP = 4
BOARD_AREA = 584   # lebar papan di layar (pixel); ukuran tile menyesuaikan BOARD_SIZE
CELL_SIZE = (BOARD_AREA - (BOARD_SIZE - 1) * CELL_GAP) // BOARD_SIZE   # 80 untuk papan 7 x 7
SPRITE_SCALE = CELL_SIZE / 80     # sprite digambar untuk tile 80 pixel
BOARD_ORIGIN = (48, 140)
BOARD_FRAME = 10
HEADER_POS = (48, 30)
BANNER_RECT = (48, 82, 584, 44)
PANEL_RECT = (676, 140, 396, 584)
PANEL_PAD = 20
DEBUG_PANEL_TOP = 300
GLOW_RADIUS = 6
MOBILITY_SEGMENTS = 8
DANGER_MOBILITY = 2

# --- Animasi ---
PULSE_SPEED = 5.0
BLINK_SPEED = 3.0
AI_SLIDE_SECONDS = 0.28
AI_HIGHLIGHT_SECONDS = 2.0
HOVER_ALPHA = 120

# --- Font ---
FONT_NAMES = "menlo,sfmono,monaco,couriernew"
FONT_SIZES = {"tiny": 13, "small": 15, "body": 18, "title": 22, "banner": 24}
PIXEL_TEXT_SCALE = {"logo": 4, "clock": 9, "result": 7, "title_logo": 10}


@cache
def font(role: str) -> pygame.font.Font:
    return pygame.font.SysFont(FONT_NAMES, FONT_SIZES[role], bold=role in ("title", "banner"))
