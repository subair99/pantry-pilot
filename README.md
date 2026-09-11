# PantryPilot: Omnichannel AI Agent for Food Banks

**PantryPilot** is an autonomous, serverless AI agent built with the **Strands Agents SDK** that streamlines food bank operations. It ingests donation requests across multiple channels (Voice, SMS, Email), uses Amazon Bedrock to extract structured data, generates IRS-compliant tax receipts, and notifies volunteers—embracing a **"Quiet until it matters"** UX philosophy.

![PantryPilot Dashboard](images/1-dashboard_before_scanning.png)

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
    A[S3 Bucket<br/>received_voice/] -->|Transcribe| B[S3 Bucket<br/>received_messages/]
    C[S3 Bucket<br/>SMS/Email Files] --> B
    B -->|HTTP GET /scan| D[Lambda Function<br/>Pipeline Orchestrator]
    D -->|Parse JSON| E[Amazon Bedrock<br/>Nova Pro]
    E -->|Structured Data| D
    D -->|HTTP POST /approve| F[Strands Agent<br/>AI Core]
    F -->|Generate PDF| G[FPDF Library]
    F -->|Send Email| H[Amazon SES]
    F -->|Search Records| I[DynamoDB]
    G -->|Upload PDF| J[S3 Bucket<br/>receipts/]
    D -->|Archive| K[S3 Bucket<br/>processed_messages/]
    I <-->|Store Metadata| L[DynamoDB<br/>PantryTable]
    M[Next.js Dashboard] -->|User Actions| D
    M -->|View PDF| J
    M -->|Search| I
    H -->|Notify| N[Volunteers<br/>SNS/Email]
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
- **Team:** AbdulKabir
- **Built with:** Strands Agents SDK, AWS CDK, Amazon Bedrock, Next.js, Python
- **Repository:** [Link to GitHub Repo](https://github.com/subair99/pantry-pilot)

---