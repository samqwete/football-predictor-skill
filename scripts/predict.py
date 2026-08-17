#!/usr/bin/env python3
"""Football match prediction model.

Computes a weighted home/draw/away probability split and expected scoreline
from six per-factor scores (range -3..+3, home-team perspective) plus goals
and xG inputs. This is the ONLY place weighted arithmetic happens -- the
agent feeds scores here and reports the output faithfully.

Usage:
    predict.py --name "TeamA vs TeamB" \\
        --h2h 1 --form 2 --fitness -1 --homeaway 2 --style 0 --sched -1 \\
        --home-gf 1.9 --home-ga 0.8 --away-gf 1.1 --away-ga 1.5
"""

import argparse
import math
import sys

WEIGHTS = {
    "h2h": 3.0,
    "form": 3.0,
    "fitness": 2.5,
    "homeaway": 2.0,
    "style": 2.0,
    "sched": 1.5,
}


def clamp(x, lo=-3.0, hi=3.0):
    return max(lo, min(hi, x))


def sig(x):
    return 1.0 / (1.0 + math.exp(-x))


def main():
    ap = argparse.ArgumentParser(description="Football match prediction model")
    ap.add_argument("--name", required=True)
    for k in WEIGHTS:
        ap.add_argument(f"--{k}", type=float, default=0.0)
    ap.add_argument("--home-gf", type=float, default=None)
    ap.add_argument("--home-ga", type=float, default=None)
    ap.add_argument("--away-gf", type=float, default=None)
    ap.add_argument("--away-ga", type=float, default=None)
    args = ap.parse_args()

    net = sum(clamp(getattr(args, k)) * w for k, w in WEIGHTS.items())
    max_abs = sum(3.0 * w for w in WEIGHTS.values())

    draw_logit = 0.9 * math.exp(-abs(net) / 14.0)
    home_logit = sig(net * 0.35) * 4.0
    away_logit = 1.0 - home_logit
    home_logit = max(home_logit, 1e-6)
    away_logit = max(away_logit, 1e-6)
    draw_logit = max(draw_logit, 1e-6)
    Z = home_logit + away_logit + draw_logit
    p_home = home_logit / Z
    p_draw = draw_logit / Z
    p_away = away_logit / Z

    if net >= 6.0:
        lean, conf = "Home win (confident)", "High"
    elif net >= 1.5:
        lean, conf = "Home win (lean)", ("Medium" if abs(net) < 4 else "High")
    elif net <= -6.0:
        lean, conf = "Away win (confident)", "High"
    elif net <= -1.5:
        lean, conf = "Away win (lean)", ("Medium" if abs(net) < 4 else "High")
    else:
        lean, conf = "Draw (or value on the draw)", "Low"

    if args.home_gf is not None and args.away_gf is not None:
        exp_home = 0.5 * args.home_gf + 0.5 * (1.4 / max(args.away_ga or 1.0, 0.001)) - 0.1
        exp_away = 0.5 * args.away_gf + 0.5 * (1.4 / max(args.home_ga or 1.0, 0.001)) - 0.1
        exp_home = max(exp_home, 0.0)
        exp_away = max(exp_away, 0.0)
    else:
        shift = net / 14.0
        exp_home = max(1.3 + shift * 2.0, 0.0)
        exp_away = max(1.1 - shift * 2.0, 0.0)

    def nearest_goal(x):
        return max(0, min(6, int(round(x))))

    base_h = nearest_goal(exp_home)
    base_a = nearest_goal(exp_away)
    if base_h == base_a:
        if net > 0.5:
            base_h += 1
        elif net < -0.5:
            base_a += 1

    dominance = min(1.0, abs(net) / 24.0)
    band = round((0.35 + 0.5 * dominance) * 100)

    print(f"Match: {args.name}")
    print(f"Weighted net score: {net:+.2f} (range {max_abs:.0f})")
    print(f"Probabilities: Home {p_home*100:.1f}% | Draw {p_draw*100:.1f}% | Away {p_away*100:.1f}%")
    print(f"Most likely scoreline: {base_h} - {base_a}")
    print(f"Lean: {lean}")
    print(f"Confidence: {conf} (band ~{band}%)")
    print("")
    print("Per-factor scores (home perspective, -3..+3):")
    for k in WEIGHTS:
        print(f"  {k:10s} {getattr(args, k):+.1f}  x {WEIGHTS[k]:.1f} = {getattr(args,k)*WEIGHTS[k]:+.1f}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
