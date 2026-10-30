"""Pembuat state dan permainan acak untuk unit test."""

import random

import rules


def make_state(human, ai, walls=(), turn=rules.AI):
    return {"human": human, "ai": ai, "walls": set(walls), "turn": turn}


def random_states(count, seed, turn=rules.AI, min_plies=2, max_plies=20):
    """State acak hasil permainan random, untuk menguji AI di banyak posisi."""
    rng = random.Random(seed)
    states = []
    while len(states) < count:
        state = rules.initial_state()
        for _ in range(rng.randint(min_plies, max_plies)):
            if rules.is_terminal(state):
                break
            state = rules.result(state, rng.choice(rules.legal_actions(state)))
        if state["turn"] == turn and not rules.is_terminal(state):
            states.append(state)
    return states
