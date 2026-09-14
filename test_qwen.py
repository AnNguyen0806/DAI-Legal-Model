import os

# ==========================================
# ÉP HUGGING FACE LƯU MODEL VÀO Ổ D
# ==========================================
os.environ["HF_HOME"] = r"D:\AI\HuggingFace"
os.environ["HF_HUB_CACHE"] = r"D:\AI\HuggingFace\hub"

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)

# ==========================================
# MODEL
# ==========================================
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"

print("=" * 60)
print("KIỂM TRA GPU")
print("=" * 60)

print("CUDA:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
else:
    print("Không tìm thấy GPU!")

print("=" * 60)
print("HF CACHE:")
print(os.environ["HF_HOME"])
print(os.environ["HF_HUB_CACHE"])
print("=" * 60)

# ==========================================
# QLoRA 4-BIT
# ==========================================
quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

# ==========================================
# LOAD TOKENIZER
# ==========================================
print("\nĐang tải tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_ID,
    cache_dir=r"D:\AI\HuggingFace\hub",
)

# ==========================================
# LOAD MODEL
# ==========================================
print("\nĐang tải Qwen 7B 4-bit...")
print("Model sẽ được lưu vào ổ D.")
print("Đừng tắt Terminal hoặc nhấn Ctrl+C.")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=quant_config,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    cache_dir=r"D:\AI\HuggingFace\hub",
)

# ==========================================
# KIỂM TRA VRAM
# ==========================================
print("\n" + "=" * 60)
print("QWEN ĐÃ LOAD THÀNH CÔNG!")
print("=" * 60)

print("GPU:", torch.cuda.get_device_name(0))

vram = torch.cuda.memory_allocated() / 1024**3
print(f"VRAM đang dùng: {vram:.2f} GB")

memory = model.get_memory_footprint() / 1024**3
print(f"Model memory: {memory:.2f} GB")

# ==========================================
# TEST CHAT
# ==========================================
messages = [
    {
        "role": "user",
        "content": "Xin chào. Hãy giới thiệu ngắn gọn về trí tuệ nhân tạo bằng tiếng Việt."
    }
]

# Tạo prompt từ chat template
prompt = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
)

# Tokenize thành tensor thật
inputs = tokenizer(
    prompt,
    return_tensors="pt",
)

# Đưa tensor lên GPU
inputs = {k: v.to(model.device) for k, v in inputs.items()}

print("\nQwen đang trả lời...\n")

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=150,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )

# Chỉ lấy phần Qwen sinh ra
input_length = inputs["input_ids"].shape[1]

answer = tokenizer.decode(
    outputs[0][input_length:],
    skip_special_tokens=True,
)

print("QWEN:")
print(answer)

print("\n" + "=" * 60)
print("TEST HOÀN TẤT")
print("=" * 60)