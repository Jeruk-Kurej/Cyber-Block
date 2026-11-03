"""Menerjemahkan event pygame menjadi perintah permainan."""

import pygame


class Intent:
    """Jenis perintah dari pemain."""
    CLICK_TILE = "click_tile"
    UNDO = "undo"
    TOGGLE_DEBUG = "toggle_debug"
    RESTART = "restart"
    START = "start"
    SELECT_LEVEL = "select_level"
    QUIT = "quit"


class Command:
    """Satu perintah: intent plus nilai (tile atau nomor level)."""

    def __init__(self, intent, value=None):
        self.intent = intent
        self.value = value


KEY_INTENTS = {
    pygame.K_ESCAPE: Intent.UNDO,
    pygame.K_TAB: Intent.TOGGLE_DEBUG,
    pygame.K_r: Intent.RESTART,
    pygame.K_SPACE: Intent.START,
    pygame.K_RETURN: Intent.START,
}
LEVEL_KEYS = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_KP1: 0, pygame.K_KP2: 1, pygame.K_KP3: 2}


def translate(event, cell_at):
    """Event pygame jadi Command, atau None kalau tidak dipakai."""
    if event.type == pygame.QUIT:
        return Command(Intent.QUIT)
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            cell = cell_at(event.pos)
            return Command(Intent.CLICK_TILE, cell) if cell is not None else None
        if event.button == 3:
            return Command(Intent.UNDO)
    if event.type == pygame.KEYDOWN:
        if event.key in LEVEL_KEYS:
            return Command(Intent.SELECT_LEVEL, LEVEL_KEYS[event.key])
        if event.key in KEY_INTENTS:
            return Command(KEY_INTENTS[event.key])
    return None
