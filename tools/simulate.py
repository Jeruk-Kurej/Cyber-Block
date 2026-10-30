import argparse
import random
import statistics

import rules
from ai import choose_action, evaluate
from config import (
    AI_MIN_THINK_SECONDS,
    HUMAN_CLOCK_SECONDS,
    LEVELS,
    SIM_BOT_EPSILON,
    SIM_GAMES,
    SIM_OPENING_RANDOM_PLIES,
    SIM_SEED,
    WIN_UTILITY,
)


# --- Bot sisi Human ---
class RandomBot:
    def __init__(self, rng):
        self.rng = rng

    def choose(self, state):
        return self.rng.choice(rules.legal_actions(state))


class GreedyBot:
    """Pemain pemula: lihat satu langkah ke depan (mobility), sesekali salah langkah."""

    def __init__(self, rng, epsilon):
        self.rng = rng
        self.epsilon = epsilon

    def choose(self, state):
        actions = rules.legal_actions(state)
        if self.rng.random() < self.epsilon:
            return self.rng.choice(actions)
        scores = [self._score(state, action) for action in actions]
        best = max(scores)
        return self.rng.choice([a for a, s in zip(actions, scores) if s == best])

    @staticmethod
    def _score(state, action):
        after = rules.result(state, action)
        if rules.is_terminal(after):
            return WIN_UTILITY
        return evaluate(after, state["turn"], 1.0)


class SearchBot:
    def __init__(self, level):
        self.level = level
        self.times = []

    def choose(self, state):
        result = choose_action(state, self.level)
        self.times.append(result["elapsed"])
        return result["action"]


# --- Satu game ---
class MatchStats:
    def __init__(self):
        self.ai_wins = 0
        self.human_turns = []
        self.ai_turn_seconds = []


def play(human_bot, ai_bot, rng, stats):
    state = rules.initial_state()
    plies = human_turns = 0
    ai_seconds = 0.0
    while not rules.is_terminal(state):
        mover = state["turn"]
        if plies < SIM_OPENING_RANDOM_PLIES:
            action = rng.choice(rules.legal_actions(state))
        elif mover == rules.HUMAN:
            action = human_bot.choose(state)
        else:
            action = ai_bot.choose(state)
            ai_seconds += max(AI_MIN_THINK_SECONDS, ai_bot.times[-1])
        human_turns += mover == rules.HUMAN
        state = rules.result(state, action)
        plies += 1
    stats.ai_wins += rules.winner(state) == rules.AI
    stats.human_turns.append(human_turns)
    stats.ai_turn_seconds.append(ai_seconds)


# --- Laporan ---
def human_bots(rng):
    yield "Random", lambda: RandomBot(rng)
    yield f"Greedy e={SIM_BOT_EPSILON}", lambda: GreedyBot(rng, SIM_BOT_EPSILON)
    yield "Greedy e=0", lambda: GreedyBot(rng, 0.0)
    for level in LEVELS[:2]:
        yield f"AI {level['name']}", lambda lv=level: SearchBot(lv)


def report(name, level, games, stats, ai_bot):
    turns = stats.human_turns
    times = sorted(ai_bot.times)
    p95 = times[int(0.95 * (len(times) - 1))]
    budget = HUMAN_CLOCK_SECONDS / statistics.mean(turns)
    print(
        f"{name:<14} vs AI {level['name']:<6} | AI menang {stats.ai_wins / games:5.0%} "
        f"| giliran Human {statistics.mean(turns):4.1f} (min {min(turns):2d}, max {max(turns):2d}) "
        f"| dtk/giliran utk 60s {budget:4.1f} "
        f"| AI dtk/move avg {statistics.mean(times):.3f} p95 {p95:.3f} max {times[-1]:.3f} "
        f"| AI total/game {statistics.mean(stats.ai_turn_seconds):4.1f}s"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=SIM_GAMES)
    parser.add_argument("--seed", type=int, default=SIM_SEED)
    args = parser.parse_args()
    for level in LEVELS:
        for name, make_bot in human_bots(random.Random(args.seed)):
            rng = random.Random(args.seed)
            human_bot, ai_bot, stats = make_bot(), SearchBot(level), MatchStats()
            for _ in range(args.games):
                play(human_bot, ai_bot, rng, stats)
            report(name, level, args.games, stats, ai_bot)
        print()


if __name__ == "__main__":
    main()
