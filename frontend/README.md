# PantryPilot: Omnichannel AI Agent for Food Banks

**PantryPilot** is an autonomous, serverless AI agent built with the **Strands Agents SDK** that streamlines food bank operations. It ingests donation requests across multiple channels (Voice, SMS, Email), uses Amazon Bedrock to extract structured data, generates IRS-compliant tax receipts, and notifies volunteers—embracing a **"Quiet until it matters"** UX philosophy.

---

## The Problem
Food banks rely on fragmented, high-volume communication channels. Volunteers are overwhelmed by:
1. Manually transcribing voicemails and reading SMS/Emails.
2. Manually entering donor data into spreadsheets.
3. Generating and mailing physical tax receipts.
4. Coordinating drop-offs with other volunteers.

---

## The Solution
PantryPilot automates the entire ingestion-to-approval pipeline. It acts as an intelligent co-pilot that silently processes incoming messages in the background, presenting food bank managers with a clean, actionable dashboard for final approval.

---

## Key Features

### Strands-Powered AI Agent
Built using the **Strands Agents SDK**, the core orchestrator uses custom `@tool` decorated Python functions to handle real-world tasks end-to-end:
- `generate_receipt`: Dynamically creates PDF tax receipts and logs them to DynamoDB.
- `send_receipt_email`: Securely emails the receipt to the donor via Amazon SES.
- `search_archive`: Queries historical donation records by name, phone, or email.

### Omnichannel Ingestion Pipeline
- **Voice:** Automatically transcribes `.wav`/`.mp3` files uploaded to S3 into text.
- **SMS & Email:** Ingests raw text files directly from the message queue.
- **Unified Processing:** All channels are normalized into a single text format before AI processing.

### "Quiet Until It Matters" UX
- **No spam:** Receipts are generated upon approval but *never* emailed to the donor until explicitly requested via the dashboard.
- **Silent Notifications:** Volunteers are notified via SNS/SMS and SES/Email only when a drop-off is confirmed.

---

## Architecture

```mermaid
graph TD
    subgraph "Ingestion Layer"
        A[S3: received_voice/] -->|Auto-Transcribe| B[S3: received_messages/]
        C[S3: received_messages/] -->|SMS/Email Files| B
    end
    
    subgraph "Processing Layer"
        B -->|HTTP GET /scan| D[Lambda: Pipeline Orchestrator]
        D -->|Extract JSON| E[Amazon Bedrock<br/>Nova Pro]
        E -->|Structured Data| D
    end
    
    subgraph "AI Agent Layer"
        D -->|HTTP POST /approve| F[Strands Agent]
        F -->|@tool generate_receipt| G[FPDF Library]
        F -->|@tool send_receipt_email| H[Amazon SES]
        F -->|@tool search_archive| I[DynamoDB Query]
    end
    
    subgraph "Storage Layer"
        G -->|PDF Upload| J[S3: receipts/]
        D -->|Archive File| K[S3: processed_messages/]
        I -->|Metadata| L[DynamoDB: PantryTable]
    end
    
    subgraph "Presentation Layer"
        M[Next.js Dashboard] -->|Scan Inbox| D
        M -->|View Receipt| J
        M -->|Search| I
    end
    
    H -->|Notify Volunteers| N[SNS/Email]
```

---

## Tech Stack

PantryPilot is built on a modern, event-driven, serverless architecture.

### Backend (Infrastructure as Code)
- **Strands Agents SDK:** Core AI agent framework with custom tool execution.
- **AWS CDK (TypeScript):** Defines all infrastructure.
- **AWS Lambda (Python 3.12):** The orchestration brain running the Strands Agent.
- **Amazon API Gateway (HTTP API):** Exposes RESTful endpoints (`/scan`, `/approve`, `/send-receipt`, `/search`).
- **Amazon Bedrock:** Invokes Amazon Nova Pro for LLM reasoning and structured JSON parsing.
- **Amazon DynamoDB:** Stores approval logs and receipt metadata.
- **Amazon S3:** File storage and pipeline state (`received_voice/`, `received_messages/`, `processed_messages/`, `receipts/`).
- **Amazon SES & SNS:** Email and SMS notifications.

### Frontend
- **Next.js (React):** Fast, responsive dashboard.
- **Tailwind CSS:** Clean, accessible UI.

---

## How to Run Locally

### Prerequisites
- Node.js 18+ & npm
- Python 3.12+ & `uv` (for fast dependency management)
- AWS CLI configured with appropriate permissions

### 1. Deploy the Backend
```bash
cd infrastructure/cdk
npm install
npx cdk deploy --force
```
*Note the `ApiEndpoint` and `BucketName` outputs.*

### 2. Setup and Run the Frontend
```bash
cd frontend
# Create .env.local and paste your API endpoint:
# NEXT_PUBLIC_API_ENDPOINT=https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com

npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## Future Improvements
- **S3 Event Notifications:** Replace the manual "Scan" button with S3 triggers to invoke the Lambda instantly upon file upload for true real-time processing.
- **Amazon Transcribe & Bedrock Voxtral:** Integrate real AWS Transcribe and Bedrock Voxtral for production-grade audio transcription.
- **Twilio / Amazon Pinpoint Integration:** Connect directly to live SMS and Voice telephony APIs for real-world ingestion.

---

## Hackathon Details
- **Track:** Agents for Humans (Good Neighbor / Everyday Agents)
- **Team:** [Your Name/Team Name]
- **Built with:** Strands Agents SDK, AWS CDK, Amazon Bedrock, Next.js, Python
- **Repository:** [Link to your GitHub Repo]

---