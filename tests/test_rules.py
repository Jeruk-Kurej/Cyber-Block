import unittest

import rules
from tests.helpers import make_state

TILE_COUNT = len(rules.ALL_TILES)


class InitialStateTest(unittest.TestCase):
    def test_start_positions_and_human_moves_first(self):
        state = rules.initial_state()
        self.assertEqual(state["human"], (0, 3))
        self.assertEqual(state["ai"], (6, 3))
        self.assertEqual(state["walls"], set())
        self.assertEqual(state["turn"], rules.HUMAN)


class MoveTest(unittest.TestCase):
    def test_center_has_eight_directions(self):
        state = make_state(human=(3, 3), ai=(6, 6), turn=rules.HUMAN)
        expected = {(r, c) for r in (2, 3, 4) for c in (2, 3, 4)} - {(3, 3)}
        self.assertEqual(set(rules.legal_moves(state, rules.HUMAN)), expected)

    def test_corner_respects_board_edges(self):
        state = make_state(human=(0, 0), ai=(6, 6), turn=rules.HUMAN)
        self.assertEqual(set(rules.legal_moves(state, rules.HUMAN)), {(0, 1), (1, 0), (1, 1)})

    def test_walls_and_opponent_block_moves(self):
        state = make_state(human=(3, 3), ai=(4, 4), walls=[(2, 2), (2, 3)], turn=rules.HUMAN)
        moves = set(rules.legal_moves(state, rules.HUMAN))
        self.assertEqual(len(moves), 5)
        self.assertTrue(moves.isdisjoint({(2, 2), (2, 3), (4, 4)}))

    def test_apply_move_rejects_illegal_tiles(self):
        state = make_state(human=(3, 3), ai=(4, 4), walls=[(2, 2)], turn=rules.HUMAN)
        for target in [(5, 5), (2, 2), (4, 4), (3, 3)]:
            with self.assertRaises(ValueError):
                rules.apply_move(state, target)

    def test_move_keeps_turn_for_place_step(self):
        moved = rules.apply_move(rules.initial_state(), (1, 3))
        self.assertEqual(moved["human"], (1, 3))
        self.assertEqual(moved["turn"], rules.HUMAN)


class PlaceTest(unittest.TestCase):
    def test_cannot_place_occupied_tiles_or_walls(self):
        state = make_state(human=(0, 3), ai=(6, 3), walls=[(3, 3)], turn=rules.HUMAN)
        places = set(rules.legal_places(state))
        self.assertEqual(len(places), TILE_COUNT - 3)
        for blocked in [(0, 3), (6, 3), (3, 3)]:
            self.assertNotIn(blocked, places)
            with self.assertRaises(ValueError):
                rules.apply_place(state, blocked)

    def test_vacated_tile_can_be_placed(self):
        moved = rules.apply_move(rules.initial_state(), (1, 3))
        self.assertIn((0, 3), rules.legal_places(moved))
        placed = rules.apply_place(moved, (0, 3))
        self.assertIn((0, 3), placed["walls"])

    def test_place_makes_permanent_wall_and_passes_turn(self):
        moved = rules.apply_move(rules.initial_state(), (1, 3))
        placed = rules.apply_place(moved, (5, 3))
        self.assertIn((5, 3), placed["walls"])
        self.assertEqual(placed["turn"], rules.AI)
        self.assertNotIn((5, 3), rules.legal_moves(placed, rules.AI))


class ActionsTest(unittest.TestCase):
    def test_initial_actions_are_every_move_times_every_empty_tile(self):
        actions = rules.legal_actions(rules.initial_state())
        self.assertEqual(len(actions), 5 * (TILE_COUNT - 2))
        self.assertEqual(len(set(actions)), len(actions))

    def test_result_applies_move_then_place(self):
        state = rules.result(rules.initial_state(), ((1, 2), (5, 2)))
        self.assertEqual(state["human"], (1, 2))
        self.assertIn((5, 2), state["walls"])
        self.assertEqual(state["turn"], rules.AI)


class TerminalTest(unittest.TestCase):
    def test_player_without_moves_loses(self):
        state = make_state(human=(0, 0), ai=(1, 1), walls=[(0, 1), (1, 0)], turn=rules.HUMAN)
        self.assertTrue(rules.is_terminal(state))
        self.assertEqual(rules.winner(state), rules.AI)

    def test_trapped_opponent_does_not_end_game_on_own_turn(self):
        state = make_state(human=(0, 0), ai=(1, 1), walls=[(0, 1), (1, 0)], turn=rules.AI)
        self.assertFalse(rules.is_terminal(state))
        self.assertIsNone(rules.winner(state))


if __name__ == "__main__":
    unittest.main()
