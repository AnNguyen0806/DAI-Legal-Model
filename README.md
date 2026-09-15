# DAI-Legal-Model

AI Legal Assistant using **Qwen2.5-7B-Instruct**, **QLoRA/LoRA**, **Retrieval-Augmented Generation (RAG)**, **Model Context Protocol (MCP)**, **Qdrant**, **FastAPI**, and a web frontend.

## 📌 Overview

DAI-Legal-Model is an academic/research prototype for a Vietnamese legal assistant. The system combines a domain-adapted language model with retrieval of legal administrative-procedure data before answer generation.

### Main components

- **LLM:** Qwen2.5-7B-Instruct
- **Fine-tuning:** QLoRA / LoRA / PEFT
- **RAG:** semantic retrieval of legal procedures from Qdrant
- **Vector database:** Qdrant
- **MCP:** tool interface for legal-document and procedure search
- **Model API:** FastAPI service on port `8001`
- **Core API:** FastAPI service on port `8000`
- **Frontend:** web application on port `5173`
- **Embedding model:** `bkai-foundation-models/vietnamese-bi-encoder`
- **Hardware tested:** NVIDIA RTX 4070 12GB

---

## 🏗️ System Architecture

```text
┌──────────────────────┐
│      Frontend        │
│   localhost:5173     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      Core API        │
│   FastAPI :8000      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      MCP Server      │
│     stdio tools      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│       Qdrant         │
│    legal_docs        │
└──────────┬───────────┘
           │ retrieved context
           ▼
┌──────────────────────┐
│      Model API       │
│   FastAPI :8001      │
│ Qwen2.5-7B + LoRA V3 │
└──────────┬───────────┘
           │
           ▼
      Generated Answer
```

The current pipeline uses **RAG for factual grounding** and **LoRA fine-tuning for domain-specific response behavior**. Retrieved legal-procedure context is provided to Qwen before answer generation.

---

## 📂 Project Structure

```text
DAI-Legal-Model/
│
├── backend/
│   ├── main.py                    # Core API / RAG orchestration
│   └── import_dvc_to_qdrant.py    # Import DVC dataset into Qdrant
│
├── FE/                            # Frontend application
│
├── data/                          # Local datasets (Git LFS)
│   ├── dichvucong_procedures/
│   ├── legal_train_v3/
│   └── vietnamese-legal-instruct/
│
├── dataset/                       # Earlier project dataset
│
├── mcp_server.py                  # MCP legal search tools
├── model_api.py                   # Qwen + LoRA inference API
├── train_v3.py                    # QLoRA V3 training
├── test_trained_v3.py             # V3 model testing
├── download_dvc_dataset.py        # Download DVC procedure dataset
├── download_legal_dataset.py      # Download legal instruction dataset
├── prepare_legal_dataset.py       # Prepare/filter training data
├── check_dataset.py               # Dataset inspection
│
├── train.py                       # Earlier training script
├── test_qwen.py                   # Base model test
├── test_trained.py                # Earlier trained model test
├── test_trained_v2.py             # V2 model test
├── evaluate.py                    # Evaluation script
├── demo_model.py                  # Model demo
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
├── .gitattributes                 # Git LFS configuration
└── README.md                      # Project documentation
```

> Model checkpoints in `outputs/` and the Python virtual environment are not stored in Git. The large dataset files under `data/` are tracked with **Git LFS**.

---

## 🤖 Model

The current model uses:

```text
Base model: Qwen/Qwen2.5-7B-Instruct
Fine-tuning: QLoRA / LoRA
Adapter: outputs/qwen-legal-lora-v3
Quantization: 4-bit NF4
GPU tested: RTX 4070 12GB
```

The V3 adapter was trained on Vietnamese legal instruction data. Fine-tuning is intended to improve legal-domain response behavior, while RAG provides the factual context used for current procedure information.

---

## 🧠 Model Training — V3

The V3 training data is prepared from the Vietnamese legal instruction dataset and saved locally in:

```text
 data/legal_train_v3/
```

Training is performed with `train_v3.py`.

```bash
python train_v3.py
```

The current V3 configuration uses QLoRA with 4-bit NF4 quantization, LoRA adapters, BF16, gradient checkpointing, gradient accumulation, and paged AdamW 8-bit optimization.

The trained adapter is saved to:

```text
outputs/qwen-legal-lora-v3/
```

> `outputs/` is excluded from the Git repository because model checkpoints are large. The training scripts remain in Git so the training process can be reproduced when the required base model and datasets are available.

---

## 📚 Datasets

### 1. Vietnamese Legal Instruction Dataset

Source:

```text
HF: duyet/vietnamese-legal-instruct
```

Used primarily for legal-domain instruction fine-tuning.

### 2. National Public Service Portal Procedure Dataset

Source:

```text
HF: tmquan/dichvucong-gov-vn
```

Used for the RAG knowledge base. It contains Vietnamese administrative procedures sourced from the National Public Service Portal.

The downloaded dataset is stored in:

```text
data/dichvucong_procedures/
```

### 3. Prepared V3 training dataset

```text
data/legal_train_v3/
```

This is the processed dataset used by `train_v3.py`.

---

## 🔎 RAG Pipeline

```text
User Question
      │
      ▼
Core API :8000
      │
      ▼
MCP search_legal_documents
      │
      ▼
Qdrant: legal_docs
      │
      ▼
Relevant legal procedure context
      │
      ▼
Prompt + retrieved context
      │
      ▼
Model API :8001
      │
      ▼
Qwen2.5-7B-Instruct + LoRA V3
      │
      ▼
Grounded answer
```

The MCP retrieval layer prioritizes an exact procedure-name match when possible and then fills the remaining results with semantically relevant documents.

---

## 🔌 MCP Integration

The MCP server is implemented in:

```text
mcp_server.py
```

Current tools include:

- `search_legal_documents`
- `search_procedure`

The Core API launches the MCP server as a subprocess, so a separate MCP terminal is normally **not required** when running the full application.

For standalone MCP testing:

```bash
python mcp_server.py
```

---

## 🗄️ Qdrant

The project uses Qdrant as the vector database.

Default address:

```text
http://localhost:6333
```

Collection:

```text
legal_docs
```

Qdrant can be run through Docker. Example:

```bash
docker compose up -d
```

After downloading the DVC dataset, import it into Qdrant with:

```bash
python backend/import_dvc_to_qdrant.py
```

> The import script adds the DVC procedure data to the existing `legal_docs` collection and does not delete the existing collection.

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/AnNguyen0806/DAI-Legal-Model.git
cd DAI-Legal-Model
```

## 2. Git LFS

The project stores large dataset files with Git LFS.

Install Git LFS and run:

```bash
git lfs install
```

Then retrieve LFS files after cloning:

```bash
git lfs pull
```

> The current dataset is several GB, so cloning/pulling the repository requires sufficient disk space and Git LFS bandwidth/storage quota.

## 3. Create Python environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

## 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

# 📥 Download Datasets

If the datasets are not already available locally, run:

```bash
python download_dvc_dataset.py
```

and:

```bash
python download_legal_dataset.py
```

Prepare the V3 training dataset with:

```bash
python prepare_legal_dataset.py
```

Inspect the dataset with:

```bash
python check_dataset.py
```

---

# ▶️ Running the Full System

The current system uses three main services.

## 1. Start Model API — Port 8001

From the project root:

```powershell
cd D:\DAI-Legal-Model
.\.venv\Scripts\activate
python model_api.py
```

The service runs at:

```text
http://localhost:8001
```

## 2. Start Core API — Port 8000

Open another terminal:

```powershell
cd D:\DAI-Legal-Model
.\.venv\Scripts\activate
python backend\main.py
```

The service runs at:

```text
http://localhost:8000
```

Core API responsibilities include:

- receiving frontend requests
- calling MCP tools
- retrieving legal context from Qdrant
- constructing the grounded prompt
- calling the Model API
- streaming the answer back to the frontend

## 3. Start Frontend — Port 5173

Open another terminal:

```powershell
cd D:\DAI-Legal-Model\FE
npm install
npm run dev
```

The frontend is available at:

```text
http://localhost:5173/
```

---

# 🧪 Testing

### Test V3 model directly

```bash
python test_trained_v3.py
```

### Test the base Qwen model

```bash
python test_qwen.py
```

### Earlier model tests

```bash
python test_trained.py
python test_trained_v2.py
```

### Evaluation

```bash
python evaluate.py
```

---

# 🧪 Suggested RAG Tests

Example questions for evaluating retrieval and grounding:

```text
1. Thủ tục đăng ký tạm trú cần những giấy tờ gì?
2. Đăng ký tạm trú có mất phí không?
3. Đăng ký tạm trú mất bao lâu?
4. Có thể đăng ký tạm trú online không?
5. Thủ tục xóa đăng ký tạm trú cần những gì?
6. Thủ tục gia hạn tạm trú thực hiện như thế nào?
7. Đăng ký kết hôn cần những giấy tờ gì?
8. Đăng ký kết hôn mất bao lâu?
9. Chứng thực chữ ký cần những giấy tờ gì?
10. Chứng thực chữ ký mất bao lâu?
11. Cấp bản sao trích lục hộ tịch cần hồ sơ gì?
12. Thủ tục cấp giấy khai sinh cần những giấy tờ gì?
13. Thủ tục cấp hộ chiếu cần những giấy tờ gì?
14. Thủ tục đăng ký xe cần những giấy tờ gì?
15. Thủ tục không tồn tại trong dữ liệu cần những gì?
```

Evaluation should consider:

- **Retrieval quality** — whether the relevant procedure is retrieved.
- **Grounding** — whether the answer follows the retrieved legal context.
- **Hallucination** — whether unsupported facts are introduced.
- **Answer quality** — clarity, completeness, and relevance.

---

# 🔐 Security

Never commit sensitive information to GitHub.

Do not upload:

```text
.env
API keys
Access tokens
Passwords
Private credentials
```

Use environment variables for sensitive configuration.

---

# 🚫 Large / Generated Files

The following types of files should normally not be committed directly to Git:

```text
.venv/
__pycache__/
outputs/
*.safetensors
*.bin
*.pt
*.pth
*.gguf
.env
```

Large datasets under `data/` are currently tracked using **Git LFS**.

---

# 🛠️ Development Status

- [x] Qwen2.5-7B-Instruct integration
- [x] QLoRA / LoRA fine-tuning
- [x] LoRA V3 training
- [x] V3 model testing
- [x] Qdrant vector database
- [x] Legal procedure RAG
- [x] MCP server
- [x] Core FastAPI API
- [x] Model FastAPI API
- [x] Frontend application
- [x] DVC administrative-procedure dataset integration
- [x] Git LFS dataset storage
- [ ] Further RAG retrieval optimization
- [ ] More comprehensive legal-domain evaluation
- [ ] Further hallucination reduction
- [ ] Additional legal tools
- [ ] Production deployment

---

# 🎯 Project Goal

The project aims to develop an AI legal assistant capable of:

1. Understanding natural-language Vietnamese legal questions.
2. Retrieving relevant administrative procedures from a vector database.
3. Using retrieved context to ground generated answers.
4. Connecting the model to external tools through MCP.
5. Applying domain-specific LoRA fine-tuning.
6. Providing an interactive web interface.
7. Reducing hallucination through retrieval and grounding.

---

# ⚠️ Disclaimer

This project is an academic/research prototype.

Generated information should **not** be considered a substitute for professional legal advice. Important legal information should be verified against official legal documents and current government sources.

---

# 📄 License

This project is currently intended for academic and research purposes. Dataset licenses and source terms should be respected when redistributing or using the included data.
