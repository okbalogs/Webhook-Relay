# Webhook Relay & Replay Platform

> A self-hosted developer infrastructure tool (like Svix / Hookdeck) for ingesting, cryptographically verifying, logging, real-time streaming, and auto-retrying webhooks with exponential backoff & jitter.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-emerald.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)

---

## ⚡ Features

- **🚀 High-Throughput Async Intake**: Ingests requests in $< 20\text{ ms}$ and returns HTTP `202 Accepted` immediately.
- **🔐 Cryptographic Signature Verification**: Built-in HMAC-SHA256 verifiers for **Stripe** (`Stripe-Signature`), **GitHub** (`X-Hub-Signature-256`), **Shopify** (`X-Shopify-Hmac-SHA256`), and generic token/secret headers.
- **🐘 Partitioned PostgreSQL Storage**: Range-partitioned `events` table for high event volume and clean retention purges.
- **⚡ Partial Index & Worker Queue**: Partial index `idx_delivery_pending_retries WHERE status IN ('pending', 'retrying')` and `SKIP LOCKED` for lock-free parallel worker execution.
- **📈 Exponential Backoff & Jitter**: Automatic delivery retries with exponential backoff + randomized jitter to prevent thundering herd recovery issues.
- **🖥️ Dark-Mode Inspection Dashboard**: Real-time log streaming via Server-Sent Events (SSE), headers inspection, JSON payload viewer, and status logs.
- **🔄 One-Click Replay Request**: Edit payload JSON or target URL and re-fire past webhook events instantly.
- **🔌 Developer CLI Tunnel**: Lightweight CLI client (`cli/relay_cli.py`) forwarding live webhooks to local dev servers (`http://localhost:3000`).

---

## 📖 Deep-Dive Explanation & Learning Guide

If you are learning this tech stack (FastAPI, PostgreSQL partitioning, Async SQLAlchemy, SSE, Next.js 14), check out our comprehensive guide:
👉 **[Read the Full Codebase & Architecture Explanation Guide (EXPLANATION.md)](./EXPLANATION.md)**

---

## 🚀 Quick Start

### 1. Start Infrastructure (PostgreSQL 16 & Redis)
```bash
docker compose up -d
```

### 2. Start FastAPI Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```
Interactive Swagger Docs: `http://localhost:8000/docs`

### 3. Start Next.js Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
Dashboard UI: `http://localhost:3000`

### 4. Run Pytest Test Suite
```bash
cd backend
PYTHONPATH=. venv/bin/pytest tests/
```

---

## 📡 API Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/endpoints` | Create a new proxy ingestion endpoint |
| `GET` | `/api/v1/endpoints` | List configured ingestion endpoints |
| `POST` | `/api/v1/ingest/{endpoint_id}` | Public webhook intake URL (HMAC verified) |
| `GET` | `/api/v1/events` | Query ingested events history |
| `GET` | `/api/v1/events/{event_id}` | Fetch event details & delivery attempts log |
| `GET` | `/api/v1/events/stream/live` | Server-Sent Events (SSE) live log stream |
| `POST` | `/api/v1/events/{event_id}/replay` | Trigger manual request replay |

---

## 📄 License
MIT License.
