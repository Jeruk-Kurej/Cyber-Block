"""Menggambar papan: tile, tembok, token, highlight, hover, dan aksi terakhir AI."""

import pygame

import rules
from config import BOARD_SIZE
from game.controller import Phase
from ui import theme
from ui.effects import blit_glowing, lerp_color, pulse

STEP = theme.CELL_SIZE + theme.CELL_GAP
BOARD_PIXELS = BOARD_SIZE * theme.CELL_SIZE + (BOARD_SIZE - 1) * theme.CELL_GAP


class BoardRenderer:
    """Menggambar papan dan semua yang ada di atasnya."""

    def __init__(self, sprites):
        """Siapkan sprite dan lapisan transparan untuk highlight."""
        self.sprites = sprites
        self.rect = pygame.Rect(*theme.BOARD_ORIGIN, BOARD_PIXELS, BOARD_PIXELS)
        self.overlay = pygame.Surface(theme.WINDOW_SIZE, pygame.SRCALPHA)

    # --- Posisi ---
    def cell_rect(self, cell):
        """Kotak pixel untuk tile (baris, kolom)."""
        row, col = cell
        return pygame.Rect(self.rect.x + col * STEP, self.rect.y + row * STEP, theme.CELL_SIZE, theme.CELL_SIZE)

    def cell_at(self, pos):
        """Tile di posisi mouse, atau None kalau di luar tile."""
        x, y = pos[0] - self.rect.x, pos[1] - self.rect.y
        row, col = y // STEP, x // STEP
        if not rules.inside(row, col) or x % STEP >= theme.CELL_SIZE or y % STEP >= theme.CELL_SIZE:
            return None
        return (row, col)

    # --- Gambar ---
    def draw(self, surface, game, hover, t):
        """Gambar seluruh papan untuk satu frame."""
        self.overlay.fill((0, 0, 0, 0))
        targets = game.targets()
        self.draw_frame(surface, game, t)
        self.draw_tiles(surface, game)
        self.draw_targets(game, targets, t)
        self.draw_ai_trace(game)
        surface.blit(self.overlay, (0, 0))
        self.draw_tokens(surface, game)
        if hover is not None:
            self.draw_hover(surface, game, hover)
        if game.phase == Phase.HUMAN_MOVE:
            for cell in targets:
                self.badge(surface, cell, str(game.preview(cell)[rules.HUMAN]))

    def draw_frame(self, surface, game, t):
        """Bingkai papan, berkedip merah saat waktu hampir habis."""
        color = theme.PANEL_EDGE
        if game.human_turn() and game.clock.urgent():
            color = lerp_color(theme.PANEL_EDGE, theme.URGENT, pulse(t, theme.PULSE_SPEED * 2))
        pygame.draw.rect(surface, color, self.rect.inflate(theme.BOARD_FRAME * 2, theme.BOARD_FRAME * 2), 3)

    def draw_tiles(self, surface, game):
        """Tile kosong dan tembok."""
        walls = game.state["walls"]
        for cell in rules.ALL_TILES:
            surface.blit(self.sprites.empty, self.cell_rect(cell))
        for cell in walls:
            halo = self.sprites.wall_glow
            surface.blit(halo, halo.get_rect(center=self.cell_rect(cell).center), special_flags=pygame.BLEND_RGB_ADD)
        for cell in walls:
            surface.blit(self.sprites.wall, self.cell_rect(cell))

    def draw_targets(self, game, targets, t):
        """Highlight tile yang boleh diklik."""
        strength = 0.55 + 0.45 * pulse(t)
        if game.phase == Phase.HUMAN_MOVE:
            for cell in targets:
                self.highlight(cell, theme.MOVE_HINT, strength)
        elif game.phase == Phase.HUMAN_PLACE:
            ai_cell = game.state[rules.AI]
            own_cell = game.state[rules.HUMAN]
            for cell in targets:
                self.highlight(cell, theme.PLACE_HINT, strength * 0.7)
                if rules.distance(cell, ai_cell) == 1:
                    self.crosshair(cell, theme.AI)
                if rules.distance(cell, own_cell) == 1:
                    self.corner_dots(cell, theme.HUMAN)
            origin = game.move_origin()
            pygame.draw.rect(self.overlay, (*theme.HUMAN, 150), self.cell_rect(origin).inflate(-10, -10), 2)

    def draw_ai_trace(self, game):
        """Jejak langkah AI terakhir."""
        if game.last_ai_action is None:
            return
        fade = max(0.0, 1.0 - game.ai_action_age / theme.AI_HIGHLIGHT_SECONDS)
        start = self.cell_rect(game.last_ai_from).center
        end = self.cell_rect(game.last_ai_action[0]).center
        placed = self.cell_rect(game.last_ai_action[1])
        if fade > 0:
            pygame.draw.rect(self.overlay, (*theme.AI, int(110 * fade)), placed)
            ring = placed.inflate(int(40 * (1 - fade)), int(40 * (1 - fade)))
            pygame.draw.rect(self.overlay, (*theme.WHITE, int(220 * fade)), ring, 3)
        pygame.draw.circle(self.overlay, (*theme.AI, 90 + int(150 * fade)), start, 6)
        pygame.draw.line(self.overlay, (*theme.AI, 40 + int(200 * fade)), start, end, 3)
        self.crosshair(game.last_ai_action[1], theme.AI, alpha=150 + int(105 * fade))

    def draw_tokens(self, surface, game):
        """Token Human dan AI (AI bergeser halus)."""
        for player in (rules.HUMAN, rules.AI):
            center = self.cell_rect(game.state[player]).center
            if player == rules.AI and game.ai_action_age < theme.AI_SLIDE_SECONDS:
                amount = game.ai_action_age / theme.AI_SLIDE_SECONDS
                origin = self.cell_rect(game.last_ai_from).center
                center = (origin[0] + (center[0] - origin[0]) * amount, origin[1] + (center[1] - origin[1]) * amount)
            blit_glowing(surface, self.sprites.token[player], self.sprites.token_glow[player], center)

    def draw_hover(self, surface, game, cell):
        """Bayangan langkah di tile yang disorot mouse."""
        rect = self.cell_rect(cell)
        if game.phase == Phase.HUMAN_MOVE:
            ghost = self.sprites.ghost[rules.HUMAN]
            surface.blit(ghost, ghost.get_rect(center=rect.center))
            pygame.draw.rect(surface, theme.HUMAN_LIGHT, rect, 3)
        else:
            surface.blit(self.sprites.wall_ghost, rect)
            pygame.draw.rect(surface, theme.WALL, rect, 3)

    # --- Penanda kecil ---
    def highlight(self, cell, color, strength):
        """Warnai satu tile (isi transparan dan garis tepi)."""
        rect = self.cell_rect(cell)
        pygame.draw.rect(self.overlay, (*color, int(45 * strength)), rect)
        pygame.draw.rect(self.overlay, (*color, int(255 * strength)), rect, 2)

    def badge(self, surface, cell, text):
        """Angka kecil di pojok tile."""
        label = theme.font("small").render(text, True, theme.MOVE_HINT)
        rect = self.cell_rect(cell)
        surface.blit(label, label.get_rect(bottomright=(rect.right - 6, rect.bottom - 3)))

    def crosshair(self, cell, color, alpha=230):
        """Siku di 4 pojok tile."""
        rect = self.cell_rect(cell).inflate(-8, -8)
        arm = 14
        for corner, dx, dy in ((rect.topleft, 1, 1), (rect.topright, -1, 1), (rect.bottomleft, 1, -1), (rect.bottomright, -1, -1)):
            x, y = corner
            pygame.draw.line(self.overlay, (*color, alpha), (x, y), (x + dx * arm, y), 3)
            pygame.draw.line(self.overlay, (*color, alpha), (x, y), (x, y + dy * arm), 3)

    def corner_dots(self, cell, color):
        """Titik kecil di 4 pojok tile."""
        rect = self.cell_rect(cell).inflate(-14, -14)
        for corner in (rect.topleft, rect.topright, rect.bottomleft, rect.bottomright):
            pygame.draw.rect(self.overlay, (*color, 220), (corner[0] - 2, corner[1] - 2, 5, 5))
