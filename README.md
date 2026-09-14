# DAI-Legal-Model

AI Legal Assistant using Large Language Model (LLM), Retrieval-Augmented Generation (RAG), and Model Context Protocol (MCP).

## 📌 Overview

DAI-Legal-Model is an AI-powered legal assistant designed to support users in searching, retrieving, and understanding legal information.

The system combines:

- **Large Language Model (LLM)** for natural language understanding and answer generation.
- **Retrieval-Augmented Generation (RAG)** for retrieving relevant legal documents before generating responses.
- **Model Context Protocol (MCP)** for connecting the AI model with external tools and services.
- **FastAPI** for providing backend APIs.
- **Frontend (FE)** for interacting with the legal assistant.

The main goal of the project is to build a prototype legal AI system that can provide answers based on relevant legal knowledge rather than relying only on the model's internal knowledge.

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
                  ┌──────────┴──────────┐
                  │                     │
                  ▼                     ▼
          ┌──────────────┐      ┌──────────────┐
          │     RAG      │      │     MCP      │
          │ Retrieval    │      │    Server    │
          └──────┬───────┘      └──────┬───────┘
                 │                     │
                 └──────────┬──────────┘
                            ▼
                    ┌──────────────┐
                    │     LLM      │
                    │ Legal Model  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Response   │
                    └──────────────┘
```

---

## 📂 Project Structure

```text
DAI-Legal-Model/
│
├── backend/                  # Backend services
│
├── FE/                       # Frontend application
│
├── dataset/                  # Dataset and legal documents
│
├── outputs/                  # Training/model outputs
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
├── .gitignore                # Git ignore configuration
└── README.md                 # Project documentation
```

---

## ⚙️ Technologies

| Component | Technology |
|---|---|
| Programming Language | Python |
| LLM | Qwen |
| Fine-tuning | LoRA / PEFT |
| Retrieval | RAG |
| AI Tool Integration | MCP |
| Backend | FastAPI |
| Frontend | FE |
| API Communication | HTTP |
| Version Control | Git / GitHub |

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/AnNguyen0806/DAI-Legal-Model.git
cd DAI-Legal-Model
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

Activate the environment:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

If the project contains `requirements.txt`:

```bash
pip install -r requirements.txt
```

If dependencies are not yet defined, install the required packages according to the individual Python modules.

---

## 🧠 Model Training

The project contains scripts for training and testing the legal language model.

Main training script:

```bash
python train.py
```

Training outputs are stored locally in the `outputs/` directory.

> Model checkpoints and large model files are excluded from GitHub using `.gitignore`.

---

## 🔎 RAG Pipeline

The RAG pipeline follows the general process:

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

RAG helps the system retrieve relevant legal information before generating an answer, reducing the risk of generating responses without supporting context.

---

## 🔌 MCP Integration

The project uses **Model Context Protocol (MCP)** to provide a standardized way for the AI system to interact with external tools and services.

MCP server:

```bash
python mcp_server.py
```

The MCP layer can be extended with additional tools depending on the requirements of the project.

---

## 🌐 Running the API

The backend is implemented using FastAPI.

Example:

```bash
uvicorn model_api:app --reload
```

The API can then be accessed locally through:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 🧪 Model Testing

Test the base Qwen model:

```bash
python test_qwen.py
```

Test the trained model:

```bash
python test_trained.py
```

Test the second trained version:

```bash
python test_trained_v2.py
```

---

## 📊 Model Evaluation

Run evaluation:

```bash
python evaluate.py
```

Evaluation results are stored in:

```text
evaluation_results.json
```

The evaluation process is used to compare model responses and assess the performance of the trained model.

---

## 👥 Team Collaboration

This repository is used for collaborative development.

### Recommended workflow

Before starting work:

```bash
git pull origin main
```

After modifying the code:

```bash
git add .
git commit -m "Describe your changes"
git push origin main
```

For larger features, create a separate branch:

```bash
git checkout -b feature-name
```

Then push the branch:

```bash
git push -u origin feature-name
```

After testing, create a Pull Request to merge the changes into `main`.

### Important

Do not commit:

- `.venv/`
- `__pycache__/`
- `.env`
- Large model files
- Training checkpoints
- Temporary files

These files are excluded using `.gitignore`.

---

## 🔐 Security

Do not commit sensitive information such as:

```text
.env
API keys
Access tokens
Passwords
Private credentials
```

Use environment variables for sensitive configuration.

---

## 🛠️ Development Status

Current project components:

- [x] LLM model testing
- [x] Model fine-tuning
- [x] LoRA training
- [x] Model evaluation
- [x] FastAPI backend
- [x] MCP server
- [x] RAG architecture
- [ ] Further RAG optimization
- [ ] Improve legal-domain evaluation
- [ ] Improve frontend
- [ ] Integrate additional legal tools
- [ ] Final system integration

---

## 📚 Project Goal

The project aims to develop an AI legal assistant capable of:

1. Understanding natural-language legal questions.
2. Retrieving relevant legal information.
3. Using retrieved context to generate answers.
4. Connecting with external tools through MCP.
5. Providing a practical interface for users.
6. Improving answer reliability through RAG and domain-specific fine-tuning.

---

## ⚠️ Disclaimer

This project is an academic/research prototype.

The generated information should not be considered a substitute for professional legal advice. Users should verify important legal information against official legal documents and consult qualified legal professionals when necessary.

---

## 📄 License

This project is currently for academic and research purposes.
