# 🤖 AI Code Review Bot

> An AI-powered GitHub Pull Request review system built with FastAPI, Groq, Gemini, and the GitHub API.

AI Code Review Bot automatically analyzes GitHub Pull Requests, generates AI-powered code review feedback, posts inline review comments, maintains review history, caches review results, and exposes production monitoring APIs.

---

## ✨ Features

- 🤖 AI-powered Pull Request reviews
- 🧠 Multi-provider AI architecture
  - Groq
  - Gemini
  - Automatic provider fallback
- 💬 GitHub inline review comments
- 📊 Pull Request review summary reports
- 🔄 Automatic retry handling
- 💾 SQLite-based review cache
- 📚 Review history
- 📈 Metrics and monitoring APIs
- ❤️ Health check endpoint
- 🔒 GitHub webhook security
- ⚙️ Background review processing
- 🧪 Unit and integration test coverage
- 🔁 GitHub Actions CI/CD
- 🐳 Dockerized deployment
- 📖 Interactive Swagger/OpenAPI documentation

---

## 🏗️ Architecture

```text
                         GitHub Pull Request
                                  │
                                  ▼
                         GitHub Webhook Event
                                  │
                                  ▼
                           FastAPI Backend
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                │
                 ▼                ▼                ▼
          Background Jobs   AI Service Router   Review Cache
                                  │                │
                         ┌────────┴────────┐       │
                         │                 │       │
                         ▼                 ▼       ▼
                      Groq AI          Gemini AI  SQLite
                         │                 │
                         └────────┬────────┘
                                  ▼
                            Review Parser
                                  │
                                  ▼
                           Smart Diff Mapper
                                  │
                                  ▼
                     GitHub Inline Review Comments
                                  │
                                  ▼
                        Pull Request Summary
```

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.12 |
| Backend | FastAPI |
| AI Providers | Groq, Gemini |
| GitHub Integration | PyGithub / GitHub API |
| Database | SQLite |
| Testing | Pytest |
| Coverage | pytest-cov |
| CI/CD | GitHub Actions |
| Server | Uvicorn |
| Containerization | Docker |
| API Documentation | Swagger / OpenAPI |

---

## 📂 Project Structure

```text
ai-code-review-bot/
│
├── backend/
│   ├── api/
│   ├── config/
│   ├── core/
│   ├── data/
│   ├── exceptions/
│   ├── jobs/
│   ├── models/
│   ├── prompts/
│   ├── schemas/
│   ├── services/
│   │   └── providers/
│   ├── utils/
│   └── main.py
│
├── tests/
│   ├── integration/
│   └── ...
│
├── .github/
│   └── workflows/
│
├── Dockerfile
├── requirements.txt
├── README.md
└── .env
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Git
- GitHub token with the permissions required by the application
- Groq API key
- Gemini API key
- Docker (optional)

### Clone the Repository

```bash
git clone https://github.com/SaiSuryaHemanth2007/ai-code-review-bot.git
cd ai-code-review-bot
```

### Create a Virtual Environment

#### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

#### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Configuration

Create a `.env` file in the project root.

```env
APP_NAME=AI Code Review Bot
APP_VERSION=1.0.0
DEBUG=True

GITHUB_TOKEN=your_github_token
GITHUB_OWNER=your_username
GITHUB_REPOSITORY=repository_name

GROQ_API_KEY=your_groq_key
GROQ_MODEL=openai/gpt-oss-120b

GEMINI_API_KEY=your_gemini_key

WEBHOOK_SECRET=your_webhook_secret
```

> ⚠️ Never commit `.env`, API keys, GitHub tokens, or other secrets to source control.

---

## ▶️ Run Locally

Start the FastAPI application:

```bash
uvicorn backend.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 📖 API Endpoints

### GitHub

| Method | Endpoint |
|---|---|
| `GET` | `/api/v1/github/repository` |
| `GET` | `/api/v1/github/pulls` |
| `GET` | `/api/v1/github/pulls/{id}/files` |

### Review

| Method | Endpoint |
|---|---|
| `POST` | `/api/v1/review` |
| `GET` | `/api/v1/review/jobs` |

### Dashboard

| Method | Endpoint |
|---|---|
| `GET` | `/api/v1/dashboard/providers` |
| `GET` | `/api/v1/dashboard/repositories` |
| `GET` | `/api/v1/dashboard/leaderboard` |

### Monitoring

| Method | Endpoint |
|---|---|
| `GET` | `/api/v1/health` |
| `GET` | `/api/v1/metrics` |

### Webhooks

| Method | Endpoint |
|---|---|
| `POST` | `/api/v1/webhooks/github` |

---

## 🤖 AI Review Pipeline

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
GitHub Webhook
    │
    ▼
Background Review Job
    │
    ▼
AI Service Router
    │
    ├───────────────┐
    ▼               ▼
  Groq            Gemini
    │               │
    └───────┬───────┘
            ▼
      Review Parser
            │
            ▼
      Smart Diff Mapper
            │
            ▼
   GitHub Inline Comments
            │
            ▼
    PR Summary Report
```

The provider architecture allows the application to use multiple AI providers and fall back between providers when required.

---

## 🧪 Testing

### Run the Complete Test Suite

```bash
python -m pytest tests/
```

### Run with Coverage

```bash
python -m pytest --cov=backend --cov-report=term-missing
```

### Run a Focused Test

```bash
python -m pytest tests/test_health.py
```

### Latest Automated Test Result

The latest complete test run produced:

```text
251 passed
1443 statements
2 missed
99% total coverage
```

Focused health test:

```text
1 passed
```

### Test Areas

The automated suite includes unit and integration coverage for:

- Dashboard API
- GitHub API
- Health API
- History API
- Metrics API
- Review API
- Webhook API
- AI Service
- AI Providers
- Cache
- GitHub Event Service
- GitHub Service
- Review Service
- Review Worker
- Webhook Security
- Retry Logic
- Quality Scoring
- Exception Handling
- Job Management
- Logging

---

## 🔄 End-to-End Pull Request Validation

The production GitHub Pull Request review workflow was validated using a real cross-account Pull Request.

### E2E Flow

```text
Second GitHub Account
        │
        ▼
Surya228229/ai-code-review-bot
        │
        ▼
e2e/security-fix
        │
        ▼
Cross-Account Pull Request
        │
        ▼
SaiSuryaHemanth2007/ai-code-review-bot
        │
        ▼
GitHub pull_request Event
        │
        ▼
AI Code Review Bot
        │
        ▼
Review Processing
        │
        ├── Groq
        │
        └── Gemini
        │
        ▼
AI Review Generation
        │
        ▼
GitHub Inline Review Comments
        │
        ▼
Pull Request Summary
```

### E2E Validation

The E2E test validated:

- Cross-account Pull Request processing
- GitHub Pull Request event triggering
- Production review workflow
- AI-powered code analysis
- Security issue detection
- Maintainability issue detection
- Debug/test code detection
- Parameterized SQL false-positive filtering
- GitHub inline review comments
- AI review GitHub Check
- CI test GitHub Check
- Review cache behavior

### E2E Test Cases

| Test Case | Expected Behavior |
|---|---|
| Hardcoded password | Security issue detected |
| Hardcoded API key | Security issue detected |
| Parameterized SQL query | Should not be incorrectly flagged as SQL injection |
| Manual average calculation | Maintainability recommendation |
| Debug/test `print()` statements | Code-quality recommendation |
| Similar helper functions | Used to validate filtering behavior |

### Production E2E Review Result

The production AI reviewer generated:

```text
Quality Score: 66/100
Grade: C

Files Reviewed: 1
Issues Found: 4

Critical: 1
High: 0
Medium: 1
Low: 2
```

The review generated GitHub inline comments for findings including:

- Hardcoded password
- Hardcoded API key
- `calculate_average()` maintainability improvement
- Debug/test `print()` statements

The parameterized SQL queries were not incorrectly reported as SQL injection.

### GitHub Checks

The E2E Pull Request successfully completed:

```text
AI Code Review Bot / ai-review
Successful

AI Code Review Bot CI / test
Successful
```

The AI review was posted directly to the Pull Request as GitHub review comments and a summary report.

### E2E Test Safety

The Pull Request intentionally contained vulnerable test code and was closed without merging so the test code was not introduced into the production `main` branch.

### E2E Status

**E2E Integration Coverage: ✅ Complete**

Validated production path:

```text
GitHub Pull Request
        │
        ▼
GitHub pull_request Event
        │
        ▼
Review Processing
        │
        ▼
AI Provider
        │
        ▼
Review Generation
        │
        ▼
GitHub Inline Review Comments
        │
        ▼
GitHub AI Review Check
        │
        ▼
CI Validation
```

---

## ⚙️ GitHub Actions

Every push and Pull Request automatically runs the configured CI workflows.

The validated CI pipeline includes:

- Dependency installation
- Automated test execution
- Build verification
- AI Pull Request review workflow

Successful E2E validation confirmed both the AI review check and CI test check.

---

## 🐳 Docker

### Build

```bash
docker build -t ai-code-review-bot .
```

### Run

```bash
docker run -p 8000:8000 ai-code-review-bot
```

The production container is configured to:

- Use Python 3.12 slim
- Run as a non-root `appuser`
- Provide a container health check
- Expose port `8000`
- Run FastAPI with Uvicorn

---

## 📊 Monitoring

The application provides production-oriented monitoring endpoints.

### Health

```text
GET /api/v1/health
```

Example:

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Metrics

```text
GET /api/v1/metrics
```

Metrics include review counts, cache statistics, AI provider availability, and application version.

---

## 📈 Current Capabilities

- AI Pull Request Reviews
- Multi-provider AI Routing
- Automatic Provider Failover
- GitHub Webhooks
- Background Processing
- SQLite Review Cache
- Review History
- Inline GitHub Comments
- Review Metrics
- Health Checks
- Automated Unit Tests
- Automated Integration Tests
- 99% Test Coverage
- GitHub Actions CI/CD
- Dockerized Deployment
- Production E2E Pull Request Validation

---

## 🔮 Future Enhancements

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

## 📋 Project Status

| Component | Status |
|---|---|
| Backend | ✅ Complete |
| GitHub Integration | ✅ Complete |
| AI Review | ✅ Complete |
| Background Jobs | ✅ Complete |
| Diff Mapping | ✅ Complete |
| Inline Comments | ✅ Complete |
| Health API | ✅ Complete |
| Metrics API | ✅ Complete |
| Cache | ✅ Complete |
| Unit Testing | ✅ Complete |
| Integration Testing | ✅ Complete |
| 99% Test Coverage | ✅ Complete |
| GitHub Actions | ✅ Complete |
| Docker Support | ✅ Complete |
| Production Deployment | ✅ Complete |
| E2E PR Validation | ✅ Complete |

---

## 👨‍💻 Author

**Sai Surya Hemanth Sanapathi**

Computer Science Engineering Student

Backend Developer • AI Enthusiast • Open Source Contributor

GitHub: https://github.com/SaiSuryaHemanth2007
