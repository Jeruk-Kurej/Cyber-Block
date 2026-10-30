import itertools
import random
import unittest

import rules
from ai import candidate_actions, choose_action, evaluate, win_utility
from config import LEVELS, PLACE_RADIUS
from tests.helpers import make_state, random_states


def fixed_depth(depth, weight=2.0):
    return {"name": "Test", "depth": depth, "weight": weight}


def minimax(state, me, depth, ply, weight):
    """Minimax biasa tanpa pruning, sebagai pembanding kebenaran Alpha-Beta."""
    if rules.is_terminal(state):
        return -win_utility(ply) if state["turn"] == me else win_utility(ply)
    if depth == 0:
        return evaluate(state, me, weight)
    values = [minimax(rules.result(state, action), me, depth - 1, ply + 1, weight) for action in candidate_actions(state)]
    return max(values) if state["turn"] == me else min(values)


class BranchingControlTest(unittest.TestCase):
    def test_place_candidates_stay_near_opponent(self):
        state = make_state(human=(0, 3), ai=(6, 3))
        actions = candidate_actions(state)
        self.assertTrue(actions)
        for action in actions:
            self.assertLessEqual(rules.distance(action[1], (0, 3)), PLACE_RADIUS)

    def test_falls_back_to_all_empty_tiles_when_zone_is_full(self):
        zone = [tile for tile in rules.ALL_TILES if 0 < rules.distance(tile, (0, 0)) <= PLACE_RADIUS]
        state = make_state(human=(0, 0), ai=(6, 6), walls=zone)
        actions = candidate_actions(state)
        for move, group in itertools.groupby(actions, key=lambda action: action[0]):
            empty = set(rules.legal_places(rules.apply_move(state, move)))
            self.assertEqual({action[1] for action in group}, empty)


class AlphaBetaCorrectnessTest(unittest.TestCase):
    def assert_matches_minimax(self, states, depth):
        for state in states:
            expected = minimax(state, state["turn"], depth, 0, 2.0)
            result = choose_action(state, fixed_depth(depth))
            self.assertEqual(result["value"], expected)
            self.assertIn(result["action"], rules.legal_actions(state))

    def test_matches_plain_minimax_at_depth_two(self):
        self.assert_matches_minimax(random_states(4, seed=11), depth=2)

    def test_matches_plain_minimax_at_depth_three_late_game(self):
        self.assert_matches_minimax(random_states(2, seed=12, min_plies=24, max_plies=30), depth=3)

    def test_pruning_skips_branches(self):
        result = choose_action(random_states(1, seed=13)[0], fixed_depth(3))
        self.assertGreater(result["cutoffs"], 0)
        self.assertGreater(result["pruned"], 0)


class DecisionTest(unittest.TestCase):
    def test_takes_immediate_win(self):
        state = make_state(human=(0, 0), ai=(3, 3), walls=[(0, 1), (1, 0)])
        for level in LEVELS:
            result = choose_action(state, level)
            self.assertEqual(result["value"], win_utility(1), level["name"])
            self.assertEqual(rules.winner(rules.result(state, result["action"])), rules.AI)

    def test_takes_immediate_win_whenever_one_exists(self):
        rng = random.Random(21)
        found = 0
        while found < 10:
            state = random_states(1, seed=rng.randrange(10**6), min_plies=10, max_plies=34)[0]
            winning = [a for a in rules.legal_actions(state) if rules.is_terminal(rules.result(state, a))]
            if not winning:
                continue
            found += 1
            for level in LEVELS:
                action = choose_action(state, level)["action"]
                self.assertTrue(rules.is_terminal(rules.result(state, action)), level["name"])

    def test_never_returns_illegal_action(self):
        rng = random.Random(31)
        for _ in range(6):
            state = rules.initial_state()
            while not rules.is_terminal(state):
                legal = rules.legal_actions(state)
                if state["turn"] == rules.AI:
                    action = choose_action(state, fixed_depth(2))["action"]
                    self.assertIn(action, legal)
                else:
                    action = rng.choice(legal)
                state = rules.result(state, action)

    def test_same_state_gives_same_decision(self):
        for state in random_states(3, seed=41):
            first = choose_action(state, LEVELS[2])
            second = choose_action(state, LEVELS[2])
            self.assertEqual(first["action"], second["action"])
            self.assertEqual(first["nodes"], second["nodes"])
            self.assertEqual(first["candidates"], second["candidates"])

    def test_searches_exactly_the_level_depth(self):
        for level in LEVELS:
            self.assertEqual(choose_action(random_states(1, seed=51)[0], level)["depth"], level["depth"])


if __name__ == "__main__":
    unittest.main()
