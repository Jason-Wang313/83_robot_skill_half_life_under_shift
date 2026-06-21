import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAPER = ROOT / "paper"
DOCS = ROOT / "docs"


METHOD_LABELS = {
    "frozen_behavior_clone": "Frozen BC",
    "domain_randomized_clone": "Domain rand.",
    "fixed_interval_refresh": "Fixed refresh",
    "online_finetune": "Online FT",
    "scalar_uncertainty_gate": "Scalar gate",
    "conformal_risk_gate": "Conformal",
    "ensemble_uncertainty_gate": "Ensemble",
    "hazard_regression_refresh": "Hazard reg.",
    "bayesian_skill_survival": "Bayes survival",
    "cvar_lifetime_guard": "CVaR guard",
    "skill_half_life_scheduler_v5": "Half-life v5",
    "oracle_shift_aware_scheduler": "Oracle",
}

PLOT_METHODS = [
    "frozen_behavior_clone",
    "domain_randomized_clone",
    "fixed_interval_refresh",
    "online_finetune",
    "scalar_uncertainty_gate",
    "conformal_risk_gate",
    "ensemble_uncertainty_gate",
    "bayesian_skill_survival",
    "cvar_lifetime_guard",
    "skill_half_life_scheduler_v5",
    "oracle_shift_aware_scheduler",
]


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ascii_clean(text):
    text = (text or "").replace("–", "-").replace("—", "-").replace("“", '"').replace("”", '"').replace("’", "'")
    return text.encode("ascii", "ignore").decode("ascii")


def tex_escape(text):
    text = ascii_clean(str(text))
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in text)


def metric_lookup(rows, split, method, metric):
    for row in rows:
        if row.get("split") == split and row.get("method") == method and row.get("metric") == metric:
            return float(row["mean"]), float(row["ci95"])
    raise KeyError((split, method, metric))


def fmt_pm(mean, ci):
    return f"{mean:.3f} +/- {ci:.3f}"


def count_rows(name):
    return len(read_csv(RESULTS / name))


def bib_key(i):
    return f"pool83_{i:02d}"


def write_references():
    fixed = [
        {
            "key": "skill_pomdp_shift",
            "title": "Planning under Distribution Shifts with Causal POMDPs",
            "year": "2026",
            "note": "local pool record; http://arxiv.org/abs/2602.23545v2",
        },
        {
            "key": "uncertainty_safety_gating",
            "title": "Uncertainty-Calibrated Safety Gating for Vision-Language-Action Manipulation Under Domain Shift",
            "year": "2026",
            "note": "local pool record; https://doi.org/10.3390/s26103140",
        },
        {
            "key": "motor_skill_transfer",
            "title": "Learning and Transfer of Complex Motor Skills in Virtual Reality: A Perspective Review",
            "year": "2019",
            "note": "local pool record; https://doi.org/10.1186/s12984-019-0587-8",
        },
        {
            "key": "interface_dynamics_exosuits",
            "title": "Physical Interface Dynamics Alter How Robotic Exosuits Augment Human Movement",
            "year": "2017",
            "note": "local pool record; https://doi.org/10.1186/s12984-017-0247-9",
        },
        {
            "key": "robotic_table_tennis",
            "title": "Robotic Table Tennis: A Case Study into a High Speed Learning System",
            "year": "2023",
            "note": "local pool record; http://arxiv.org/abs/2309.03315v2",
        },
        {
            "key": "manipulation_force_profiles",
            "title": "Adaptation of Manipulation Skills in Physical Contact with the Environment to Reference Force Profiles",
            "year": "2015",
            "note": "local pool record",
        },
    ]
    entries = []
    for item in fixed:
        entries.append(
            "\n".join(
                [
                    f"@misc{{{item['key']},",
                    "  author={Local Prior Work Pool},",
                    f"  title={{{tex_escape(item['title'])}}},",
                    f"  year={{{item['year']}}},",
                    f"  note={{{tex_escape(item['note'])}}}",
                    "}",
                ]
            )
        )

    pool_rows = read_csv(DOCS / "deep_read_250.csv")[:30]
    for i, row in enumerate(pool_rows, start=1):
        title = tex_escape(row.get("title", "Untitled prior work"))
        authors = ascii_clean(row.get("authors") or "Local Prior Work Pool")
        authors = " and ".join([tex_escape(a.strip()) for a in re.split(r";", authors) if a.strip()]) or "Local Prior Work Pool"
        year_raw = ascii_clean(row.get("year") or "")
        match = re.search(r"(19|20)\d{2}", year_raw)
        year = match.group(0) if match else "2026"
        venue = tex_escape(row.get("venue") or "prior-work pool")
        link = tex_escape(row.get("doi") or row.get("url") or row.get("arxiv_id") or "local pool record")
        entries.append(
            "\n".join(
                [
                    f"@misc{{{bib_key(i)},",
                    f"  author={{{authors}}},",
                    f"  title={{{title}}},",
                    f"  year={{{year}}},",
                    f"  note={{{venue}; {link}}}",
                    "}",
                ]
            )
        )
    (PAPER / "references.bib").write_text("\n\n".join(entries) + "\n", encoding="utf-8")
    return [item["key"] for item in fixed], [bib_key(i) for i in range(1, len(pool_rows) + 1)]


def longtable(header, rows, spec, caption, label, fontsize=r"\scriptsize"):
    out = [
        r"\begin{center}",
        fontsize,
        f"\\begin{{longtable}}{{{spec}}}",
        f"\\caption{{{caption}}}\\label{{{label}}}\\\\",
        r"\toprule",
        header + r"\\",
        r"\midrule",
        r"\endfirsthead",
        f"\\caption[]{{{caption} (continued)}}\\\\",
        r"\toprule",
        header + r"\\",
        r"\midrule",
        r"\endhead",
    ]
    out.extend(rows)
    out.extend([r"\bottomrule", r"\end{longtable}", r"\normalsize", r"\end{center}"])
    return "\n".join(out)


def decision_gates(summary_text):
    gates = {}
    in_gate = False
    for line in summary_text.splitlines():
        if line.strip() == "Decision gates:":
            in_gate = True
            continue
        if in_gate and not line.strip():
            break
        if in_gate and ":" in line:
            key, value = line.split(":", 1)
            gates[key.strip()] = value.strip()
    return gates


def main():
    PAPER.mkdir(exist_ok=True)
    fixed_cites, pool_cites = write_references()
    metrics = read_csv(RESULTS / "metrics.csv")
    hard_metrics = read_csv(RESULTS / "hard_aggregate_metrics.csv")
    hard_pairs = read_csv(RESULTS / "hard_aggregate_pairwise_stats.csv")
    ablations = read_csv(RESULTS / "ablation_metrics.csv")
    ablation_seed = read_csv(RESULTS / "ablation_seed_metrics.csv")
    stress = read_csv(RESULTS / "stress_sweep.csv")
    stress_seed = read_csv(RESULTS / "stress_sweep_seed_metrics.csv")
    fixed = read_csv(RESULTS / "fixed_risk_metrics.csv")
    fixed_seed = read_csv(RESULTS / "fixed_risk_seed_metrics.csv")
    fixed_pairs = read_csv(RESULTS / "fixed_risk_pairwise.csv")
    negative = read_csv(RESULTS / "negative_cases.csv")
    prior = read_csv(DOCS / "deep_read_250.csv")[:28]
    summary_text = (RESULTS / "summary.txt").read_text(encoding="utf-8")
    gates = decision_gates(summary_text)

    prop_hard = metric_lookup(hard_metrics, "hard_regime_aggregate", "skill_half_life_scheduler_v5", "goal_success")
    best_ref = gates.get("best_reference", "cvar_lifetime_guard")
    best_ref_label = METHOD_LABELS.get(best_ref, best_ref)
    best_ref_hard = metric_lookup(hard_metrics, "hard_regime_aggregate", best_ref, "goal_success")

    lines = []
    lines.extend(
        [
            r"\documentclass{article}",
            r"\usepackage{iclr2026_conference,times}",
            r"\input{math_commands.tex}",
            r"\usepackage{hyperref}",
            r"\usepackage{url}",
            r"\usepackage{booktabs}",
            r"\usepackage{graphicx}",
            r"\usepackage{array}",
            r"\usepackage{longtable}",
            r"\usepackage{xcolor}",
            r"\hypersetup{colorlinks=false,pdfborder={0 0 1.6},citebordercolor={0 1 0},linkbordercolor={1 0.55 0},urlbordercolor={0 0.45 1}}",
            r"\graphicspath{{../figures/}}",
            r"\newcommand{\methodname}{skill half-life scheduler v5}",
            r"\title{Robot Skill Half-Life Under Physical Shift:\\An Expanded Negative ICLR-Main Readiness Audit}",
            r"\author{Anonymous Authors}",
            r"\begin{document}",
            r"\maketitle",
            r"\begin{abstract}",
            (
                "Robot skills often fail gradually under small physical shifts in friction, payload, compliance, sensing, and contact mode. "
                "This paper asks whether estimating a per-skill deployment half-life can guide execute/probe/refresh/abstain decisions better than strong uncertainty and safety-gating baselines. "
                f"We rebuild the archive into a frozen v5 audit with {count_rows('rollouts.csv'):,} main rollouts, {count_rows('dataset_summary.csv'):,} physical-state records, "
                f"{count_rows('ablation_rollouts.csv'):,} ablation rollouts, {count_rows('stress_sweep_raw.csv'):,} stress rollouts, {count_rows('fixed_risk_raw.csv'):,} fixed-risk rollouts, and {count_rows('negative_cases.csv')} retained negative cases. "
                f"On the predefined hard-regime aggregate, \\methodname{{}} reaches {fmt_pm(*prop_hard)} goal success, while the strongest non-oracle baseline, {tex_escape(best_ref_label)}, reaches {fmt_pm(*best_ref_hard)}. "
                "The paired lower confidence bound is negative, fixed-risk coverage collapses at the 0.05 budget, central ablations contradict the mechanism on contact chatter, and maximum combined stress is dominated by a Bayesian survival baseline. "
                "The correct terminal decision is therefore \\textbf{KILL/ARCHIVE}: the hypothesis remains useful, but this local evidence is not submission-ready for ICLR main."
            ),
            r"\end{abstract}",
        ]
    )

    lines.extend(
        [
            r"\section{Terminal Decision}",
            (
                "\\textbf{Decision: KILL/ARCHIVE for ICLR main.} "
                "The v5 rebuild is much stronger than the old archive: it adds 10 seeds, five skills, eight shift splits, 12 methods, a hard aggregate, strong conservative baselines, fixed-risk deployment, two-split ablations, five stress axes, negative cases, and a 25+ page evidence appendix. "
                "Those additions improve the audit, but they do not rescue the central claim."
            ),
            (
                f"The predefined hard-regime aggregate gives \\methodname{{}} {fmt_pm(*prop_hard)} goal success. "
                f"The strongest non-oracle baseline, {tex_escape(best_ref_label)}, gives {fmt_pm(*best_ref_hard)}. "
                f"The hard-margin gate is {tex_escape(gates.get('hard_margin', 'unknown'))}, and the paired lower bound is {tex_escape(gates.get('paired_lower95_vs_best', 'unknown'))}. "
                "The negative conclusion is not a presentation choice; it is the frozen result."
            ),
            (
                "This paper therefore optimizes for hostile-review survival rather than optimistic polish. "
                "It records where half-life modeling helps, where it fails, and what evidence would be needed before making a real robot-learning submission claim."
            ),
            r"\section{Problem Setting}",
            (
                "A deployed robot skill has an execution age. "
                "A policy that was reliable immediately after training or calibration may degrade as gripper friction changes, payload mass drifts, compliance differs from training, sensors become noisy, or the contact mode flips. "
                "The half-life thesis says that this degradation should be modeled directly as a survival process instead of hidden inside a single uncertainty score."
            ),
            (
                "The idea sits near continual robot learning, safety gating, motor-skill transfer, contact adaptation, and robustness under distribution shift. "
                f"The local prior-work pool includes distribution-shift planning \\citep{{{fixed_cites[0]}}}, calibrated manipulation safety gates \\citep{{{fixed_cites[1]}}}, complex motor-skill transfer \\citep{{{fixed_cites[2]}}}, physical interface dynamics \\citep{{{fixed_cites[3]}}}, high-speed robotic learning \\citep{{{fixed_cites[4]}}}, and contact-force adaptation \\citep{{{fixed_cites[5]}}}. "
                "These neighbors make the contribution fragile: if half-life scheduling is just another conservative risk gate, then the mechanism is not novel enough."
            ),
            r"\section{Skill Survival Model}",
            (
                "For skill $s$, deployment age $a$, observed physical shift $z$, and hidden physical state $x$, let $H_s(x)$ be the latent half-life and let $\\hat H_s(z)$ be the estimator used by the scheduler. "
                "The idealized survival curve is $S_s(a\\mid x)=\\exp(-\\log(2)a/H_s(x))$. "
                "A refresh resets age, a probe pays a smaller cost to reduce uncertainty, and abstention preserves safety at the cost of coverage."
            ),
            (
                "\\textbf{Definition 1 (stale execution).} "
                "An execution is stale when the policy executes at age $a>H_s(x)$ without a refresh, probe, or abstention that would have altered the action. "
                "Stale execution is not identical to failure: a stale skill can still succeed, but it is operating beyond the model's survival boundary."
            ),
            (
                "\\textbf{Lemma 1 (half-life refresh threshold).} "
                "Under exponential survival, requiring survival at least $\\tau$ implies a refresh before age $a > -\\hat H_s\\log(\\tau)/\\log(2)$. "
                "Thus a conservative lower estimate of $\\hat H_s$ yields an earlier refresh boundary. "
                "The lemma is elementary, but it clarifies why a survival model can be audited with refresh age, stale execution, and half-life error."
            ),
            (
                "\\textbf{Proposition 1 (probe/refresh dominance under calibrated hazard).} "
                "If two actions have equal nominal success and cost, and one action has weakly lower calibrated hazard upper bound and weakly higher post-probe survival estimate, then the v5 decision rule weakly prefers it. "
                "This is a design property of the local scheduler. "
                "It is not a proof of safety on real hardware."
            ),
            (
                "\\textbf{Negative identifiability theorem.} "
                "If all skill-specific hazards are generated by a single latent scalar shift and the observations cannot separate friction, mass, compliance, and contact mode, then per-skill survival parameters are not identifiable from deployment outcomes alone. "
                "In that regime a scalar, conformal, Bayesian, or CVaR gate can match or beat the explicit half-life decomposition. "
                "The ablation results below show this is not a theoretical nuisance; it appears in the local contact-chatter split."
            ),
            r"\section{Frozen Experimental Protocol}",
            (
                "The protocol was written before execution in \\texttt{docs/paper83\\_expanded\\_submission\\_plan\\_20260621.md}. "
                "The main evaluation uses 10 seeds, five skills, 64 deployment steps, eight physical-shift splits, and 12 methods. "
                "The hard-regime aggregate includes every non-nominal split: friction, payload mass, compliance, sensor noise, contact-mode chatter, probe-cost shift, and combined micro-shift."
            ),
            (
                "The baselines are intentionally uncomfortable: conformal risk gating, ensemble uncertainty, a hazard-regression refresher, Bayesian skill survival, a CVaR lifetime guard, and an oracle upper bound. "
                "The decision gate marks \\texttt{STRONG\\_REVISE} only if v5 beats the strongest non-oracle baseline by at least 0.03 absolute hard-regime success, has a positive paired lower bound, does not worsen safety, passes ablation necessity, preserves fixed-risk coverage at budget 0.05, and is not dominated at maximum combined stress."
            ),
        ]
    )

    hard_rows = []
    for method in PLOT_METHODS:
        success = metric_lookup(hard_metrics, "hard_regime_aggregate", method, "goal_success")
        late = metric_lookup(hard_metrics, "hard_regime_aggregate", method, "late_success")
        unsafe = metric_lookup(hard_metrics, "hard_regime_aggregate", method, "unsafe_failure")
        stale = metric_lookup(hard_metrics, "hard_regime_aggregate", method, "stale_execution")
        safety = metric_lookup(hard_metrics, "hard_regime_aggregate", method, "safety_utility")
        hard_rows.append(
            f"{tex_escape(METHOD_LABELS[method])} & {fmt_pm(*success)} & {late[0]:.3f} & {unsafe[0]:.4f} & {stale[0]:.4f} & {safety[0]:.3f}\\\\"
        )
    lines.extend(
        [
            r"\section{Main Hard-Regime Results}",
            (
                "Table~\\ref{tab:hard-main} is the central result. "
                "Half-life v5 beats weak static and scalar gates, but loses to the CVaR lifetime guard and Bayesian survival baseline. "
                "The loss is small enough to be scientifically interesting and large enough to block a positive main-conference claim."
            ),
            longtable(
                r"Method & Goal success & Late & Unsafe & Stale & Safety utility",
                hard_rows,
                r"p{0.24\linewidth}ccccc",
                "Hard-regime aggregate over seven non-nominal splits.",
                "tab:hard-main",
            ),
            r"\begin{figure}[t]",
            r"\centering",
            r"\includegraphics[width=0.98\linewidth]{half_life_hard_success.png}",
            r"\caption{Hard-regime aggregate goal success. Half-life v5 is useful but not the strongest non-oracle method.}",
            r"\label{fig:hard-success}",
            r"\end{figure}",
            r"\begin{figure}[t]",
            r"\centering",
            r"\includegraphics[width=0.98\linewidth]{half_life_failure_modes_v5.png}",
            r"\caption{Unsafe and stale execution rates. Conservative baselines erase stale execution and reduce unsafe failures, but success still decides the gate.}",
            r"\label{fig:failure-modes}",
            r"\end{figure}",
        ]
    )

    pair_rows = []
    for row in hard_pairs:
        if row["reference"] == best_ref:
            pair_rows.append(
                f"{tex_escape(row['metric'])} & {row['mean_diff']} & {row['ci95']} & {row['lower95']} & {row['target_better_seeds']}/{row['seeds']}\\\\"
            )
    lines.extend(
        [
            r"\section{Paired Hard-Aggregate Test}",
            (
                f"The predefined paired test compares Half-life v5 with {tex_escape(best_ref_label)}, selected only because it is the strongest non-oracle hard-aggregate baseline. "
                "The target loses all 10 paired seeds on goal success and late success. "
                "Its lower confidence bound is negative for goal success and safety utility."
            ),
            longtable(
                r"Metric & Mean diff & CI95 & Lower95 & Better seeds",
                pair_rows,
                r"p{0.30\linewidth}cccc",
                f"Paired seed differences for Half-life v5 minus {tex_escape(best_ref_label)}.",
                "tab:paired",
            ),
            r"\begin{figure}[t]",
            r"\centering",
            r"\includegraphics[width=0.96\linewidth]{half_life_decay_curves_v5.png}",
            r"\caption{Deployment-age bins on combined micro-shift. The proposal is competitive, but the stronger survival/CVaR baselines remain uncomfortable.}",
            r"\label{fig:decay}",
            r"\end{figure}",
        ]
    )

    ablation_rows = []
    for row in ablations:
        ablation_rows.append(
            f"{tex_escape(row['split'])} & {tex_escape(row['ablation'])} & {row['goal_success']} & {row['ci95_success']} & {row['unsafe_failure']} & {row['stale_execution']} & {row['half_life_error']} & {row['safety_utility']}\\\\"
        )
    lines.extend(
        [
            r"\section{Ablations}",
            (
                "The ablation gate fails. "
                "On combined micro-shift, the full method is the best success variant, but several removals improve cost or half-life error. "
                "On contact-mode chatter, removing per-skill survival, removing shift decomposition, and removing skill-age state beat the full method on success. "
                "This is exactly the identifiability failure the theory section warned about."
            ),
            longtable(
                r"Split & Ablation & Success & CI95 & Unsafe & Stale & HLE & Safety utility",
                ablation_rows,
                r"p{0.17\linewidth}p{0.27\linewidth}cccccc",
                "Ablations on combined micro-shift and contact-mode chatter.",
                "tab:ablations",
            ),
            r"\begin{figure}[t]",
            r"\centering",
            r"\includegraphics[width=0.98\linewidth]{half_life_ablation_v5.png}",
            r"\caption{Combined micro-shift ablations. The full method is strongest there, but the second ablation split contradicts mechanism necessity.}",
            r"\label{fig:ablation}",
            r"\end{figure}",
        ]
    )

    stress_focus = [r for r in stress if r["stress_axis"] == "combined"]
    stress_rows = []
    for row in stress_focus:
        stress_rows.append(
            f"{row['stress_level']} & {tex_escape(METHOD_LABELS.get(row['method'], row['method']))} & {row['goal_success']} & {row['ci95_success']} & {row['unsafe_failure']} & {row['stale_execution']} & {row['half_life_error']} & {row['safety_utility']}\\\\"
        )
    lines.extend(
        [
            r"\section{Stress Tests}",
            (
                "The stress sweep varies drift rate, sensor noise, contact-mode chatter, probe cost, and combined physical shift. "
                "At maximum combined stress, Half-life v5 reaches 0.7919 success while Bayesian skill survival reaches 0.8388. "
                "The proposal therefore fails the maximum-stress gate."
            ),
            r"\begin{figure}[t]",
            r"\centering",
            r"\includegraphics[width=0.98\linewidth]{half_life_stress_sweep_v5.png}",
            r"\caption{Combined stress sweep across seven levels. Half-life v5 is dominated by a Bayesian survival baseline at the hardest level.}",
            r"\label{fig:stress}",
            r"\end{figure}",
            longtable(
                r"Level & Method & Success & CI95 & Unsafe & Stale & HLE & Safety utility",
                stress_rows,
                r"cp{0.25\linewidth}cccccc",
                "Combined stress sweep.",
                "tab:stress-combined",
            ),
        ]
    )

    fixed_rows = []
    for row in fixed:
        fixed_rows.append(
            f"{tex_escape(row['split'])} & {row['risk_budget']} & {tex_escape(METHOD_LABELS.get(row['method'], row['method']))} & {row['coverage']} & {row['fixed_risk_success']} & {row['executed_success']} & {row['false_safe_rate']} & {row['unsafe_failure']}\\\\"
        )
    lines.extend(
        [
            r"\section{Fixed-Risk Deployment}",
            (
                "A survival paper has to answer a deployment question: can the method execute only when estimated unsafe stale-execution risk is below a fixed budget? "
                "At budget 0.05, all non-oracle methods abstain on both hard fixed-risk splits. "
                "This is safer than false confidence, but it is not a deployable result. "
                "The fixed-risk gate therefore fails."
            ),
            r"\begin{figure}[t]",
            r"\centering",
            r"\includegraphics[width=0.96\linewidth]{half_life_fixed_risk_v5.png}",
            r"\caption{Fixed-risk deployment at budget 0.05 on combined micro-shift. Non-oracle coverage collapses to zero.}",
            r"\label{fig:fixed-risk}",
            r"\end{figure}",
            longtable(
                r"Split & Budget & Method & Coverage & Fixed success & Executed success & False-safe & Unsafe",
                fixed_rows,
                r"p{0.18\linewidth}cp{0.18\linewidth}ccccc",
                "Fixed-risk deployment over two splits and four budgets.",
                "tab:fixed-risk",
            ),
        ]
    )

    neg_rows = []
    for row in negative:
        neg_rows.append(
            f"{tex_escape(row['source'])} & {tex_escape(row['split'])} & {tex_escape(row['skill'])} & {tex_escape(row['method'])} & {tex_escape(row['failure_label'])} & {row['risk_upper']} & {tex_escape(row['lesson'])}\\\\"
        )
    lines.extend(
        [
            r"\section{Negative Cases}",
            (
                "The negative cases are retained to prevent accidental optimism. "
                "They include v5 failures, strong-baseline successes, ablation counterexamples, and fixed-risk abstentions. "
                "They show that the local benchmark can expose a weakness rather than only create flattering figures."
            ),
            longtable(
                r"Source & Split & Skill & Method & Outcome & Risk & Lesson",
                neg_rows,
                r"p{0.15\linewidth}p{0.16\linewidth}p{0.13\linewidth}p{0.18\linewidth}p{0.15\linewidth}cp{0.21\linewidth}",
                "Retained negative cases.",
                "tab:negative-cases",
            ),
        ]
    )

    split_rows = []
    for split in sorted({r["split"] for r in metrics}):
        for method in PLOT_METHODS:
            success = metric_lookup(metrics, split, method, "goal_success")
            late = metric_lookup(metrics, split, method, "late_success")
            unsafe = metric_lookup(metrics, split, method, "unsafe_failure")
            hle = metric_lookup(metrics, split, method, "half_life_error")
            safety = metric_lookup(metrics, split, method, "safety_utility")
            split_rows.append(
                f"{tex_escape(split)} & {tex_escape(METHOD_LABELS[method])} & {fmt_pm(*success)} & {late[0]:.3f} & {unsafe[0]:.4f} & {hle[0]:.3f} & {safety[0]:.3f}\\\\"
            )
    full_pair_rows = []
    for row in hard_pairs:
        full_pair_rows.append(
            f"{tex_escape(METHOD_LABELS.get(row['reference'], row['reference']))} & {tex_escape(row['metric'])} & {row['mean_diff']} & {row['ci95']} & {row['lower95']} & {row['target_better_seeds']}/{row['seeds']}\\\\"
        )
    full_stress_rows = []
    for row in stress:
        full_stress_rows.append(
            f"{tex_escape(row['stress_axis'])} & {row['stress_level']} & {tex_escape(METHOD_LABELS.get(row['method'], row['method']))} & {row['goal_success']} & {row['ci95_success']} & {row['unsafe_failure']} & {row['stale_execution']} & {row['safety_utility']}\\\\"
        )
    stress_seed_rows = []
    for row in stress_seed:
        stress_seed_rows.append(
            f"{tex_escape(row['stress_axis'])} & {row['stress_level']} & {tex_escape(METHOD_LABELS.get(row['method'], row['method']))} & {row['seed']} & {row['goal_success']} & {row['unsafe_failure']} & {row['stale_execution']} & {row['safety_utility']}\\\\"
        )
    ablation_seed_rows = []
    for row in ablation_seed:
        ablation_seed_rows.append(
            f"{tex_escape(row['split'])} & {tex_escape(row['method'])} & {row['seed']} & {row['goal_success']} & {row['unsafe_failure']} & {row['half_life_error']} & {row['total_cost']} & {row['safety_utility']}\\\\"
        )
    fixed_seed_rows = []
    for row in fixed_seed:
        fixed_seed_rows.append(
            f"{tex_escape(row['split'])} & {row['risk_budget']} & {tex_escape(METHOD_LABELS.get(row['method'], row['method']))} & {row['seed']} & {row['coverage']} & {row['fixed_risk_success']} & {row['executed_success']} & {row['false_safe_rate']}\\\\"
        )
    fixed_pair_rows = []
    for row in fixed_pairs:
        fixed_pair_rows.append(
            f"{tex_escape(row['split'])} & {row['risk_budget']} & {tex_escape(METHOD_LABELS.get(row['reference'], row['reference']))} & {tex_escape(row['metric'])} & {row['mean_diff']} & {row['ci95']} & {row['lower95']}\\\\"
        )
    prior_rows = []
    for i, row in enumerate(prior, start=1):
        citation = pool_cites[i - 1] if i - 1 < len(pool_cites) else pool_cites[0]
        prior_rows.append(
            f"\\citep{{{citation}}} & {tex_escape(row.get('title', ''))} & {tex_escape(row.get('year', ''))} & {tex_escape(row.get('venue', ''))} & {tex_escape(row.get('hostile_score', ''))}\\\\"
        )

    lines.extend(
        [
            r"\section{Reviewer Attack Surface}",
            (
                "A hostile reviewer can make several fair attacks. "
                "First, the strongest baselines already encode conservative lifetime risk and win the hard aggregate. "
                "Second, fixed-risk deployment has zero non-oracle coverage at the strict 0.05 budget. "
                "Third, contact-mode chatter ablations contradict mechanism necessity. "
                "Fourth, all evidence remains local and synthetic, with no real robot, no recognized simulator benchmark, and no externally trained baselines."
            ),
            (
                "The strongest defense is modest: the repository now gives a reproducible, high-scale diagnostic of a plausible mechanism. "
                "That is valuable for deciding what to build next, but it is not enough for ICLR main."
            ),
            r"\section{Reproducibility}",
            r"\begin{verbatim}",
            r"python src\run_experiment.py",
            r"python scripts\generate_manuscript.py",
            r"cd paper",
            r"pdflatex -interaction=nonstopmode -halt-on-error main.tex",
            r"bibtex main",
            r"pdflatex -interaction=nonstopmode -halt-on-error main.tex",
            r"pdflatex -interaction=nonstopmode -halt-on-error main.tex",
            r"python ..\scripts\validate_submission_artifacts.py",
            r"\end{verbatim}",
            (
                "The canonical numbered PDF is \\texttt{C:/Users/wangz/Downloads/83.pdf}. "
                "No PDF should be copied to the visible Desktop. "
                "The validator checks row counts, page count, link settings, unresolved references, artifact placement, and SHA256."
            ),
            r"\section{Limitations}",
            (
                "The limitations are submission-critical rather than decorative. "
                "The benchmark is deterministic and local; it may miss real contact dynamics, perception failures, controller instabilities, and data-collection bias. "
                "The learned and Bayesian baselines are lightweight analytic policies rather than trained neural systems. "
                "The prior-work pool is noisy and must be manually vetted before a real submission. "
                "Most importantly, fixed-risk coverage collapse means the current risk estimates are not useful deployment certificates."
            ),
            r"\section{Conclusion}",
            (
                "Robot skill half-life remains an appealing way to think about gradual policy degradation under physical shift. "
                "The expanded v5 audit shows that survival-aware scheduling can beat weak static baselines, but it loses to CVaR/Bayesian survival baselines, fails paired and stress gates, fails fixed-risk coverage, and is contradicted by contact-chatter ablations. "
                "The honest action is \\textbf{KILL/ARCHIVE}, not submission."
            ),
            r"\appendix",
            r"\section{Full Split Metrics}",
            longtable(
                r"Split & Method & Success & Late & Unsafe & HLE & Safety utility",
                split_rows,
                r"p{0.20\linewidth}p{0.20\linewidth}ccccc",
                "Per-split metrics for all methods.",
                "tab:split-metrics",
            ),
            r"\section{Full Hard-Aggregate Pairwise Table}",
            longtable(
                r"Reference & Metric & Mean diff & CI95 & Lower95 & Better seeds",
                full_pair_rows,
                r"p{0.22\linewidth}p{0.22\linewidth}cccc",
                "All hard-regime aggregate paired seed differences for Half-life v5.",
                "tab:full-pairwise",
            ),
            r"\section{Full Stress Sweep Across All Axes}",
            longtable(
                r"Axis & Level & Method & Success & CI95 & Unsafe & Stale & Safety utility",
                full_stress_rows,
                r"p{0.13\linewidth}cp{0.20\linewidth}ccccc",
                "All stress axes, levels, and methods.",
                "tab:full-stress",
            ),
            r"\section{Stress Seed-Level Metrics}",
            longtable(
                r"Axis & Level & Method & Seed & Success & Unsafe & Stale & Safety utility",
                stress_seed_rows,
                r"p{0.13\linewidth}cp{0.20\linewidth}ccccc",
                "Seed-level stress metrics.",
                "tab:stress-seeds",
            ),
            r"\section{Ablation Seed-Level Metrics}",
            longtable(
                r"Split & Ablation & Seed & Success & Unsafe & HLE & Cost & Safety utility",
                ablation_seed_rows,
                r"p{0.16\linewidth}p{0.27\linewidth}cccccc",
                "Seed-level ablation metrics.",
                "tab:ablation-seeds",
            ),
            r"\section{Fixed-Risk Seed-Level Metrics}",
            longtable(
                r"Split & Budget & Method & Seed & Coverage & Fixed success & Executed success & False-safe",
                fixed_seed_rows,
                r"p{0.17\linewidth}cp{0.18\linewidth}ccccc",
                "Seed-level fixed-risk metrics.",
                "tab:fixed-risk-seeds",
            ),
            r"\section{Fixed-Risk Pairwise Metrics}",
            longtable(
                r"Split & Budget & Reference & Metric & Mean diff & CI95 & Lower95",
                fixed_pair_rows,
                r"p{0.17\linewidth}cp{0.20\linewidth}p{0.18\linewidth}ccc",
                "Fixed-risk pairwise differences for Half-life v5.",
                "tab:fixed-pairwise",
            ),
            r"\section{Full Prior-Work Pressure Table}",
            (
                "The table below is a pressure table from the local shared pool, not a claim that every item is a direct baseline. "
                "Its purpose is to make the surrounding novelty risk visible and to avoid pretending the half-life framing lives in an empty literature."
            ),
            longtable(
                r"Citation & Title & Year & Venue & Hostile score",
                prior_rows,
                r"p{0.12\linewidth}p{0.42\linewidth}cp{0.25\linewidth}c",
                "Hostile prior-work pressure from the local deep-read pool.",
                "tab:prior-work",
            ),
            r"\bibliographystyle{iclr2026_conference}",
            r"\bibliography{references}",
            r"\end{document}",
        ]
    )
    (PAPER / "main.tex").write_text("\n\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {PAPER / 'main.tex'} and {PAPER / 'references.bib'}")


if __name__ == "__main__":
    main()
