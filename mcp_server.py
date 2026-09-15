import os

from mcp.server import MCPServer
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


# ==========================================
# MCP SERVER
# ==========================================

mcp = MCPServer("DAI Legal MCP")


# ==========================================
# CONFIG
# ==========================================

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "legal_docs"

EMBEDDING_MODEL = "bkai-foundation-models/vietnamese-bi-encoder"


# ==========================================
# QDRANT
# ==========================================

client = QdrantClient(QDRANT_URL)

print("Đang load embedding model...", file=__import__("sys").stderr)

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)

print("Embedding model OK", file=__import__("sys").stderr)


# ==========================================
# SEARCH
# ==========================================

def search_qdrant(query: str, limit: int = 10):

    vector = embedding_model.encode(
        query
    ).tolist()

    result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=limit,
        with_payload=True,
    )

    return result.points


# ==========================================
# TOOL: SEARCH LEGAL DOCUMENTS
# ==========================================

@mcp.tool()
def search_legal_documents(query: str) -> list[str]:

    """
    Tìm kiếm thủ tục hành chính và văn bản pháp luật
    liên quan đến câu hỏi của người dùng.
    """

    query_lower = query.lower().strip()

    points = search_qdrant(
        query,
        limit=10
    )

    # ==========================================
    # ƯU TIÊN TÊN THỦ TỤC KHỚP TRUY VẤN
    # ==========================================

    exact_matches = []
    other_matches = []

    for point in points:

        payload = point.payload or {}

        procedure_name = str(
            payload.get(
                "thu_tuc",
                ""
            )
        ).strip()

        procedure_lower = procedure_name.lower()

        text = str(
            payload.get(
                "text",
                ""
            )
        ).strip()

        # Nếu tên thủ tục xuất hiện trong câu hỏi
        if (
            procedure_lower
            and procedure_lower in query_lower
        ):

            exact_matches.append(
                (
                    point.score,
                    text
                )
            )

        else:

            other_matches.append(
                (
                    point.score,
                    text
                )
            )


    # ==========================================
    # ƯU TIÊN CÁC KẾT QUẢ KHỚP TÊN
    # ==========================================

    exact_matches.sort(
        key=lambda x: x[0],
        reverse=True
    )

    other_matches.sort(
        key=lambda x: x[0],
        reverse=True
    )


    # ==========================================
    # LẤY KẾT QUẢ
    # ==========================================

    selected = []

    # Tối đa 3 kết quả khớp tên thủ tục
    for score, text in exact_matches[:3]:

        selected.append(text)


    # Nếu chưa đủ 5 kết quả,
    # bổ sung semantic search
    for score, text in other_matches:

        if len(selected) >= 5:
            break

        selected.append(text)


    # ==========================================
    # FALLBACK
    # ==========================================

    if not selected:

        for point in points[:5]:

            payload = point.payload or {}

            text = str(
                payload.get(
                    "text",
                    ""
                )
            ).strip()

            if text:
                selected.append(text)


    print(
        f"MCP SEARCH: {query}",
        file=__import__("sys").stderr
    )

    print(
        f"MCP RESULTS: {len(selected)}",
        file=__import__("sys").stderr
    )

    return selected


# ==========================================
# TOOL: SEARCH PROCEDURE
# ==========================================

@mcp.tool()
def search_procedure(keyword: str) -> list[str]:

    """
    Tìm thủ tục hành chính theo từ khóa.
    """

    return search_legal_documents(
        keyword
    )


# ==========================================
# RUN MCP
# ==========================================

if __name__ == "__main__":

    mcp.run(
        transport="stdio"
    )