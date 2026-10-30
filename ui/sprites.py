"""Sprite pixel art dari matriks karakter (warna lihat theme.PALETTE, '.' = transparan)."""

import pygame

import rules
from ui import theme
from ui.effects import glow, matrix_surface

# --- Matriks tile 20x20 ---
EMPTY_TILE = (
    "GGGGGGGGGGGGGGGGGGGG",
    "GggggggggggggggggggG",
    "GgccggggggggggggccgG",
    "GgcggggggggggggggcgG",
    "GggggggggggggggggggG",
    "GggggggggggggggggggG",
    "GggggggggggggggggggG",
    "GggggggggggggggggggG",
    "GggggggggggggggggggG",
    "GggggggggggggggggggG",
    "GggggggggggggggggggG",
    "GggggggggggggggggggG",
    "GggggggggggggggggggG",
    "GggggggggggggggggggG",
    "GggggggggggggggggggG",
    "GggggggggggggggggggG",
    "GgcggggggggggggggcgG",
    "GgccggggggggggggccgG",
    "GggggggggggggggggggG",
    "GGGGGGGGGGGGGGGGGGGG",
)

WALL_TILE = (
    "YYYYYYYYYYYYYYYYYYYY",
    "YhhhhhhhhYhhhhhhhhhY",
    "YyyyyyyyyYyyyyyyyyyY",
    "YyyyyyyyyYyyyyyyyyyY",
    "YyyyyyyyyYyyyyyyyyyY",
    "YyyyyyyyyYyyyyyyyyyY",
    "YYYYYYYYYYYYYYYYYYYY",
    "YhhhYhhhhhhhhhYhhhhY",
    "YyyyYyyyyyyyyyYyyyyY",
    "YyyyYyyyyyyyyyYyyyyY",
    "YyyyYyyyyyyyyyYyyyyY",
    "YyyyYyyyyyyyyyYyyyyY",
    "YyyyYyyyyyyyyyYyyyyY",
    "YYYYYYYYYYYYYYYYYYYY",
    "YhhhhhhhhYhhhhhhhhhY",
    "YyyyyyyyyYyyyyyyyyyY",
    "YyyyyyyyyYyyyyyyyyyY",
    "YyyyyyyyyYyyyyyyyyyY",
    "YyyyyyyyyYyyyyyyyyyY",
    "YYYYYYYYYYYYYYYYYYYY",
)

# --- Matriks token 16x16 ---
HUMAN_TOKEN = (
    "................",
    ".....bbbbbb.....",
    "...bbBBBBBBbb...",
    "..bBBBBBBBBBBb..",
    "..bBBBBBBBBBBb..",
    ".bBBCCCCCCCCBBb.",
    ".bBCCWWCCWWCCBb.",
    ".bBCCWWCCWWCCBb.",
    ".bBBCCCCCCCCBBb.",
    "..bBBBBBBBBBBb..",
    "...bBBBbbBBBb...",
    "....bbBBBBbb....",
    "...bBBBBBBBBb...",
    "..bBBBCBBCBBBb..",
    ".bBBBBCBBCBBBBb.",
    ".bbbbbbbbbbbbbb.",
)

AI_TOKEN = (
    "...rr......rr...",
    "...rRr....rRr...",
    "....rRrrrrRr....",
    "...rRRRRRRRRr...",
    "..rRRRRRRRRRRr..",
    ".rRRRRRRRRRRRRr.",
    ".rRRrrrrrrrrRRr.",
    ".rRrOOWWWWOOrRr.",
    ".rRrOOOWWOOOrRr.",
    ".rRRrrrrrrrrRRr.",
    "..rRRRRRRRRRRr..",
    "..rRrRrRRrRrRr..",
    "...rRRRRRRRRr...",
    "....rRrRRrRr....",
    ".....rrrrrr.....",
    "................",
)


# --- Surface siap pakai (dibuat setelah display aktif) ---
class Sprites:
    def __init__(self):
        self.empty = _build(EMPTY_TILE)
        self.wall = _build(WALL_TILE)
        self.wall_glow = glow(self.wall, theme.WALL, strength=0.35)
        self.wall_ghost = _faded(self.wall)
        tokens = {rules.HUMAN: (HUMAN_TOKEN, theme.HUMAN), rules.AI: (AI_TOKEN, theme.AI)}
        self.token = {player: _build(rows) for player, (rows, _) in tokens.items()}
        self.token_glow = {player: glow(self.token[player], color) for player, (_, color) in tokens.items()}
        self.ghost = {player: _faded(surface) for player, surface in self.token.items()}
        # Versi ukuran tetap (tidak ikut BOARD_SIZE) untuk layar judul dan ikon di panel
        self.title_token = {player: _build(rows, scale=1) for player, (rows, _) in tokens.items()}
        self.title_token_glow = {player: glow(self.title_token[player], color) for player, (_, color) in tokens.items()}
        self.icon = {player: pygame.transform.scale_by(surface, 0.5) for player, surface in self.title_token.items()}


def _build(rows: tuple[str, ...], scale: float = theme.SPRITE_SCALE) -> pygame.Surface:
    surface = matrix_surface(rows, theme.PALETTE, theme.PIXEL)
    if scale != 1:
        surface = pygame.transform.scale_by(surface, scale)
    return surface


def _faded(surface: pygame.Surface) -> pygame.Surface:
    faded = surface.copy()
    faded.set_alpha(theme.HOVER_ALPHA)
    return faded
