"""Test alur giliran: move, place, undo, giliran AI, dan akhir game."""

import unittest

import rules
from ai import choose_action
from config import AI_MIN_THINK_SECONDS, HUMAN_CLOCK_SECONDS
from game.controller import GameController, Phase
from game.scoring import AI_WIN, HUMAN_WIN, TIMEOUT
from tests.helpers import make_state

QUICK = {"name": "Quick", "depth": 2, "weight": 2.0}


class InstantAI:
    """Pengganti AIPlayer tanpa thread supaya test deterministik."""

    def __init__(self):
        """Belum ada hasil."""
        self._result = None

    def start(self, state):
        """Langsung hitung action (tanpa thread)."""
        self._result = choose_action(state, QUICK)

    def poll(self):
        """Kembalikan hasil sekali, lalu kosongkan."""
        result, self._result = self._result, None
        return result


def new_game(state=None):
    """Game baru dengan AI instan, supaya test cepat."""
    return GameController(QUICK, ai=InstantAI(), state=state)


class HumanTurnTest(unittest.TestCase):
    """Giliran Human: klik, undo, dan pratinjau."""

    def test_starts_in_move_phase_with_clock_running(self):
        game = new_game()
        self.assertEqual(game.phase, Phase.HUMAN_MOVE)
        self.assertTrue(game.clock.running)
        self.assertEqual(set(game.targets()), set(rules.legal_moves(game.state, rules.HUMAN)))

    def test_invalid_clicks_are_ignored(self):
        game = new_game()
        before = game.state
        for target in [(6, 3), (4, 4), (0, 3)]:
            self.assertFalse(game.click(target))
        self.assertEqual(game.phase, Phase.HUMAN_MOVE)
        self.assertEqual(game.state, before)

    def test_move_then_undo_restores_turn_start(self):
        game = new_game()
        before = game.state
        self.assertTrue(game.click((1, 3)))
        self.assertEqual(game.phase, Phase.HUMAN_PLACE)
        self.assertEqual(game.move_origin(), (0, 3))
        self.assertIn((0, 3), game.targets())
        self.assertTrue(game.undo())
        self.assertEqual(game.phase, Phase.HUMAN_MOVE)
        self.assertEqual(game.state, before)
        self.assertFalse(game.undo())

    def test_place_hands_turn_to_ai_and_pauses_clock(self):
        game = new_game()
        game.click((1, 3))
        game.click((5, 3))
        self.assertEqual(game.phase, Phase.AI_THINKING)
        self.assertFalse(game.clock.running)
        self.assertEqual(game.turns_survived, 1)

    def test_preview_shows_mobility_after_place(self):
        game = new_game()
        game.click((1, 3))
        now = game.mobility()
        self.assertEqual(game.preview((5, 3)), {rules.HUMAN: now[rules.HUMAN], rules.AI: now[rules.AI] - 1})


class AITurnTest(unittest.TestCase):
    """Giliran AI: jeda minimal lalu AI bergerak."""

    def test_ai_waits_minimum_think_time_then_moves(self):
        game = new_game()
        game.click((1, 3))
        game.click((5, 3))
        remaining = game.clock.remaining
        game.update(AI_MIN_THINK_SECONDS / 2)
        self.assertEqual(game.phase, Phase.AI_THINKING)
        self.assertEqual(game.clock.remaining, remaining)
        game.update(AI_MIN_THINK_SECONDS)
        self.assertEqual(game.phase, Phase.HUMAN_MOVE)
        self.assertEqual(game.last_ai_from, (6, 3))
        self.assertEqual(game.state["ai"], game.last_ai_action[0])
        self.assertIn(game.last_ai_action[1], game.state["walls"])
        self.assertTrue(game.clock.running)


class GameOverTest(unittest.TestCase):
    """Akhir game: waktu habis, AI terkurung, Human terkurung."""

    def test_clock_running_out_loses(self):
        game = new_game()
        game.update(HUMAN_CLOCK_SECONDS + 1)
        self.assertEqual(game.phase, Phase.GAME_OVER)
        self.assertEqual(game.outcome, TIMEOUT)
        self.assertEqual(game.score["total"], 0)
        self.assertFalse(game.click((1, 3)))

    def test_trapping_ai_wins(self):
        state = make_state(human=(2, 2), ai=(0, 0), walls=[(0, 1), (1, 0)], turn=rules.HUMAN)
        game = new_game(state)
        game.click((2, 3))
        game.click((1, 1))
        self.assertEqual(game.outcome, HUMAN_WIN)
        self.assertGreater(game.score["time_bonus"], 0)

    def test_trapped_human_loses_at_turn_start(self):
        state = make_state(human=(0, 0), ai=(1, 1), walls=[(0, 1), (1, 0)], turn=rules.HUMAN)
        game = new_game(state)
        self.assertEqual(game.phase, Phase.GAME_OVER)
        self.assertEqual(game.outcome, AI_WIN)


if __name__ == "__main__":
    unittest.main()
