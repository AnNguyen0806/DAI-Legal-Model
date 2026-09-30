import os
import json
import shutil


# ==========================================
# CONFIG
# ==========================================

AUTO_DIR = r"outputs\auto"

ACTIVE_DIR = r"outputs\active"

ACTIVE_ADAPTER = os.path.join(
    ACTIVE_DIR,
    "current"
)

REGISTRY_FILE = os.path.join(
    ACTIVE_DIR,
    "registry.json"
)

OLD_ADAPTER = r"outputs\qwen-legal-lora-v3"


# ==========================================
# FIND LATEST ADAPTER
# ==========================================

print("=" * 70)
print("AUTO MODEL ACTIVATION")
print("=" * 70)


if not os.path.exists(AUTO_DIR):

    raise RuntimeError(
        "Không tìm thấy outputs\\auto"
    )


adapters = []

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

    evaluation_file = os.path.join(
        path,
        "evaluation.json"
    )

    if (
        os.path.exists(adapter_file)
        and
        os.path.exists(evaluation_file)
    ):

        adapters.append(
            (
                os.path.getmtime(path),
                path
            )
        )


if not adapters:

    raise RuntimeError(
        "Không tìm thấy adapter đã evaluation."
    )


adapters.sort(
    reverse=True
)

latest_adapter = adapters[0][1]


print(
    "Latest adapter:",
    latest_adapter
)


# ==========================================
# LOAD EVALUATION
# ==========================================

evaluation_file = os.path.join(
    latest_adapter,
    "evaluation.json"
)


with open(
    evaluation_file,
    "r",
    encoding="utf-8"
) as f:

    evaluation = json.load(f)


average_score = evaluation.get(
    "average_score",
    0
)

pass_rate = evaluation.get(
    "pass_rate",
    0
)

overall_pass = evaluation.get(
    "overall_pass",
    False
)


print("\nEvaluation:")
print(
    "Average score:",
    average_score
)

print(
    "Pass rate:",
    f"{pass_rate * 100:.2f}%"
)

print(
    "Overall:",
    "PASS" if overall_pass else "FAIL"
)


# ==========================================
# FAIL
# ==========================================

if not overall_pass:

    print("\n" + "=" * 70)
    print("ACTIVATION: SKIPPED")
    print("=" * 70)

    print(
        "Adapter mới không đạt evaluation."
    )

    print(
        "Giữ model hiện tại:"
    )

    print(
        OLD_ADAPTER
    )

    # Registry
    os.makedirs(
        ACTIVE_DIR,
        exist_ok=True
    )

    registry = {

        "status": "rollback",

        "active_adapter": OLD_ADAPTER,

        "candidate_adapter": latest_adapter,

        "average_score": average_score,

        "pass_rate": pass_rate,

        "evaluation": "FAIL",

    }

    with open(
        REGISTRY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            registry,
            f,
            ensure_ascii=False,
            indent=2
        )


    print(
        "\nRegistry saved:"
    )

    print(
        REGISTRY_FILE
    )

    print("\nAUTO PIPELINE COMPLETE")

    raise SystemExit(0)


# ==========================================
# PASS
# ==========================================

print("\n" + "=" * 70)
print("ACTIVATING NEW ADAPTER")
print("=" * 70)


os.makedirs(
    ACTIVE_DIR,
    exist_ok=True
)


if os.path.exists(
    ACTIVE_ADAPTER
):

    shutil.rmtree(
        ACTIVE_ADAPTER
    )


shutil.copytree(
    latest_adapter,
    ACTIVE_ADAPTER
)


# ==========================================
# REGISTRY
# ==========================================

registry = {

    "status": "active",

    "active_adapter": ACTIVE_ADAPTER,

    "candidate_adapter": latest_adapter,

    "previous_adapter": OLD_ADAPTER,

    "average_score": average_score,

    "pass_rate": pass_rate,

    "evaluation": "PASS",

}


with open(
    REGISTRY_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        registry,
        f,
        ensure_ascii=False,
        indent=2
    )


# ==========================================
# DONE
# ==========================================

print("\n" + "=" * 70)
print("AUTO ACTIVATION COMPLETE")
print("=" * 70)

print(
    "Active adapter:"
)

print(
    ACTIVE_ADAPTER
)

print(
    "\nRegistry:"
)

print(
    REGISTRY_FILE
)