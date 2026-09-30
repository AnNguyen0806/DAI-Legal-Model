import os
import json
import re

# ==========================================
# HUGGING FACE CACHE
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

# run_auto.py sẽ tự cập nhật giá trị này
ADAPTER_DIR = r"outputs\auto\adapter_20260930_130523"

TEST_FILE = os.path.join(
    ADAPTER_DIR,
    "test.jsonl"
)

RESULT_FILE = os.path.join(
    ADAPTER_DIR,
    "evaluation.json"
)


# ==========================================
# SETTINGS
# ==========================================

MAX_NEW_TOKENS = 512

MIN_SCORE = 0.60


# ==========================================
# HEADER
# ==========================================

print("=" * 70)
print("AUTO FINE-TUNING - EVALUATOR")
print("=" * 70)

print("Base model :", MODEL_ID)
print("Adapter    :", ADAPTER_DIR)
print("Test file  :", TEST_FILE)


# ==========================================
# GPU CHECK
# ==========================================

print("\n" + "=" * 70)
print("GPU CHECK")
print("=" * 70)

if not torch.cuda.is_available():
    raise RuntimeError(
        "Không tìm thấy CUDA."
    )

print(
    "GPU:",
    torch.cuda.get_device_name(0)
)

print(
    "VRAM:",
    round(
        torch.cuda.get_device_properties(0).total_memory
        / 1024**3,
        2
    ),
    "GB"
)


# ==========================================
# LOAD TEST DATA
# ==========================================

print("\n" + "=" * 70)
print("LOAD TEST DATA")
print("=" * 70)

test_records = []

with open(
    TEST_FILE,
    "r",
    encoding="utf-8"
) as f:

    for line in f:

        line = line.strip()

        if not line:
            continue

        test_records.append(
            json.loads(line)
        )


print(
    "Test records:",
    len(test_records)
)


if not test_records:
    raise RuntimeError(
        "Test dataset rỗng."
    )


# ==========================================
# TOKENIZER
# ==========================================

print("\n" + "=" * 70)
print("LOAD TOKENIZER")
print("=" * 70)

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_ID,
    cache_dir=r"D:\AI\HuggingFace\hub",
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


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
# LOAD BASE MODEL
# ==========================================

print("\n" + "=" * 70)
print("LOAD BASE QWEN2.5-7B")
print("=" * 70)

base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    cache_dir=r"D:\AI\HuggingFace\hub",
)

base_model.config.use_cache = True


# ==========================================
# LOAD LORA
# ==========================================

print("\n" + "=" * 70)
print("LOAD AUTO LORA")
print("=" * 70)

print(
    "Adapter:",
    ADAPTER_DIR
)

model = PeftModel.from_pretrained(
    base_model,
    ADAPTER_DIR,
)

model.eval()


# ==========================================
# NORMALIZE TEXT
# ==========================================

def normalize_text(text):

    text = str(text).lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = text.strip()

    return text


# ==========================================
# TOKEN OVERLAP SCORE
# ==========================================

def calculate_score(
    expected,
    predicted
):

    expected = normalize_text(
        expected
    )

    predicted = normalize_text(
        predicted
    )

    expected_words = set(
        expected.split()
    )

    predicted_words = set(
        predicted.split()
    )

    if not expected_words:
        return 0.0

    overlap = (
        expected_words
        & predicted_words
    )

    score = (
        len(overlap)
        /
        len(expected_words)
    )

    return score


# ==========================================
# GENERATE
# ==========================================

def generate_answer(
    instruction,
    input_text
):

    if input_text:

        user_content = (
            instruction
            + "\n\n"
            + input_text
        )

    else:

        user_content = instruction


    messages = [
        {
            "role": "user",
            "content": user_content,
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
    ).to(model.device)


    with torch.no_grad():

        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            temperature=None,
            top_p=None,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )


    generated_tokens = outputs[
        0
    ][
        inputs["input_ids"].shape[1]:
    ]


    answer = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    )


    return answer.strip()


# ==========================================
# EVALUATION
# ==========================================

print("\n" + "=" * 70)
print("START EVALUATION")
print("=" * 70)


results = []

total_score = 0.0

passed = 0


for index, record in enumerate(
    test_records,
    start=1
):

    instruction = record.get(
        "instruction",
        ""
    )

    input_text = record.get(
        "input",
        ""
    )

    expected = record.get(
        "output",
        ""
    )


    print(
        f"\n[{index}/{len(test_records)}]"
    )

    print(
        "Question:",
        instruction[:150]
    )


    try:

        predicted = generate_answer(
            instruction,
            input_text
        )


        score = calculate_score(
            expected,
            predicted
        )


        is_pass = (
            score >= MIN_SCORE
        )


        if is_pass:
            passed += 1


        total_score += score


        print(
            "Score:",
            round(score, 4)
        )

        print(
            "Status:",
            "PASS" if is_pass else "FAIL"
        )


        results.append({

            "index": index,

            "instruction": instruction,

            "input": input_text,

            "expected": expected,

            "predicted": predicted,

            "score": round(
                score,
                4
            ),

            "pass": is_pass,

        })


    except Exception as e:

        print(
            "ERROR:",
            str(e)
        )


        results.append({

            "index": index,

            "instruction": instruction,

            "input": input_text,

            "expected": expected,

            "predicted": "",

            "score": 0.0,

            "pass": False,

            "error": str(e),

        })


# ==========================================
# FINAL SCORE
# ==========================================

total = len(results)

if total > 0:

    average_score = (
        total_score
        / total
    )

else:

    average_score = 0.0


pass_rate = (

    passed
    / total
    if total > 0
    else 0.0
)


# ==========================================
# FINAL DECISION
# ==========================================

overall_pass = (
    average_score >= MIN_SCORE
    and
    pass_rate >= 0.60
)


# ==========================================
# SAVE RESULT
# ==========================================

evaluation = {

    "base_model": MODEL_ID,

    "adapter": ADAPTER_DIR,

    "test_file": TEST_FILE,

    "total_tests": total,

    "passed": passed,

    "failed": total - passed,

    "average_score": round(
        average_score,
        4
    ),

    "pass_rate": round(
        pass_rate,
        4
    ),

    "minimum_score": MIN_SCORE,

    "overall_pass": overall_pass,

    "results": results,

}


with open(
    RESULT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        evaluation,
        f,
        ensure_ascii=False,
        indent=2,
    )


# ==========================================
# SUMMARY
# ==========================================

print("\n")

print("=" * 70)
print("AUTO EVALUATION COMPLETE")
print("=" * 70)

print(
    "Total tests :",
    total
)

print(
    "Passed      :",
    passed
)

print(
    "Failed      :",
    total - passed
)

print(
    "Average     :",
    round(
        average_score,
        4
    )
)

print(
    "Pass rate   :",
    f"{pass_rate * 100:.2f}%"
)

print(
    "Threshold   :",
    MIN_SCORE
)

print("=" * 70)


if overall_pass:

    print(
        "RESULT: PASS"
    )

    print(
        "Adapter đủ điều kiện để ACTIVATE."
    )

else:

    print(
        "RESULT: FAIL"
    )

    print(
        "Giữ adapter cũ."
    )


print("\nEvaluation saved:")

print(
    RESULT_FILE
)

print("=" * 70)