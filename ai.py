import time
from threading import Thread

import rules
from config import PLACE_RADIUS, WIN_UTILITY

INF = float("inf")


# ---------------------------------------------------------------- 1. evaluation function

def evaluate(state, player, weight):
    """Nilai state yang belum selesai, dari sudut pandang player.
    WEIGHT > 1 artinya AI lebih mementingkan mengurung lawan daripada menambah ruang geraknya sendiri."""
    return rules.mobility(state, player) - weight * rules.mobility(state, rules.opponent(player))


def win_utility(ply):
    """UTILITY untuk menang. Dikurangi ply supaya AI memilih kemenangan tercepat
    (dan menunda kekalahan selama mungkin)."""
    return WIN_UTILITY - ply


# ---------------------------------------------------------------- 2. place candidate filtering

def candidate_actions(state):
    """Seperti rules.legal_actions(), tetapi kandidat place hanya tile kosong yang dekat lawan
    (jarak <= PLACE_RADIUS). Jika di sekitar lawan sudah penuh, semua tile kosong dipakai."""
    enemy = state[rules.opponent(state["turn"])]
    actions = []
    for move in rules.legal_moves(state, state["turn"]):
        empty = rules.legal_places(rules.apply_move(state, move))
        near = [tile for tile in empty if rules.distance(tile, enemy) <= PLACE_RADIUS]
        if not near:
            near = empty
        for place in near:
            actions.append((move, place))
    return actions


# ---------------------------------------------------------------- 3. move ordering

def order_actions(state, depth, maximizing, info):
    """Urutkan action dari yang paling menjanjikan. MAX: nilai terbesar dulu, MIN: terkecil dulu.
    Di depth 1 tidak perlu diurutkan, karena child-nya langsung dinilai."""
    actions = candidate_actions(state)
    if depth > 1:
        actions.sort(key=lambda action: evaluate(rules.result(state, action), info["me"], info["weight"]), reverse=maximizing)
    return actions


# ---------------------------------------------------------------- 4. titik masuk

def choose_action(state, level):
    """AI memilih action terbaik untuk pemain yang sedang giliran.

    level = salah satu isi config.LEVELS, misalnya {"name": "Hard", "depth": 3, "weight": 2.0}.
    Hasilnya dictionary: action terpilih, nilainya, dan statistik search untuk debug mode.
    """
    depth = level["depth"]
    # info dibawa ke semua fungsi search: siapa MAX, WEIGHT, dan penghitung statistik
    info = {"me": state["turn"], "weight": level["weight"], "nodes": 0, "cutoffs": 0, "pruned": 0}
    start = time.perf_counter()

    alpha = -INF
    candidates = []
    for action in order_actions(state, depth, True, info):
        value = min_value(rules.result(state, action), depth - 1, alpha, INF, 1, info)
        # value > alpha: nilai minimax yang tepat.
        # value <= alpha: hanya batas atas, karena cabangnya sudah dipangkas (pasti tidak lebih baik).
        candidates.append({"action": action, "value": value, "exact": value > alpha})
        alpha = max(alpha, value)

    if not candidates:
        raise ValueError("State terminal: tidak ada action legal")
    candidates.sort(key=lambda candidate: -candidate["value"])
    best = candidates[0]
    return {
        "action": best["action"],
        "value": best["value"],
        "depth": depth,
        "nodes": info["nodes"],
        "cutoffs": info["cutoffs"],
        "pruned": info["pruned"],
        "elapsed": time.perf_counter() - start,
        "candidates": candidates,
    }


# ---------------------------------------------------------------- 5. Minimax dengan Alpha-Beta Pruning
# alpha = nilai terbaik yang SUDAH DIJAMIN untuk MAX di jalur dari root sampai node ini.
# beta  = nilai terbaik yang SUDAH DIJAMIN untuk MIN di jalur yang sama.
# Di node MAX: jika value >= beta, MIN di atasnya tidak akan memilih jalur ini -> sisa child dipangkas.
# Di node MIN: jika value <= alpha, MAX di atasnya tidak akan memilih jalur ini -> sisa child dipangkas.
# ply = jarak node dari root (dipakai di UTILITY).

def max_value(state, depth, alpha, beta, ply, info):
    info["nodes"] += 1
    if rules.is_terminal(state):
        return -win_utility(ply)          # MAX terkurung: MAX kalah
    if depth == 0:
        return evaluate(state, info["me"], info["weight"])   # depth limit: pakai evaluation function

    value = -INF
    actions = order_actions(state, depth, True, info)
    for i, action in enumerate(actions):
        value = max(value, min_value(rules.result(state, action), depth - 1, alpha, beta, ply + 1, info))
        if value >= beta:
            count_prune(info, len(actions) - i - 1)
            return value
        alpha = max(alpha, value)
    return value


def min_value(state, depth, alpha, beta, ply, info):
    info["nodes"] += 1
    if rules.is_terminal(state):
        return win_utility(ply)           # MIN terkurung: MAX menang
    if depth == 0:
        return evaluate(state, info["me"], info["weight"])

    value = INF
    actions = order_actions(state, depth, False, info)
    for i, action in enumerate(actions):
        value = min(value, max_value(rules.result(state, action), depth - 1, alpha, beta, ply + 1, info))
        if value <= alpha:
            count_prune(info, len(actions) - i - 1)
            return value
        beta = min(beta, value)
    return value


def count_prune(info, skipped):
    """Statistik untuk debug mode: berapa kali cutoff terjadi dan berapa cabang yang dilewati."""
    info["cutoffs"] += 1
    info["pruned"] += skipped


# ---------------------------------------------------------------- 6. search di background

class AIPlayer:
    """Search dijalankan di thread terpisah supaya window pygame tetap responsif.
    Cara pakai: start(state), lalu panggil poll() setiap frame sampai hasilnya bukan None."""

    def __init__(self, level):
        self.level = level
        self.thread = None
        self.result = None

    def start(self, state):
        self.result = None
        self.thread = Thread(target=self.run, args=(state,), daemon=True)
        self.thread.start()

    def run(self, state):
        self.result = choose_action(state, self.level)

    def poll(self):
        if self.thread is None or self.thread.is_alive():
            return None
        self.thread = None
        return self.result
