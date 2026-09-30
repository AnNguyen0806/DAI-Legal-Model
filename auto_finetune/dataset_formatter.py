import json
import random
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "datasets" / "current"

QUESTION_KEYS = [
    "instruction",
    "question",
    "prompt",
    "query",
]

INPUT_KEYS = [
    "input",
    "context",
    "details",
]

ANSWER_KEYS = [
    "output",
    "answer",
    "response",
    "completion",
]


def load_jsonl(path):
    records = []

    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):
            line = line.strip()

            if not line:
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"JSONL lỗi tại dòng {line_number}: {e}"
                )

    return records


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    if isinstance(data, dict) and isinstance(data.get("data"), list):
        return data["data"]

    if isinstance(data, dict):
        return [data]

    raise ValueError("JSON không chứa dữ liệu hợp lệ.")


def load_csv(path):
    import csv

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        return list(csv.DictReader(f))


def load_dataset(path):
    suffix = path.suffix.lower()

    if suffix == ".jsonl":
        return load_jsonl(path)

    if suffix == ".json":
        return load_json(path)

    if suffix == ".csv":
        return load_csv(path)

    raise ValueError(
        f"Không hỗ trợ định dạng {suffix}. "
        "Hỗ trợ: .jsonl, .json, .csv"
    )


def find_value(record, keys):
    for key in keys:
        if key in record:
            value = record[key]

            if value is not None:
                value = str(value).strip()

                if value:
                    return value

    return ""


def normalize_record(record):
    instruction = find_value(record, QUESTION_KEYS)
    input_text = find_value(record, INPUT_KEYS)
    output = find_value(record, ANSWER_KEYS)

    if not instruction:
        raise ValueError(
            "Record thiếu instruction/question/prompt/query."
        )

    if not output:
        raise ValueError(
            "Record thiếu output/answer/response/completion."
        )

    return {
        "instruction": instruction,
        "input": input_text,
        "output": output,
    }


def save_jsonl(records, path):
    with path.open(
        "w",
        encoding="utf-8"
    ) as f:

        for record in records:
            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                )
                + "\n"
            )


def format_dataset(dataset_path):
    dataset_path = Path(dataset_path)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy dataset: {dataset_path}"
        )

    print("=" * 60)
    print("AUTO FINE-TUNING - DATASET FORMATTER")
    print("=" * 60)
    print(f"Input: {dataset_path}")
    print()

    # ---------------------------------------------------------
    # 1. LOAD
    # ---------------------------------------------------------

    records = load_dataset(dataset_path)

    print(f"Records ban đầu: {len(records)}")

    if not records:
        raise ValueError("Dataset rỗng.")

    # ---------------------------------------------------------
    # 2. NORMALIZE
    # ---------------------------------------------------------

    normalized = []

    for index, record in enumerate(records, 1):
        try:
            normalized_record = normalize_record(record)
            normalized.append(normalized_record)

        except Exception as e:
            raise ValueError(
                f"Lỗi tại record #{index}: {e}"
            )

    print(f"Records sau chuẩn hóa: {len(normalized)}")

    # ---------------------------------------------------------
    # 3. SHUFFLE
    # ---------------------------------------------------------

    random.Random(42).shuffle(normalized)

    # ---------------------------------------------------------
    # 4. SPLIT
    # ---------------------------------------------------------

    total = len(normalized)

    train_size = int(total * 0.80)
    validation_size = int(total * 0.10)

    # Đảm bảo luôn có test
    if total >= 10:
        test_size = total - train_size - validation_size
    else:
        test_size = max(
            1,
            total - train_size - validation_size
        )

    train_records = normalized[:train_size]

    validation_end = train_size + validation_size

    validation_records = normalized[
        train_size:validation_end
    ]

    test_records = normalized[
        validation_end:
    ]

    # ---------------------------------------------------------
    # 5. CREATE OUTPUT
    # ---------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    train_path = OUTPUT_DIR / "train.jsonl"
    validation_path = OUTPUT_DIR / "validation.jsonl"
    test_path = OUTPUT_DIR / "test.jsonl"

    save_jsonl(
        train_records,
        train_path
    )

    save_jsonl(
        validation_records,
        validation_path
    )

    save_jsonl(
        test_records,
        test_path
    )

    # ---------------------------------------------------------
    # 6. RESULT
    # ---------------------------------------------------------

    print()
    print("DATASET FORMAT HOÀN TẤT")
    print("-" * 60)

    print(f"Total      : {total}")
    print(f"Train      : {len(train_records)}")
    print(f"Validation : {len(validation_records)}")
    print(f"Test       : {len(test_records)}")

    print()
    print("Output:")

    print(f"  {train_path}")
    print(f"  {validation_path}")
    print(f"  {test_path}")

    print()
    print("Format:")
    print("  instruction")
    print("  input")
    print("  output")

    print()
    print("✅ DATASET READY FOR AUTO FINE-TUNING")


if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:
        print(
            "Cách dùng:"
        )

        print(
            "python auto_finetune\\dataset_formatter.py "
            "<dataset_path>"
        )

        sys.exit(1)

    try:
        format_dataset(sys.argv[1])

    except Exception as e:
        print()
        print("❌ FORMAT DATASET FAILED")
        print(f"Lỗi: {e}")
        sys.exit(1)