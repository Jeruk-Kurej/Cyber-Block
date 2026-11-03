"""Simulasi tanpa UI: bot sisi Human melawan AI untuk mengukur giliran, waktu berpikir AI, dan win rate.

Pakai: uv run python -m tools.simulate [--games N] [--seed S] [--weight W [W ...]]
Contoh uji WEIGHT: uv run python -m tools.simulate --games 10 --weight 1 2 3
Efficiency (Alpha-Beta vs Minimax tanpa pruning): uv run python -m tools.simulate --compare
"""

import argparse
import random
import statistics
import time

import rules
from ai import candidate_actions, choose_action, evaluate, win_utility
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
    """Baseline: pemain yang asal memilih action."""

    def __init__(self, rng):
        """Simpan pengacak."""
        self.rng = rng

    def choose(self, state):
        """Pilih action legal secara acak."""
        return self.rng.choice(rules.legal_actions(state))


class GreedyBot:
    """Pemain pemula: lihat satu langkah ke depan (mobility), sesekali salah langkah."""

    def __init__(self, rng, epsilon):
        """epsilon = peluang memilih langkah acak (meniru salah langkah)."""
        self.rng = rng
        self.epsilon = epsilon

    def choose(self, state):
        """Pilih action dengan nilai satu langkah terbaik (kadang acak)."""
        actions = rules.legal_actions(state)
        if self.rng.random() < self.epsilon:
            return self.rng.choice(actions)
        scores = [self.score(state, action) for action in actions]
        best = max(scores)
        return self.rng.choice([a for a, s in zip(actions, scores) if s == best])

    def score(self, state, action):
        """Nilai satu langkah ke depan, menang langsung paling tinggi.
        Pakai mobility 1 langkah (tile yang menempel), supaya baseline tidak ikut berubah kalau evaluate AI diganti."""
        after = rules.result(state, action)
        if rules.is_terminal(after):
            return WIN_UTILITY
        me = state["turn"]
        return rules.mobility(after, me) - rules.mobility(after, rules.opponent(me))


class SearchBot:
    """AI kita (Minimax dengan Alpha-Beta) sebagai pemain di simulasi."""

    def __init__(self, level):
        """Simpan level dan siapkan pencatat waktu berpikir."""
        self.level = level
        self.times = []

    def choose(self, state):
        """Pilih action dengan choose_action dan catat waktunya."""
        result = choose_action(state, self.level)
        self.times.append(result["elapsed"])
        return result["action"]


# --- Satu game ---
class MatchStats:
    """Kumpulan hasil semua game di satu baris laporan."""

    def __init__(self):
        """Mulai dari nol."""
        self.ai_wins = 0
        self.human_turns = []
        self.ai_turn_seconds = []


def play(human_bot, ai_bot, rng, stats):
    """Mainkan satu game sampai selesai, catat hasilnya di stats."""
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


def levels_to_test(weights):
    """LEVELS apa adanya, atau tiap level dengan WEIGHT yang diganti."""
    if not weights:
        return LEVELS
    # {**level, ...} = salinan level dengan nama dan weight yang diganti
    return [{**level, "name": f"{level['name']} w={w:g}", "weight": w} for level in LEVELS for w in weights]


# --- Laporan ---
def human_bots(rng):
    """Daftar lawan baseline untuk AI: pasangan (nama, fungsi pembuat bot)."""
    # yield = kirim satu pasangan setiap kali; lambda = fungsi kecil tanpa nama untuk membuat bot baru
    yield "Random", lambda: RandomBot(rng)
    yield f"Greedy e={SIM_BOT_EPSILON}", lambda: GreedyBot(rng, SIM_BOT_EPSILON)
    yield "Greedy e=0", lambda: GreedyBot(rng, 0.0)
    for level in LEVELS[:2]:
        yield f"AI {level['name']}", lambda lv=level: SearchBot(lv)


def report(name, level, games, stats, ai_bot):
    """Cetak satu baris hasil simulasi."""
    turns = stats.human_turns
    times = sorted(ai_bot.times)
    p95 = times[int(0.95 * (len(times) - 1))]
    budget = HUMAN_CLOCK_SECONDS / statistics.mean(turns)
    print(
        f"{name:<14} vs AI {level['name']:<12} | AI menang {stats.ai_wins / games:5.0%} "
        f"| giliran Human {statistics.mean(turns):4.1f} (min {min(turns):2d}, max {max(turns):2d}) "
        f"| dtk/giliran utk {HUMAN_CLOCK_SECONDS:.0f}s {budget:4.1f} "
        f"| AI dtk/move avg {statistics.mean(times):.3f} p95 {p95:.3f} max {times[-1]:.3f} "
        f"| AI total/game {statistics.mean(stats.ai_turn_seconds):4.1f}s"
    )


# --- Efficiency: Alpha-Beta vs Minimax tanpa pruning ---
def plain_minimax(state, me, depth, ply, weight, info):
    """Minimax biasa tanpa pruning. Kandidat action sama dengan AI, supaya perbandingannya adil."""
    info["nodes"] += 1
    if rules.is_terminal(state):
        return -win_utility(ply) if state["turn"] == me else win_utility(ply)
    if depth == 0:
        return evaluate(state, me, weight)
    values = [plain_minimax(rules.result(state, a), me, depth - 1, ply + 1, weight, info) for a in candidate_actions(state)]
    return max(values) if state["turn"] == me else min(values)


def random_ai_states(count, rng):
    """Posisi uji: state giliran AI dari permainan random."""
    states = []
    while len(states) < count:
        state = rules.initial_state()
        for _ in range(rng.randint(2, 20)):
            if rules.is_terminal(state):
                break
            state = rules.result(state, rng.choice(rules.legal_actions(state)))
        if state["turn"] == rules.AI and not rules.is_terminal(state):
            states.append(state)
    return states


def compare(count, seed):
    """Jumlah node dan waktu per giliran di posisi dan depth yang sama."""
    states = random_ai_states(count, random.Random(seed))
    print(f"Efficiency di {count} posisi acak (depth sama, kandidat action sama)")
    for level in LEVELS:
        ab_nodes, ab_times, mm_nodes, mm_times, same = [], [], [], [], 0
        for state in states:
            result = choose_action(state, level)
            ab_nodes.append(result["nodes"])
            ab_times.append(result["elapsed"])
            info = {"nodes": -1}  # root tidak dihitung, sama seperti choose_action
            start = time.perf_counter()
            value = plain_minimax(state, rules.AI, level["depth"], 0, level["weight"], info)
            mm_times.append(time.perf_counter() - start)
            mm_nodes.append(info["nodes"])
            same += value == result["value"]
        ratio = sum(mm_nodes) / sum(ab_nodes)
        print(
            f"{level['name']:<7} | node Alpha-Beta {statistics.mean(ab_nodes):9.0f} | Minimax {statistics.mean(mm_nodes):9.0f} "
            f"| {ratio:4.0f}x lebih sedikit | dtk/giliran {statistics.mean(ab_times):.3f} vs {statistics.mean(mm_times):.3f} "
            f"| nilai sama {same}/{count}"
        )


def main():
    """Baca opsi (--games, --seed, --weight, --compare) lalu jalankan simulasi."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=SIM_GAMES)
    parser.add_argument("--seed", type=int, default=SIM_SEED)
    parser.add_argument("--weight", type=float, nargs="+", help="uji beberapa nilai WEIGHT untuk tiap level")
    parser.add_argument("--compare", type=int, nargs="?", const=10, help="bandingkan dengan Minimax tanpa pruning di N posisi")
    args = parser.parse_args()
    if args.compare:
        compare(args.compare, args.seed)
        return
    for level in levels_to_test(args.weight):
        for name, make_bot in human_bots(random.Random(args.seed)):
            rng = random.Random(args.seed)
            human_bot, ai_bot, stats = make_bot(), SearchBot(level), MatchStats()
            for _ in range(args.games):
                play(human_bot, ai_bot, rng, stats)
            report(name, level, args.games, stats, ai_bot)
        print()


if __name__ == "__main__":
    main()
