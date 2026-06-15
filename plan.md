# Plan

Paper 83 `robot_skill_half_life_under_shift` is in the 2026-06-15 ICLR-main submission-readiness audit pass.

Execution plan:

1. Rerun the full deterministic skill-survival benchmark from source.
2. Audit all main, ablation, stress, pairwise, and negative-case outputs.
3. Apply the ICLR-main evidence gate without overclaiming local synthetic evidence.
4. Preserve the terminal decision as `KILL_ARCHIVE` unless the proposed method decisively beats conformal risk gating and its central ablations degrade.
5. Rebuild `C:/Users/wangz/Downloads/83.pdf` only, update root reports, commit, push, and verify the public GitHub repo.
