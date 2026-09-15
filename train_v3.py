import os

# ==========================================
# HUGGING FACE CACHE - Ổ D
# ==========================================
os.environ["HF_HOME"] = r"D:\AI\HuggingFace"
os.environ["HF_HUB_CACHE"] = r"D:\AI\HuggingFace\hub"

import torch
from datasets import load_from_disk
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

DATASET_PATH = "data/legal_train_v3"

# KHÔNG ĐỤNG VÀO V2
OUTPUT_DIR = "outputs/qwen-legal-lora-v3"


# ==========================================
# GPU
# ==========================================

print("=" * 60)
print("GPU CHECK - TRAIN V3")
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
# DATASET
# ==========================================

print("\nĐang load Legal Dataset V3...")

dataset = load_from_disk(DATASET_PATH)

print("Tổng dataset:", len(dataset))
print("Các cột:", dataset.column_names)


# Chia 95% train - 5% validation
split_dataset = dataset.train_test_split(
    test_size=0.05,
    seed=42
)

train_dataset = split_dataset["train"]
eval_dataset = split_dataset["test"]

print("Train:", len(train_dataset))
print("Validation:", len(eval_dataset))


# ==========================================
# TOKENIZER
# ==========================================

print("\nĐang load tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_ID,
    cache_dir=r"D:\AI\HuggingFace\hub",
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


# ==========================================
# 4-BIT QLoRA
# ==========================================

print("\nĐang cấu hình 4-bit QLoRA...")

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)


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

model.config.use_cache = False


# ==========================================
# LORA
# ==========================================

print("\nĐang cấu hình LoRA V3...")

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


# ==========================================
# FORMAT DATASET
# ==========================================

def formatting_func(example):

    return tokenizer.apply_chat_template(
        example["conversations"],
        tokenize=False,
        add_generation_prompt=False,
    )


# ==========================================
# TRAINING CONFIG
# ==========================================

training_args = SFTConfig(

    output_dir=OUTPUT_DIR,

    # -------------------------
    # Batch
    # -------------------------
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,

    gradient_accumulation_steps=8,

    # -------------------------
    # Training
    # -------------------------
    num_train_epochs=1,

    learning_rate=2e-5,

    # -------------------------
    # Sequence
    # -------------------------
    max_length=2048,

    # -------------------------
    # Precision
    # -------------------------
    bf16=True,

    # -------------------------
    # Memory
    # -------------------------
    gradient_checkpointing=True,

    # -------------------------
    # Optimizer
    # -------------------------
    optim="paged_adamw_8bit",

    # -------------------------
    # Logging
    # -------------------------
    logging_steps=10,

    # -------------------------
    # Evaluation
    # -------------------------
    eval_strategy="steps",
    eval_steps=500,

    # -------------------------
    # Saving
    # -------------------------
    save_strategy="steps",
    save_steps=500,
    save_total_limit=2,

    # -------------------------
    # Other
    # -------------------------
    report_to="none",
    remove_unused_columns=False,
)


# ==========================================
# TRAINER
# ==========================================

print("\nĐang tạo SFT Trainer...")

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
print("=" * 60)
print("BẮT ĐẦU TRAIN QWEN 7B - LEGAL V3")
print("=" * 60)

print("Dataset:", DATASET_PATH)
print("Train:", len(train_dataset))
print("Validation:", len(eval_dataset))
print("Output:", OUTPUT_DIR)

trainer.train()


# ==========================================
# SAVE
# ==========================================

print("\nĐang lưu LoRA V3...")

trainer.save_model(OUTPUT_DIR)

tokenizer.save_pretrained(OUTPUT_DIR)


print("\n")
print("=" * 60)
print("TRAIN V3 HOÀN TẤT!")
print("=" * 60)

print("LoRA V3 được lưu tại:")
print(OUTPUT_DIR)