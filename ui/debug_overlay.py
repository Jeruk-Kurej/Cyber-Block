"""Debug mode (Tab): statistik search AI, kandidat action teratas, dan penandanya di papan."""

import pygame

import rules
from config import BOARD_SIZE, DEBUG_TOP_CANDIDATES, MOBILITY_STEPS, WIN_UTILITY
from ui import theme
from ui.text import draw_text


def format_value(value):
    """Nilai search untuk ditampilkan (menang/kalah dalam N ply)."""
    if value > WIN_UTILITY / 2:
        return f"MENANG {WIN_UTILITY - value:.0f} ply"
    if value < -WIN_UTILITY / 2:
        return f"KALAH {WIN_UTILITY + value:.0f} ply"
    return f"{value:+.1f}"


def format_count(value):
    """Angka dengan titik ribuan, misal 12.345."""
    return f"{value:,}".replace(",", ".")


class DebugOverlay:
    """Panel debug mode: cara AI berpikir di giliran terakhirnya."""

    def __init__(self, board_renderer):
        """Pakai BoardRenderer untuk tahu posisi tile di layar."""
        self.board = board_renderer
        panel = pygame.Rect(theme.PANEL_RECT)
        self.rect = pygame.Rect(panel.x, panel.y + theme.DEBUG_PANEL_TOP, panel.width, panel.height - theme.DEBUG_PANEL_TOP)
        self.left = self.rect.x + theme.PANEL_PAD

    # --- Gambar ---
    def draw(self, surface, game):
        """Panel debug dan penanda kandidat di papan."""
        self.draw_coordinates(surface)
        pygame.draw.rect(surface, theme.PANEL_BG, self.rect)
        pygame.draw.rect(surface, theme.WALL, self.rect, 2)
        y = self.rect.y + 12
        draw_text(surface, "DEBUG AI · Minimax + Alpha-Beta", "body", theme.WALL, (self.left, y))
        y += 28
        if game.last_search is None:
            draw_text(surface, "Belum ada keputusan AI.", "small", theme.TEXT_DIM, (self.left, y))
            return
        self.draw_stats(surface, game, game.last_search, y)
        self.draw_candidate_marks(surface, game.last_search)

    def draw_stats(self, surface, game, result, y):
        """Statistik search dan daftar kandidat teratas."""
        level = game.level
        rate = result["nodes"] / result["elapsed"] if result["elapsed"] else 0
        lines = (
            f"depth   {result['depth']} (level {level['name']})",
            f"node    {format_count(result["nodes"])} dikunjungi",
            f"prune   {format_count(result["cutoffs"])} cutoff · {format_count(result["pruned"])} cabang",
            f"waktu   {result['elapsed']:.3f} dtk · {format_count(int(rate))} node/dtk",
            f"eval    ruang_AI - {level['weight']:g} x ruang_kamu ({MOBILITY_STEPS} langkah)",
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

    def draw_candidate_marks(self, surface, result):
        """Tanda #N (move) dan xN (place) di papan."""
        moves, places = {}, {}
        for rank, candidate in enumerate(result["candidates"][:DEBUG_TOP_CANDIDATES], start=1):
            # setdefault: kalau tile sudah punya nomor, pakai nomor yang pertama (kandidat terbaik)
            moves.setdefault(candidate["action"][0], rank)
            places.setdefault(candidate["action"][1], rank)
        for cell, rank in moves.items():
            self.tag(surface, cell, f"#{rank}", theme.AI, "topleft")
        for cell, rank in places.items():
            self.tag(surface, cell, f"x{rank}", theme.WALL, "bottomleft")

    def tag(self, surface, cell, text, color, corner):
        """Label kecil di pojok tile."""
        label = theme.font("tiny").render(text, True, color)
        rect = self.board.cell_rect(cell).inflate(-6, -6)
        box = label.get_rect(**{corner: getattr(rect, corner)}).inflate(6, 2)    # tempel label di pojok tile
        pygame.draw.rect(surface, theme.BACKGROUND, box)
        pygame.draw.rect(surface, color, box, 1)
        surface.blit(label, label.get_rect(center=box.center))

    def draw_coordinates(self, surface):
        """Nomor baris dan kolom di tepi papan."""
        for i in range(BOARD_SIZE):
            row_rect = self.board.cell_rect((i, 0))
            col_rect = self.board.cell_rect((BOARD_SIZE - 1, i))
            draw_text(surface, str(i), "tiny", theme.TEXT_DIM, (row_rect.left - 24, row_rect.centery), anchor="center")
            draw_text(surface, str(i), "tiny", theme.TEXT_DIM, (col_rect.centerx, col_rect.bottom + 22), anchor="center")
