import os

# ==========================================
# HUGGING FACE CACHE - Ổ D
# ==========================================
os.environ["HF_HOME"] = r"D:\AI\HuggingFace"
os.environ["HF_HUB_CACHE"] = r"D:\AI\HuggingFace\hub"

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)
from peft import PeftModel


# ==========================================
# CONFIG
# ==========================================

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"

LORA_PATH = r"D:\DAI-Legal-Model\outputs\qwen-legal-lora-v3"


# ==========================================
# GPU CHECK
# ==========================================

print("=" * 60)
print("TEST QWEN LEGAL - V3")
print("=" * 60)

print("CUDA:", torch.cuda.is_available())

if not torch.cuda.is_available():
    raise RuntimeError("Không tìm thấy CUDA!")

print("GPU:", torch.cuda.get_device_name(0))

print(
    "VRAM:",
    round(
        torch.cuda.get_device_properties(0).total_memory / 1024**3,
        2
    ),
    "GB"
)


# ==========================================
# 4-BIT CONFIG
# ==========================================

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)


# ==========================================
# LOAD TOKENIZER
# ==========================================

print("\nĐang load tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_ID,
    cache_dir=r"D:\AI\HuggingFace\hub",
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


# ==========================================
# LOAD BASE MODEL
# ==========================================

print("\nĐang load Qwen 7B...")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    cache_dir=r"D:\AI\HuggingFace\hub",
)


# ==========================================
# LOAD LORA V3
# ==========================================

print("\nĐang load LoRA V3...")

model = PeftModel.from_pretrained(
    model,
    LORA_PATH,
)

model.eval()

print("ĐÃ LOAD LOẠRA V3 THÀNH CÔNG!")


# ==========================================
# FUNCTION
# ==========================================

def ask_model(question):

    messages = [
        {
            "role": "system",
            "content": (
                "Bạn là trợ lý AI chuyên hỗ trợ tra cứu "
                "pháp luật Việt Nam. "
                "Trả lời bằng tiếng Việt, rõ ràng, "
                "ngắn gọn và chính xác."
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
    ).to(model.device)

    with torch.no_grad():

        outputs = model.generate(
            **inputs,

            max_new_tokens=300,

            do_sample=False,

            repetition_penalty=1.05,

            pad_token_id=tokenizer.eos_token_id,
        )

    generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]

    answer = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    )

    return answer.strip()


# ==========================================
# TEST
# ==========================================

print("\n")
print("=" * 60)
print("MODEL V3 SẴN SÀNG")
print("=" * 60)

while True:

    question = input(
        "\nNhập câu hỏi (gõ 'exit' để thoát): "
    ).strip()

    if question.lower() == "exit":
        print("\nĐã thoát.")
        break

    if not question:
        continue

    print("\nĐang suy luận...\n")

    try:

        answer = ask_model(question)

        print("=" * 60)
        print("CÂU TRẢ LỜI V3:")
        print("=" * 60)

        print(answer)

        print("=" * 60)

    except Exception as e:

        print("\nLỖI:", repr(e))