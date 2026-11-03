"""Window, loop utama, dan perpindahan antara layar siap dan permainan."""

import pygame

from config import DEFAULT_LEVEL, LEVELS
from game.controller import GameController, Phase
from ui import theme
from ui.board_renderer import BoardRenderer
from ui.debug_overlay import DebugOverlay
from ui.effects import grid_background, scanlines
from ui.game_over_overlay import GameOverOverlay
from ui.hud import Hud
from ui.input_handler import Intent, translate
from ui.sprites import Sprites
from ui.title_screen import TitleScreen

MAX_FRAME_SECONDS = 0.25


class Scene:
    """Layar yang sedang tampil: layar judul atau permainan."""
    TITLE = "title"
    PLAYING = "playing"


class App:
    """Window game: loop utama, input, update, dan gambar."""

    def __init__(self):
        """Buka window dan siapkan semua bagian tampilan."""
        pygame.init()
        self.screen = pygame.display.set_mode(theme.WINDOW_SIZE)
        pygame.display.set_caption(theme.WINDOW_TITLE)
        sprites = Sprites()
        self.board = BoardRenderer(sprites)
        self.hud = Hud(sprites)
        self.debug = DebugOverlay(self.board)
        self.title = TitleScreen(sprites)
        self.game_over = GameOverOverlay()
        self.background = grid_background(theme.WINDOW_SIZE)
        self.scanlines = scanlines(theme.WINDOW_SIZE)
        self.level = DEFAULT_LEVEL
        self.scene = Scene.TITLE
        self.game = None
        self.show_debug = False
        self.running = True
        self.time = 0.0
        self.mouse_pos = (0, 0)
        self.cursor = None

    # --- Loop ---
    def run(self):
        """Loop utama: baca input, update, gambar."""
        clock = pygame.time.Clock()
        while self.running:
            dt = min(clock.tick(theme.FPS) / 1000, MAX_FRAME_SECONDS)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEMOTION:
                    self.mouse_pos = event.pos
                command = translate(event, self.board.cell_at)
                if command:
                    self.handle(command)
            self.update(dt)
            self.set_cursor(pygame.SYSTEM_CURSOR_HAND if self.hover_cell() is not None else pygame.SYSTEM_CURSOR_ARROW)
            self.render()
            pygame.display.flip()
        pygame.quit()

    def handle(self, command):
        """Jalankan satu perintah dari pemain."""
        intent = command.intent
        if intent == Intent.QUIT:
            self.running = False
        elif intent == Intent.TOGGLE_DEBUG:
            self.show_debug = not self.show_debug
        elif self.scene == Scene.TITLE:
            if intent == Intent.SELECT_LEVEL:
                self.level = command.value
            elif intent == Intent.START:
                self.game = GameController(LEVELS[self.level])
                self.scene = Scene.PLAYING
        elif intent == Intent.CLICK_TILE:
            self.game.click(command.value)
        elif intent == Intent.UNDO:
            self.game.undo()
        elif intent == Intent.RESTART and self.game.phase == Phase.GAME_OVER:
            self.scene = Scene.TITLE

    def update(self, dt):
        """Majukan waktu game satu frame."""
        self.time += dt
        if self.scene == Scene.PLAYING:
            self.game.update(dt)

    # --- Render ---
    def hover_cell(self):
        """Tile valid yang sedang disorot mouse, atau None."""
        if self.scene != Scene.PLAYING:
            return None
        cell = self.board.cell_at(self.mouse_pos)
        return cell if cell in self.game.targets() else None

    def render(self):
        """Gambar satu frame: latar, layar judul atau papan + HUD, lalu scanline."""
        self.screen.blit(self.background, (0, 0))
        hover = self.hover_cell()
        if self.scene == Scene.TITLE:
            self.title.draw(self.screen, self.level, self.time)
        else:
            self.hud.draw(self.screen, self.game, hover, self.time)
            self.board.draw(self.screen, self.game, hover, self.time)
            if self.show_debug:
                self.debug.draw(self.screen, self.game)
            if self.game.phase == Phase.GAME_OVER:
                self.game_over.draw(self.screen, self.game, self.time)
        self.screen.blit(self.scanlines, (0, 0))

    def set_cursor(self, cursor):
        """Ganti kursor hanya kalau berubah."""
        if cursor != self.cursor:
            pygame.mouse.set_cursor(cursor)
            self.cursor = cursor
