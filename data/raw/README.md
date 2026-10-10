# Raw Data

The project was built from three raw E2A benchmark archives:

- `prompt-injection.zip`
- `phishing.zip`
- `notinject.zip`

These archives are the inputs expected by `scripts/clean_data.py`.

## Large raw archive

`prompt-injection.zip` is approximately **56 MB** and is therefore not committed to this repository because it exceeds GitHub's browser upload limit.

To reproduce the preprocessing pipeline:

1. Obtain the original E2A benchmark archives from the dataset source documented in `DATA_SOURCES.md`.
2. Place the downloaded archives in this directory using these exact names:
   - `prompt-injection.zip`
   - `phishing.zip`
   - `notinject.zip`
3. Run the preprocessing script from the repository root.

```bash
python scripts/clean_data.py \
  --prompt_zip data/raw/prompt-injection.zip \
  --phishing_zip data/raw/phishing.zip \
  --notinject_zip data/raw/notinject.zip \
  --output_dir data/cleaned
```

The repository includes the resulting cleaned dataset and cleaning report so the project can be reviewed without requiring the large raw archive.

The raw source data retains its original attribution and license requirements. See `DATA_SOURCES.md` before redistributing any source archive.
