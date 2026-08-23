# pantry-pilot
PantryPilot is an autonomous multi-agent co-pilot for food banks. Built on Strands SDK, it silently OCRs donations, logs inventory, and drafts volunteer SMS shifts. Embracing a "quiet until it matters" UX, it only pings humans for approvals, eliminating admin burnout so volunteers can focus on serving families.

🎉 **Congratulations! Your code is successfully pushed to GitHub!** 

However, you have a classic Git warning: **you accidentally committed your `node_modules` folder** to the repository. GitHub is warning you that a file inside it is 92.25 MB (GitHub's soft limit is 50 MB, hard limit is 100 MB). 

While it didn't block the push this time, it bloats your repo and looks unprofessional to judges. Let's clean this up in 4 quick steps.

---

### 🧹 How to Fix the Large File Warning

Run these commands in your terminal (from the root `pantry-pilot` directory):

```bash
# 1. Ensure node_modules is ignored by Git
echo "node_modules/" >> .gitignore
echo ".venv/" >> .gitignore
echo "__pycache__/" >> .gitignore

# 2. Remove node_modules from Git's tracking (this does NOT delete your local files)
git rm -r --cached frontend/node_modules
git rm -r --cached backend/.venv

# 3. Commit the cleanup
git commit -m "chore: remove node_modules and .venv from git tracking"

# 4. Force push to overwrite the remote history with the clean version
git push origin main --force
```

*(Note: Force pushing is perfectly safe and standard practice in hackathons to keep the repository clean and lightweight.)*

---

### ⚠️ CRITICAL HACKATHON REMINDER: Avoid Auto-Disqualification

Earlier, you asked me to exclude `README.md` and `LICENSE` from the scaffold to keep the script clean. **However, the official Devpost rules explicitly state:**

> *"Devpost disqualifies projects that miss this basic requirement: a visible MIT or Apache 2.0 license and a clear README.md with setup instructions."*

Before you submit, you **must** add these two files to your root directory. Here is the fastest way to do it:

#### 1. Create `LICENSE` (Root directory)
```text
MIT License

Copyright (c) 2024 PantryPilot Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

#### 2. Create `README.md` (Root directory)
```markdown
# 🥫 PantryPilot

**An autonomous, multi-agent back-office co-pilot for volunteer-run food banks.**

## 🎯 The Problem
Small food pantries run almost entirely on volunteer labor doing grinding admin every week: logging donations by hand, texting volunteers, and writing tax receipts. This eats hours that should go to serving people.

## 🚀 The Solution
PantryPilot runs silently in the background. It OCRs donation texts, logs inventory, drafts IRS-compliant receipts, and matches surplus food to volunteer availability. It only pings the human coordinator for high-stakes approvals.

## 🛠️ Tech Stack
- **Orchestration**: Strands Agents SDK
- **Deployment**: Amazon Bedrock AgentCore Runtime
- **Tools**: Model Context Protocol (MCP) for Twilio, AWS Textract, and local DB
- **Frontend**: Next.js + Tailwind CSS (Human-in-the-Loop Dashboard)

## 🏁 Quick Start
### Backend
```bash
cd backend
uv init --no-readme
uv add strands-agents boto3 fastapi "uvicorn[standard]" pydantic python-dotenv httpx twilio
uv run uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📜 License
MIT License - See LICENSE file for details.
```

