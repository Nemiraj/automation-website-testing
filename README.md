# 🚀 AI-Powered Website Automation Testing Platform

A modern, production-ready, autonomous website testing platform. Built with **FastAPI**, **Playwright Python**, **PostgreSQL**, **Redis/Celery**, and **React (TypeScript + Tailwind CSS)**.

The platform crawls websites, runs multi-device tests (Desktop, Tablet, Mobile), discovers layout overflows, broken links/images, JavaScript crashes, form validation gaps, accessibility violations, and performance metrics, and uses an **AI Analysis Engine** to synthesize structured evidence into actionable developer fixes with root-cause explanations.

---

## 🌟 Key Features

* **Multi-Device Responsive Auditing**: Inspects viewports across Desktop (`1920x1080`, `1366x768`), Tablet (`768x1024`), and Mobile (`390x844`, `375x812`).
* **Deep Intelligent Crawler**: Normalizes URLs, extracts internal links, respects domain boundaries, and collects complete DOM metadata.
* **UI & Layout Overflow Detection**: Finds horizontal scroll leaks, undersized click targets (<24px), zero-size elements, and heading hierarchy breaks.
* **Link & Image Diagnostics**: Tests HTTP responses (404, 403, 500, loops), identifies broken images, missing alt tags, and missing image dimensions.
* **JavaScript & Network Monitoring**: Captures live `pageerror` uncaught exceptions, `console.error` logs, and failed network assets.
* **Form Discovery & Safe Testing**: Discovers `<form>` controls, verifies input labels, checks email field types, and tests validation without spamming.
* **Accessibility Compliance**: Audits document `lang` attributes, empty buttons/links, duplicate DOM IDs, and ARIA labels.
* **Performance Navigation Timing**: Measures `pageLoadTime`, `DOMContentLoaded`, `First Contentful Paint (FCP)`, and heavy asset payloads.
* **Visual Regression**: Compares screenshots against previous test runs with visual difference overlay masks.
* **Deterministic Scoring (0–100)**: Transparent, weighted formulas across UI, Responsive, Functional, Forms, Accessibility, and Performance.
* **AI Diagnosis & Priority Fixes**: Generates root-cause analysis ("Why it happened") and concrete recommendations ("How to fix it") strictly from deterministic test evidence.
* **Real-time Live Progress**: Live progress bar, stage timeline, and event logs via Server-Sent Events (SSE).

---

## 🏗️ Architecture

```text
React (TypeScript + Tailwind + Recharts)
   │ (REST API + SSE Stream)
   ▼
FastAPI (Asynchronous API Layer)
   ├── PostgreSQL (Projects, TestRuns, Pages, Issues, Forms, Screenshots)
   ├── Redis + Celery (Background Test Workers)
   └── Playwright Chromium (Headless Browser Engine)
         ├── UI / Responsive Engine
         ├── Link / Image / Network Engine
         ├── Form Validation Engine
         ├── Accessibility Engine
         └── Performance Analyzer
   ▼
AI Analysis Engine (Gemini / Expert Synthesizer)
   ▼
Comprehensive Report Dashboard
```

---

## 🚀 Quick Start (Docker)

To run the entire full-stack system with a single command:

```bash
docker compose up --build
```

Access the application:
* **React Web Dashboard**: [http://localhost:3000](http://localhost:3000)
* **FastAPI Interactive Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ Local Development (Standalone)

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
playwright install chromium

# Start FastAPI server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at [http://localhost:5173](http://localhost:5173).

---

## 🧪 Running Automated Tests

Run backend unit and integration tests using `pytest`:

```bash
pytest backend/tests -v
```

---

## 🔒 Security & SSRF Safeguards

* **SSRF Protection**: Internal IP ranges (`127.0.0.1`, `10.0.0.0/8`, `192.168.0.0/16`, `172.16.0.0/12`), loopbacks, and cloud metadata endpoints (`169.254.169.254`) are blocked by default.
* **Form Safety**: Automated form testing defaults to `FORM_SUBMISSION_MODE=validation_only` to prevent unintended live submissions.
