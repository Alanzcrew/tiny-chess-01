"""v6: v5 + 80k nodes, rook-on-7th term."""
import json, os, sys, urllib.request

VAL = [0, 100, 320, 330, 500, 900, 0]
MATE = 100000
NODES = 80000
KN = (14, 18, 31, 33, -14, -18, -31, -33)
KI = (1, -1, 16, -16, 15, 17, -15, -17)
BI = (15, 17, -15, -17)
RO = (1, -1, 16, -16)
CM = {4: 3, 0: 2, 7: 1, 116: 12, 112: 8, 119: 4}
RK = {6: (7, 5), 2: (0, 3), 118: (119, 117), 114: (112, 115)}
VS = [sq for sq in range(128) if not (sq & 0x88)]
PV = [[0] * 128 for _ in range(6)]
KM = [0] * 128
KE = [0] * 128
for _r in range(8):
    for _f in range(8):
        _q = _r * 16 + _f
        _c = min(_f, 7 - _f) + min(_r, 7 - _r)
        PV[1][_q] = 100 + (0, 0, 4, 8, 14, 24, 40, 0)[_r] + ((0, 0, 0, 10, 15, 10, 5, 0)[_r] if _f in (3, 4) else 0)
        PV[2][_q] = 320 + 6 * _c - 20
        PV[3][_q] = 330 + 4 * _c - 8
        PV[4][_q] = 500 + (15 if _r == 6 else 0) + (5 if _r == 0 and _f in (3, 4) else 0)
        PV[5][_q] = 900 + 2 * _c - 6
        KM[_q] = (20, 25, 10, 0, 0, 10, 25, 20)[_f] if _r == 0 else max(-50, -15 * _r)
        KE[_q] = 8 * _c - 24


class Board:
    def __init__(self):
        self.b = [0] * 128
        back = [4, 2, 3, 5, 6, 3, 2, 4]
        for f in range(8):
            self.b[f] = back[f]; self.b[16 + f] = 1
            self.b[96 + f] = -1; self.b[112 + f] = -back[f]
        self.turn = 1
        self.cast = 15
        self.ep = -1
        self.half = 0
        self.npm = 4100
        self.st = []
        self.kg = [116, 4]

    def key(self):
        return (tuple(self.b), self.turn, self.cast, self.ep)

    def attacked(self, sq, by):
        b = self.b
        for d in (-15 * by, -17 * by):
            t = sq + d
            if not (t & 0x88) and b[t] == by: return True
        for D, c in ((KN, 2), (KI, 6)):
            for d in D:
                t = sq + d
                if not (t & 0x88) and b[t] == c * by: return True
        for D, c in ((BI, 3), (RO, 4)):
            for d in D:
                t = sq + d
                while not (t & 0x88):
                    p = b[t]
                    if p:
                        if p == c * by or p == 5 * by: return True
                        break
                    t += d
        return False

    def gen(self):
        b, turn = self.b, self.turn
        _e = 7 if turn == 1 else 0
        _s = 1 if turn == 1 else 6
        ms = []
        for f in VS:
            p = b[f]
            if p * turn <= 0: continue
            ap = abs(p)
            if ap == 1:
                d = 16 * turn
                t = f + d
                if not (t & 0x88) and b[t] == 0:
                    if (t >> 4) == _e:
                        for pr in (5, 4, 3, 2): ms.append((f, t, pr))
                    else:
                        ms.append((f, t, 0))
                        if (f >> 4) == _s:
                            t2 = f + 2 * d
                            if b[t2] == 0: ms.append((f, t2, 0))
                for dd in (d - 1, d + 1):
                    t = f + dd
                    if t & 0x88: continue
                    q = b[t]
                    if q * turn < 0:
                        if (t >> 4) == _e:
                            for pr in (5, 4, 3, 2): ms.append((f, t, pr))
                        else: ms.append((f, t, 0))
                    elif t == self.ep:
                        ms.append((f, t, 0))
            elif ap == 2 or ap == 6:
                for d in (KN if ap == 2 else KI):
                    t = f + d
                    if not (t & 0x88) and b[t] * turn <= 0: ms.append((f, t, 0))
            else:
                for d in (BI if ap == 3 else RO if ap == 4 else BI + RO):
                    t = f + d
                    while not (t & 0x88):
                        q = b[t]
                        if q == 0: ms.append((f, t, 0))
                        else:
                            if q * turn < 0: ms.append((f, t, 0))
                            break
                        t += d
        B = 0 if turn == 1 else 112
        k = B + 4
        if self.cast & (1 if B == 0 else 4) and b[B + 5] == 0 and b[B + 6] == 0 and not self.attacked(k, -turn) and not self.attacked(B + 5, -turn) and not self.attacked(B + 6, -turn):
            ms.append((k, B + 6, 0))
        if self.cast & (2 if B == 0 else 8) and b[B + 3] == 0 and b[B + 2] == 0 and b[B + 1] == 0 and not self.attacked(k, -turn) and not self.attacked(B + 3, -turn) and not self.attacked(B + 2, -turn):
            ms.append((k, B + 2, 0))
        return ms

    def make(self, m):
        f, t, pr = m
        b = self.b
        p = b[f]; cap = b[t]; epc = -1
        if abs(p) == 1 and t == self.ep and cap == 0:
            epc = t - 16 * self.turn; cap = b[epc]
        self.st.append((m, cap, self.cast, self.ep, self.half, epc))
        if cap and abs(cap) > 1: self.npm -= VAL[abs(cap)]
        if pr: self.npm += VAL[pr] - 100
        np = pr * self.turn if pr else p
        b[t] = np; b[f] = 0
        if epc >= 0: b[epc] = 0
        if abs(p) == 6:
            self.kg[(self.turn + 1) // 2] = t
            if abs(t - f) == 2:
                _r = RK[t]; b[_r[1]] = b[_r[0]]; b[_r[0]] = 0
        self.cast &= ~CM.get(f, 0) & ~CM.get(t, 0)
        self.ep = (f + t) // 2 if (abs(p) == 1 and abs(t - f) == 32) else -1
        self.half = 0 if (abs(p) == 1 or cap) else self.half + 1
        self.turn = -self.turn
        if self.attacked(self.kg[(-self.turn + 1) // 2], self.turn):
            self.unmake(); return False
        return True

    def unmake(self):
        m, cap, cast, ep, half, epc = self.st.pop()
        f, t, pr = m
        b = self.b
        self.turn = -self.turn; self.cast = cast; self.ep = ep; self.half = half
        if cap and abs(cap) > 1: self.npm += VAL[abs(cap)]
        if pr: self.npm -= VAL[pr] - 100
        p = b[t]
        if abs(p) == 6:
            self.kg[(self.turn + 1) // 2] = f
        b[f] = (1 if p > 0 else -1) if pr else p
        if epc >= 0:
            b[t] = 0; b[epc] = cap
        else:
            b[t] = cap
        if abs(p) == 6 and abs(t - f) == 2:
            _r = RK[t]; b[_r[0]] = b[_r[1]]; b[_r[1]] = 0

    def evaluate(self):
        b = self.b
        s = 0; np = 0; bi = [0, 0]; ksq = [0, 0]
        for sq in VS:
            p = b[sq]
            if not p: continue
            w = p > 0; ap = abs(p)
            if ap == 6:
                ksq[0 if w else 1] = sq
                continue
            s += PV[ap][sq] if w else -PV[ap][sq ^ 112]
            if ap != 1: np += VAL[ap]
            if ap == 3: bi[0 if w else 1] += 1
            if ap == 4 and (sq >> 4) == (6 if w else 1): s += 20 if w else -20
        ph = min(np, 6400)
        k = lambda q: (KM[q] * ph + KE[q] * (6400 - ph)) // 6400
        s += k(ksq[0]) - k(ksq[1] ^ 112)
        s += 40 * ((bi[0] >= 2) - (bi[1] >= 2))
        return s if self.turn == 1 else -s

    def uci(self, m):
        f, t, pr = m
        s = "abcdefgh"[f & 7] + str((f >> 4) + 1) + "abcdefgh"[t & 7] + str((t >> 4) + 1)
        return s + ({2: "n", 3: "b", 4: "r", 5: "q"}[pr] if pr else "")

    def from_uci(self, u):
        f = (ord(u[0]) - 97) + (int(u[1]) - 1) * 16
        t = (ord(u[2]) - 97) + (int(u[3]) - 1) * 16
        pr = "nbrq".index(u[4]) + 2 if len(u) == 5 else 0
        return (f, t, pr)

    def set_from_moves(self, moves_uci, hist=None):
        self.__init__()
        for u in moves_uci:
            m = self.from_uci(u)
            if not self.make(m):
                return False
            if hist is not None:
                k = self.key()
                hist[k] = hist.get(k, 0) + 1
        return True


class Search:
    def __init__(self, board, node_limit):
        self.bd = board
        self.limit = node_limit
        self.nodes = 0
        self.tt = {}
        self.killers = [0] * 300
        self.hist = {}
        self.hh = {}
        self.abort = False

    def order(self, moves, ply, tt_move):
        bd = self.bd
        def score(m):
            if tt_move is not None and m == tt_move:
                return 1000000
            f, t, pr = m
            s = 0
            cap = bd.b[t]
            if cap:
                s += 100000 + VAL[abs(cap)] * 10 - VAL[abs(bd.b[f])]
            if pr:
                s += 200000 + VAL[pr]
            if s == 0:
                if m == self.killers[ply * 2]: s = 50000
                elif m == self.killers[ply * 2 + 1]: s = 40000
                else: s = self.hh.get(m, 0)
            return s
        return sorted(moves, key=score, reverse=True)

    def quiesce(self, alpha, beta, ply):
        self.nodes += 1
        if self.nodes >= self.limit:
            self.abort = True
            return 0
        bd = self.bd
        if ply >= 128:
            return bd.evaluate()
        in_check = bd.attacked(bd.kg[(bd.turn + 1) // 2], -bd.turn)
        best = -MATE - 1
        if not in_check:
            stand = bd.evaluate()
            if stand >= beta:
                return stand
            best = stand
            if stand > alpha:
                alpha = stand
        moves = bd.gen() if in_check else [m for m in bd.gen() if bd.b[m[1]] or m[2] or m[1] == bd.ep]
        moves = self.order(moves, ply, None)
        legal = 0
        for m in moves:
            if not in_check and not m[2]:
                v = bd.b[m[1]]
                if v:
                    if stand + VAL[abs(v)] + 200 < alpha:
                        continue
                elif m[1] == bd.ep:
                    if stand + 300 < alpha:
                        continue
            if not bd.make(m):
                continue
            legal += 1
            sc = -self.quiesce(-beta, -alpha, ply + 1)
            bd.unmake()
            if self.abort:
                return 0
            if sc > best:
                best = sc
            if sc >= beta:
                return sc
            if sc > alpha:
                alpha = sc
        if in_check and legal == 0:
            return -MATE + ply
        return best

    def search(self, depth, alpha, beta, ply, key):
        bd = self.bd
        if ply > 0 and (bd.half >= 100 or self.hist.get(key, 0) >= 2):
            return 0
        if depth <= 0:
            return self.quiesce(alpha, beta, ply)
        self.nodes += 1
        if self.nodes >= self.limit:
            self.abort = True
            return 0
        chk = bd.attacked(bd.kg[(bd.turn + 1) // 2], -bd.turn)
        if chk and ply < 32:
            depth += 1
        entry = self.tt.get(key)
        tt_move = None
        if entry is not None:
            d, sc, flag, tm = entry
            tt_move = tm
            if sc > 99800: sc -= ply
            elif sc < -99800: sc += ply
            if d >= depth:
                if flag == 0:
                    return sc
                elif flag == 1 and sc >= beta:
                    return beta
                elif flag == 2 and sc <= alpha:
                    return alpha
        if depth >= 3 and ply > 0 and not chk and bd.npm > 400:
            _s = bd.turn; _e = bd.ep; _h = bd.half
            bd.turn = -_s; bd.ep = -1; bd.half = _h + 1
            _k = bd.key()
            self.hist[_k] = self.hist.get(_k, 0) + 1
            sc = -self.search(depth - (3 if depth >= 6 else 2), -beta, -beta + 1, ply + 1, _k)
            self.hist[_k] -= 1
            bd.turn = _s; bd.ep = _e; bd.half = _h
            if self.abort:
                return 0
            if sc >= beta:
                return beta
        moves = self.order(bd.gen(), ply, tt_move)
        best = -MATE - 1
        bm = None
        oa = alpha
        legal = 0
        for m in moves:
            f, t, pr = m
            cap = bd.b[t] or (t == bd.ep and abs(bd.b[f]) == 1)
            if not bd.make(m):
                continue
            legal += 1
            k2 = bd.key()
            self.hist[k2] = self.hist.get(k2, 0) + 1
            if depth >= 3 and legal > 3 and not cap and not pr and not chk:
                sc = -self.search(depth - 2, -beta, -alpha, ply + 1, k2)
                if sc > alpha:
                    sc = -self.search(depth - 1, -beta, -alpha, ply + 1, k2)
            else:
                sc = -self.search(depth - 1, -beta, -alpha, ply + 1, k2)
            self.hist[k2] -= 1
            bd.unmake()
            if self.abort:
                return 0
            if bm is None or sc > best:
                best = sc
                bm = m
            if sc > alpha:
                alpha = sc
            if alpha >= beta:
                if not cap and not pr:
                    kl = ply * 2
                    if self.killers[kl] != m:
                        self.killers[kl + 1] = self.killers[kl]
                        self.killers[kl] = m
                    h = self.hh.get(m, 0) + depth * depth
                    self.hh[m] = h if h < 30000 else 30000
                break
        if legal == 0:
            if bd.attacked(bd.kg[(bd.turn + 1) // 2], -bd.turn):
                return -MATE + ply
            return 0
        flag = 0 if best > oa and best < beta else (1 if best >= beta else 2)
        _s = best
        if _s > 99800: _s += ply
        elif _s < -99800: _s -= ply
        if len(self.tt) > 300000:
            self.tt.clear()
        self.tt[key] = (depth, _s, flag, bm)
        return best

    def root(self, max_depth=64):
        bd = self.bd
        order = []
        for _m in bd.gen():
            if bd.make(_m):
                order.append([_m, 0]); bd.unmake()
        if not order:
            return None
        order = [[m, 0] for m in self.order([x[0] for x in order], 0, None)]
        best = order[0][0]
        self.nodes = 0
        self.hh = {}
        for depth in range(1, max_depth + 1):
            self.abort = False
            alpha = -MATE - 1
            beta = MATE + 1
            for pair in order:
                m = pair[0]
                if not bd.make(m):
                    continue
                k2 = bd.key()
                self.hist[k2] = self.hist.get(k2, 0) + 1
                pair[1] = -self.search(depth - 1, -beta, -alpha, 1, k2)
                self.hist[k2] -= 1
                bd.unmake()
                if self.abort:
                    break
                if pair[1] > alpha:
                    alpha = pair[1]
            if self.abort:
                break
            order.sort(key=lambda x: -x[1])
            best = order[0][0]
            if order[0][1] >= MATE - 128:
                break
        return best


ENV_URL = os.environ.get("MAKEFUN_ENV_URL") or sys.exit("no-url")


def post(path, body):
    req = urllib.request.Request(ENV_URL + path, data=json.dumps(body).encode(), headers={"content-type": "application/json"})
    with urllib.request.urlopen(req) as res:
        return json.load(res)


def main():
    bd = Board()
    srch = Search(bd, NODES)
    while True:
        g = post("/game", {})
        if g["status"] == "done":
            break
        srch.hist = {}
        if not bd.set_from_moves(g["moves"], srch.hist):
            sys.exit("replay")
        while g["status"] == "your_move":
            legal_uci = set(g["legal_moves"])
            m = srch.root()
            u = bd.uci(m)
            if u not in legal_uci:
                u = min(legal_uci)
            g = post("/move", {"game": g["game"], "move": u})
            if g["status"] == "your_move":
                srch.hist = {}
                if not bd.set_from_moves(g["moves"], srch.hist):
                    sys.exit("replay")
    print("done", g.get("wins"), g.get("draws"), g.get("losses"))


if __name__ == "__main__":
    main()
