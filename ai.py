"""AI Cyber Block: Minimax dengan Alpha-Beta Pruning.

Isi file ini (urutannya sama dengan proposal):
    1. evaluate()            -> evaluation function: mobility_AI - WEIGHT x mobility_Human
                                (mobility = tile yang bisa dicapai dalam MOBILITY_STEPS langkah)
    2. candidate_actions()   -> place candidate filtering (mengurangi branching factor)
    3. order_actions()       -> move ordering (supaya pruning terjadi lebih awal)
    4. choose_action()       -> titik masuk: AI memilih satu action
    5. max_value(), min_value() -> Minimax dengan Alpha-Beta Pruning, dengan depth limit
    6. AIPlayer              -> menjalankan search di background supaya window tidak freeze

Pemain yang sedang giliran saat choose_action() dipanggil adalah MAX (di game: AI).
Lawannya MIN (di game: Human). Semua nilai dihitung dari sudut pandang MAX.
"""

import time
from threading import Thread

import rules
from config import MOBILITY_STEPS, PLACE_RADIUS, WIN_UTILITY

INF = float("inf")


# ---------------------------------------------------------------- 1. evaluation function

def mobility(state, player, steps=MOBILITY_STEPS):
    """Jumlah tile kosong yang bisa dicapai player dengan jalan paling banyak `steps` langkah.
    Tembok dan bidak lawan menghalangi jalan. steps = 1 sama dengan rules.mobility()."""
    enemy = state[rules.opponent(player)]
    reached = {state[player]}
    frontier = [state[player]]
    for _ in range(steps):
        next_frontier = []
        for tile in frontier:
            for neighbor in rules.neighbors(tile):
                if neighbor not in reached and neighbor not in state["walls"] and neighbor != enemy:
                    reached.add(neighbor)
                    next_frontier.append(neighbor)
        frontier = next_frontier
    return len(reached) - 1    # posisi player sendiri tidak dihitung


def evaluate(state, player, weight):
    """Nilai state yang belum selesai, dari sudut pandang player.
    WEIGHT > 1 artinya AI lebih mementingkan mengurung lawan daripada menambah ruang geraknya sendiri."""
    return mobility(state, player) - weight * mobility(state, rules.opponent(player))


def win_utility(ply):
    """UTILITY untuk menang. Dikurangi ply supaya AI memilih kemenangan tercepat
    (dan menunda kekalahan selama mungkin)."""
    return WIN_UTILITY - ply


# ---------------------------------------------------------------- 2. place candidate filtering

def candidate_actions(state):
    """Seperti rules.legal_actions(), tetapi kandidat place hanya tile kosong yang dekat lawan
    (jarak <= PLACE_RADIUS), ditambah 1 tile netral. Jika di sekitar lawan sudah penuh, semua tile kosong dipakai."""
    enemy = state[rules.opponent(state["turn"])]
    actions = []
    for move in rules.legal_moves(state, state["turn"]):
        empty = rules.legal_places(rules.apply_move(state, move))
        near = [tile for tile in empty if rules.distance(tile, enemy) <= PLACE_RADIUS]
        if not near:
            near = empty
        else:
            spare = neutral_tile(empty, enemy, move)
            if spare is not None:
                near.append(spare)
        for place in near:
            actions.append((move, place))
    return actions


def neutral_tile(empty, enemy, me):
    """Tile di luar jarak PLACE_RADIUS dari lawan yang paling jauh dari kedua bidak.
    Tembok di sini tidak mengurung siapa pun, jadi gunanya untuk "membuang giliran"."""
    best = None
    best_gap = -1
    for tile in empty:
        if rules.distance(tile, enemy) <= PLACE_RADIUS:
            continue                        # tile dekat lawan sudah jadi kandidat
        gap = min(rules.distance(tile, enemy), rules.distance(tile, me))   # jarak ke bidak terdekat
        if gap > best_gap:
            best, best_gap = tile, gap
    return best


# ---------------------------------------------------------------- 3. move ordering

def order_actions(state, depth, maximizing, info):
    """Urutkan action dari yang paling menjanjikan. MAX: nilai terbesar dulu, MIN: terkecil dulu.
    Di depth 1 tidak perlu diurutkan, karena child-nya langsung dinilai."""
    actions = candidate_actions(state)
    if depth > 1:
        def quick_value(action):
            """Nilai sementara untuk mengurutkan: evaluate langsung setelah action."""
            return evaluate(rules.result(state, action), info["me"], info["weight"])
        actions.sort(key=quick_value, reverse=maximizing)
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
    candidates.sort(key=candidate_value, reverse=True)    # nilai terbesar di urutan pertama
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


def candidate_value(candidate):
    """Kunci pengurutan kandidat: nilainya."""
    return candidate["value"]


# ---------------------------------------------------------------- 5. Minimax dengan Alpha-Beta Pruning
# alpha = nilai terbaik yang SUDAH DIJAMIN untuk MAX di jalur dari root sampai node ini.
# beta  = nilai terbaik yang SUDAH DIJAMIN untuk MIN di jalur yang sama.
# Di node MAX: jika value >= beta, MIN di atasnya tidak akan memilih jalur ini -> sisa child dipangkas.
# Di node MIN: jika value <= alpha, MAX di atasnya tidak akan memilih jalur ini -> sisa child dipangkas.
# ply = jarak node dari root (dipakai di UTILITY).

def max_value(state, depth, alpha, beta, ply, info):
    """Giliran MAX (AI): ambil nilai terbesar dari semua child, pangkas jika value >= beta."""
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
    """Giliran MIN (Human): ambil nilai terkecil dari semua child, pangkas jika value <= alpha."""
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
        """Simpan level; belum ada search yang berjalan."""
        self.level = level
        self.thread = None
        self.result = None

    def start(self, state):
        """Mulai search di thread baru (game tetap jalan selama AI berpikir)."""
        self.result = None
        self.thread = Thread(target=self.run, args=(state,), daemon=True)
        self.thread.start()

    def run(self, state):
        """Isi thread: jalankan choose_action dan simpan hasilnya."""
        self.result = choose_action(state, self.level)

    def poll(self):
        """Hasil search jika sudah selesai, atau None jika AI masih berpikir."""
        if self.thread is None or self.thread.is_alive():
            return None
        self.thread = None
        return self.result
