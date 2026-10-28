"""Render complete P10 calibration tables from saved case records only."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from run_p10_evaluation import _dataset_metrics, _render_dataset

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"eval"/"p10_evaluation_cases.json"
RENDER_ROOT=ROOT/"eval"/"rendered_p10"


def _family_levels(cases:list[dict])->list[str]:
    lines=["", "### Per-family confidence-level accuracy and coverage", "",
        "| Family | Model | Level | n | Coverage | Top-1 accuracy |",
        "|---|---|---|---:|---:|---:|"]
    for family in sorted({case["scenario"] for case in cases}):
        group=[case for case in cases if case["scenario"]==family]
        for model in ("calibrated","constant","margin_only"):
            counts={level:[] for level in ("high","medium","low","insufficient_evidence")}
            for case in group:
                counts[case["levels"][model]].append(case)
            for level,rows in counts.items():
                accuracy=(sum(bool(row["correct"]) for row in rows)/len(rows)) if rows else None
                lines.append(f"| {family} | {model} | {level} | {len(rows)} | {len(rows)/len(group):.3f} | {accuracy:.3f} |" if accuracy is not None else f"| {family} | {model} | {level} | 0 | 0.000 | n/a |")
    return lines


def main()->None:
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output_dir=RENDER_ROOT/stamp
    output_dir.mkdir(parents=True,exist_ok=False)
    output=output_dir/"results.md"
    cases_output=output_dir/"cases.json"
    data=json.loads(INPUT.read_text(encoding="utf-8"))
    chunks=["# P10 Calibrated Confidence Evaluation — Complete Tables", "",
        f"Run commit: `{data['commit']}`  ",f"Config SHA-256: `{data['config_sha256']}`  ",
        f"Confidence model SHA-256: `{data['model_sha256']}`  ",
        "Primary: seeds 72–91 (280 cases). Secondary: seeds 52–71 (280 cases), not used for fitting. Holdout seeds 7–9 were not run.", ""]
    final={"commit":data["commit"],"config_sha256":data["config_sha256"],"model_sha256":data["model_sha256"]}
    for key,title in (("fresh","Primary fresh evaluation: seeds 72–91"),("secondary","Secondary evaluation: seeds 52–71")):
        cases=data[key]["cases"]; metrics=_dataset_metrics(cases); final[key]={"cases":cases,"metrics":metrics}
        chunks.extend(_render_dataset(title,cases,metrics))
        chunks.extend(_family_levels(cases))
    chunks += ["## Required plain statements", "",
        "On seeds 72–91, calibrated Brier is 0.0831 versus 0.0850 for each baseline, while calibrated ECE is 0.0289 versus 0.0284 for each baseline. The model is not consistently better calibrated: its Brier improvement is small and its ECE is slightly worse.",
        "Withholding low and insufficient-evidence cases gives 90.8% top-1 at 66.1% coverage versus 90.7% top-1 without withholding; this is a negligible observed increase, not a meaningful demonstrated gain.",
        "All evaluated probabilities fall in the top reliability bin and the model emits no medium or low cases; silent_cause is sharply overconfident. Treat these synthetic calibration results as weak evidence, not operational calibration.", ""]
    output.write_text("\n".join(chunks),encoding="utf-8")
    cases_output.write_text(json.dumps(final,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(f"Rendered saved P10 case records to {output.relative_to(ROOT)}")


if __name__=="__main__": main()
