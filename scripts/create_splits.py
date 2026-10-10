"""Create leakage-safe 70/15/15 train/validation/test splits.

Related email variants share a group_id, so all rows from the same group
must remain in exactly one split.
"""

from pathlib import Path
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split

SEED = 42


def create_group_splits(input_csv: str, output_dir: str) -> None:
    df = pd.read_csv(input_csv)
    df["group_id"] = df["group_id"].astype(str)

    group_table = (
        df.groupby("group_id", as_index=False)
          .agg(label=("label", "first"), n_rows=("id", "size"))
    )

    if group_table.groupby("group_id")["label"].nunique().max() > 1:
        raise ValueError("A group_id contains mixed labels.")

    train_groups, temp_groups = train_test_split(
        group_table,
        test_size=0.30,
        random_state=SEED,
        stratify=group_table["label"],
    )

    validation_groups, test_groups = train_test_split(
        temp_groups,
        test_size=0.50,
        random_state=SEED,
        stratify=temp_groups["label"],
    )

    train_ids = set(train_groups["group_id"])
    validation_ids = set(validation_groups["group_id"])
    test_ids = set(test_groups["group_id"])

    train_df = df[df["group_id"].isin(train_ids)].reset_index(drop=True)
    validation_df = df[df["group_id"].isin(validation_ids)].reset_index(drop=True)
    test_df = df[df["group_id"].isin(test_ids)].reset_index(drop=True)

    assert train_ids.isdisjoint(validation_ids)
    assert train_ids.isdisjoint(test_ids)
    assert validation_ids.isdisjoint(test_ids)

    train_text = set(train_df["text"])
    validation_text = set(validation_df["text"])
    test_text = set(test_df["text"])

    assert train_text.isdisjoint(validation_text)
    assert train_text.isdisjoint(test_text)
    assert validation_text.isdisjoint(test_text)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    train_df.to_csv(out / "train.csv", index=False)
    validation_df.to_csv(out / "validation.csv", index=False)
    test_df.to_csv(out / "test.csv", index=False)

    print(f"Train:      {len(train_df)}")
    print(f"Validation: {len(validation_df)}")
    print(f"Test:       {len(test_df)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/cleaned/prompt_injection_clean.csv",
        help="Cleaned dataset CSV.",
    )
    parser.add_argument(
        "--output_dir",
        default="data/splits",
        help="Directory for train/validation/test CSV files.",
    )
    args = parser.parse_args()
    create_group_splits(args.input, args.output_dir)
