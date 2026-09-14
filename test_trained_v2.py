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


BASE_MODEL = "Qwen/Qwen2.5-7B-Instruct"
LORA_MODEL = r"outputs/qwen-legal-lora-v2"


# ==============================
# LOAD
# ==============================

print("Đang load Qwen...")

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    cache_dir=r"D:\AI\HuggingFace\hub",
)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    cache_dir=r"D:\AI\HuggingFace\hub",
)

print("Đang load LoRA V2...")

model = PeftModel.from_pretrained(
    model,
    LORA_MODEL,
)

model.eval()

print("\nMODEL V2 READY!")
print("GPU:", torch.cuda.get_device_name(0))
print(
    "VRAM:",
    round(torch.cuda.memory_allocated() / 1024**3, 2),
    "GB"
)


# ==============================
# CHAT
# ==============================

def ask(question):

    messages = [
        {
            "role": "user",
            "content": question
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
            max_new_tokens=250,

            # Không random để đánh giá model
            do_sample=False,

            repetition_penalty=1.05,
        )

    input_length = inputs["input_ids"].shape[1]

    answer = tokenizer.decode(
        outputs[0][input_length:],
        skip_special_tokens=True,
    )

    return answer.strip()


# ==============================
# TEST
# ==============================

questions = [

    "Thủ tục đăng ký khai sinh cần những giấy tờ gì?",

    "Lệ phí đăng ký khai sinh là bao nhiêu?",

    "Thủ tục xác nhận tình trạng hôn nhân giải quyết trong bao lâu?",

    "Hồ sơ đăng ký kết hôn gồm những gì?",

    "Thủ tục đăng ký khai tử giải quyết trong bao lâu?",
]


for i, question in enumerate(questions, 1):

    print("\n" + "=" * 70)

    print(f"CÂU {i}")

    print("=" * 70)

    print("USER:")
    print(question)

    print("\nQWEN V2:")

    answer = ask(question)

    print(answer)


print("\n" + "=" * 70)
print("TEST V2 HOÀN TẤT")
print("=" * 70)