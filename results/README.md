# Results

This directory stores the final benchmark and error-analysis outputs from the fixed held-out test split.

## Final benchmark

| Model | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| **BiLSTM** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| Logistic Regression | 0.9983 | 1.0000 | 0.9966 | 0.9983 |
| DistilBERT | 0.9983 | 1.0000 | 0.9966 | 0.9983 |
| CNN | 0.9983 | 1.0000 | 0.9966 | 0.9983 |
| DeBERTa | 0.9949 | 0.9932 | 0.9966 | 0.9949 |
| Naive Bayes | 0.9932 | 0.9864 | 1.0000 | 0.9932 |

The benchmark contains the completed models evaluated on the same fixed held-out test split.

## Files

- `final_benchmark.csv` — completed model comparison.
- `final_error_analysis.csv` — error rows for the current best model.
- `source_error_analysis.csv` — errors grouped by dataset source.
- `surface_error_analysis.csv` — performance by email rendering surface.

Only full held-out test-set results should be treated as official benchmark results.
