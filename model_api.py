import os
import torch

from fastapi import FastAPI
from pydantic import BaseModel

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)
from peft import PeftModel


# =========================================================
# 1. CẤU HÌNH
# =========================================================

BASE_MODEL = "Qwen/Qwen2.5-7B-Instruct"

LORA_MODEL = r"D:\DAI-Legal-Model\outputs\qwen-legal-lora-v2"

HF_CACHE = r"D:\AI\HuggingFace\hub"

os.environ["HF_HOME"] = r"D:\AI\HuggingFace"
os.environ["HF_HUB_CACHE"] = HF_CACHE


# =========================================================
# 2. FASTAPI
# =========================================================

app = FastAPI(title="DAI Legal Model API")


# =========================================================
# 3. REQUEST
# =========================================================

class ChatRequest(BaseModel):
    question: str


# =========================================================
# 4. 4-BIT QUANTIZATION
# =========================================================

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)


# =========================================================
# 5. LOAD TOKENIZER
# =========================================================

print("=" * 60)
print("Loading tokenizer...")
print("=" * 60)

tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    cache_dir=HF_CACHE,
)


# =========================================================
# 6. LOAD BASE MODEL
# =========================================================

print("\nLoading Qwen2.5-7B...")

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto",
    cache_dir=HF_CACHE,
)

print("Base model loaded.")


# =========================================================
# 7. LOAD LORA
# =========================================================

print("\nLoading LoRA V2...")

model = PeftModel.from_pretrained(
    model,
    LORA_MODEL,
)

model.eval()

print("LoRA V2 loaded.")


# =========================================================
# 8. GPU
# =========================================================

if torch.cuda.is_available():

    gpu_name = torch.cuda.get_device_name(0)

    vram = (
        torch.cuda.get_device_properties(0).total_memory
        / 1024**3
    )

    print("\nGPU:", gpu_name)
    print(f"VRAM: {vram:.1f} GB")


# =========================================================
# 9. HÀM INFERENCE
# =========================================================

def ask_model(question: str):

    messages = [
        {
            "role": "system",
            "content": (
                "Bạn là trợ lý hỗ trợ tra cứu thủ tục hành chính. "
                "Trả lời bằng tiếng Việt, ngắn gọn và rõ ràng. "
                "Chỉ cung cấp thông tin liên quan đến câu hỏi."
            ),
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
    )

    inputs = {
        key: value.to(model.device)
        for key, value in inputs.items()
    }

    with torch.no_grad():

        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            do_sample=False,
            repetition_penalty=1.05,
            pad_token_id=tokenizer.eos_token_id,
        )

    input_length = inputs["input_ids"].shape[1]

    generated_tokens = outputs[0][input_length:]

    answer = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    )

    return answer.strip()


# =========================================================
# 10. API
# =========================================================

@app.get("/")
def root():

    return {
        "status": "running",
        "model": "Qwen2.5-7B-Instruct + QLoRA V2"
    }


@app.post("/generate")
def generate(request: ChatRequest):

    answer = ask_model(request.question)

    return {
        "success": True,
        "answer": answer
    }


# =========================================================
# 11. RUN SERVER
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001
    )