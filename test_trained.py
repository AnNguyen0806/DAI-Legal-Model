import os

os.environ["HF_HOME"] = r"D:\AI\HuggingFace"
os.environ["HF_HUB_CACHE"] = r"D:\AI\HuggingFace\hub"

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)
from peft import PeftModel


# ==============================
# MODEL
# ==============================

BASE_MODEL = "Qwen/Qwen2.5-7B-Instruct"
LORA_MODEL = r"outputs/qwen-legal-lora"


# ==============================
# GPU
# ==============================

print("=" * 60)
print("LOAD MODEL SAU KHI TRAIN")
print("=" * 60)

print("GPU:", torch.cuda.get_device_name(0))
print("CUDA:", torch.cuda.is_available())


# ==============================
# 4-BIT CONFIG
# ==============================

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)


# ==============================
# TOKENIZER
# ==============================

print("\nĐang load tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    cache_dir=r"D:\AI\HuggingFace\hub",
)


# ==============================
# BASE MODEL
# ==============================

print("\nĐang load Qwen 7B...")

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    cache_dir=r"D:\AI\HuggingFace\hub",
)


# ==============================
# LOAD LORA
# ==============================

print("\nĐang load LoRA đã train...")

model = PeftModel.from_pretrained(
    model,
    LORA_MODEL,
)

model.eval()

print("\n" + "=" * 60)
print("MODEL SAU TRAIN ĐÃ SẴN SÀNG!")
print("=" * 60)


# ==============================
# CHAT FUNCTION
# ==============================

def ask_qwen(question):

    messages = [
        {
            "role": "user",
            "content": question,
        }
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
        k: v.to(model.device)
        for k, v in inputs.items()
    }

    with torch.no_grad():

        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            do_sample=True,
            temperature=0.3,
            top_p=0.9,
        )

    input_length = inputs["input_ids"].shape[1]

    answer = tokenizer.decode(
        outputs[0][input_length:],
        skip_special_tokens=True,
    )

    return answer


# ==============================
# TEST QUESTIONS
# ==============================

questions = [
    "Thủ tục đăng ký khai sinh cần những giấy tờ gì?",
    
    "Lệ phí đăng ký khai sinh là bao nhiêu?",
    
    "Thủ tục xác nhận tình trạng hôn nhân giải quyết trong bao lâu?",
    
    "Hồ sơ đăng ký kết hôn gồm những gì?",
]


# ==============================
# RUN TEST
# ==============================

for i, question in enumerate(questions, 1):

    print("\n")
    print("=" * 60)
    print(f"CÂU HỎI {i}")
    print("=" * 60)

    print("USER:")
    print(question)

    print("\nQWEN SAU TRAIN:")

    answer = ask_qwen(question)

    print(answer)


print("\n")
print("=" * 60)
print("TEST HOÀN TẤT")
print("=" * 60)