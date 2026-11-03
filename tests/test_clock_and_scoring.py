import unittest
from unittest import mock

import rules
from ai import evaluate, win_utility
from config import CLOCK_URGENT_SECONDS, LEVELS, SCORE_WIN_BONUS
from game import scoring
from game.chess_clock import ChessClock
from game.scoring import AI_WIN, HUMAN_WIN, TIMEOUT, compute_score


class ChessClockTest(unittest.TestCase):
    def test_only_ticks_while_running(self):
        clock = ChessClock(60)
        clock.tick(5)
        self.assertEqual(clock.remaining, 60)
        clock.start()
        clock.tick(5)
        clock.stop()
        clock.tick(5)
        self.assertEqual(clock.remaining, 55)

    def test_expires_at_zero_and_never_negative(self):
        clock = ChessClock(3)
        clock.start()
        clock.tick(10)
        self.assertEqual(clock.remaining, 0)
        self.assertTrue(clock.expired())

    def test_urgent_below_threshold(self):
        clock = ChessClock(60)
        clock.start()
        self.assertFalse(clock.urgent())
        clock.tick(60 - CLOCK_URGENT_SECONDS)
        self.assertTrue(clock.urgent())


class ScoringTest(unittest.TestCase):
    def test_win_counts_bonus_time_and_turns(self):
        score = compute_score(HUMAN_WIN, seconds_left=12.7, turns_survived=9)
        self.assertEqual(score["win_bonus"], SCORE_WIN_BONUS)
        self.assertGreater(score["time_bonus"], 0)
        self.assertGreater(score["turn_bonus"], 0)

    def test_loss_ignores_time_left(self):
        for outcome in (AI_WIN, TIMEOUT):
            score = compute_score(outcome, seconds_left=40, turns_survived=5)
            self.assertEqual((score["win_bonus"], score["time_bonus"]), (0, 0))

    def test_any_win_beats_any_loss(self):
        weakest_win = compute_score(HUMAN_WIN, seconds_left=0, turns_survived=1)
        longest_loss = compute_score(AI_WIN, seconds_left=0, turns_survived=len(rules.ALL_TILES))
        self.assertGreater(weakest_win["total"], longest_loss["total"])


class ScoringConfigTest(unittest.TestCase):
    """Rumus skor ikut angka di config, bukan angka tetap."""

    def test_other_config_values(self):
        with mock.patch.multiple(scoring, SCORE_WIN_BONUS=500, SCORE_PER_SECOND_LEFT=5, SCORE_PER_TURN=10):
            win = scoring.compute_score(scoring.HUMAN_WIN, 12.5, 4)
            timeout = scoring.compute_score(scoring.TIMEOUT, 12.5, 4)
        self.assertEqual(win, {"win_bonus": 500, "time_bonus": 62, "turn_bonus": 40, "total": 602})
        self.assertEqual(timeout["total"], 40)


class EvaluationTest(unittest.TestCase):
    def test_evaluation_at_start(self):
        state = rules.initial_state()
        self.assertEqual(rules.mobility(state, rules.HUMAN), 5)
        self.assertEqual(evaluate(state, rules.AI, weight=2), 5 - 2 * 5)

    def test_win_utility_dominates_heuristic(self):
        max_weight = max(level["weight"] for level in LEVELS)
        best_heuristic = 8 + max_weight * 8
        deepest = max(level["depth"] for level in LEVELS)
        self.assertGreater(win_utility(deepest), best_heuristic)


if __name__ == "__main__":
    unittest.main()
