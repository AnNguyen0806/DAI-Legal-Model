import os
import json
from datetime import datetime

# ==========================================
# HUGGING FACE CACHE - Ổ D
# ==========================================

os.environ["HF_HOME"] = r"D:\AI\HuggingFace"
os.environ["HF_HUB_CACHE"] = r"D:\AI\HuggingFace\hub"

import torch

from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)

from peft import LoraConfig
from trl import SFTTrainer, SFTConfig


# ==========================================
# CONFIG
# ==========================================

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"

DATASET_DIR = r"auto_finetune\datasets\current"

# Không đụng V3
BASE_OUTPUT_DIR = r"outputs\auto"


# ==========================================
# TẠO OUTPUT VERSION
# ==========================================

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

OUTPUT_DIR = os.path.join(
    BASE_OUTPUT_DIR,
    f"adapter_{timestamp}"
)


# ==========================================
# HEADER
# ==========================================

print("=" * 70)
print("AUTO FINE-TUNING - QWEN2.5-7B + QLORA")
print("=" * 70)

print("Base model :", MODEL_ID)
print("Dataset    :", DATASET_DIR)
print("Output     :", OUTPUT_DIR)


# ==========================================
# GPU CHECK
# ==========================================

print("\n" + "=" * 70)
print("GPU CHECK")
print("=" * 70)

print("CUDA:", torch.cuda.is_available())

if not torch.cuda.is_available():
    raise RuntimeError(
        "Không tìm thấy CUDA. Không thể Auto Fine-Tuning."
    )

gpu_name = torch.cuda.get_device_name(0)

vram_gb = (
    torch.cuda.get_device_properties(0).total_memory
    / 1024**3
)

print("GPU :", gpu_name)
print("VRAM:", round(vram_gb, 2), "GB")


# ==========================================
# LOAD JSONL
# ==========================================

def load_jsonl(path):

    records = []

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            records.append(
                json.loads(line)
            )

    return records


# ==========================================
# CONVERT DATASET
# ==========================================

def convert_record(record):

    instruction = str(
        record.get("instruction", "")
    ).strip()

    input_text = str(
        record.get("input", "")
    ).strip()

    output = str(
        record.get("output", "")
    ).strip()

    if not instruction:
        raise ValueError(
            "Record thiếu instruction."
        )

    if not output:
        raise ValueError(
            "Record thiếu output."
        )

    # --------------------------------------
    # Ghép instruction + input
    # --------------------------------------

    if input_text:

        user_content = (
            instruction
            + "\n\n"
            + input_text
        )

    else:

        user_content = instruction

    # --------------------------------------
    # Qwen Chat Format
    # --------------------------------------

    conversations = [

        {
            "role": "user",
            "content": user_content,
        },

        {
            "role": "assistant",
            "content": output,
        },

    ]

    return {
        "conversations": conversations
    }


# ==========================================
# LOAD DATASET
# ==========================================

print("\n" + "=" * 70)
print("LOAD DATASET")
print("=" * 70)


train_path = os.path.join(
    DATASET_DIR,
    "train.jsonl"
)

validation_path = os.path.join(
    DATASET_DIR,
    "validation.jsonl"
)

test_path = os.path.join(
    DATASET_DIR,
    "test.jsonl"
)


train_records = load_jsonl(train_path)
validation_records = load_jsonl(validation_path)
test_records = load_jsonl(test_path)


print("Train      :", len(train_records))
print("Validation :", len(validation_records))
print("Test       :", len(test_records))


# ==========================================
# CONVERT
# ==========================================

print("\nĐang convert dataset sang Qwen chat format...")


train_data = [
    convert_record(x)
    for x in train_records
]

validation_data = [
    convert_record(x)
    for x in validation_records
]

test_data = [
    convert_record(x)
    for x in test_records
]


train_dataset = Dataset.from_list(
    train_data
)

eval_dataset = Dataset.from_list(
    validation_data
)

test_dataset = Dataset.from_list(
    test_data
)


print("\nDataset sau convert:")

print(
    "Train:",
    len(train_dataset)
)

print(
    "Validation:",
    len(eval_dataset)
)

print(
    "Test:",
    len(test_dataset)
)


# ==========================================
# TOKENIZER
# ==========================================

print("\n" + "=" * 70)
print("TOKENIZER")
print("=" * 70)

print("Đang load tokenizer...")


tokenizer = AutoTokenizer.from_pretrained(
    MODEL_ID,
    cache_dir=r"D:\AI\HuggingFace\hub",
)


if tokenizer.pad_token is None:

    tokenizer.pad_token = tokenizer.eos_token


# ==========================================
# FORMAT FUNCTION
# ==========================================

def formatting_func(example):

    return tokenizer.apply_chat_template(
        example["conversations"],
        tokenize=False,
        add_generation_prompt=False,
    )


# ==========================================
# 4-BIT QLORA
# ==========================================

print("\n" + "=" * 70)
print("4-BIT QLORA")
print("=" * 70)


bnb_config = BitsAndBytesConfig(

    load_in_4bit=True,

    bnb_4bit_quant_type="nf4",

    bnb_4bit_compute_dtype=torch.bfloat16,

    bnb_4bit_use_double_quant=True,
)


print("4-bit        : True")
print("Quantization : NF4")
print("Compute      : BF16")
print("Double Quant : True")


# ==========================================
# LOAD MODEL
# ==========================================

print("\n" + "=" * 70)
print("LOAD QWEN2.5-7B")
print("=" * 70)

print("Đang load model...")


model = AutoModelForCausalLM.from_pretrained(

    MODEL_ID,

    quantization_config=bnb_config,

    device_map="auto",

    torch_dtype=torch.bfloat16,

    cache_dir=r"D:\AI\HuggingFace\hub",
)


model.config.use_cache = False


# ==========================================
# LORA
# ==========================================

print("\n" + "=" * 70)
print("LORA CONFIG")
print("=" * 70)


peft_config = LoraConfig(

    r=16,

    lora_alpha=32,

    lora_dropout=0.05,

    bias="none",

    task_type="CAUSAL_LM",

    target_modules=[

        "q_proj",

        "k_proj",

        "v_proj",

        "o_proj",

        "gate_proj",

        "up_proj",

        "down_proj",

    ],
)


print("LoRA rank    : 16")
print("LoRA alpha   : 32")
print("LoRA dropout : 0.05")


# ==========================================
# TRAINING CONFIG
# ==========================================

print("\n" + "=" * 70)
print("TRAINING CONFIG")
print("=" * 70)


training_args = SFTConfig(

    output_dir=OUTPUT_DIR,

    # --------------------------------------
    # Batch
    # --------------------------------------

    per_device_train_batch_size=1,

    per_device_eval_batch_size=1,

    gradient_accumulation_steps=8,


    # --------------------------------------
    # Training
    # --------------------------------------

    num_train_epochs=1,

    learning_rate=2e-5,


    # --------------------------------------
    # Sequence
    # --------------------------------------

    max_length=2048,


    # --------------------------------------
    # Precision
    # --------------------------------------

    bf16=True,


    # --------------------------------------
    # Memory
    # --------------------------------------

    gradient_checkpointing=True,


    # --------------------------------------
    # Optimizer
    # --------------------------------------

    optim="paged_adamw_8bit",


    # --------------------------------------
    # Logging
    # --------------------------------------

    logging_steps=10,


    # --------------------------------------
    # Evaluation
    # --------------------------------------

    eval_strategy="steps",

    eval_steps=500,


    # --------------------------------------
    # Saving
    # --------------------------------------

    save_strategy="steps",

    save_steps=500,

    save_total_limit=2,


    # --------------------------------------
    # Other
    # --------------------------------------

    report_to="none",

    remove_unused_columns=False,
)


# ==========================================
# TRAINER
# ==========================================

print("\n" + "=" * 70)
print("CREATE SFT TRAINER")
print("=" * 70)


trainer = SFTTrainer(

    model=model,

    args=training_args,

    train_dataset=train_dataset,

    eval_dataset=eval_dataset,

    peft_config=peft_config,

    formatting_func=formatting_func,

    processing_class=tokenizer,
)


# ==========================================
# TRAIN
# ==========================================

print("\n")

print("=" * 70)
print("BẮT ĐẦU AUTO FINE-TUNING")
print("=" * 70)

print("Base model :", MODEL_ID)

print(
    "Train      :",
    len(train_dataset)
)

print(
    "Validation :",
    len(eval_dataset)
)

print(
    "Test       :",
    len(test_dataset)
)

print(
    "Output     :",
    OUTPUT_DIR
)

print("=" * 70)


trainer.train()


# ==========================================
# SAVE ADAPTER
# ==========================================

print("\n" + "=" * 70)
print("SAVE AUTO ADAPTER")
print("=" * 70)


trainer.save_model(
    OUTPUT_DIR
)

tokenizer.save_pretrained(
    OUTPUT_DIR
)


# ==========================================
# SAVE TEST DATA
# ==========================================

test_output = os.path.join(
    OUTPUT_DIR,
    "test.jsonl"
)

with open(
    test_output,
    "w",
    encoding="utf-8"
) as f:

    for record in test_records:

        f.write(
            json.dumps(
                record,
                ensure_ascii=False
            )
            + "\n"
        )


# ==========================================
# DONE
# ==========================================

print("\n")

print("=" * 70)
print("AUTO FINE-TUNING HOÀN TẤT!")
print("=" * 70)

print("Adapter được lưu tại:")

print(
    OUTPUT_DIR
)

print("\nKhông ảnh hưởng:")

print(
    "outputs/qwen-legal-lora-v3"
)

print("\nAUTO TRAINING PIPELINE:")

print(
    "Dataset"
    " → Validation"
    " → Format"
    " → QLoRA"
    " → Train"
    " → Save Adapter"
)

print("=" * 70)