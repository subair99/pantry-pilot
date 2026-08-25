# Building PantryPilot: Multi-Agent Orchestration for Good Neighbors with Strands Agents SDK (Agents for Humans)

For the **Agents for Humans** hackathon, my team and I wanted to build something that didn't just automate a developer's workflow, but actually gave time back to community heroes. We looked at local food banks and pantries, which run almost entirely on volunteer labor. We found that coordinators spend up to 15 hours a week on grinding administrative tasks: logging donations by hand, texting volunteers to fill shifts, and writing tax receipts. 

Enter **PantryPilot**: an autonomous, multi-agent back-office co-pilot for volunteer-run food banks. It runs silently in the background, handling the heavy lifting, and only pings the human coordinator for high-stakes approvals. 

Here is a look at how we built it using the **Strands Agents SDK**, **Model Context Protocol (MCP)**, and **Amazon Bedrock AgentCore**.

## The Architecture: Multi-Agent Orchestration

To solve this, we didn't just build a chatbot; we built a distributed problem-solving network. PantryPilot relies on a multi-agent architecture where specialized agents handle distinct parts of the workflow:

1. **The Intake Agent**: Receives raw SMS or photo donations, uses OCR to parse the items, and logs them into the inventory database.
2. **The Dispatch Agent**: Once a donation is approved, this agent matches the drop-off time with volunteer availability and drafts a personalized SMS shift request.
3. **The Logistics Agent**: Analyzes current stock against historical demand to flag shortages or overstock situations, ensuring the pantry never runs out of critical items.
4. **The Orchestrator**: Manages the state, routes tasks, and enforces the **Human-in-the-Loop (HITL)** boundary.

## Why Strands Agents SDK?

We chose the **Strands Agents SDK** because of its model-driven approach and native support for tool calling. Instead of hardcoding complex state machines, we define our agents with clear system prompts and register our tools. 

Here is a simplified look at how we initialize our Intake Agent with Strands:

```python
from strands import Agent
from tools.ocr_mcp import extract_donation_details
from tools.inventory_db import log_donation

intake_agent = Agent(
    model="anthropic.claude-3-5-sonnet-20241022-v2:0",
    system_prompt="You are the Intake Agent. Parse the SMS, extract details, and log the donation.",
    tools=[extract_donation_details, log_donation]
)

# The SDK handles the agentic loop, tool execution, and context management automatically
response = intake_agent("Hi, dropping off 12 boxes of pasta and 20lbs of apples at 5 PM.")
```

By leveraging Strands, we were able to focus on the *logic* of the food bank rather than the plumbing of the LLM context window.

## The "Human-First" Factor: Transparency & HITL

The core theme of the **Agents for Humans** hackathon is trust. AI agents shouldn't be black boxes, especially when dealing with real-world actions like sending texts to volunteers or logging financial tax receipts.

We implemented a strict **Human-in-the-Loop (HITL)** gate. Before the Dispatch Agent actually sends an SMS via Twilio, it pauses and pushes a "Decision Card" to our Next.js frontend. This card explicitly shows the **Agent Reasoning**—explaining *why* it chose a specific volunteer and *what* it plans to say. The human coordinator simply clicks "Approve" or "Reject." 

We also implemented strict application-level guardrails. For example, if the agent attempts to hallucinate a monetary value for a tax receipt, the guardrail intercepts it and redacts the value to ensure IRS compliance. This design pattern ensures the agent acts as a co-pilot, not an autopilot, keeping the human firmly in control.

## Scaling with Amazon Bedrock AgentCore

For production readiness, we designed PantryPilot to be deployed on **Amazon Bedrock AgentCore Runtime**. AgentCore provides serverless, session-isolated scaling, which is crucial for an application that might need to handle sudden spikes in donation texts during holiday drives. By decoupling the agent logic from the underlying infrastructure, we ensure that the food bank coordinators get a reliable, always-on experience without managing servers.

## What's Next?

Building PantryPilot for the **Agents for Humans** hackathon was an incredible experience. It proved that when you combine the orchestration power of the Strands Agents SDK with a deeply empathetic, human-centered UX, you can build tools that don't just write code—they feed communities.

If you are building your own agent for the hackathon, I highly recommend leaning into the HITL pattern. Judges and users alike want to see *how* the agent thinks, not just what it outputs. 

Check out our open-source code on GitHub [Link to your GitHub Repo] and let us know what you think!

***

### 💡 Final Hackathon Checklist Before You Submit:
1. **Publish this post** on `builder.aws.com`.
2. **Add your GitHub link** at the bottom of the post.
3. **Include 1-2 screenshots** of your beautiful, animated PantryPilot dashboard in the blog post (judges love visual proof).
4. **Submit your Devpost entry**, making sure to link this blog post in the "Project Details" or "Bonus Points" section!