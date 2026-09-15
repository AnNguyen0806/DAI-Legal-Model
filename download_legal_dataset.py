from datasets import load_dataset

print("Đang tải dataset...")

dataset = load_dataset(
    "duyet/vietnamese-legal-instruct",
    split="train"
)

print(dataset)
print("Số lượng mẫu:", len(dataset))

dataset.save_to_disk(
    "data/vietnamese-legal-instruct"
)

print("ĐÃ TẢI DATASET THÀNH CÔNG!")