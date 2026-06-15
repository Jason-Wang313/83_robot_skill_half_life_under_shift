# Paper 83 ICLR-Main Submission-Readiness Execution Plan

Date: 2026-06-15

Paper: `83_robot_skill_half_life_under_shift`

Target venue standard: ICLR main conference, with an evidence-first gate. The paper can be advanced only if the rebuilt results show real, reproducible separation from strong baselines and the mechanism survives ablation. Otherwise it must remain `STRONG_REVISE` or `KILL_ARCHIVE`.

## Current State

The repository currently reports a v4 terminal decision of `KILL_ARCHIVE`. The existing claim is that a skill half-life scheduler should decide when to execute, probe, refresh, or abstain under physical shift. The prior audit found that the proposed scheduler is statistically indistinguishable from a strong conformal risk gate on the hard split, while the `minus_per_skill_survival` ablation improves the main success metric. The current evidence is local synthetic simulation, not hardware or a recognized high-fidelity robotics benchmark.

## Execution Order

1. Verify repository hygiene before touching results.
   - Confirm the worktree is clean.
   - Confirm the GitHub remote exists and is public.
   - Record the pre-audit commit.

2. Re-run the full evidence generator from source.
   - Compile-check `src/run_experiment.py`.
   - Run `python src/run_experiment.py`.
   - Preserve all generated CSVs, figures, and `results/summary.txt`.

3. Audit evidence completeness.
   - Confirm seven seeds are present.
   - Confirm all methods, skills, splits, ablations, and stress axes are represented.
   - Confirm row counts and schemas for rollout, seed metric, aggregate metric, pairwise, ablation, stress, and negative-case files.

4. Apply the ICLR-main decision gate.
   - Require proposed-method improvement over the strongest non-oracle baseline on combined micro-shift success and success AUC.
   - Require unsafe failures to improve without hiding cost or abstention.
   - Require paired seed-level effects that are not swallowed by uncertainty.
   - Require ablations to degrade when the claimed mechanism is removed.
   - Require stress tests to support the same conclusion under drift, noise, mode flips, probe cost, and combined stress.

5. Decide honestly.
   - If all gates pass but evidence remains local synthetic only, mark at most `STRONG_REVISE`.
   - If baseline separation or mechanism ablation fails, keep or strengthen `KILL_ARCHIVE`.
   - Do not claim ICLR-main readiness without hardware or recognized high-fidelity benchmark evidence.

6. Update the paper and child documentation.
   - Make `README.md`, `child_status.md`, `plan.md`, audit docs, attack log, readiness decision, hostile reviewer response, and version log match the new evidence.
   - Add a terminal audit document with exact row counts, seed coverage, statistical conclusions, and PDF hash.

7. Build and verify the PDF.
   - Build `paper/main.pdf` with LaTeX.
   - Copy only the numbered PDF to `C:/Users/wangz/Downloads/83.pdf`.
   - Do not copy any PDF to the visible Desktop.
   - Scan logs for LaTeX/BibTeX warnings that affect submission quality.

8. Update root reports.
   - Update `GLOBAL_POOL_STATUS.md`, `BATCH_STATUS.md`, `SUBMISSION_STATUS.md`, `MASTER_REPORT.md`, and `MASTER_SUBMISSION_REPORT.md`.
   - Mark Paper 83 with the final terminal decision, commit hash, PDF hash, GitHub URL, and concise evidence.

9. Commit, push, and verify.
   - Commit only Paper 83 files inside its child repo.
   - Push `main` to the public GitHub repo.
   - Verify local `HEAD` equals `origin/main`.
   - Verify `C:/Users/wangz/Downloads/83.pdf` exists and `C:/Users/wangz/Desktop/83.pdf` does not.

## Expected Outcome Risk

The likely outcome is `KILL_ARCHIVE`, because the existing v4 evidence already reports a negligible paired advantage over conformal risk gating and an ablation contradiction. The audit will still run end-to-end; the decision will be evidence-bound, not assumed.
