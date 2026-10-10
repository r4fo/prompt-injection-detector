import argparse
import json
import re
import shutil
import zipfile
from pathlib import Path
from io import BytesIO
from email import policy
from email.parser import BytesParser
from email.header import decode_header, make_header

import pandas as pd
from bs4 import BeautifulSoup
from pypdf import PdfReader


def normalize_text(text):
    """Light normalization without deleting attack vocabulary or obfuscation."""
    if not text:
        return ""
    text = str(text).replace("\x00", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def decode_subject(message):
    raw = message.get("subject", "")
    try:
        return str(make_header(decode_header(raw)))
    except Exception:
        return str(raw)


def decode_text_part(part):
    """Decode one MIME text part as safely as possible."""
    try:
        payload = part.get_payload(decode=True)
        if payload is None:
            content = part.get_content()
            return content if isinstance(content, str) else ""

        charset = part.get_content_charset() or "utf-8"
        try:
            return payload.decode(charset, errors="replace")
        except Exception:
            return payload.decode("utf-8", errors="replace")
    except Exception:
        return ""


def extract_email_text(eml_path):
    """
    Convert a raw .eml into the text given to the classifiers.

    We preserve:
      - Subject text
      - Plain-text MIME parts
      - HTML text (including text hidden by CSS in the raw HTML)
      - PDF attachment text when extractable
      - Other text/* attachments

    We do NOT include labels or threat metadata in model text.
    """
    message = BytesParser(policy=policy.default).parsebytes(Path(eml_path).read_bytes())

    subject = normalize_text(decode_subject(message))
    chunks = []

    for part in message.walk():
        if part.is_multipart():
            continue

        content_type = (part.get_content_type() or "").lower()
        disposition = (part.get_content_disposition() or "").lower()
        filename = part.get_filename() or ""

        if content_type == "text/plain":
            text = normalize_text(decode_text_part(part))
            if text:
                chunks.append(text)

        elif content_type == "text/html":
            raw_html = decode_text_part(part)
            soup = BeautifulSoup(raw_html, "html.parser")
            text = normalize_text(soup.get_text("\n"))
            if text:
                chunks.append(text)

        elif content_type == "application/pdf" or filename.lower().endswith(".pdf"):
            try:
                data = part.get_payload(decode=True)
                if data:
                    reader = PdfReader(BytesIO(data))
                    pdf_text = "\n".join((page.extract_text() or "") for page in reader.pages)
                    pdf_text = normalize_text(pdf_text)
                    if pdf_text:
                        chunks.append(pdf_text)
            except Exception:
                pass

        elif content_type.startswith("text/") and disposition == "attachment":
            text = normalize_text(decode_text_part(part))
            if text:
                chunks.append(text)

    unique_chunks = []
    seen_chunks = set()
    for chunk in chunks:
        if chunk not in seen_chunks:
            seen_chunks.add(chunk)
            unique_chunks.append(chunk)

    pieces = []
    if subject:
        pieces.extend(["SUBJECT:", subject])
    if unique_chunks:
        pieces.extend(["BODY:", "\n".join(unique_chunks)])

    return normalize_text("\n".join(pieces))


def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def extract_zip(zip_path, destination):
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(destination)


def make_record(item, text, label, dataset_source, group_id):
    label_info = item.get("label", {})
    provenance = item.get("provenance", {})

    return {
        "id": item.get("id"),
        "text": text,
        "label": int(label),
        "threat_type": label_info.get("threat_type", "benign" if label == 0 else "prompt_injection"),
        "attack_type": label_info.get("injection_technique", "none") if label == 1 else "none",
        "scenario": label_info.get("scenario", label_info.get("category", "none")),
        "surface": "|".join(item.get("surface", [])),
        "source": provenance.get("source", "unknown"),
        "dataset_source": dataset_source,
        "group_id": str(group_id),
    }


def build_clean_dataset(prompt_zip, phishing_zip, notinject_zip, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    extracted = output_dir / "_extracted_raw"
    if extracted.exists():
        shutil.rmtree(extracted)
    extracted.mkdir(parents=True)

    extract_zip(prompt_zip, extracted)
    extract_zip(phishing_zip, extracted)
    extract_zip(notinject_zip, extracted)

    rows = []

    prompt_manifest = read_jsonl(extracted / "prompt-injection" / "manifest.jsonl")

    for item in prompt_manifest:
        eml_path = extracted / "prompt-injection" / "eml" / Path(item["eml_path"]).name
        text = extract_email_text(eml_path)

        group_id = (
            item.get("provenance", {}).get("base_payload_id")
            or item.get("provenance", {}).get("source_id")
            or item["id"]
        )

        rows.append(
            make_record(
                item=item,
                text=text,
                label=1,
                dataset_source="e2a_prompt_injection",
                group_id=group_id,
            )
        )

    benign_manifest = read_jsonl(
        extracted / "prompt-injection" / "benign" / "manifest.jsonl"
    )

    for item in benign_manifest:
        eml_path = (
            extracted
            / "prompt-injection"
            / "benign"
            / "eml"
            / Path(item["eml_path"]).name
        )
        text = extract_email_text(eml_path)

        group_id = (
            item.get("provenance", {}).get("base_payload_id")
            or item.get("provenance", {}).get("source_id")
            or item["id"]
        )

        rows.append(
            make_record(
                item=item,
                text=text,
                label=0,
                dataset_source="e2a_matched_benign",
                group_id=group_id,
            )
        )

    phishing_manifest = read_jsonl(extracted / "phishing" / "manifest.jsonl")

    for item in phishing_manifest:
        label_info = item.get("label", {})
        if not (
            label_info.get("is_malicious") is False
            and label_info.get("threat_type") == "benign"
        ):
            continue

        eml_path = extracted / "phishing" / "corpus" / Path(item["eml_path"]).name
        text = extract_email_text(eml_path)

        group_id = (
            item.get("provenance", {}).get("source_id")
            or item["id"]
        )

        rows.append(
            make_record(
                item=item,
                text=text,
                label=0,
                dataset_source="spamassassin_ham",
                group_id=group_id,
            )
        )

    notinject_manifest = read_jsonl(extracted / "notinject" / "manifest.jsonl")

    for item in notinject_manifest:
        eml_path = extracted / "notinject" / "eml" / Path(item["eml_path"]).name
        text = extract_email_text(eml_path)

        group_id = (
            item.get("provenance", {}).get("source_id")
            or item["id"]
        )

        rows.append(
            make_record(
                item=item,
                text=text,
                label=0,
                dataset_source="notinject",
                group_id=group_id,
            )
        )

    raw_df = pd.DataFrame(rows)

    report = {
        "candidate_rows": int(len(raw_df)),
        "candidate_safe": int((raw_df["label"] == 0).sum()),
        "candidate_prompt_injection": int((raw_df["label"] == 1).sum()),
        "empty_text_rows": int((raw_df["text"].str.strip() == "").sum()),
    }

    clean_df = raw_df[raw_df["text"].str.strip() != ""].copy()

    label_counts = clean_df.groupby("text")["label"].nunique()
    conflicting_texts = set(label_counts[label_counts > 1].index)
    report["conflicting_text_values"] = int(len(conflicting_texts))

    if conflicting_texts:
        clean_df = clean_df[~clean_df["text"].isin(conflicting_texts)].copy()

    before_dedup = len(clean_df)
    clean_df = clean_df.drop_duplicates(subset=["text"], keep="first").copy()
    report["exact_duplicate_rows_removed"] = int(before_dedup - len(clean_df))

    clean_df = clean_df.reset_index(drop=True)

    if clean_df["text"].duplicated().any():
        raise RuntimeError("Exact duplicate text remains after cleaning.")
    if (clean_df["text"].str.strip() == "").any():
        raise RuntimeError("Empty text remains after cleaning.")
    if not set(clean_df["label"].unique()).issubset({0, 1}):
        raise RuntimeError("Unexpected class labels found.")
    if clean_df.groupby("group_id")["label"].nunique().max() > 1:
        raise RuntimeError("A group_id contains mixed labels.")

    report.update(
        {
            "final_rows": int(len(clean_df)),
            "final_safe": int((clean_df["label"] == 0).sum()),
            "final_prompt_injection": int((clean_df["label"] == 1).sum()),
            "unique_groups": int(clean_df["group_id"].nunique()),
            "source_distribution": {
                str(k): int(v)
                for k, v in clean_df["dataset_source"].value_counts().to_dict().items()
            },
        }
    )

    csv_path = output_dir / "prompt_injection_clean.csv"
    report_path = output_dir / "cleaning_report.json"

    clean_df.to_csv(csv_path, index=False)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    shutil.rmtree(extracted, ignore_errors=True)

    print(json.dumps(report, indent=2))
    print(f"\nSaved cleaned dataset to: {csv_path}")
    print(f"Saved cleaning report to:  {report_path}")

    return clean_df, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt_zip", required=True)
    parser.add_argument("--phishing_zip", required=True)
    parser.add_argument("--notinject_zip", required=True)
    parser.add_argument("--output_dir", required=True)
    args = parser.parse_args()

    build_clean_dataset(
        prompt_zip=args.prompt_zip,
        phishing_zip=args.phishing_zip,
        notinject_zip=args.notinject_zip,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
