# DAI-Legal-Model

> **AI Legal Assistant for Vietnamese administrative procedures**  
> Qwen2.5-7B-Instruct + LoRA V3 + BGE-M3 RAG + Qdrant + Reranker + MCP/DVC + FastAPI + React/Vite

## 📌 Overview

DAI-Legal-Model is an academic/research prototype for a Vietnamese legal assistant. The system combines a domain-adapted Large Language Model (LLM) with Retrieval-Augmented Generation (RAG), semantic reranking, and permission-controlled external retrieval so that answers can be grounded in Vietnamese administrative-procedure data.

The project currently supports:

- Vietnamese legal-domain question answering
- LoRA/QLoRA fine-tuning of Qwen2.5-7B-Instruct
- Semantic legal-document retrieval with Qdrant
- MCP tools for legal procedure search and DVC external retrieval
- Permission-gated fallback from Local RAG to external DVC retrieval
- Auto Fine-Tuning pipeline with validation, QLoRA training, evaluation, and adapter activation/rollback
- FastAPI Core API and Model API
- React/Vite web frontend
- Public Internet access through Cloudflare Tunnel
- Deployment on a local RTX 4070 12GB machine

---

## 🏗️ System Architecture

```text
USER
  ↓
FRONTEND (React / Vite)
  ↓
CORE API :8000
  ↓
ORCHESTRATOR
  ↓
SYNONYM MAPPING
  ↓
BGE-M3
  ↓
QUERY EMBEDDING
  ↓
QDRANT
  ↓
TOP-K
  ↓
BGE RERANKER
  ↓
ENOUGH DATA?
  ├── YES
  │    ↓
  │  LEGAL CONTEXT
  │    ↓
  │  QWEN2.5-7B + LORA V3
  │    ↓
  │  ANSWER
  │
  └── NO
       ↓
    ASK USER
       ↓
    USER ALLOW?
       ↓ YES
      MCP
       ↓
     DVC API
       ↓
   LEGAL CONTEXT
       ↓
  QWEN2.5-7B + LORA V3
       ↓
     ANSWER
```

### Core principle

**Local RAG is the primary retrieval path.** BGE-M3 converts the user query into an embedding, Qdrant retrieves candidate procedures, and BGE Reranker filters/reorders the candidates before the system decides whether the local evidence is sufficient.

**MCP is a fallback mechanism**, not the first retrieval path. When local evidence is insufficient, the system asks the user for permission before accessing the whitelisted DVC source.

**LoRA** adapts the model's legal-domain response behavior, while **RAG** supplies factual context for administrative-procedure questions.

## 🤖 Model

| Component | Configuration |
|---|---|
| Base model | `Qwen/Qwen2.5-7B-Instruct` |
| Fine-tuning | QLoRA / LoRA / PEFT |
| Adapter | `outputs/qwen-legal-lora-v3` |
| Quantization | 4-bit NF4 |
| Compute dtype | BF16 |
| GPU tested | NVIDIA RTX 4070 12GB |
| Training dataset | `duyet/vietnamese-legal-instruct` |

### V3 training

The V3 adapter was trained with:

- 4-bit NF4 quantization
- LoRA adapters
- BF16
- Gradient checkpointing
- Gradient accumulation
- Paged AdamW 8-bit optimizer
- Maximum sequence length: 2048
- Training data prepared under `data/legal_train_v3/`

Train with:

```powershell
python train_v3.py
```

The resulting adapter is saved to:

```text
outputs/qwen-legal-lora-v3/
```

Model checkpoints are intentionally excluded from Git because of their size.

---

## 📚 Datasets

### 1. Vietnamese Legal Instruction Dataset

```text
duyet/vietnamese-legal-instruct
```

Used primarily for legal-domain instruction fine-tuning.

### 2. National Public Service Portal Procedure Dataset

```text
tmquan/dichvucong-gov-vn
```

Used as the main RAG knowledge source for Vietnamese administrative procedures from the National Public Service Portal.

Local path:

```text
data/dichvucong_procedures/
```

### 3. Prepared V3 dataset

```text
data/legal_train_v3/
```

This is the processed dataset used by `train_v3.py`.

Large dataset files are stored in the repository using **Git LFS**.

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
Qdrant / legal_docs
     │
     ▼
Relevant legal procedure
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
Generated Answer
```

The current Core API limits and reranks the retrieved context before sending it to the model to reduce irrelevant context, hallucination risk, inference latency, and request timeouts.

---

## 🔌 MCP

MCP server:

```text
mcp_server.py
```

Available tools:

- `search_legal_documents`
- `search_procedure`

The Core API starts the MCP server as a subprocess, so a separate MCP terminal is normally **not required** for the full application.

Standalone test:

```powershell
python mcp_server.py
```

---

## 🗄️ Qdrant

Qdrant is used as the local vector database for the Local RAG pipeline.

Default address:

```text
http://localhost:6333
```

Current collection:

```text
legal_docs_bge_m3
```

Embedding model:

```text
BAAI/bge-m3
```

Vector size:

```text
1024
```

Distance:

```text
COSINE
```

The current DVC import workflow uses:

```powershell
python backend/import_dvc_to_qdrant.py
```

The system uses Qdrant as the primary local knowledge base before considering external MCP retrieval.

## 🌐 Web Frontend

Frontend technology:

- React
- Vite
- Tailwind CSS
- Lucide React

Local development server:

```text
http://localhost:5173
```

The browser tab is configured as:

```text
AI Pháp Lý
```

The frontend communicates with the Core API through the `/api/v1/chat/completions` endpoint using streaming responses.

---

## 🌍 Internet Deployment

The application has been exposed to the Internet using **Cloudflare Tunnel** while keeping the model running on the local RTX 4070 machine.

Current routing:

```text
legal.donghai.uk
        │
        ▼
localhost:5173
Frontend
```

```text
api.donghai.uk
        │
        ▼
localhost:8000
Core API
```

The Cloudflare agent is installed as a Windows Service.

Verified deployment flow:

```text
Other Device
     │
     ▼
Internet
     │
     ▼
Cloudflare Tunnel
     │
     ├── Frontend :5173
     │
     └── Core API :8000
              │
              ▼
         MCP + Qdrant
              │
              ▼
       Model API :8001
              │
              ▼
     Qwen2.5-7B + LoRA V3
```

The system has been tested from another device through the public domain.

> The local PC must remain powered on and connected to the Internet for the public demo to remain available.

---

## 📂 Project Structure

```text
DAI-Legal-Model/
│
├── backend/
│   ├── main.py
│   └── import_dvc_to_qdrant.py
│
├── FE/
│   └── src/
│       ├── App.jsx
│       └── api.js
│
├── auto_finetune/
│   ├── auto_activation.py
│   ├── auto_evaluator.py
│   ├── auto_trainer.py
│   ├── dataset_formatter.py
│   ├── dataset_manager.py
│   ├── dataset_validator.py
│   ├── run_auto.py
│   └── datasets/
│       └── current/
│
├── mcp_server.py
├── model_api.py
├── run_test_cases.py
├── test_reranker.py
├── requirements.txt
├── .gitignore
└── README.md
```

Large datasets, model checkpoints, local databases, and runtime-generated files should not be committed to the repository unless they are intentionally managed through Git LFS or another artifact-storage mechanism.

## ⚙️ Installation

### 1. Clone repository

```powershell
git clone https://github.com/AnNguyen0806/DAI-Legal-Model.git
cd DAI-Legal-Model
```

### 2. Git LFS

Install Git LFS and initialize it:

```powershell
git lfs install
git lfs pull
```

The repository contains several GB of dataset files, so sufficient disk space and Git LFS quota are required.

### 3. Create Python environment

Windows:

```powershell
python -m venv .venv
.\.venv\Scriptsctivate
```

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📥 Dataset Preparation

Download the DVC procedure dataset:

```powershell
python download_dvc_dataset.py
```

Download the legal instruction dataset:

```powershell
python download_legal_dataset.py
```

Prepare the V3 training data:

```powershell
python prepare_legal_dataset.py
```

Inspect the prepared dataset:

```powershell
python check_dataset.py
```

---

## ▶️ Running the Full System

The application uses three main services.

### 1. Model API

```powershell
cd D:\DAI-Legal-Model
.\.venv\Scriptsctivate
python model_api.py
```

Model API:

```text
http://localhost:8001
```

### 2. Core API

Open another terminal:

```powershell
cd D:\DAI-Legal-Model
.\.venv\Scriptsctivate
python backend\main.py
```

Core API:

```text
http://localhost:8000
```

### 3. Frontend

Open another terminal:

```powershell
cd D:\DAI-Legal-Model\FE
npm run dev
```

Frontend:

```text
http://localhost:5173
```

MCP is automatically launched by the Core API during normal operation.

---

## 🧪 Testing

### Test the trained model

```powershell
python test_trained_v3.py
```

### Test the MCP server

```powershell
python mcp_server.py
```

### Recommended RAG questions

Examples:

```text
Thủ tục đăng ký tạm trú cần những giấy tờ gì?

Đăng ký kết hôn mất bao lâu?

Chứng thực chữ ký mất bao lâu?

Lệ phí đăng ký tạm trú là bao nhiêu?

Đăng ký tạm trú thực hiện ở đâu?
```

When evaluating the system, pay attention to:

- Retrieval relevance
- Exact procedure matching
- Factual grounding
- Hallucination
- Answer completeness
- Response latency

---

## 🔄 Auto Fine-Tuning

The project includes an automated fine-tuning pipeline under `auto_finetune/`:

```text
Dataset
  ↓
Validation
  ↓
Formatting
  ↓
QLoRA Training
  ↓
Evaluation
  ↓
Activation / Rollback
```

A new dataset can be placed into the current dataset directory and processed by `run_auto.py`. The candidate adapter is activated only when evaluation passes; otherwise the previously active adapter is retained.

Run:

```powershell
python auto_finetune/run_auto.py
```

## 🔄 Current Development Status

### Completed

- [x] Qwen2.5-7B-Instruct inference
- [x] LoRA V3 fine-tuning
- [x] Auto Fine-Tuning pipeline
- [x] Vietnamese legal instruction dataset preparation
- [x] DVC procedure dataset integration
- [x] Qdrant vector database
- [x] BGE-M3 RAG retrieval pipeline
- [x] BGE Reranker
- [x] MCP legal search tools
- [x] Permission-controlled external retrieval
- [x] FastAPI Core API
- [x] FastAPI Model API
- [x] React/Vite frontend
- [x] Streaming AI responses
- [x] Frontend UI update
- [x] Git LFS dataset storage
- [x] Cloudflare Tunnel deployment
- [x] Public Internet testing from another device

### Next steps

- [ ] Add deterministic legal source references to generated answers
- [ ] Run a larger legal-question evaluation set
- [ ] Record retrieval and answer-quality results
- [ ] Create `start.bat` for one-click startup
- [ ] Revisit Docker packaging after native demo is stable
- [ ] Capture screenshots for the academic report
- [ ] Prepare presentation slides and demo script

---

## ⚠️ Limitations

- Retrieval quality depends on the quality and coverage of the local legal dataset.
- External DVC search may return noisy or partially mismatched procedures, so procedure matching remains an important limitation.
- The multi-stage pipeline can increase response latency compared with direct LLM inference.
- RAG reduces hallucination risk but cannot guarantee that generated answers are always correct.
- The current knowledge scope focuses strongly on Vietnamese administrative procedures and does not represent the complete body of Vietnamese law.
- External retrieval depends on the availability and response quality of the DVC source.

## ⚠️ Disclaimer

This project is an **academic/research prototype** and is not a substitute for professional legal advice.

Legal procedures, fees, required documents, processing times, and regulations may change. Users should verify important information against current official sources before taking legal or administrative action.

---

## 👨‍💻 Project

**DAI-Legal-Model**

Vietnamese Legal AI Assistant using:

```text
Qwen2.5-7B-Instruct
        +
LoRA / QLoRA
        +
RAG
        +
Qdrant
        +
MCP
        +
FastAPI
        +
React / Vite
        +
Cloudflare Tunnel
```
