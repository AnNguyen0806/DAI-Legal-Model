import json
import csv
from pathlib import Path


SUPPORTED_EXTENSIONS = {".json", ".jsonl", ".csv"}

QUESTION_KEYS = [
    "instruction",
    "question",
    "prompt",
    "input",
    "query",
]

ANSWER_KEYS = [
    "output",
    "answer",
    "response",
    "completion",
]


def load_records(dataset_path: str):
    path = Path(dataset_path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset không tồn tại: {path}")

    suffix = path.suffix.lower()

    if suffix == ".jsonl":
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

    if suffix == ".json":
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            # Hỗ trợ dạng {"data": [...]}
            if isinstance(data.get("data"), list):
                return data["data"]

            # Hỗ trợ dataset chỉ có một record
            return [data]

        raise ValueError("JSON phải chứa object hoặc list.")

    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))

    raise ValueError(
        f"Định dạng không được hỗ trợ: {suffix}. "
        f"Chỉ hỗ trợ: {SUPPORTED_EXTENSIONS}"
    )


def find_value(record: dict, possible_keys: list):
    for key in possible_keys:
        if key in record:
            value = record[key]

            if value is not None and str(value).strip():
                return str(value).strip()

    return None


def validate_record(record: dict, index: int):
    errors = []

    if not isinstance(record, dict):
        return [f"Record #{index}: không phải object/dictionary."]

    question = find_value(record, QUESTION_KEYS)
    answer = find_value(record, ANSWER_KEYS)

    if not question:
        errors.append(
            f"Record #{index}: thiếu instruction/question/prompt/query."
        )

    if not answer:
        errors.append(
            f"Record #{index}: thiếu output/answer/response/completion."
        )

    return errors


def validate_dataset(dataset_path: str):
    print("=" * 60)
    print("AUTO FINE-TUNING - DATASET VALIDATOR")
    print("=" * 60)

    path = Path(dataset_path)

    print(f"Dataset: {path}")
    print()

    try:
        records = load_records(dataset_path)
    except Exception as e:
        print("❌ LOAD DATASET FAILED")
        print(f"Lỗi: {e}")
        return False

    total = len(records)

    print(f"Số lượng records: {total}")

    if total == 0:
        print("❌ DATASET RỖNG")
        return False

    errors = []

    for index, record in enumerate(records, 1):
        record_errors = validate_record(record, index)
        errors.extend(record_errors)

    valid_records = total - len(
        set(
            error.split(":", 1)[0]
            for error in errors
        )
    )

    print(f"Records hợp lệ: {valid_records}")
    print(f"Lỗi phát hiện: {len(errors)}")
    print()

    if errors:
        print("❌ DATASET KHÔNG HỢP LỆ")
        print()
        print("Một số lỗi:")

        for error in errors[:20]:
            print(f"  - {error}")

        if len(errors) > 20:
            print(
                f"  ... và {len(errors) - 20} lỗi khác."
            )

        return False

    print("✅ DATASET HỢP LỆ")
    print()
    print("Dataset đủ điều kiện chuyển sang bước:")
    print("→ Dataset Formatter")
    print("→ Auto Fine-Tuning")

    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "Cách dùng:\n"
            "python dataset_validator.py <dataset_path>"
        )
        sys.exit(1)

    dataset_path = sys.argv[1]

    success = validate_dataset(dataset_path)

    sys.exit(0 if success else 1)