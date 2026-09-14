import os
import json
import torch

os.environ["HF_HOME"] = r"D:\AI\HuggingFace"
os.environ["HF_HUB_CACHE"] = r"D:\AI\HuggingFace\hub"

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)
from peft import PeftModel


# ==========================================
# CONFIG
# ==========================================

BASE_MODEL = "Qwen/Qwen2.5-7B-Instruct"
LORA_MODEL = r"outputs/qwen-legal-lora-v2"
TEST_FILE = r"dataset/test.jsonl"

RESULT_FILE = r"evaluation_results.json"


# ==========================================
# LOAD MODEL
# ==========================================

print("=" * 70)
print("ĐÁNH GIÁ QWEN LEGAL V2")
print("=" * 70)

print("\nGPU:", torch.cuda.get_device_name(0))

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

print("\nĐang load tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    cache_dir=r"D:\AI\HuggingFace\hub",
)

print("Đang load Qwen 7B...")

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


# ==========================================
# LOAD TEST DATA
# ==========================================

print("\nĐang đọc test dataset...")

with open(TEST_FILE, "r", encoding="utf-8") as f:
    test_data = [
        json.loads(line)
        for line in f
    ]

print("Số mẫu test:", len(test_data))


# ==========================================
# ASK MODEL
# ==========================================

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
            do_sample=False,
            repetition_penalty=1.05,
        )

    input_length = inputs["input_ids"].shape[1]

    answer = tokenizer.decode(
        outputs[0][input_length:],
        skip_special_tokens=True,
    )

    return answer.strip()


# ==========================================
# EVALUATE
# ==========================================

results = []

for i, item in enumerate(test_data, 1):

    question = item["instruction"]
    expected = item["output"]

    print("\n")
    print("=" * 70)
    print(f"CÂU {i}/{len(test_data)}")
    print("=" * 70)

    print("\nQUESTION:")
    print(question)

    print("\nEXPECTED:")
    print(expected)

    print("\nQWEN V2:")
    
    answer = ask_qwen(question)

    print(answer)

    results.append({
        "question": question,
        "expected": expected,
        "answer": answer,
    })


# ==========================================
# SAVE RESULTS
# ==========================================

with open(
    RESULT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        ensure_ascii=False,
        indent=2,
    )


# ==========================================
# FINISH
# ==========================================

print("\n")
print("=" * 70)
print("ĐÁNH GIÁ HOÀN TẤT")
print("=" * 70)

print(f"\nĐã test: {len(results)} câu")

print(f"Kết quả được lưu tại:")
print(RESULT_FILE)