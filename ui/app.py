"""Window, loop utama, dan perpindahan antara layar siap dan permainan."""

from enum import Enum, auto

import pygame

from config import DEFAULT_LEVEL, LEVELS
from game.controller import GameController, Phase
from ui import theme
from ui.board_renderer import BoardRenderer
from ui.debug_overlay import DebugOverlay
from ui.effects import grid_background, scanlines
from ui.game_over_overlay import GameOverOverlay
from ui.hud import Hud
from ui.input_handler import Command, Intent, translate
from ui.sprites import Sprites
from ui.title_screen import TitleScreen

MAX_FRAME_SECONDS = 0.25


class Scene(Enum):
    TITLE = auto()
    PLAYING = auto()


class App:
    def __init__(self):
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
        self.game: GameController | None = None
        self.show_debug = False
        self.running = True
        self.time = 0.0
        self.mouse_pos = (0, 0)
        self._cursor = None

    # --- Loop ---
    def run(self) -> None:
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
            self._set_cursor(pygame.SYSTEM_CURSOR_HAND if self.hover_cell() is not None else pygame.SYSTEM_CURSOR_ARROW)
            self.render()
            pygame.display.flip()
        pygame.quit()

    def handle(self, command: Command) -> None:
        intent = command.intent
        if intent is Intent.QUIT:
            self.running = False
        elif intent is Intent.TOGGLE_DEBUG:
            self.show_debug = not self.show_debug
        elif self.scene is Scene.TITLE:
            if intent is Intent.SELECT_LEVEL:
                self.level = command.value
            elif intent is Intent.START:
                self.game = GameController(LEVELS[self.level])
                self.scene = Scene.PLAYING
        elif intent is Intent.CLICK_TILE:
            self.game.click(command.value)
        elif intent is Intent.UNDO:
            self.game.undo()
        elif intent is Intent.RESTART and self.game.phase == Phase.GAME_OVER:
            self.scene = Scene.TITLE

    def update(self, dt: float) -> None:
        self.time += dt
        if self.scene is Scene.PLAYING:
            self.game.update(dt)

    # --- Render ---
    def hover_cell(self):
        if self.scene is not Scene.PLAYING:
            return None
        cell = self.board.cell_at(self.mouse_pos)
        return cell if cell in self.game.targets() else None

    def render(self) -> None:
        self.screen.blit(self.background, (0, 0))
        hover = self.hover_cell()
        if self.scene is Scene.TITLE:
            self.title.draw(self.screen, self.level, self.time)
        else:
            self.hud.draw(self.screen, self.game, hover, self.time)
            self.board.draw(self.screen, self.game, hover, self.time)
            if self.show_debug:
                self.debug.draw(self.screen, self.game)
            if self.game.phase == Phase.GAME_OVER:
                self.game_over.draw(self.screen, self.game, self.time)
        self.screen.blit(self.scanlines, (0, 0))

    def _set_cursor(self, cursor: int) -> None:
        if cursor != self._cursor:
            pygame.mouse.set_cursor(cursor)
            self._cursor = cursor
