# football-predictor

IronClaw agent skill **v0.1.0** — evidence-based football (soccer) match prediction.

Analyzes upcoming or requested fixtures across **six signals** and produces a structured, evidence-based outcome prediction with explicit confidence, reasoning, and the highest-impact factors that could flip the result.

## What it does

The skill gathers real data across six signal areas, scores each on a **-3..+3** scale (from the home team's perspective), and assembles them into a weighted net score:

| Signal | Weight |
|--------|-------:|
| Head-to-head (H2H) | 3.0 |
| Current form (streaks) | 3.0 |
| Players & fitness | 2.5 |
| Home / away performance | 2.0 |
| Goals, style & context | 2.0 |
| Scheduling & fatigue | 1.5 |

Net score = Σ(factor × weight). Interpretation:

- **≥ +6.0** → confident home win
- **+1.5 to +5.99** → lean home win
- **−1.49 to +1.49** → draw / value on the draw
- **−5.99 to −1.5** → lean away win
- **≤ −6.0** → confident away win

The weighted total is always computed by the bundled model — never by hand arithmetic.

## Files

- `SKILL.md` — skill definition: activation keywords/patterns, six-signal framework, step-by-step procedure, and hard rules.
- `scripts/predict.py` — weighted home/draw/away probability model; the only place weighted arithmetic happens.

## Usage

Run the model directly (no data-gathering) with `--name` and the six per-factor scores, plus optional goals inputs:

```bash
python3 scripts/predict.py --name "TeamA vs TeamB" \
    --h2h 1 --form 2 --fitness -1 --homeaway 2 --style 0 --sched -1 \
    --home-gf 1.9 --home-ga 0.8 --away-gf 1.1 --away-ga 1.5
```

Flags and defaults:

```
--name        required
--h2h         float, default 0.0
--form        float, default 0.0
--fitness     float, default 0.0
--homeaway    float, default 0.0
--style       float, default 0.0
--sched       float, default 0.0
--home-gf     float, optional
--home-ga     float, optional
--away-gf     float, optional
--away-ga     float, optional
```

Example output:

```
Match: TeamA vs TeamB
Weighted net score: +9.00 (range 42)
Probabilities: Home 89.0% | Draw 11.0% | Away 0.0%
Most likely scoreline: 2 - 1
Lean: Home win (confident)
Confidence: High (band ~54%)
```

## Install as an IronClaw skill

Install the skill from this repository via the ironclaw skill installer (SKILL.md bundle), then activate it to run the bundled `scripts/predict.py` from the workspace.

## License

MIT — see `LICENSE`.