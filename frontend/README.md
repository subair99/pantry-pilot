# PantryPilot: Omnichannel AI Co-Pilot for Food Banks

**PantryPilot** is an autonomous, serverless AI agent designed to streamline food bank operations. It ingests donation requests across multiple channels (Voice, SMS, Email), uses Amazon Bedrock (Nova Pro) to extract structured data, generates IRS-compliant tax receipts, and notifies volunteers—embracing a **"Quiet until it matters"** UX philosophy.

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

###  Omnichannel Ingestion Pipeline
* **Voice:** Automatically transcribes `.wav`/`.mp3` files uploaded to S3 into text.
* **SMS & Email:** Ingests raw text files directly from the message queue.
* **Unified Processing:** All channels are normalized into a single text format before AI processing.

### AI-Powered Data Extraction
* Uses **Amazon Bedrock (Nova Pro)** via the Converse API to parse unstructured messages.
* Accurately extracts donor names, contact info, item lists, quantities, and drop-off times.

### Automated IRS-Compliant Receipts
* Dynamically generates professional PDF tax receipts using `fpdf2`.
* Securely stores receipts in Amazon S3 with public-read access for easy sharing.

### "Quiet Until It Matters" UX
* **No spam:** Receipts are generated upon approval but *never* emailed to the donor until explicitly requested via the dashboard.
* **Silent Notifications:** Volunteers are notified via SNS/SMS and SES/Email only when a drop-off is confirmed.

### Searchable Archive
* All approvals are logged in **Amazon DynamoDB**.
* Managers can instantly search historical records by donor name, phone number, or email.

---

## Architecture & Tech Stack

PantryPilot is built on a modern, event-driven, serverless architecture using **AWS CDK**.

### The S3 File-Based Pipeline
Instead of complex message queues, we use S3 folders as a state machine:
1. `received_voice/`: Raw audio files (Source of Truth).
2. `received_messages/`: Transcribed text and incoming SMS/Emails.
3. `processed_messages/`: Archived messages post-approval.

### Backend (Infrastructure as Code)
* **AWS CDK (TypeScript):** Defines all infrastructure.
* **AWS Lambda (Python 3.12):** The orchestration brain.
* **Amazon API Gateway (HTTP API):** Exposes RESTful endpoints (`/scan`, `/approve`, `/send-receipt`, `/search`).
* **Amazon Bedrock:** Invokes Amazon Nova Pro for LLM reasoning.
* **Amazon DynamoDB:** Stores approval logs and receipt metadata.
* **Amazon S3:** File storage and pipeline state.
* **Amazon SES & SNS:** Email and SMS notifications.

### Frontend
* **Next.js (React):** Fast, responsive dashboard.
* **Tailwind CSS:** Clean, accessible UI.

---

## How to Run Locally

### Prerequisites
* Node.js 18+ & npm
* Python 3.12+ & `uv` (for fast dependency management)
* AWS CLI configured with appropriate permissions

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
* **S3 Event Notifications:** Replace the manual "Scan" button with S3 triggers to invoke the Lambda instantly upon file upload for true real-time processing.
* **Amazon Transcribe & Voxtral:** Integrate real AWS Transcribe and Bedrock Voxtral for production-grade audio transcription.
* **Twilio / Amazon Pinpoint Integration:** Connect directly to live SMS and Voice telephony APIs for real-world ingestion.

---

##  Hackathon Details
* **Track:** AI / Serverless / Social Good
* **Team:** AbdulKabir
* **Built with:** AWS CDK, Amazon Bedrock, Next.js, Python

---