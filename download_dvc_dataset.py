from datasets import load_dataset

print("Đang tải dataset thủ tục hành chính...")

dataset = load_dataset(
    "tmquan/dichvucong-gov-vn",
    "procedures",
    split="train"
)

print("\n==============================")
print("DATASET DỊCH VỤ CÔNG")
print("==============================")

print(dataset)
print("Số lượng:", len(dataset))
print("Các cột:")
print(dataset.column_names)

print("\nMẫu đầu tiên:")
print(dataset[0])

dataset.save_to_disk(
    "data/dichvucong_procedures"
)

print("\n==============================")
print("ĐÃ TẢI THÀNH CÔNG!")
print("==============================")
print("Lưu tại:")
print("D:\\DAI-Legal-Model\\data\\dichvucong_procedures")