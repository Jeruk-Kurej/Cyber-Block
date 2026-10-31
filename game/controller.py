"""Alur satu game: giliran Human (move lalu place), giliran AI, chess clock, dan hasil akhir.

Fase giliran:
    HUMAN_MOVE  -> Human klik tile biru untuk move
    HUMAN_PLACE -> Human klik tile kosong untuk place (jadi tembok), giliran pindah ke AI
    AI_THINKING -> AI menjalankan search di background
    GAME_OVER   -> ada yang terkurung atau waktu Human habis
"""

import rules
from ai import AIPlayer
from config import AI_MIN_THINK_SECONDS, HUMAN_CLOCK_SECONDS
from game.chess_clock import ChessClock
from game.scoring import AI_WIN, HUMAN_WIN, TIMEOUT, compute_score


class Phase:
    HUMAN_MOVE = "human_move"
    HUMAN_PLACE = "human_place"
    AI_THINKING = "ai_thinking"
    GAME_OVER = "game_over"


class GameController:
    def __init__(self, level, ai=None, state=None):
        self.level = level                          # salah satu isi config.LEVELS
        self.ai = ai or AIPlayer(level)
        self.state = state or rules.initial_state()
        self.clock = ChessClock(HUMAN_CLOCK_SECONDS)
        self.phase = Phase.HUMAN_MOVE
        self.turns_survived = 0
        self.turn_start = self.state                # untuk undo move
        self.think_time = 0.0
        # Untuk tampilan: action AI terakhir dan hasil search-nya (debug mode)
        self.last_ai_action = None
        self.last_ai_from = None
        self.ai_action_age = float("inf")
        self.last_search = None
        self.outcome = None
        self.score = None
        self.begin_human_turn()

    # ---------------------------------------------------------------- dibaca oleh UI

    def human_turn(self):
        return self.phase in (Phase.HUMAN_MOVE, Phase.HUMAN_PLACE)

    def move_origin(self):
        """Tile asal Human sebelum move (ditandai di layar saat fase place)."""
        if self.phase == Phase.HUMAN_PLACE:
            return self.turn_start[rules.HUMAN]
        return None

    def targets(self):
        """Tile yang boleh diklik sekarang."""
        if self.phase == Phase.HUMAN_MOVE:
            return rules.legal_moves(self.state, rules.HUMAN)
        if self.phase == Phase.HUMAN_PLACE:
            return rules.legal_places(self.state)
        return []

    def mobility(self):
        return mobility_of_both(self.state)

    def preview(self, tile):
        """Mobility kedua pemain seandainya Human mengklik tile ini."""
        if self.phase == Phase.HUMAN_MOVE:
            return mobility_of_both(rules.apply_move(self.state, tile))
        return mobility_of_both(rules.apply_place(self.state, tile))

    # ---------------------------------------------------------------- input dari Human

    def click(self, tile):
        if tile not in self.targets():
            return False
        if self.phase == Phase.HUMAN_MOVE:
            self.state = rules.apply_move(self.state, tile)
            self.phase = Phase.HUMAN_PLACE
        else:
            self.state = rules.apply_place(self.state, tile)
            self.end_human_turn()
        return True

    def undo(self):
        """Batalkan move (hanya bisa saat fase place)."""
        if self.phase != Phase.HUMAN_PLACE:
            return False
        self.state = self.turn_start
        self.phase = Phase.HUMAN_MOVE
        return True

    def update(self, dt):
        """Dipanggil setiap frame: jalankan jam Human atau tunggu hasil search AI."""
        self.ai_action_age += dt
        if self.human_turn():
            self.clock.tick(dt)
            if self.clock.expired():
                self.finish(TIMEOUT)
        elif self.phase == Phase.AI_THINKING:
            self.think_time += dt
            if self.think_time >= AI_MIN_THINK_SECONDS:
                result = self.ai.poll()
                if result is not None:
                    self.apply_ai(result)

    # ---------------------------------------------------------------- pergantian giliran

    def begin_human_turn(self):
        if rules.is_terminal(self.state):
            self.finish(AI_WIN)
            return
        self.turn_start = self.state
        self.phase = Phase.HUMAN_MOVE
        self.clock.start()

    def end_human_turn(self):
        self.clock.stop()
        self.turns_survived += 1
        if rules.is_terminal(self.state):
            self.finish(HUMAN_WIN)
            return
        self.phase = Phase.AI_THINKING
        self.think_time = 0.0
        self.ai.start(self.state)

    def apply_ai(self, result):
        self.last_ai_from = self.state[rules.AI]
        self.state = rules.result(self.state, result["action"])
        self.last_ai_action = result["action"]
        self.last_search = result
        self.ai_action_age = 0.0
        self.begin_human_turn()

    def finish(self, outcome):
        self.clock.stop()
        self.phase = Phase.GAME_OVER
        self.outcome = outcome
        self.score = compute_score(outcome, self.clock.remaining, self.turns_survived)


def mobility_of_both(state):
    return {rules.HUMAN: rules.mobility(state, rules.HUMAN), rules.AI: rules.mobility(state, rules.AI)}
