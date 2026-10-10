# Fixed Data Splits

The project uses a leakage-safe **70/15/15 group-aware split** based on
`group_id`.

Expected output files:

- `train.csv`
- `validation.csv`
- `test.csv`

Generate them reproducibly with:

```bash
python scripts/create_splits.py
```

With the final cleaned dataset and seed 42, the expected row counts are:

- Train: **2,740**
- Validation: **608**
- Test: **589**

All structural variants belonging to the same underlying group stay in only
one split.
