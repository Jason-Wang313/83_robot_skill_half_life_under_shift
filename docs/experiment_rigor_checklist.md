# Experiment Rigor Checklist

## v2 Synthetic Rigor
- [x] Multiple seeds.
- [x] Error bars.
- [x] Stronger synthetic baselines.
- [x] Ablations.
- [x] Stress tests.
- [x] Negative cases.

## v4 Local Skill-Survival Rigor
- [x] Paper-specific sequential deployment benchmark.
- [x] Four skills and five physical-shift splits.
- [x] Eight methods including conformal risk gating and oracle upper bound.
- [x] Seed-level paired comparisons.
- [x] Ablation suite for half-life mechanism.
- [x] Stress sweeps for drift, sensor noise, mode flips, probe cost, and combined stress.
- [x] Negative cases documented.

## ICLR Main Bar
- [ ] Real-robot validation.
- [ ] High-fidelity simulator benchmark.
- [ ] Implemented learned model.
- [ ] Implemented real competing baselines.
- [ ] Manual related-work synthesis.
- [ ] Paper-specific qualitative figures.

Decision: fail ICLR main empirical-rigor gate because the v4 result is negative and still local-only; archive.
