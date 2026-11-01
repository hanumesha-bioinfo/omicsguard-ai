# OmicsGuard AI — Limitations

## 1. Dataset Limitations

OmicsGuard AI currently demonstrates its functionality using one gene-expression dataset: GSE10072.

- The dataset contains 107 samples and 22,283 expression features.
- Results from one dataset may not represent the characteristics of other biological datasets.
- The demonstration does not establish performance across different organisms, platforms, experiments, or sequencing technologies.
- Dataset quality depends on the original experimental design, measurement procedures, and metadata supplied by the data provider.

## 2. Integrity Check Limitations

The integrity module checks missing values, duplicate sample IDs, duplicate probe IDs, constant features, and metadata consistency.

These checks cover selected structural problems only.

- A dataset can pass all implemented checks and still contain incorrect measurements.
- Constant features are flagged as potential issues, but their biological significance requires review.
- Matching sample identifiers do not guarantee that metadata values are scientifically correct.
- The checks do not validate every possible formatting, annotation, or experimental-design problem.

## 3. Anomaly Detection Limitations

PCA and Isolation Forest are used for exploratory anomaly screening.

- An unusual expression profile is not necessarily a defective sample.
- A biologically meaningful subgroup may appear statistically unusual.
- Isolation Forest depends on its contamination parameter and other modelling assumptions.
- PCA is a dimensionality-reduction method and does not establish biological relationships.
- Results may change when datasets, preprocessing methods, or model parameters change.

Anomaly flags should be investigated using sample metadata, experimental records, and biological knowledge.

## 4. Fault-Injection Benchmark Limitations

The current benchmark evaluates five injected defect types using one clean baseline and one example for each defect type.

This is a controlled software demonstration, not a comprehensive benchmark.

- The number of experiments is small.
- The injected defects may not represent all real-world data-quality problems.
- Results do not establish general detection accuracy on unseen datasets.
- Precision, recall, and F1-score from this small benchmark should not be interpreted as broad performance estimates.
- Additional defect patterns, repeated trials, and independent datasets are required for stronger evaluation.

## 5. Machine-Learning Leakage Audit Limitations

The leakage audit screens for sample overlap, duplicate expression profiles, and unusually high target-feature association.

It has important limitations:

- Sample overlap detection depends on available sample identifiers.
- Identical-profile detection may miss similar but non-identical samples.
- High target-feature correlation is a warning, not proof of leakage.
- Correlation screening may identify legitimate biological associations.
- The tool does not inspect the complete model-training pipeline, feature-selection process, or every possible source of leakage.

The audit should be treated as an initial screening step rather than a guarantee of leakage-free machine learning.

## 6. Reporting and Audit History Limitations

Audit history is stored locally in a JSON file.

- It is not a centralized database.
- It does not provide multi-user synchronization.
- Local history may be lost if the file is deleted or the working environment is reset.
- It is not designed as a validated regulatory audit-trail system.

## 7. General Scientific Limitations

OmicsGuard AI is a research-support prototype.

It does not:

- Prove that a dataset is biologically valid.
- Establish causality between genes or biological conditions.
- Replace domain-expert review.
- Guarantee that a machine-learning model is unbiased or generalizable.
- Replace independent experimental validation.

## 8. Future Improvements

Potential future improvements include:

1. Testing with additional GEO datasets and biological platforms.
2. Increasing the number and diversity of fault-injection experiments.
3. Adding more comprehensive metadata and annotation validation.
4. Expanding machine-learning leakage screening.
5. Adding more reproducibility and provenance information.
6. Evaluating performance on independently curated datasets.
7. Improving persistent audit-history storage and reporting.

## 9. Responsible Interpretation

All outputs should be interpreted as technical screening evidence.

A warning or anomaly flag requires investigation. A passing result means only that the implemented check did not detect its target condition.

Scientific conclusions must be supported by appropriate experimental evidence and biological interpretation.