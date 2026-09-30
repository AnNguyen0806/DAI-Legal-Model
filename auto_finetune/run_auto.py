import os
import sys
import json
import subprocess


# =========================================================
# CONFIG
# =========================================================

PROJECT_DIR = r"D:\DAI-Legal-Model"

AUTO_DIR = os.path.join(
    PROJECT_DIR,
    "outputs",
    "auto"
)

PYTHON = sys.executable


# =========================================================
# RUN COMMAND
# =========================================================

def run_command(
    title,
    command
):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)

    print(
        "COMMAND:",
        " ".join(command)
    )

    result = subprocess.run(
        command,
        cwd=PROJECT_DIR
    )

    if result.returncode != 0:

        print("\n" + "=" * 70)
        print(title, "FAILED")
        print("=" * 70)

        raise RuntimeError(
            f"{title} thất bại."
        )

    print("\n")
    print(title, "COMPLETED")


# =========================================================
# FIND LATEST ADAPTER
# =========================================================

def find_latest_adapter():

    if not os.path.exists(AUTO_DIR):

        return None

    candidates = []

    for name in os.listdir(AUTO_DIR):

        path = os.path.join(
            AUTO_DIR,
            name
        )

        if not os.path.isdir(path):
            continue

        adapter_file = os.path.join(
            path,
            "adapter_model.safetensors"
        )

        if os.path.exists(
            adapter_file
        ):

            candidates.append(
                path
            )

    if not candidates:

        return None

    candidates.sort(
        key=os.path.getmtime,
        reverse=True
    )

    return candidates[0]


# =========================================================
# UPDATE EVALUATOR ADAPTER
# =========================================================

def update_evaluator_adapter(
    adapter_path
):

    evaluator_path = os.path.join(
        PROJECT_DIR,
        "auto_finetune",
        "auto_evaluator.py"
    )

    if not os.path.exists(
        evaluator_path
    ):

        raise RuntimeError(
            "Không tìm thấy auto_evaluator.py"
        )

    with open(
        evaluator_path,
        "r",
        encoding="utf-8"
    ) as f:

        content = f.read()


    # -----------------------------------------
    # Thay ADAPTER_DIR
    # -----------------------------------------

    lines = content.splitlines()

    new_lines = []

    replaced = False

    for line in lines:

        stripped = line.strip()

        if stripped.startswith(
            "ADAPTER_DIR ="
        ):

            new_lines.append(
                f'ADAPTER_DIR = r"{adapter_path}"'
            )

            replaced = True

        else:

            new_lines.append(
                line
            )


    if not replaced:

        raise RuntimeError(
            "Không tìm thấy ADAPTER_DIR "
            "trong auto_evaluator.py"
        )


    with open(
        evaluator_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(new_lines)
            + "\n"
        )


# =========================================================
# UPDATE ACTIVATION ADAPTER
# =========================================================

def activation_will_find_latest():

    # auto_activation.py tự tìm adapter mới nhất.
    # Không cần sửa file.

    return True


# =========================================================
# MAIN
# =========================================================

def main():

    print("=" * 70)
    print("DAI LEGAL MODEL - AUTO FINE-TUNING PIPELINE")
    print("=" * 70)

    print(
        "Project:",
        PROJECT_DIR
    )

    print(
        "Python:",
        PYTHON
    )


    # =====================================================
    # STEP 1 - VALIDATOR
    # =====================================================

    run_command(

        "STEP 1 - DATASET VALIDATOR",

        [

            PYTHON,

            os.path.join(
                "auto_finetune",
                "dataset_validator.py"
            ),

            os.path.join(
                "dataset",
                "train.jsonl"
            ),

        ]
    )


    # =====================================================
    # STEP 2 - FORMATTER
    # =====================================================

    run_command(

        "STEP 2 - DATASET FORMATTER",

        [

            PYTHON,

            os.path.join(
                "auto_finetune",
                "dataset_formatter.py"
            ),

            os.path.join(
                "dataset",
                "train.jsonl"
            ),

        ]
    )


    # =====================================================
    # STEP 3 - TRAIN
    # =====================================================

    run_command(

        "STEP 3 - AUTO QLORA TRAINING",

        [

            PYTHON,

            os.path.join(
                "auto_finetune",
                "auto_trainer.py"
            ),

        ]
    )


    # =====================================================
    # FIND NEW ADAPTER
    # =====================================================

    latest_adapter = find_latest_adapter()


    if latest_adapter is None:

        raise RuntimeError(
            "Training hoàn tất nhưng "
            "không tìm thấy adapter."
        )


    print("\n")
    print("=" * 70)
    print("NEW ADAPTER FOUND")
    print("=" * 70)

    print(
        latest_adapter
    )


    # =====================================================
    # STEP 4 - UPDATE EVALUATOR
    # =====================================================

    print("\n")
    print("=" * 70)
    print("PREPARING AUTO EVALUATION")
    print("=" * 70)

    update_evaluator_adapter(
        latest_adapter
    )

    print(
        "Evaluator adapter updated."
    )


    # =====================================================
    # STEP 5 - EVALUATION
    # =====================================================

    run_command(

        "STEP 4 - AUTO EVALUATION",

        [

            PYTHON,

            os.path.join(
                "auto_finetune",
                "auto_evaluator.py"
            ),

        ]
    )


    # =====================================================
    # CHECK EVALUATION
    # =====================================================

    evaluation_file = os.path.join(

        latest_adapter,

        "evaluation.json"

    )


    if not os.path.exists(
        evaluation_file
    ):

        raise RuntimeError(
            "Không tìm thấy evaluation.json"
        )


    with open(
        evaluation_file,
        "r",
        encoding="utf-8"
    ) as f:

        evaluation = json.load(f)


    overall_pass = evaluation.get(
        "overall_pass",
        False
    )


    print("\n")
    print("=" * 70)
    print("EVALUATION DECISION")
    print("=" * 70)

    print(
        "Average score:",
        evaluation.get(
            "average_score"
        )
    )

    print(
        "Pass rate:",
        evaluation.get(
            "pass_rate"
        )
    )

    print(
        "Overall:",
        "PASS" if overall_pass else "FAIL"
    )


    # =====================================================
    # STEP 6 - ACTIVATION
    # =====================================================

    # auto_activation.py tự đọc evaluation
    # và chỉ activate nếu PASS.

    run_command(

        "STEP 5 - AUTO ACTIVATION",

        [

            PYTHON,

            os.path.join(
                "auto_finetune",
                "auto_activation.py"
            ),

        ]
    )


    # =====================================================
    # FINAL
    # =====================================================

    print("\n")
    print("=" * 70)
    print("AUTO FINE-TUNING PIPELINE COMPLETE")
    print("=" * 70)


    if overall_pass:

        print(
            "RESULT: NEW ADAPTER ACTIVATED"
        )

    else:

        print(
            "RESULT: OLD ADAPTER KEPT"
        )

        print(
            "Current model remains:"
        )

        print(
            r"outputs\qwen-legal-lora-v3"
        )


    print("\nPipeline:")

    print(
        "Dataset"
        " → Validator"
        " → Formatter"
        " → QLoRA"
        " → Evaluation"
        " → Activation"
    )

    print("=" * 70)


# =========================================================
# ENTRY
# =========================================================

if __name__ == "__main__":

    main()