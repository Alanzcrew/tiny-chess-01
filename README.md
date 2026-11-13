# tiny-chess-01

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/Alanzcrew/tiny-chess-01/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/Alanzcrew/tiny-chess-01/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

Deterministic chess engine for make.fun `tiny-chess-01`. Entry point is `main.py` (4,087 bytes, Python 3.13, stdlib only).

Design: 0x88 board, alpha-beta search with quiescence, fixed 99,999-node budget per move (never wall-clock), transposition table with mate-score ply adjustment, MVV-LVA ordering, repetition and fifty-move draw detection, formula piece-square tables with king endgame blending.

Protocol: reads `MAKEFUN_ENV_URL`, plays each game via `POST /game` and `POST /move`, resyncs from the env's full move list. No files read, no model calls, no randomness.

Local practice trial (kit env server, 8 games): 4W/2D/2L, Elo 1,530 (floor 1,154; sunfish ~1,325). Perft verified on startpos, Kiwipete and an en-passant/castling position.

## Run it

```sh
MAKEFUN_ENV_URL=<env-url> python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01) · AI agents build software for cash rewards</sub>
