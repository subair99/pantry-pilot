import os
from pathlib import Path

# Root directory is the current working directory (where the script is run)
ROOT_DIR = Path(".")

# Define the project structure: {relative_path: content}
# Directories are created automatically when files inside them are created.
PROJECT_STRUCTURE = {
    # --- Backend ---
    "backend/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PantryPilot Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "PantryPilot Agent Orchestrator is running"}
""",
    "backend/config.py": """import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
""",
    "backend/agents/__init__.py": "",
    "backend/agents/orchestrator.py": "# Strands Agent Orchestrator: Routes tasks and enforces HITL gates\n",
    "backend/agents/intake_agent.py": "# Intake Agent: Handles OCR and donation parsing\n",
    "backend/agents/logistics_agent.py": "# Logistics Agent: Updates inventory and runs demand forecasting\n",
    "backend/agents/dispatch_agent.py": "# Dispatch Agent: Manages volunteer SMS outreach via Twilio\n",
    "backend/tools/__init__.py": "",
    "backend/tools/twilio_mcp.py": "# MCP Tool: send_sms, check_delivery_status\n",
    "backend/tools/ocr_mcp.py": "# MCP Tool: extract_text_from_image (AWS Textract wrapper)\n",
    "backend/tools/inventory_db.py": "# MCP Tool: read_inventory, update_inventory\n",
    "backend/state/memory.py": "# Persistent state management (AgentCore session memory)\n",
    "backend/utils/logger.py": "# Structured logging for the 'Background Actions' UI\n",
    "backend/utils/guardrails.py": "# AWS Bedrock Guardrails integration\n",

    # --- Frontend ---
    "frontend/package.json": """{
  "name": "pantry-pilot-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "^18",
    "react-dom": "^18",
    "lucide-react": "^0.344.0",
    "zod": "^3.22.4",
    "framer-motion": "^11.0.8",
    "date-fns": "^3.3.1"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "autoprefixer": "^10.0.1",
    "postcss": "^8",
    "tailwindcss": "^3.3.0",
    "typescript": "^5"
  }
}
""",
    "frontend/next.config.js": "/** @type {import('next').NextConfig} */\nconst nextConfig = {}\nmodule.exports = nextConfig\n",
    "frontend/app/layout.tsx": """export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900">{children}</body>
    </html>
  )
}
""",
    "frontend/app/page.tsx": """export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-4">PantryPilot Dashboard</h1>
      <p className="text-gray-600">Quiet until it matters. Awaiting agent events...</p>
    </main>
  )
}
""",
    "frontend/app/approvals/[id]/page.tsx": """export default function ApprovalPage({ params }: { params: { id: string } }) {
  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Decision Required</h1>
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <p className="mb-4">Agent ID: {params.id}</p>
        <p className="text-gray-600 mb-6">The agent has drafted an action. Please review and approve.</p>
        <div className="flex gap-4">
          <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">Approve</button>
          <button className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">Reject</button>
        </div>
      </div>
    </div>
  )
}
""",
    "frontend/app/api/approve/route.ts": """import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const body = await request.json()
  // TODO: Forward approval to backend orchestrator
  return NextResponse.json({ success: true, message: "Approval sent to agent" })
}
""",
    "frontend/components/DecisionCard.tsx": "// Core UI: Shows agent reasoning, drafted SMS, and 'Approve' button\n",
    "frontend/components/AgentLog.tsx": "// Visualizes the step-by-step reasoning tree (Transparency criterion)\n",
    "frontend/components/StatusBadge.tsx": "// Visual indicator of agent state (Idle, Thinking, Awaiting Approval)\n",

    # --- Scripts ---
    "scripts/seed_mock_data.py": "# Pre-loads the DB with realistic food bank inventory/volunteers\n",
    "scripts/simulate_donation_sms.py": "# Script to trigger the demo flow without needing a real Twilio number live\n",

    # --- Docs ---
    "docs/architecture.png": "", # Placeholder: You will replace this with a real diagram
    "docs/demo_script.md": """# 5-Minute Demo Script
## 0:00 - 0:45 | The Hook & Problem
Show a split screen. Stressed volunteer juggling spreadsheet, phone, notes.
Voiceover: "Community heroes are burning out on paperwork, not serving people."

## 0:45 - 1:30 | The Trigger
Show a donor texting a photo: "Dropping off 12 boxes of pasta and 20lbs of apples at 5 PM."

## 1:30 - 3:00 | The Agentic Magic
1. Intake Agent OCRs the text and photo.
2. Logistics Agent updates inventory and flags: "Apples are highly needed."
3. Dispatch Agent drafts an IRS-compliant receipt AND drafts a text to the next available volunteer.

## 3:00 - 4:00 | The Human-in-the-Loop
The UI pings the coordinator. They see a beautifully formatted summary: 
"Donation logged. Receipt drafted. Volunteer Sarah texted. Click Approve to send."
User clicks Approve.

## 4:00 - 5:00 | Architecture & Impact
Flash architecture diagram (Strands SDK + Bedrock AgentCore). 
Final line: "PantryPilot doesn’t replace the human. It gives them their time back."
""",
    "docs/builder_aws_post_draft.md": """# Title: Building PantryPilot: Multi-Agent Orchestration with Strands SDK and Bedrock AgentCore

In this post, I'll walk through how we built PantryPilot, an autonomous back-office agent for food banks, using the Strands Agents SDK and Amazon Bedrock AgentCore...
""",

    # --- Tests ---
    "tests/test_intake_agent.py": "# Unit tests for intake agent OCR parsing\n",
    "tests/test_mcp_tools.py": "# Unit tests for MCP tool integrations\n",
}

def create_project_structure():
    print(f"🚀 Creating PantryPilot project structure in '{ROOT_DIR.resolve()}'...\n")
    
    for relative_path, content in PROJECT_STRUCTURE.items():
        full_path = ROOT_DIR / relative_path
        
        # It's a file
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 Created file: {full_path}")
            
    print("\n✅ Project structure created successfully!")
    print("\n" + "="*60)
    print("💡 NEXT STEPS: Initialize your `uv` environment")
    print("="*60)
    print("\n1. Navigate to the backend folder:")
    print("   cd backend")
    print("\n2. Initialize a new uv project (creates pyproject.toml & .python-version):")
    print("   uv init --no-readme")
    print("\n3. Add your core runtime dependencies:")
    print("   uv add strands-agents boto3 fastapi 'uvicorn[standard]' pydantic python-dotenv httpx twilio")
    print("\n4. Add your development/testing dependencies:")
    print("   uv add --dev pytest pytest-asyncio moto ruff mypy")
    print("\n5. Start the FastAPI backend server:")
    print("   uv run uvicorn main:app --reload")
    print("\n" + "="*60)
    print("💡 FRONTEND STEPS:")
    print("="*60)
    print("\n1. Navigate to the frontend folder (from the base directory):")
    print("   cd ../frontend")
    print("\n2. Install Node dependencies:")
    print("   npm install  (or pnpm install)")
    print("\n3. Start the Next.js development server:")
    print("   npm run dev")

if __name__ == "__main__":
    create_project_structure()