from pathlib import Path
import json
import html
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"


def load_json(path):
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def safe(value):
    return html.escape(str(value))


def generate_full_report():
    RESULTS.mkdir(exist_ok=True)

    integrity_history = [
        item for item in load_json(RESULTS / "audit_history.json")
        if item.get("analysis_type", "").lower() == "integrity"
    ]
    leakage_history = [
        item for item in load_json(RESULTS / "audit_history.json")
        if item.get("analysis_type", "").lower() == "leakage"
    ]

    anomaly = load_json(RESULTS / "anomaly_summary.json")
    benchmark = load_json(
        RESULTS / "benchmark" / "fault_injection_summary.json"
    )

    expression_path = ROOT / "data/processed/GSE10072_expression.csv"
    metadata_path = ROOT / "data/processed/GSE10072_metadata.csv"

    expression = pd.read_csv(expression_path, index_col=0)
    metadata = pd.read_csv(metadata_path)

    integrity = integrity_history[-1]["summary"] if integrity_history else {}
    leakage = leakage_history[-1]["summary"] if leakage_history else {}

    pca_variance = anomaly.get("pca_explained_variance", [])
    pca_percent = sum(pca_variance) * 100 if pca_variance else None

    benchmark_metrics = benchmark.get("per_check_metrics", [])

    metric_rows = "".join(
        "<tr>"
        f"<td>{safe(row.get('check', ''))}</td>"
        f"<td>{safe(row.get('precision', ''))}</td>"
        f"<td>{safe(row.get('recall', ''))}</td>"
        f"<td>{safe(row.get('f1_score', ''))}</td>"
        "</tr>"
        for row in benchmark_metrics
    )

    html_report = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OmicsGuard AI - Scientific Audit Report</title>
<style>
body {{
    font-family: Arial, sans-serif;
    max-width: 1050px;
    margin: 35px auto;
    padding: 0 24px;
    color: #202938;
    line-height: 1.6;
    background: #f5f7fa;
}}
header, section {{
    background: white;
    padding: 25px;
    margin-bottom: 20px;
    border-radius: 10px;
    border: 1px solid #e1e6ed;
}}
h1, h2 {{ color: #17365d; }}
h1 {{ margin-bottom: 5px; }}
.subtitle {{ color: #64748b; }}
.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
}}
.metric {{
    background: #edf4fb;
    padding: 15px;
    border-radius: 8px;
}}
.metric strong {{
    display: block;
    font-size: 25px;
    color: #17365d;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
}}
th, td {{
    border: 1px solid #dce2e9;
    padding: 10px;
    text-align: left;
}}
th {{ background: #edf2f7; }}
.note {{
    background: #fff8e7;
    padding: 14px;
    border-left: 4px solid #d69e2e;
}}
footer {{
    color: #64748b;
    text-align: center;
    padding: 15px;
}}
@media print {{
    body {{ background: white; margin: 0; max-width: none; }}
    header, section {{ break-inside: avoid; box-shadow: none; }}
    .no-print {{ display: none; }}
}}
</style>
</head>
<body>

<header>
<h1>OmicsGuard AI</h1>
<div class="subtitle">Bioinformatics Dataset Integrity and ML Reliability Auditor</div>
<h2>Scientific Audit Report</h2>
<p><strong>Dataset:</strong> GSE10072</p>
<p><strong>Platform:</strong> GPL96 - Affymetrix Human Genome U133A</p>
<p><strong>Report generated:</strong> Current report generation time</p>
<button class="no-print" onclick="window.print()">Print / Save as PDF</button>
</header>

<section>
<h2>1. Dataset Overview</h2>
<div class="grid">
<div class="metric"><strong>{len(expression):,}</strong>Samples</div>
<div class="metric"><strong>{expression.shape[1]:,}</strong>Expression features</div>
<div class="metric"><strong>{len(metadata):,}</strong>Metadata records</div>
<div class="metric"><strong>{int(expression.isna().sum().sum())}</strong>Missing expression values</div>
</div>
<p>The report uses the processed GSE10072 expression and metadata files.</p>
<p>GEO metadata reports RMA-based normalization. The OmicsGuard ingestion pipeline reads and formats the processed matrix; it does not independently perform RMA normalization.</p>
</section>

<section>
<h2>2. Dataset Integrity Audit</h2>
<p>Five checks are implemented: missing values, duplicate sample IDs, duplicate probe IDs, constant features and expression-metadata alignment.</p>
<div class="grid">
<div class="metric"><strong>{safe(integrity.get('passed', 'Not recorded'))}</strong>Passed</div>
<div class="metric"><strong>{safe(integrity.get('warnings', 'Not recorded'))}</strong>Warnings</div>
<div class="metric"><strong>{safe(integrity.get('failed', 'Not recorded'))}</strong>Failed</div>
<div class="metric"><strong>{safe(integrity.get('skipped', 'Not recorded'))}</strong>Skipped</div>
</div>
<p>Latest recorded integrity history entry is used for this summary.</p>
<p><strong>Interpretation:</strong> Passing checks indicate that the tested structural conditions were satisfied. Metadata alignment does not establish biological correctness or metadata completeness.</p>
</section>

<section>
<h2>3. Anomaly Detection and PCA</h2>
<div class="grid">
<div class="metric"><strong>{safe(anomaly.get('total_samples', 'Not recorded'))}</strong>Total samples</div>
<div class="metric"><strong>{safe(anomaly.get('potential_anomalies', 'Not recorded'))}</strong>Potential anomalies</div>
<div class="metric"><strong>{safe(anomaly.get('flagged_percentage', 'Not recorded'))}%</strong>Flagged</div>
<div class="metric"><strong>{f'{pca_percent:.2f}%' if pca_percent is not None else 'Not recorded'}</strong>Variance in first two PCs</div>
</div>
<p><strong>Method:</strong> {safe(anomaly.get('method', 'Not recorded'))}</p>
<p><strong>Contamination parameter:</strong> {safe(anomaly.get('contamination_parameter', 'Not recorded'))}</p>
<p>{safe(anomaly.get('interpretation', 'Potential outliers require further investigation.'))}</p>
<p class="note">Anomaly flags are statistical screening results. They do not establish that a sample is defective, biologically abnormal or unsuitable for analysis.</p>
</section>

<section>
<h2>4. Controlled Fault-Injection Benchmark</h2>
<div class="grid">
<div class="metric"><strong>{safe(benchmark.get('total_experiments', 'Not recorded'))}</strong>Total experiments</div>
<div class="metric"><strong>{safe(benchmark.get('detected_defects', 'Not recorded'))}/{safe(benchmark.get('injected_defect_experiments', 'Not recorded'))}</strong>Defects detected</div>
<div class="metric"><strong>{float(benchmark.get('detection_rate', 0))*100:.1f}%</strong>Detection rate</div>
<div class="metric"><strong>{safe(benchmark.get('mean_runtime_seconds', 'Not recorded'))} s</strong>Mean runtime</div>
</div>
<h3>Per-check metrics</h3>
<table>
<tr><th>Check</th><th>Precision</th><th>Recall</th><th>F1-score</th></tr>
{metric_rows}
</table>
<p><strong>Clean baseline passed:</strong> {safe(benchmark.get('clean_baseline_passed', 'Not recorded'))}</p>
<p><strong>Unexpected flags:</strong> {safe(benchmark.get('total_unexpected_flags', 'Not recorded'))}</p>
<p class="note">{safe(benchmark.get('note', 'Benchmark limitations were not recorded.'))}</p>
</section>

<section>
<h2>5. Data Leakage Screening</h2>
<div class="grid">
<div class="metric"><strong>{safe(leakage.get('total_samples', 'Not recorded'))}</strong>Total samples</div>
<div class="metric"><strong>{safe(leakage.get('training_samples', 'Not recorded'))}</strong>Training samples</div>
<div class="metric"><strong>{safe(leakage.get('testing_samples', 'Not recorded'))}</strong>Testing samples</div>
<div class="metric"><strong>{safe(leakage.get('passed', 'Not recorded'))}/{safe(leakage.get('total_checks', 'Not recorded'))}</strong>Checks passed</div>
</div>
<p><strong>Split:</strong> {safe(leakage.get('split', 'Not recorded'))}</p>
<p><strong>Random state:</strong> {safe(leakage.get('random_state', 'Not recorded'))}</p>
<p><strong>Training classes:</strong> {safe(leakage.get('training_class_counts', 'Not recorded'))}</p>
<p><strong>Testing classes:</strong> {safe(leakage.get('testing_class_counts', 'Not recorded'))}</p>
<p class="note">This is preliminary leakage screening. Sample overlap within a split created from one dataset does not test external pipeline contamination. Exact duplicate-profile and target-correlation checks do not rule out preprocessing leakage, patient-level leakage, batch effects or other leakage mechanisms.</p>
</section>

<section>
<h2>6. Reproducibility Validation</h2>
<p>A manual repeatability test was performed by running anomaly analysis twice on the same processed expression matrix.</p>
<table>
<tr><th>Output compared</th><th>Observed result</th></tr>
<tr><td>Anomaly predictions</td><td>Identical</td></tr>
<tr><td>Anomaly scores</td><td>Identical</td></tr>
<tr><td>PCA coordinates</td><td>Identical</td></tr>
<tr><td>Flagged samples</td><td>6 in both runs</td></tr>
</table>
<p class="note">This demonstrates repeatability under the tested input, software environment and configuration. It does not guarantee identical results across different software versions, hardware or datasets. This manual test is not stored as an automated audit-history record.</p>
</section>

<section>
<h2>7. Scientific Limitations</h2>
<ul>
<li>The validation uses one GEO dataset, GSE10072.</li>
<li>The fault-injection benchmark uses one injected example per defect type and one clean baseline.</li>
<li>Anomaly detection identifies statistical outliers, not confirmed biological or technical errors.</li>
<li>The PCA first two components represent only the reported proportion of total variance.</li>
<li>Leakage screening is preliminary and does not cover every possible ML pipeline or patient-level leakage mechanism.</li>
<li>Passing integrity checks does not prove biological validity, absence of batch effects or suitability for every downstream analysis.</li>
</ul>
</section>

<section>
<h2>8. Overall Conclusion</h2>
<p>OmicsGuard AI provides a modular workflow for inspecting gene-expression dataset integrity, screening potential anomalies, testing selected leakage signals and evaluating integrity checks through controlled fault injection.</p>
<p>The current GSE10072 results demonstrate the functionality of these modules under the tested conditions. Broader validation across independent datasets and more diverse injected faults is required before making general performance claims.</p>
</section>

<footer>
OmicsGuard AI | Scientific audit report | Research and educational demonstration
</footer>
</body>
</html>
"""

    output = RESULTS / "OmicsGuard_AI_Scientific_Audit_Report.html"
    output.write_text(html_report, encoding="utf-8")

    print("Report generated successfully:")
    print(output)


if __name__ == "__main__":
    generate_full_report()
