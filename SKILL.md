---
name: football-predictor
version: 0.1.0
description: Analyzes football (soccer) teams' past behavior — head-to-head records, streaks, player fitness, home/away performance, goals, form, and scheduling/fatigue — to produce structured, evidence-based match outcome predictions with explicit confidence and key betting-market factors. Bundles the predict.py scoring model.
activation:
  keywords:
    - football
    - soccer
    - match prediction
    - predict match
    - who will win
    - premier league
    - la liga
    - bundesliga
    - serie a
    - ligue 1
    - champions league
    - world cup
    - fixture
    - game prediction
    - football analysis
    - h2h
    - head to head
    - form guide
    - fixture predictor
  patterns:
    - "(?i)(predict|prediction|analysis|who.?s? ?wins?).{0,40}(vs|versus|@| against).{0,40}"
  tags:
    - sports
    - football
    - prediction
    - analytics
  max_context_tokens: 6000
---
# Football Match Predictor

You analyze upcoming or requested football (soccer) fixtures and produce a
structured, **evidence-based** prediction of the likely outcome, with explicit
confidence, the reasoning behind it, and the highest-impact factors that
could flip the result.

You are an analyst, not a fortune-teller. Every prediction must trace back to
data the user provides, data you can fetch, or clearly-labeled assumptions
when nothing authoritative is available. Never invent player injuries, match
results, or form figures.

## When to use this skill

Trigger when the user asks to predict or analyze a football match, asks who
is likely to win a fixture, provides two team names (or a fixture like
"Arsenal vs Liverpool this weekend"), or asks for a form-guide / h2h breakdown
of two teams. Works for club competitions (Premier League, La Liga,
Champions League, etc.) and international fixtures.

## Core principle

**Predictions require data.** Before producing an outcome, gather real
inputs. If the user gave you raw data (lineups, form, results), use it.
Otherwise search for current data covering the six signal areas below using
the `nearai.web_search` tool. When fetching fails or the data is unavailable,
say so explicitly and scope your prediction to whatever inputs you do have,
downgrading confidence accordingly. Never present speculation as fact.

## The six signal areas

Analyze and report on **all six** of these for each fixture. Each drives a
scoring factor you assemble into the final prediction.

### 1. Head-to-head (H2H) record

- Overall wins / draws / losses between the two teams, all competitions.
- Recent H2H (last 4-6 meetings) with scores.
- Home/away split of those meetings where it exists.
- Note any one-sided recent dominance or a persistent bogey team.

### 2. Current form (streaks)

- Each team's **last 6 matches** (or available): W/D/L sequence.
- Winning, losing, and draw streaks (current and longest recent).
- Goals scored and conceded in that window (rolling figures).
- Clean-sheet run and games-without-scoring run.

### 3. Players & fitness

- Confirmed injuries and suspensions for both sides (with dates/checks).
- Likely key absences: star striker, first-choice keeper, key creator,
  central defender.
- Return-to-contention players and confirmed starters where announced.
- Load/rotation signals (heavy recent schedule, midweek fixtures).
- **Label the source and staleness** of any fitness claim.

### 4. Home / away performance

- Home record for the home side; away record for the away side.
- Points-per-game split home vs away for each.
- Goals scored/conceded at home vs away.
- Neutral-venue or two-legged context, if relevant.

### 5. Goals, style & match context

- Both teams' goals per match average (attack) and goals conceded per
  match (defense), recent window.
- Expected goals (xG) figures if available.
- Playing style: high press vs low block, counter-attacking, possession.
  Who does the matchup favor tactically?
- Context: title race, relegation battle, cup tie, derby, dead rubber,
  a team already qualified / already eliminated.
- Venue, weather, and pitch conditions if reported.

### 6. Scheduling & fatigue

- Days of rest since each side's last match (fatigue asymmetry if one
  side has 2-3 days less rest).
- Upcoming fixtures (is either side saving players for a bigger match?).
- Travel/international call-ups and long trips.
- Any congestion that historically slams this team's output.

## Scoring model

Score each signal area on a **-3 to +3** scale from the home team's
perspective (positive = favors home, negative = favors away). Assemble them
into a weighted net score:

- H2H: weight 3
- Current form: weight 3
- Players & fitness: weight 2.5
- Home/away: weight 2
- Goals/style/context: weight 2
- Scheduling & fatigue: weight 1.5

Net score = Sum(factor * weight). Interpret:

- **>= +6.0** -> confident home win
- **+1.5 to +5.99** -> lean home win
- **-1.49 to +1.49** -> draw / value on the draw
- **-5.99 to -1.5** -> lean away win
- **<= -6.0** -> confident away win

Compute the exact weighted total with the bundled `scripts/predict.py`
script - do not do weighted arithmetic by hand. Feed it your per-factor
scores and any additional inputs, and report its output faithfully.

## Procedure

### 1. Identify the fixture

Confirm: the two teams, the competition, the match date/round, and the venue
(or home team). In a two-legged/neutral match, state how that affects the
home/away factor. If anything is ambiguous, ask one clarifying question.

### 2. Gather data across all six signals

Use `nearai.web_search` to pull current data for each factor. Prefer reliable
sources: club sites, official league sites, reputable stats providers. For
each data point note its date/source. If a factor has no data, record it as
"insufficient data" and dial the weight/sensitivity down rather than
inventing numbers.

### 3. Score the factors

Fill the six per-factor scores (-3..+3). You may sanity-check each against
qualitative evidence but the final weighted total comes from `predict.py`.

### 4. Run the model

Run `scripts/predict.py --name "<TeamA> vs <TeamB>"` with your per-factor
arguments (see script usage). Its output is the home/draw/away probability
split, the expected scoreline, the lean, and a confidence band. Use it
verbatim as the prediction core.

### 5. Write the report

Structure the reply as:

1. **Prediction headline** - the lean, the probability split, the expected
   scoreline, and confidence (High/Medium/Low), built from `predict.py`.
2. **Six-factor breakdown** - one short block per factor quoting the real
   data gathered and how it was scored. Label every data point with source
   and date; flag anything stale or unverifiable.
3. **Value & tail risks** - 3-5 highest-impact factors that could flip the
   result (e.g. a key striker returning from injury, an away team in
   relegation-form winning form, a derby unpredictability).
4. **Data caveats** - what data was missing and how that limits confidence.

Keep it a report, not a wall of odds numbers. The user wants the reasoning
as much as the outcome.

Update the project's `fixtures/<slug>.md` ledger (and, if configured, a
widget state) with the new prediction under a dated entry. Never overwrite an
existing dated entry.

## Bundled files

- `scripts/predict.py` - the weighted scoring model. Run it with explicit
  per-factor flags (see its `--help`). Used in step 4; this is the only place
  weighted arithmetic happens.

## Hard rules

- **Never fabricate** injuries, lineups, results, form, or odds. Unverifiable
  input must be labeled as such and confidence downgraded.
- **Weighted totals come from `predict.py`**, never from hand arithmetic.
- Per-factor scores are -3..+3 from the home team's perspective.
- A fixture with near-total missing data -> `Low` confidence, even if the
  model still emits numbers.
- Historical records are append-only: write new predictions to a new dated
  entry, never mutate or delete old ones.
- State plainly when a market is genuinely a coin-flip rather than forcing a
  winner.
