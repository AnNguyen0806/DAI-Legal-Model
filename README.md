# DAI-Legal-Model

> **AI Legal Assistant for Vietnamese administrative procedures**  
> Qwen2.5-7B-Instruct + LoRA V3 + RAG + Qdrant + MCP + FastAPI + React/Vite

## 📌 Overview

DAI-Legal-Model is an academic/research prototype for a Vietnamese legal assistant. The system combines a domain-adapted Large Language Model (LLM) with Retrieval-Augmented Generation (RAG) so that answers can be grounded in retrieved legal administrative-procedure data.

The project currently supports:

- Vietnamese legal-domain question answering
- LoRA/QLoRA fine-tuning of Qwen2.5-7B-Instruct
- Semantic legal-document retrieval with Qdrant
- MCP tools for legal procedure search
- FastAPI Core API and Model API
- React/Vite web frontend
- Public Internet access through Cloudflare Tunnel
- Deployment on a local RTX 4070 12GB machine

---

## 🏗️ System Architecture

```text
                         Internet
                            │
                            ▼
                  ┌─────────────────────┐
                  │  Cloudflare Tunnel  │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │      Frontend       │
                  │    React / Vite     │
                  │     :5173           │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │      Core API       │
                  │      FastAPI        │
                  │       :8000         │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │     MCP Server      │
                  │      stdio tools    │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │       Qdrant        │
                  │   collection:       │
                  │     legal_docs      │
                  └──────────┬──────────┘
                             │
                       Retrieved Context
                             │
                             ▼
                  ┌─────────────────────┐
                  │      Model API      │
                  │      FastAPI        │
                  │       :8001         │
                  │ Qwen2.5-7B + LoRA V3│
                  └──────────┬──────────┘
                             │
                             ▼
                     Grounded Answer
```

### Core principle

**LoRA** is used mainly to adapt the model's legal-domain response behavior, while **RAG** provides the factual context used for administrative-procedure questions.

The MCP retrieval layer prioritizes an exact procedure-name match when possible and then fills the remaining results with semantically relevant documents.

---

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

The current Core API limits the main retrieved context before sending it to the model to avoid excessive inference latency and request timeouts.

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

Qdrant is used as the vector database.

Default address:

```text
http://localhost:6333
```

Collection:

```text
legal_docs
```

Embedding model:

```text
bkai-foundation-models/vietnamese-bi-encoder
```

Start Qdrant with Docker:

```powershell
docker compose up -d
```

Download the DVC dataset:

```powershell
python download_dvc_dataset.py
```

Import the DVC procedure data:

```powershell
python backend/import_dvc_to_qdrant.py
```

The import script adds DVC data to the existing `legal_docs` collection and does not delete the existing collection.

---

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
│   ├── src/
│   ├── index.html
│   └── vite.config.js
│
├── data/
│   ├── dichvucong_procedures/
│   ├── legal_train_v3/
│   └── vietnamese-legal-instruct/
│
├── dataset/
│
├── mcp_server.py
├── model_api.py
├── train_v3.py
├── test_trained_v3.py
├── download_dvc_dataset.py
├── download_legal_dataset.py
├── prepare_legal_dataset.py
├── check_dataset.py
├── requirements.txt
├── docker-compose.yml
├── .gitignore
├── .gitattributes
└── README.md
```

---

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

## 🔄 Current Development Status

### Completed

- [x] Qwen2.5-7B-Instruct inference
- [x] LoRA V3 fine-tuning
- [x] Vietnamese legal instruction dataset preparation
- [x] DVC procedure dataset integration
- [x] Qdrant vector database
- [x] RAG retrieval pipeline
- [x] MCP legal search tools
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
- [ ] Verify Qdrant Docker auto-start
- [ ] Capture screenshots for the academic report
- [ ] Prepare presentation slides and demo script

---

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
