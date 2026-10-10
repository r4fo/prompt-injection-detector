# Prompt Injection Detector

Binary NLP classification project for detecting prompt-injection attacks in email content.

## Task

The project classifies each email as:

- `0 = SAFE`
- `1 = PROMPT_INJECTION`

The final pipeline starts from raw E2A email data, performs reproducible parsing and cleaning, creates leakage-safe train/validation/test splits, and benchmarks classical ML, neural networks, and Transformer models.

## Dataset

The project uses raw/semi-structured E2A benchmark components:

- E2A prompt-injection emails
- E2A matched benign controls
- SpamAssassin benign ham emails included in the E2A phishing package
- NotInject hard-negative controls

Raw candidate composition:

| Source | Class | Candidate rows |
|---|---:|---:|
| E2A prompt injection | 1 | 2,776 |
| E2A matched benign controls | 0 | 200 |
| SpamAssassin ham | 0 | 1,500 |
| NotInject | 0 | 339 |
| **Total** |  | **4,815** |

After parsing, validation, conflict checking, and exact-text deduplication:

- **3,937 final examples**
- **2,014 SAFE**
- **1,923 PROMPT_INJECTION**
- **878 exact duplicate model inputs removed**

## Preprocessing

`scripts/clean_data.py` performs the full preprocessing pipeline:

1. Extracts the raw ZIP files.
2. Parses `.eml` messages.
3. Decodes subjects.
4. Extracts plain-text MIME content.
5. Converts HTML to text.
6. Extracts supported PDF attachment text.
7. Preserves prompt-injection wording and obfuscation.
8. Standardizes labels and metadata.
9. Uses only benign ham rows from the phishing package.
10. Removes empty records.
11. Removes conflicting exact-text labels if present.
12. Removes exact duplicate model inputs.
13. Preserves `group_id` for leakage-safe splitting.
14. Generates `prompt_injection_clean.csv`.

## Leakage Prevention

E2A contains multiple structural renderings of the same underlying attack payload. A random row split could leak variants of the same attack across train and test.

The project therefore uses a **group-aware split**:

- 70% training
- 15% validation
- 15% testing

Final split sizes:

- Train: **2,740**
- Validation: **608**
- Test: **589**

## Models

- Multinomial Naive Bayes
- Logistic Regression
- CNN
- BiLSTM
- DistilBERT (`distilbert-base-uncased`)
- DeBERTa (`microsoft/deberta-v3-small`)

JEV was tested manually on a small 10-example sample, but it was excluded from the final benchmark because the full API benchmark requires paid credits.

## Evaluation Metrics

Primary ranking metric:

- **Prompt-injection F1-score**

Also reported:

- Accuracy
- Precision
- Recall
- Macro-F1

Recall is an important secondary metric because a false negative means a real prompt-injection attack was classified as SAFE.

## Final Benchmark

The following results use the same fixed 589-example held-out test split:

| Model | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| **BiLSTM** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| Logistic Regression | 0.9983 | 1.0000 | 0.9966 | 0.9983 |
| DistilBERT | 0.9983 | 1.0000 | 0.9966 | 0.9983 |
| CNN | 0.9983 | 1.0000 | 0.9966 | 0.9983 |
| DeBERTa | 0.9949 | 0.9932 | 0.9966 | 0.9949 |
| Naive Bayes | 0.9932 | 0.9864 | **1.0000** | 0.9932 |

**BiLSTM is the top-performing completed method** on the fixed held-out test set.

## Repository Structure

```text
prompt-injection-detector/
├── README.md
├── LICENSE
├── requirements.txt
├── DATA_SOURCES.md
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── splits/
├── scripts/
│   ├── clean_data.py
│   └── create_splits.py
├── notebooks/
│   └── final_project.ipynb
├── results/
└── contributions/
```

## Reproducibility

Create the cleaned dataset from the raw archives with `scripts/clean_data.py`.
Then create the exact group-aware train/validation/test split with:

```bash
python scripts/create_splits.py
```

The raw source archives belong in `data/raw/`. The generated fixed split files belong in `data/splits/`.

## Team Contributions

Each team member must add a file using:

```text
contributions/STUDENT_NAME_STUDENT_ID_GITHUB_USERNAME.md
```

The contribution description should match the member's actual work and Git history.

## License and Attribution

Repository code is distributed under Apache License 2.0.

Raw datasets retain their original licenses and attribution requirements. See `DATA_SOURCES.md`.
