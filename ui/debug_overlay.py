import pygame

import rules
from config import BOARD_SIZE, DEBUG_TOP_CANDIDATES, WIN_UTILITY
from game.controller import GameController
from ui import theme
from ui.board_renderer import BoardRenderer
from ui.text import draw_text


def format_value(value: float) -> str:
    if value > WIN_UTILITY / 2:
        return f"MENANG {WIN_UTILITY - value:.0f} ply"
    if value < -WIN_UTILITY / 2:
        return f"KALAH {WIN_UTILITY + value:.0f} ply"
    return f"{value:+.1f}"


def format_count(value: int) -> str:
    return f"{value:,}".replace(",", ".")


class DebugOverlay:
    def __init__(self, board_renderer: BoardRenderer):
        self.board = board_renderer
        panel = pygame.Rect(theme.PANEL_RECT)
        self.rect = pygame.Rect(panel.x, panel.y + theme.DEBUG_PANEL_TOP, panel.width, panel.height - theme.DEBUG_PANEL_TOP)
        self.left = self.rect.x + theme.PANEL_PAD

    # --- Gambar ---
    def draw(self, surface: pygame.Surface, game: GameController) -> None:
        self._draw_coordinates(surface)
        pygame.draw.rect(surface, theme.PANEL_BG, self.rect)
        pygame.draw.rect(surface, theme.WALL, self.rect, 2)
        y = self.rect.y + 12
        draw_text(surface, "DEBUG AI · Minimax + Alpha-Beta", "body", theme.WALL, (self.left, y))
        y += 28
        if game.last_search is None:
            draw_text(surface, "Belum ada keputusan AI.", "small", theme.TEXT_DIM, (self.left, y))
            return
        self._draw_stats(surface, game, game.last_search, y)
        self._draw_candidate_marks(surface, game.last_search)

    def _draw_stats(self, surface, game: GameController, result, y: int) -> None:
        level = game.level
        rate = result["nodes"] / result["elapsed"] if result["elapsed"] else 0
        lines = (
            f"depth   {result['depth']} (level {level['name']})",
            f"node    {format_count(result["nodes"])} dikunjungi",
            f"prune   {format_count(result["cutoffs"])} cutoff · {format_count(result["pruned"])} cabang",
            f"waktu   {result['elapsed']:.3f} dtk · {format_count(int(rate))} node/dtk",
            f"eval    langkah_AI - {level['weight']:g} x langkah_kamu",
        )
        for line in lines:
            draw_text(surface, line, "tiny", theme.TEXT, (self.left, y))
            y += 19
        y += 8
        draw_text(surface, "KANDIDAT TERATAS (nilai untuk AI)", "small", theme.TEXT_DIM, (self.left, y))
        y += 22
        for rank, candidate in enumerate(result["candidates"][:DEBUG_TOP_CANDIDATES], start=1):
            action = candidate["action"]
            value = format_value(candidate["value"]) if candidate["exact"] else f"<= {format_value(candidate["value"])}"
            color = theme.AI if rank == 1 else theme.TEXT
            text = f"#{rank} gerak {rules.format_tile(action[0])} place {rules.format_tile(action[1])}"
            draw_text(surface, text, "tiny", color, (self.left, y))
            draw_text(surface, value, "tiny", color, (self.rect.right - theme.PANEL_PAD, y), anchor="topright")
            y += 19
        draw_text(surface, "<= : dipangkas alpha-beta (tak lebih baik)", "tiny", theme.TEXT_DIM, (self.left, y + 6))

    def _draw_candidate_marks(self, surface, result) -> None:
        moves, places = {}, {}
        for rank, candidate in enumerate(result["candidates"][:DEBUG_TOP_CANDIDATES], start=1):
            moves.setdefault(candidate["action"][0], rank)
            places.setdefault(candidate["action"][1], rank)
        for cell, rank in moves.items():
            self._tag(surface, cell, f"#{rank}", theme.AI, "topleft")
        for cell, rank in places.items():
            self._tag(surface, cell, f"x{rank}", theme.WALL, "bottomleft")

    def _tag(self, surface, cell, text: str, color, corner: str) -> None:
        label = theme.font("tiny").render(text, True, color)
        rect = self.board.cell_rect(cell).inflate(-6, -6)
        box = label.get_rect(**{corner: getattr(rect, corner)}).inflate(6, 2)
        pygame.draw.rect(surface, theme.BACKGROUND, box)
        pygame.draw.rect(surface, color, box, 1)
        surface.blit(label, label.get_rect(center=box.center))

    def _draw_coordinates(self, surface) -> None:
        for i in range(BOARD_SIZE):
            row_rect = self.board.cell_rect((i, 0))
            col_rect = self.board.cell_rect((BOARD_SIZE - 1, i))
            draw_text(surface, str(i), "tiny", theme.TEXT_DIM, (row_rect.left - 24, row_rect.centery), anchor="center")
            draw_text(surface, str(i), "tiny", theme.TEXT_DIM, (col_rect.centerx, col_rect.bottom + 22), anchor="center")
