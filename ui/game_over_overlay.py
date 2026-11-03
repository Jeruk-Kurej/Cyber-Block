"""Overlay akhir game: hasil, alasan, rincian skor, dan instruksi restart."""

import pygame

from config import SCORE_PER_SECOND_LEFT, SCORE_PER_TURN
from game.scoring import AI_WIN, HUMAN_WIN, TIMEOUT
from ui import theme
from ui.effects import lerp_color, pulse
from ui.text import draw_pixel_text, draw_text

RESULTS = {
    HUMAN_WIN: ("KAMU MENANG", theme.HUMAN, "AI terkurung, tidak ada langkah tersisa."),
    AI_WIN: ("AI MENANG", theme.AI, "Kamu terkurung, tidak ada langkah tersisa."),
    TIMEOUT: ("WAKTU HABIS", theme.URGENT, "Waktumu habis sebelum giliranmu selesai."),
}


class GameOverOverlay:
    def __init__(self):
        self.dim = pygame.Surface(theme.WINDOW_SIZE, pygame.SRCALPHA)
        self.dim.fill(theme.OVERLAY_DIM)

    def draw(self, surface, game, t):
        """Hasil akhir, rincian skor, dan ajakan restart."""
        title, color, reason = RESULTS[game.outcome]
        score = game.score
        surface.blit(self.dim, (0, 0))
        box = pygame.Rect(0, 0, 640, 430)
        box.center = (theme.WINDOW_SIZE[0] // 2, theme.WINDOW_SIZE[1] // 2)
        pygame.draw.rect(surface, theme.PANEL_BG, box)
        pygame.draw.rect(surface, color, box, 3)
        draw_pixel_text(surface, title, theme.PIXEL_TEXT_SCALE["result"], color, (box.centerx, box.y + 70))
        draw_text(surface, reason, "body", theme.TEXT, (box.centerx, box.y + 136), anchor="center")

        won = game.outcome == HUMAN_WIN
        time_label = f"Sisa waktu {game.clock.remaining:.1f} dtk x {SCORE_PER_SECOND_LEFT}" if won else "Sisa waktu (hanya dihitung jika menang)"
        rows = (
            ("Bonus menang", score["win_bonus"]),
            (time_label, score["time_bonus"]),
            (f"Giliran bertahan {game.turns_survived} x {SCORE_PER_TURN}", score["turn_bonus"]),
        )
        y = box.y + 178
        for label, value in rows:
            draw_text(surface, label, "body", theme.TEXT_DIM, (box.x + 48, y))
            draw_text(surface, str(value), "body", theme.TEXT, (box.right - 48, y), anchor="topright")
            y += 32
        pygame.draw.line(surface, theme.PANEL_EDGE, (box.x + 48, y + 4), (box.right - 48, y + 4), 2)
        draw_text(surface, "TOTAL SKOR", "title", theme.TEXT, (box.x + 48, y + 40), anchor="midleft")
        draw_pixel_text(surface, str(score["total"]), theme.PIXEL_TEXT_SCALE["logo"], theme.WALL, (box.right - 48, y + 40), "midright")
        draw_text(surface, f"Level {game.level['name']}", "small", theme.TEXT_DIM, (box.x + 48, box.bottom - 40))
        prompt = lerp_color(theme.HUMAN_DARK, theme.HUMAN_LIGHT, pulse(t))
        draw_text(surface, "Tekan R untuk restart", "title", prompt, (box.right - 48, box.bottom - 30), anchor="midright")
