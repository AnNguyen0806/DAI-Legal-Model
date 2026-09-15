import pandas as pd
from datasets import load_from_disk
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer


# ==========================================
# CONFIG
# ==========================================

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "legal_docs"

DATASET_PATH = r"D:\DAI-Legal-Model\data\dichvucong_procedures"

START_ID = 100000


# ==========================================
# CONNECT QDRANT
# ==========================================

print("=" * 60)
print("IMPORT DỊCH VỤ CÔNG → QDRANT")
print("=" * 60)

client = QdrantClient(QDRANT_URL)

print("Đang kiểm tra Qdrant...")

info = client.get_collection(COLLECTION_NAME)

print("Collection:", COLLECTION_NAME)
print("Points hiện tại:", info.points_count)


# ==========================================
# LOAD DATASET
# ==========================================

print("\nĐang load dataset...")

dataset = load_from_disk(DATASET_PATH)

print("Số lượng:", len(dataset))
print("Các cột:", dataset.column_names)


# ==========================================
# LOAD EMBEDDING MODEL
# ==========================================

print("\nĐang load embedding model...")

model = SentenceTransformer(
    "bkai-foundation-models/vietnamese-bi-encoder"
)

print("Embedding model OK")


# ==========================================
# CREATE POINTS
# ==========================================

print("\nĐang tạo embeddings...")

points = []

for index, row in enumerate(dataset):

    procedure_name = str(
        row.get("procedure_name", "")
    ).strip()

    profile_components = str(
        row.get("profile_components", "")
    ).strip()

    execution_steps = str(
        row.get("execution_steps", "")
    ).strip()

    fees = str(
        row.get("fees", "")
    ).strip()

    legal_basis = str(
        row.get("legal_basis", "")
    ).strip()

    results = str(
        row.get("results", "")
    ).strip()

    agencies = str(
        row.get("executing_agencies", "")
    ).strip()

    content_text = f"""
Thủ tục: {procedure_name}

Thành phần hồ sơ:
{profile_components}

Trình tự thực hiện:
{execution_steps}

Phí, lệ phí:
{fees}

Căn cứ pháp lý:
{legal_basis}

Kết quả:
{results}

Cơ quan thực hiện:
{agencies}
""".strip()

    vector = model.encode(
        content_text
    ).tolist()

    points.append(
        PointStruct(
            id=START_ID + index,
            vector=vector,
            payload={
                "thu_tuc": procedure_name,
                "text": content_text,
                "source": "tmquan/dichvucong-gov-vn",
            }
        )
    )

    if len(points) >= 100:

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

        print(
            f"Đã import {index + 1}/{len(dataset)}"
        )

        points = []


# ==========================================
# REMAINING POINTS
# ==========================================

if points:

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )


# ==========================================
# CHECK
# ==========================================

info = client.get_collection(
    COLLECTION_NAME
)

print("\n")
print("=" * 60)
print("IMPORT HOÀN TẤT!")
print("=" * 60)

print(
    "Tổng points hiện tại:",
    info.points_count
)

print("=" * 60)