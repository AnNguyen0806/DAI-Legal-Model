import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Kết nối Qdrant
client = QdrantClient("http://localhost:6333")
COLLECTION_NAME = "legal_docs"

# 1. Ép xóa hoàn toàn collection cũ
try:
    client.delete_collection(collection_name=COLLECTION_NAME)
    print("Đã xóa collection cũ.")
except Exception:
    pass

# 2. Tạo mới collection
client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
)

print("Đang tải model nhúng...")
model = SentenceTransformer('bkai-foundation-models/vietnamese-bi-encoder')

print("Đang đọc file cleaned_data.xlsx...")
df = pd.read_excel('cleaned_data.xlsx')

points = []
for index, row in df.iterrows():
    thu_tuc = str(row.get('Tên thủ tục hành chính', '')).strip()
    linh_vuc = str(row.get('Lĩnh vực', '')).strip()
    ho_so = str(row.get('Thành phần hồ sơ', '')).strip()
    thoi_gian = str(row.get('Thời gian giải quyết', '')).strip()
    le_phi = str(row.get('Lệ phí', '')).strip()
    dia_diem = str(row.get('Địa điểm tiếp nhận hồ sơ trực tiếp (nếu có)', '')).strip()

    content_text = (
        f"Thủ tục: {thu_tuc}. Lĩnh vực: {linh_vuc}.\n"
        f"- Thành phần hồ sơ: {ho_so}\n"
        f"- Thời gian giải quyết: {thoi_gian}\n"
        f"- Lệ phí: {le_phi}\n"
        f"- Địa điểm tiếp nhận: {dia_diem}"
    )

    vector = model.encode(content_text).tolist()

    points.append(
        PointStruct(
            id=index + 1,
            vector=vector,
            payload={
                "thu_tuc": thu_tuc,
                "text": content_text
            }
        )
    )

client.upsert(collection_name=COLLECTION_NAME, points=points)
print(f"✅ ĐÃ NẠP THÀNH CÔNG {len(points)} THỦ TỤC VÀO QDRANT!")