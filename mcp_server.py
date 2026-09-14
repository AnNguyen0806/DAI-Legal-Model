from mcp.server import MCPServer

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


# =========================================================
# 1. MCP SERVER
# =========================================================

mcp = MCPServer("DAI Legal MCP")


# =========================================================
# 2. QDRANT
# =========================================================

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "legal_docs"



qdrant_client = QdrantClient(QDRANT_URL)



embedding_model = SentenceTransformer(
    "bkai-foundation-models/vietnamese-bi-encoder"
)




# =========================================================
# 3. TOOL: SEARCH LEGAL DOCUMENTS
# =========================================================

@mcp.tool()
def search_legal_documents(query: str) -> list[str]:
    """
    Tìm kiếm các văn bản pháp luật và thủ tục hành chính
    liên quan đến câu hỏi của người dùng.
    """

    try:

        # Chuyển câu hỏi thành vector
        query_vector = embedding_model.encode(
            query
        ).tolist()

        # Tìm kiếm Qdrant
        response = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=5
        )

        results = []

        for point in response.points:

            if point.payload and "text" in point.payload:

                results.append(
                    point.payload["text"]
                )

        return results

    except Exception as e:

        return [
            f"Lỗi khi tìm kiếm dữ liệu pháp luật: {str(e)}"
        ]


# =========================================================
# 4. TOOL: SEARCH PROCEDURES
# =========================================================

@mcp.tool()
def search_procedure(keyword: str) -> list[str]:
    """
    Tìm kiếm thủ tục hành chính theo từ khóa.
    """

    try:

        query_vector = embedding_model.encode(
            keyword
        ).tolist()

        response = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=5
        )

        results = []

        for point in response.points:

            if point.payload:

                results.append(
                    str(point.payload)
                )

        return results

    except Exception as e:

        return [
            f"Lỗi khi tìm thủ tục: {str(e)}"
        ]


# =========================================================
# 5. RUN MCP SERVER
# =========================================================

if __name__ == "__main__":

    mcp.run(transport="stdio")