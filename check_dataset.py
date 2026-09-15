from datasets import load_from_disk

print("Đang mở dataset V3...")

dataset = load_from_disk(
    "data/legal_train_v3"
)

print("\n==============================")
print("THÔNG TIN DATASET")
print("==============================")

print(dataset)
print("Số mẫu:", len(dataset))
print("Các cột:", dataset.column_names)

print("\n==============================")
print("MẪU ĐẦU TIÊN")
print("==============================")

print(dataset[0]["conversations"])