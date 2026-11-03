"""HUD: logo, banner fase, chess clock, langkah tersisa kedua pemain, dan info giliran."""

import math

import pygame

import rules
from game.controller import Phase
from ui import pixel_font, theme
from ui.effects import blink, pulse
from ui.text import draw_pixel_text, draw_text

PHASE_TEXT = {
    Phase.HUMAN_MOVE: ("Giliranmu: Gerak", "klik tile biru", theme.HUMAN),
    Phase.HUMAN_PLACE: ("Giliranmu: Place", "Esc/klik kanan: batal", theme.WALL),
    Phase.AI_THINKING: ("AI sedang berpikir...", "", theme.AI),
    Phase.GAME_OVER: ("Permainan selesai", "tekan R", theme.TEXT),
}

HELP_TEXT = {
    Phase.HUMAN_MOVE: (
        ("Angka di tile = jalan keluar", theme.MOVE_HINT),
        ("jika kamu pindah ke sana.", theme.MOVE_HINT),
    ),
    Phase.HUMAN_PLACE: (
        ("Bidikan merah: kurangi langkah AI", theme.AI),
        ("Titik biru: kurangi langkahmu", theme.HUMAN),
        ("Arahkan kursor untuk pratinjau.", theme.TEXT_DIM),
    ),
    Phase.AI_THINKING: (("Jamnya berhenti saat AI berpikir.", theme.TEXT_DIM),),
    Phase.GAME_OVER: (),
}


class Hud:
    def __init__(self, sprites):
        self.sprites = sprites
        self.panel = pygame.Rect(theme.PANEL_RECT)
        self.left = self.panel.x + theme.PANEL_PAD
        self.right = self.panel.right - theme.PANEL_PAD

    # --- Gambar ---
    def draw(self, surface, game, hover, t):
        """Gambar header, banner, dan panel info di kanan."""
        self.draw_header(surface, game)
        self.draw_banner(surface, game, t)
        pygame.draw.rect(surface, theme.PANEL_BG, self.panel)
        pygame.draw.rect(surface, theme.PANEL_EDGE, self.panel, 2)
        y = self.panel.y + theme.PANEL_PAD
        y = self.draw_clock(surface, game, y, t)
        y = self.draw_mobility(surface, game, hover, y + 26, t)
        y = self.draw_turn_info(surface, game, y + 18)
        self.draw_help(surface, game, y + 22)
        draw_text(surface, "Tab: lihat cara AI berpikir", "small", theme.TEXT_DIM, (self.left, self.panel.bottom - 34))

    def draw_header(self, surface, game):
        """Logo dan nama level."""
        draw_pixel_text(surface, "CYBER-BLOCK", theme.PIXEL_TEXT_SCALE["logo"], theme.WALL, theme.HEADER_POS, "topleft")
        label = f"LEVEL {game.level['name'].upper()}"
        draw_text(surface, label, "title", theme.TEXT, (self.right, theme.HEADER_POS[1] + 2), anchor="topright")

    def draw_banner(self, surface, game, t):
        """Banner fase giliran di atas papan."""
        title, hint, color = PHASE_TEXT[game.phase]
        rect = pygame.Rect(theme.BANNER_RECT)
        tint = pygame.Surface(rect.size, pygame.SRCALPHA)
        tint.fill((*color, 40))
        surface.blit(tint, rect)
        pygame.draw.rect(surface, color, rect, 2)
        pygame.draw.rect(surface, color, (rect.x, rect.y, 8, rect.height))
        draw_text(surface, title, "banner", color, (rect.x + 22, rect.centery), anchor="midleft")
        if hint:
            draw_text(surface, hint, "small", theme.TEXT_DIM, (rect.right - 14, rect.centery), anchor="midright")
        if game.phase == Phase.AI_THINKING:
            for i in range(3):
                lit = int(t * 6) % 3 == i
                pygame.draw.rect(surface, color if lit else theme.AI_DARK, (rect.right - 70 + i * 18, rect.centery - 6, 12, 12))

    def draw_clock(self, surface, game, y, t):
        """Chess clock Human. Mengembalikan y berikutnya."""
        clock = game.clock
        urgent = clock.urgent() and game.phase != Phase.GAME_OVER
        color = theme.URGENT if urgent else theme.HUMAN_LIGHT
        draw_text(surface, "WAKTUMU", "small", theme.TEXT_DIM, (self.left, y))
        status = "berjalan" if clock.running else "berhenti"
        draw_text(surface, status, "small", color if clock.running else theme.TEXT_DIM, (self.right, y), anchor="topright")
        seconds = f"{clock.remaining:.1f}" if urgent else str(math.ceil(clock.remaining))
        digits = pixel_font.render(seconds, theme.PIXEL_TEXT_SCALE["clock"], color)
        spot = digits.get_rect(topleft=(self.left, y + 26))
        if urgent and clock.running:
            halo = pixel_font.render_glow(seconds, theme.PIXEL_TEXT_SCALE["clock"], color)
            halo.set_alpha(int(255 * pulse(t, theme.PULSE_SPEED * 2)))
            surface.blit(halo, halo.get_rect(center=spot.center))
        surface.blit(digits, spot)
        draw_text(surface, "detik", "body", theme.TEXT_DIM, (spot.right + 12, spot.bottom), anchor="bottomleft")
        if urgent and blink(t):
            draw_text(surface, "WAKTU HAMPIR HABIS!", "title", theme.URGENT, (self.right, spot.centery), anchor="midright")
        bar = pygame.Rect(self.left, spot.bottom + 14, self.right - self.left, 10)
        pygame.draw.rect(surface, theme.CELL_EMPTY, bar)
        pygame.draw.rect(surface, color, (bar.x, bar.y, int(bar.width * clock.fraction()), bar.height))
        return bar.bottom

    def draw_mobility(self, surface, game, hover, y, t):
        """Bar langkah tersisa, plus pratinjau saat hover."""
        draw_text(surface, "LANGKAH TERSISA", "small", theme.TEXT_DIM, (self.left, y))
        now = game.mobility()
        after = game.preview(hover) if hover is not None else now
        rows = ((rules.HUMAN, "KAMU", theme.HUMAN), (rules.AI, "AI", theme.AI))
        y += 26
        for player, name, color in rows:
            value, preview = now[player], after[player]
            danger = value <= theme.DANGER_MOBILITY and game.phase != Phase.GAME_OVER
            bar_color = theme.DANGER if danger and blink(t) else color
            icon = self.sprites.icon[player]
            surface.blit(icon, (self.left, y))
            draw_text(surface, name, "title", color, (self.left + 42, y + 16), anchor="midleft")
            for i in range(theme.MOBILITY_SEGMENTS):
                seg = pygame.Rect(self.left + 112 + i * 22, y + 8, 18, 18)
                filled = i < preview
                lost = preview <= i < value
                pygame.draw.rect(surface, bar_color if filled else theme.CELL_EMPTY, seg)
                if lost:
                    pygame.draw.rect(surface, theme.WHITE, seg, 2)
            label = str(value) if preview == value else f"{value}→{preview}"
            draw_text(surface, label, "title", theme.WHITE if preview != value else color, (self.right, y + 16), anchor="midright")
            y += 42
        warning = self.mobility_warning(game, now)
        if warning:
            draw_text(surface, warning[0], "body", warning[1], (self.left, y))
        return y + 24

    def mobility_warning(self, game, now):
        """Pesan peringatan kalau ada yang hampir terkurung."""
        if game.phase == Phase.GAME_OVER:
            return None
        if now[rules.HUMAN] <= theme.DANGER_MOBILITY:
            return "Awas, kamu hampir terkurung!", theme.DANGER
        if now[rules.AI] <= theme.DANGER_MOBILITY:
            return "AI hampir terkurung, serang!", theme.WALL
        return None

    def draw_turn_info(self, surface, game, y):
        """Jumlah giliran bertahan dan aksi terakhir AI."""
        draw_text(surface, "GILIRAN BERTAHAN", "small", theme.TEXT_DIM, (self.left, y))
        draw_text(surface, str(game.turns_survived), "title", theme.TEXT, (self.right, y - 3), anchor="topright")
        y += 30
        draw_text(surface, "AKSI TERAKHIR AI", "small", theme.TEXT_DIM, (self.left, y))
        action = game.last_ai_action
        draw_text(surface, rules.format_action(action) if action else "belum ada", "body", theme.AI if action else theme.TEXT_DIM, (self.left, y + 22))
        return y + 46

    def draw_help(self, surface, game, y):
        """Petunjuk singkat sesuai fase."""
        for line, color in HELP_TEXT[game.phase]:
            draw_text(surface, line, "small", color, (self.left, y))
            y += 22

