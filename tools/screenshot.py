"""Render layar-layar penting tanpa window (headless) ke PNG untuk verifikasi visual.

Pakai: uv run python -m tools.screenshot <folder_output>
"""

import os
import sys
import time
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

import rules  # noqa: E402
from config import HUMAN_CLOCK_SECONDS, LEVELS  # noqa: E402
from game.controller import GameController, Phase  # noqa: E402
from tests.helpers import make_state  # noqa: E402
from ui.app import App, Scene  # noqa: E402
from ui.input_handler import Command, Intent  # noqa: E402

FRAME = 1 / 60


# --- Bantuan skenario ---
def hover(app: App, row: int, col: int) -> None:
    app.mouse_pos = app.board.cell_rect((row, col)).center


def advance(app: App, seconds: float) -> None:
    for _ in range(int(seconds / FRAME)):
        app.update(FRAME)


def wait_for_human_turn(app: App) -> None:
    while app.game.phase == Phase.AI_THINKING:
        app.update(FRAME)
        time.sleep(0.005)


def start_game(app: App, state) -> None:
    app.game = GameController(LEVELS[app.level], state=state)


def capture(app: App, out: Path, name: str) -> None:
    app.render()
    pygame.image.save(app.screen, out / f"{name}.png")
    print(f"saved {name}.png")


# --- Skenario ---
def main(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    app = App()
    capture(app, out, "01_title")

    app.handle(Command(Intent.START))
    hover(app, 1, 3)
    advance(app, 0.4)
    capture(app, out, "02_move_phase_hover")

    app.game.click((1, 3))
    hover(app, 5, 3)
    capture(app, out, "03_place_phase_hover")

    app.game.click((5, 3))
    advance(app, 0.2)
    capture(app, out, "04_ai_thinking")

    wait_for_human_turn(app)
    app.game.ai_action_age = 0.12
    capture(app, out, "05_ai_action_slide")
    app.game.ai_action_age = 0.8
    hover(app, 2, 3)
    capture(app, out, "06_ai_action_highlight")

    app.show_debug = True
    capture(app, out, "07_debug_overlay")
    app.show_debug = False

    walls = [(0, 1), (1, 1), (2, 2), (2, 4), (3, 4), (4, 1), (4, 2), (5, 5), (6, 2), (1, 5), (3, 0)]
    start_game(app, make_state(human=(2, 3), ai=(5, 3), walls=walls, turn=rules.HUMAN))
    app.game.clock.remaining = 7.6
    hover(app, 3, 3)
    advance(app, 0.3)
    capture(app, out, "08_urgent_clock")

    app.game.click((3, 3))
    hover(app, 4, 4)
    capture(app, out, "09_urgent_place")

    start_game(app, make_state(human=(2, 2), ai=(0, 0), walls=[(0, 1), (1, 0)], turn=rules.HUMAN))
    app.game.clock.remaining = 23.4
    app.game.click((2, 3))
    app.game.click((1, 1))
    capture(app, out, "10_win")

    start_game(app, make_state(human=(0, 0), ai=(1, 1), walls=[(0, 1), (1, 0)], turn=rules.HUMAN))
    capture(app, out, "11_lose")

    start_game(app, make_state(human=(0, 3), ai=(6, 3), turn=rules.HUMAN))
    advance(app, HUMAN_CLOCK_SECONDS + 0.5)
    capture(app, out, "12_timeout")

    app.handle(Command(Intent.RESTART))
    assert app.scene is Scene.TITLE
    pygame.quit()


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "screenshots"))
