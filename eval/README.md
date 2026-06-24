# Description-triggering eval set

`trigger-eval.json` is the labelled trigger eval for the `proxuma-blog` skill:
20 queries, 10 positives (should fire the skill) + 10 negatives (look-alikes that
should not). It feeds the skill-creator description-optimization loop
(`skill-creator/scripts/run_loop.py`).

## Running it (read this before you run)

Two things will silently zero out the results if you skip them:

1. **`--num-workers 1`.** The eval installs each candidate description as a
   transient command in the *shared* `~/.claude/commands/` dir, all with the
   same description but different unique names. With parallel workers, several
   coexist and a given `claude -p` invokes an arbitrary sibling instead of the
   one its detector is watching, so every positive reads as a miss
   (`recall=0%`). One worker = one transient command alive at a time = correct
   measurement.

2. **Move the live skill aside during the run.** If `~/.claude/skills/proxuma-blog`
   is installed while the loop runs, positive queries trigger the *real* skill
   instead of the transient candidate and the detector misses. Point
   `--skill-path` at a copy and move the live dir out of `~/.claude/skills/`
   for the duration, then restore it.

```bash
cd ~/.claude/skills/skill-creator
python3 -m scripts.run_loop \
  --skill-path <copy-of-skill> \
  --eval-set <this-dir>/trigger-eval.json \
  --model opus \
  --num-workers 1 --max-iterations 5 --runs-per-query 3 --holdout 0.4 \
  --results-dir <out> --verbose --report none
```

Trust the **held-out (test)** score, not train. Adopt a rewrite only if it beats
the current description on the held-out split.

## Last run (2026-06-24, M1 Pro, opus)

12 train / 8 test. All 5 iterations tied at **7/8 held-out**; the original
description was selected as best. No rewrite beat it on held-out (a couple
improved train to 11/12 — overfitting). Description kept as-is.
