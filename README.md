# DAI-Legal-Model

AI Legal Assistant using Large Language Model (LLM), Retrieval-Augmented Generation (RAG), and Model Context Protocol (MCP).

## 📌 Overview

DAI-Legal-Model is an AI-powered legal assistant designed to support users in searching, retrieving, and understanding legal information.

The system combines:

- **Large Language Model (LLM)** for natural language understanding and answer generation.
- **Retrieval-Augmented Generation (RAG)** for retrieving relevant legal documents before generating responses.
- **Model Context Protocol (MCP)** for connecting the AI system with external tools and services.
- **FastAPI** for backend API services.
- **Frontend (FE)** for user interaction.
- **LoRA / PEFT** for domain-specific model fine-tuning.

This project is developed as an academic/research prototype for applying LLM, RAG, MCP, and fine-tuning techniques to the legal domain.

---

## 🏗️ System Architecture

```text
                         ┌──────────────────┐
                         │    Frontend      │
                         │       (FE)       │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │     Backend      │
                         └────────┬─────────┘
                                  │
                     ┌────────────┴────────────┐
                     │                         │
                     ▼                         ▼
              ┌──────────────┐         ┌──────────────┐
              │     RAG      │         │     MCP      │
              │  Retrieval   │         │    Server    │
              └──────┬───────┘         └──────┬───────┘
                     │                         │
                     └────────────┬────────────┘
                                  ▼
                         ┌──────────────────┐
                         │       LLM        │
                         │   Legal Model    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     Response     │
                         └──────────────────┘
```

---

## 📂 Project Structure

```text
DAI-Legal-Model/
│
├── backend/                  # Backend services
├── FE/                       # Frontend application
├── dataset/                  # Dataset and legal documents
│
├── ai_service.py             # AI service
├── demo_model.py             # Model demonstration
├── evaluate.py               # Model evaluation
├── evaluation_results.json   # Evaluation results
├── mcp_server.py             # MCP server
├── model_api.py              # Model API
│
├── test_qwen.py              # Test base Qwen model
├── test_trained.py           # Test trained model
├── test_trained_v2.py        # Test trained model V2
│
├── train.py                  # Model training
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore configuration
└── README.md                 # Project documentation
```

> `outputs/`, `.venv/`, `__pycache__/`, model checkpoints, and other large/generated files are excluded from Git using `.gitignore`.

---

## ⚙️ Technologies

| Component | Technology |
|---|---|
| Programming Language | Python |
| Large Language Model | Qwen |
| Fine-tuning | LoRA / PEFT |
| Retrieval | RAG |
| AI Tool Integration | MCP |
| Backend | FastAPI |
| Frontend | FE |
| API Communication | HTTP |
| Version Control | Git / GitHub |

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/AnNguyen0806/DAI-Legal-Model.git
cd DAI-Legal-Model
```

## 2. Create a Python virtual environment

Windows:

```bash
python -m venv .venv
```

Activate the environment:

```bash
.venv\Scripts\activate
```

After activation, the terminal should show something similar to:

```text
(.venv) D:\DAI-Legal-Model>
```

## 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

# 🤖 Model

The project uses **Qwen** as the base Large Language Model.

The repository contains scripts for:

- Base model testing
- Fine-tuning
- LoRA / PEFT training
- Trained model testing
- Model evaluation

Large model files and checkpoints are intentionally excluded from GitHub.

---

# 🧠 Model Training

The main training script is:

```bash
python train.py
```

Training outputs are stored locally in:

```text
outputs/
```

The `outputs/` directory is excluded from GitHub to avoid uploading large model checkpoints.

---

# 🔎 RAG Pipeline

The RAG pipeline follows this process:

```text
User Question
      │
      ▼
Query Processing
      │
      ▼
Document Retrieval
      │
      ▼
Relevant Legal Documents
      │
      ▼
Context + User Question
      │
      ▼
LLM
      │
      ▼
Generated Answer
```

RAG allows the system to retrieve relevant legal information and provide it as context to the language model before generating an answer.

---

# 🔌 MCP Integration

The project uses **Model Context Protocol (MCP)** to provide a standardized interface between the AI system and external tools or services.

The MCP server is implemented in:

```text
mcp_server.py
```

Run the MCP server with:

```bash
python mcp_server.py
```

---

# 🌐 Running the Backend API

The backend API uses **FastAPI**.

Run:

```bash
uvicorn model_api:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🖥️ Frontend

The frontend source code is located in:

```text
FE/
```

Navigate to the frontend directory:

```bash
cd FE
```

The exact frontend installation and startup commands depend on the frontend framework and package configuration.

---

# 🧪 Model Testing

### Test the base Qwen model

```bash
python test_qwen.py
```

### Test the trained model

```bash
python test_trained.py
```

### Test trained model V2

```bash
python test_trained_v2.py
```

---

# 📊 Model Evaluation

Run the evaluation script:

```bash
python evaluate.py
```

Evaluation results are stored in:

```text
evaluation_results.json
```

---

# 🧩 Demo

The project contains a model demonstration script:

```bash
python demo_model.py
```

Depending on the current configuration, additional services such as the FastAPI backend, MCP server, or frontend may need to be started separately.

---

# 👥 Team Collaboration

This repository is used for collaborative development.

## Recommended Git workflow

Do not directly modify `main` when working on a new feature.

Create a feature branch:

```bash
git checkout -b feature/your-feature-name
```

Example:

```bash
git checkout -b feature/rag
```

After modifying the code:

```bash
git add .
git commit -m "Add RAG functionality"
git push -u origin feature/rag
```

Then create a **Pull Request** on GitHub to merge the feature branch into `main`.

### Before starting new work

```bash
git checkout main
git pull origin main
```

Then create a new feature branch:

```bash
git checkout -b feature/your-feature-name
```

### Recommended branch structure

```text
main
│
├── feature/backend
├── feature/frontend
├── feature/rag
└── feature/ai-model
```

The `main` branch should contain the stable version of the project.

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

# 🚫 Files Excluded From Git

The following files/directories are excluded through `.gitignore`:

```text
.venv/
__pycache__/
outputs/
checkpoints/
runs/
*.bin
*.safetensors
*.pt
*.pth
*.gguf
.env
```

Large model checkpoints should be stored separately rather than committed directly to the repository.

---

# 🛠️ Development Status

Current project components:

- [x] LLM model testing
- [x] Qwen model integration
- [x] LoRA / PEFT fine-tuning
- [x] Model evaluation
- [x] FastAPI backend
- [x] MCP server
- [x] Initial RAG architecture
- [x] Dataset integration
- [x] Frontend application
- [ ] Further RAG optimization
- [ ] Improve legal-domain evaluation
- [ ] Improve frontend
- [ ] Integrate additional legal tools
- [ ] Final system integration

---

# 🎯 Project Goal

The project aims to develop an AI legal assistant capable of:

1. Understanding natural-language legal questions.
2. Retrieving relevant legal information.
3. Using retrieved context to generate answers.
4. Connecting with external tools through MCP.
5. Providing a practical user interface.
6. Improving answer reliability through RAG.
7. Applying domain-specific fine-tuning to the legal language model.

---

# ⚠️ Disclaimer

This project is an academic/research prototype.

The generated information should **not** be considered a substitute for professional legal advice.

Users should verify important legal information against official legal documents and consult qualified legal professionals when necessary.

---

# 📄 License

This project is currently intended for academic and research purposes.
