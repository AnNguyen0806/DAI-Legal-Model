from datasets import load_from_disk, concatenate_datasets

DATASET_PATH = "data/vietnamese-legal-instruct"

print("Đang đọc dataset...")

dataset = load_from_disk(DATASET_PATH)

print("Tổng số mẫu:", len(dataset))

# Những loại dữ liệu phù hợp nhất với Legal Assistant
TARGET_TYPES = [
    "qa_practical",
    "explain_simple",
    "summarize",
    "key_provisions",
    "legal_basis",
    "scope",
    "amounts",
    "meta_status",
]

datasets = []

for qa_type in TARGET_TYPES:

    print(f"\nĐang lấy loại: {qa_type}")

    subset = dataset.filter(
        lambda x: x["qa_type"] == qa_type
    )

    print("Số mẫu:", len(subset))

    if len(subset) > 0:
        datasets.append(subset)


print("\nĐang gộp dataset...")

combined = concatenate_datasets(datasets)

print("Tổng trước khi chọn:", len(combined))

# Trộn dữ liệu
combined = combined.shuffle(seed=42)

# Với RTX 4070 12GB, bắt đầu bằng 2000 mẫu
MAX_SAMPLES = 2000

if len(combined) > MAX_SAMPLES:
    combined = combined.select(
        range(MAX_SAMPLES)
    )

print("\n================================")
print("DATASET TRAIN V3")
print("================================")
print("Số mẫu:", len(combined))
print("================================")

# Lưu dataset mới
combined.save_to_disk(
    "data/legal_train_v3"
)

print("\nĐÃ TẠO DATASET LEGAL TRAIN V3!")
print("Vị trí:")
print("D:\\DAI-Legal-Model\\data\\legal_train_v3")