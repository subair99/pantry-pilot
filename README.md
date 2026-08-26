# 📦 PantryPilot: Autonomous Multi-Agent AI for Food Bank Operations

**PantryPilot** is an intelligent, multi-agent orchestration system that automates the entire donation lifecycle for food banks. From unstructured voice notes and text messages to IRS-compliant tax receipts, our AI handles the administrative heavy lifting so food bank staff can focus on feeding their communities.

---

##  The Problem
Food banks operate on thin margins and rely heavily on volunteer staff. However, the donation intake process is highly manual and fragmented:
* Donors send unstructured messages via SMS, Email, and Voicemail.
* Staff must manually transcribe audio, parse details, and log inventory.
* Generating and mailing IRS-compliant tax receipts for donors is a massive administrative bottleneck.
* **Result:** Burnout, data entry errors, and lost future donations.

## 💡 The Solution
PantryPilot introduces a **Human-in-the-Loop (HITL) Multi-Agent Architecture**. It ingests unstructured data from multiple channels, uses Multimodal AI to transcribe and parse the intent, and presents a transparent "Agent Reasoning" plan to the staff. Once approved, downstream agents automatically dispatch volunteers, forecast inventory, and generate instant PDF tax receipts.

---

## ✨ Key Features

### 🎙️ Multimodal Voice & Text Intake
* Seamlessly processes SMS, Email, and Voice messages.
* Uses **Qwen CosyVoice-v3-flash** to generate realistic voice notes and **Qwen ASR** to transcribe incoming audio with high accuracy.

### 🤖 Transparent Agentic Workflow
* **Intake Agent:** Parses unstructured text/audio into structured JSON (Donor, Items, Quantity, Drop-off time).
* **Dispatch Agent:** Automatically routes drop-offs to volunteers and sends proactive SMS engagement if donor contact info is missing.
* **Logistics Agent:** Analyzes incoming inventory to flag shortages and forecast food security.

### ️ Human-in-the-Loop (HITL) Approval
* AI never acts blindly. The system presents a clear **"Agent Reasoning"** card detailing exactly what it plans to do.
* Staff simply click "Approve & Log" to trigger the downstream automated workflows.

###  Automated IRS Tax Receipts
* Upon approval, the system instantly generates a beautifully formatted, IRS-compliant PDF tax receipt.
* Donors receive immediate confirmation, building trust and encouraging recurring donations.

### 📊 Real-Time System Observability
* A live dashboard tracking Total Requests, Success Rates, and Average Latency.
* Full agent tracing and logging to monitor AI decision-making in real-time.

---

## ️ Architecture & Data Flow

1. **Ingestion:** Files (`.txt` for SMS/Email, `.wav` for Voice) are dropped into the backend queue folders.
2. **Transcription & Parsing:** The Queue Processor triggers the Qwen ASR API for voice files. The Intake Agent (powered by Qwen LLM) extracts structured data.
3. **HITL Review:** The frontend displays the parsed donation with an "Awaiting Approval" status.
4. **Execution:** Upon clicking "Approve", the Orchestrator triggers:
   * The **Dispatch Agent** (sends SMS/Email).
   * The **Logistics Agent** (updates inventory health).
   * The **Receipt Generator** (creates a PDF via `fpdf2`).
5. **Download:** The user clicks "Download Receipt" to instantly fetch the generated PDF.

---

## ️ Tech Stack

* **Frontend:** Next.js 16 (Turbopack), React, TypeScript, Tailwind CSS, Framer Motion, Lucide Icons.
* **Backend:** Python, FastAPI, Pydantic.
* **AI & LLMs:** Alibaba Cloud Qwen (DashScope)
  * `cosyvoice-v3-flash` (Text-to-Speech)
  * `qwen3-asr-flash` (Speech-to-Text / Multimodal ASR)
  * `qwen-plus` (Structured Data Extraction & Reasoning)
* **Tools:** `fpdf2` (PDF Generation), OpenAI-compatible protocol for seamless API integration.

---

## 🚀 How to Run Locally

### Prerequisites
* Node.js 18+
* Python 3.10+
* [uv](https://github.com/astral-sh/uv)
* A Qwen/DashScope API Key

### 1. Backend Setup
```bash
cd pantry-pilot/backend
cp .env.example .env  # Add your QWEN_API_KEY here
uv sync
uv run uvicorn main:app --reload
```

### 2. Frontend Setup
```bash
cd pantry-pilot/frontend
npm install
npm run dev
```

### 3. Running the Demo
1. Open your browser to `http://localhost:3000`.
2. Drop sample files into the queue directories:
   * **SMS:** `backend/received_messages/sms/new_sms/`
   * **Email:** `backend/received_messages/email/new_email/`
   * **Voice:** `backend/received_messages/voice/new_voice/`
3. Click **"Process Queue & Refresh"** on the dashboard.
4. Click **"Approve & Log"** on a donation card, then click **"Download Receipt"** to see the AI-generated PDF!

---

## 🏆 Hackathon Track
**AI for Social Impact / Agentic AI**

## 👥 Team
Built with ❤️ by [Your Name/Team Name]

