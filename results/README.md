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

The benchmark contains the completed locally trained models. JEV was tested manually on a small 10-example sample but was excluded from the final benchmark because the full API benchmark requires paid credits.

## Files

- `final_benchmark.csv` — completed model comparison.
- `final_error_analysis.csv` — error rows for the current best model.
- `source_error_analysis.csv` — errors grouped by dataset source.
- `surface_error_analysis.csv` — performance by email rendering surface.
- `deberta_metrics.json` — verified detailed DeBERTa result.

Only full held-out test-set results should be treated as official benchmark results.
