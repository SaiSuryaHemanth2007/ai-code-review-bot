# 🤖 AI Code Review Bot

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116-green?logo=fastapi)
![GitHub Actions](https://img.shields.io/github/actions/workflow/status/SaiSuryaHemanth2007/ai-code-review-bot/tests.yml?branch=main&label=CI)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Tests](https://img.shields.io/badge/Tests-8%20Passed-success)
![AI](https://img.shields.io/badge/AI-Groq%20%7C%20Gemini-purple)

> AI-powered GitHub Pull Request Review System built with FastAPI, Groq, Gemini, and GitHub API.

> An AI-powered GitHub Pull Request Review System built with **FastAPI**, **Groq**, **Gemini**, and the **GitHub API**.

Automatically reviews GitHub Pull Requests, generates intelligent AI feedback, posts inline review comments, caches results, tracks review history, and provides production-ready monitoring APIs.

---

# 🚀 Features

- 🤖 AI-powered Pull Request Reviews
- 🧠 Multi-AI Provider Architecture
  - Groq
  - Gemini
  - Automatic Provider Fallback
- 💬 GitHub Inline Review Comments
- 📝 GitHub PR Summary Comments
- 📂 Smart Diff Mapping
- ⚡ Background Review Jobs
- 🔁 Automatic Retry Mechanism
- 💾 SQLite Review Cache
- 📚 Review History
- 📊 Metrics API
- ❤️ Health Check API
- 🔒 Secure GitHub Webhooks
- 🧪 Automated Testing using Pytest
- ⚙️ GitHub Actions CI/CD
- 🐳 Docker Support
- 📖 Interactive Swagger Documentation

---

# 🏗️ Architecture

```text
                    GitHub Pull Request
                             │
                             ▼
                    GitHub Webhook
                             │
                             ▼
                     FastAPI Backend
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
  Background Jobs      AI Service Router     Review Cache
        │                    │                    │
        │             ┌──────┴──────┐             │
        │             │             │             │
        ▼             ▼             ▼             ▼
     Groq AI      Gemini AI      Future AI     SQLite
        │
        ▼
 Inline GitHub Review Comments
        │
        ▼
 Pull Request Summary Comment
```

---

# 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.12 |
| Framework | FastAPI |
| AI | Groq, Gemini |
| GitHub | PyGithub |
| Database | SQLite |
| Testing | Pytest |
| CI/CD | GitHub Actions |
| Server | Uvicorn |
| Container | Docker |

---

# 📂 Project Structure

```text
AI-CODE-REVIEW-BOT
│
├── backend
│   ├── api
│   ├── config
│   ├── core
│   ├── data
│   ├── exceptions
│   ├── jobs
│   ├── models
│   ├── prompts
│   ├── schemas
│   ├── services
│   │   └── providers
│   ├── utils
│   └── main.py
│
├── tests
│
├── .github
│   └── workflows
│
├── Dockerfile
├── requirements.txt
├── README.md
└── .env
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/<your-username>/ai-code-review-bot.git

cd ai-code-review-bot
```

---

## Create Virtual Environment

Windows

```bash
python -m venv venv

venv\Scripts\activate
```

Linux/macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment

Create a `.env` file.

```env
APP_NAME=AI Code Review Bot
APP_VERSION=1.0.0
DEBUG=True

GITHUB_TOKEN=your_github_token
GITHUB_OWNER=your_username
GITHUB_REPOSITORY=repository_name

GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.3-70b-versatile

GEMINI_API_KEY=your_gemini_key

WEBHOOK_SECRET=your_webhook_secret
```

---

# ▶️ Run Application

```bash
uvicorn backend.main:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

---

# 📖 API Endpoints

## GitHub

| Method | Endpoint |
|---------|----------|
| GET | /api/v1/github/repository |
| GET | /api/v1/github/pulls |
| GET | /api/v1/github/pulls/{id}/files |

---

## Review

| Method | Endpoint |
|---------|----------|
| POST | /api/v1/review |
| GET | /api/v1/review/jobs |

---

## Dashboard

| Method | Endpoint |
|---------|----------|
| GET | /api/v1/dashboard/providers |
| GET | /api/v1/dashboard/repositories |
| GET | /api/v1/dashboard/leaderboard |

---

## Monitoring

| Method | Endpoint |
|---------|----------|
| GET | /api/v1/health |
| GET | /api/v1/metrics |

---

## Webhooks

| Method | Endpoint |
|---------|----------|
| POST | /api/v1/webhooks/github |

---

# 🤖 AI Review Flow

```text
Developer
    │
    ▼
Push Code
    │
    ▼
GitHub Pull Request
    │
    ▼
Webhook Trigger
    │
    ▼
Background Review Job
    │
    ▼
AI Router
    │
 ┌──┴──────────────┐
 │                 │
 ▼                 ▼
Groq           Gemini
 │                 │
 └───────┬─────────┘
         ▼
Review Parser
         ▼
Smart Diff Mapper
         ▼
GitHub Inline Comments
         ▼
PR Summary Comment
```

---

# 🧪 Testing

Run all tests

```bash
python -m pytest tests/
```

Run a single test

```bash
python -m pytest tests/test_health.py
```

Current test coverage includes:

- Health API
- Metrics API
- Retry Utility
- Cache Database
- Diff Mapper
- AI Service

---

# ⚙️ GitHub Actions

Every push and Pull Request automatically runs:

- Install Dependencies
- Execute Pytest
- Verify Build

---

# 🐳 Docker

Build

```bash
docker build -t ai-code-review-bot .
```

Run

```bash
docker run -p 8000:8000 ai-code-review-bot
```

---

# 📈 Current Capabilities

- AI Pull Request Reviews
- Multi-provider AI Routing
- Automatic Provider Failover
- GitHub Webhooks
- Background Processing
- SQLite Cache
- Review History
- Inline Comments
- Metrics
- Health Checks
- Automated Testing
- CI/CD Pipeline

---

# 🔮 Future Enhancements

- OpenAI Support
- Ollama Support
- Anthropic Claude
- SonarQube Integration
- Slack Notifications
- Microsoft Teams Integration
- Email Reports
- Kubernetes Deployment
- Redis Queue
- PostgreSQL Support

---

# 📊 Project Status

| Component | Status |
|----------|--------|
| Backend | ✅ Complete |
| GitHub Integration | ✅ Complete |
| AI Review | ✅ Complete |
| Background Jobs | ✅ Complete |
| Diff Mapping | ✅ Complete |
| Inline Comments | ✅ Complete |
| Health API | ✅ Complete |
| Metrics API | ✅ Complete |
| Cache | ✅ Complete |
| Testing | ✅ Complete |
| GitHub Actions | ✅ Complete |

---

# 👨‍💻 Author

**Sai Surya Hemanth Sanapathi**

Computer Science Engineering Student

Backend Developer • AI Enthusiast • Open Source Contributor

GitHub:
https://github.com/SaiSuryaHemanth2007

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub!
