from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import httpx
import json
import asyncio
import os
import sys


app = FastAPI(title="DAI Legal Core API")


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# PATH MCP SERVER
# =========================

BASE_DIR = r"D:\DAI-Legal-Model"
MCP_SERVER_PATH = os.path.join(BASE_DIR, "mcp_server.py")

MODEL_API_URL = "http://localhost:8001/generate"


# =========================
# HOME
# =========================

@app.get("/")
async def root():
    return {
        "success": True,
        "message": "DAI Legal Core API đang chạy",
        "mcp_server": MCP_SERVER_PATH,
        "model_api": MODEL_API_URL
    }


# =========================
# GỌI MCP
# =========================

async def search_with_mcp(question: str):

    print("\n==============================")
    print("MCP QUESTION:", question)

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[MCP_SERVER_PATH],
        env={
            **os.environ,
            "PYTHONIOENCODING": "utf-8"
        }
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            # Khởi tạo MCP session
            await session.initialize()

            print("MCP CONNECTED")

            # Gọi tool MCP
            result = await session.call_tool(
                "search_legal_documents",
                arguments={
                    "query": question
                }
            )

            print("MCP TOOL CALLED")

            contexts = []

            for content in result.content:

                if hasattr(content, "text"):

                    text = content.text

                    if text:
                        contexts.append(text)

            print("MCP RESULTS:", len(contexts))

            for i, text in enumerate(contexts):

                print(f"\n--- MCP DOCUMENT {i + 1} ---")
                print(text[:500])

            return contexts


# =========================
# CHAT API
# =========================

@app.post("/api/v1/chat/completions")
async def chat_completions(data: dict):

    question = data.get("prompt", "").strip()

    async def generate():

        if not question:

            yield "event: chunk\n"
            yield (
                "data: "
                + json.dumps(
                    {"delta": "Vui lòng nhập câu hỏi."},
                    ensure_ascii=False
                )
                + "\n\n"
            )

            return

        # =========================
        # STATUS
        # =========================

        yield "event: status\n"
        yield (
            'data: {"status":"searching_mcp"}\n\n'
        )

        # =========================
        # MCP SEARCH
        # =========================

        try:

            contexts = await search_with_mcp(question)

        except Exception as e:

            print("MCP ERROR:", repr(e))

            yield "event: chunk\n"
            yield (
                "data: "
                + json.dumps(
                    {
                        "delta": "Không thể kết nối MCP Server."
                    },
                    ensure_ascii=False
                )
                + "\n\n"
            )

            yield "event: done\n"
            yield 'data: {"status":"done"}\n\n'

            return

        # =========================
        # CONTEXT
        # =========================

        if contexts:

            main_context = contexts[0]
            main_context = main_context[:8000]  
            context_text = f"[Văn bản chính]\n{main_context}"
                   
            

        else:

            context_text = (
                "Mình chưa tìm thấy thông tin phù hợp trong dữ liệu hiện có."
            )

        print("\n==============================")
        print("CONTEXT TỪ MCP:")
        print(context_text[:3000])

        # =========================
        # PROMPT
        # =========================

        system_prompt = f"""
Bạn là trợ lý AI chuyên hỗ trợ tra cứu thủ tục hành chính Việt Nam.

Hãy trả lời câu hỏi dựa trên dữ liệu pháp lý được cung cấp.

QUY TẮC:
- Ưu tiên tuyệt đối dữ liệu pháp lý bên dưới.
- Không tự bịa thông tin.
- Nếu dữ liệu không đủ để trả lời, hãy nói:
  "Mình chưa tìm thấy thông tin phù hợp trong dữ liệu hiện có."
- Không trả lời cụt như "Không có".
- Trả lời bằng tiếng Việt.
- Nếu có thành phần hồ sơ thì liệt kê rõ từng giấy tờ.
- Trả lời ngắn gọn nhưng đầy đủ.

DỮ LIỆU PHÁP LÝ:
{context_text}

CÂU HỎI:
{question}

CÂU TRẢ LỜI:
"""

        # =========================
        # MODEL API
        # =========================

        yield "event: status\n"
        yield (
            'data: {"status":"thinking"}\n\n'
        )

        try:

            async with httpx.AsyncClient() as client:

                response = await client.post(
                    MODEL_API_URL,
                    json={
                        "question": system_prompt
                    },
                    timeout=180.0
                )

            print("MODEL STATUS:", response.status_code)

            if response.status_code != 200:

                print("MODEL ERROR:", response.text)

                answer = (
                    "Model API trả về lỗi."
                )

            else:

                result = response.json()

                print("MODEL RESULT:", result)

                answer = result.get(
                    "answer",
                    ""
                ).strip()

                if not answer:

                    answer = (
                        "Model không trả về câu trả lời."
                    )

        except Exception as e:

            print("MODEL API ERROR:", repr(e))

            answer = (
                "Không thể kết nối Model API :8001."
            )

        # =========================
        # RESPONSE
        # =========================

        yield "event: chunk\n"

        yield (
            "data: "
            + json.dumps(
                {"delta": answer},
                ensure_ascii=False
            )
            + "\n\n"
        )

        yield "event: done\n"

        yield (
            'data: {"status":"done"}\n\n'
        )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# =========================
# RUN
# =========================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )