# Building PantryPilot: Multi-Agent Orchestration for Good Neighbors with Strands Agents SDK (Agents for Humans)

For the **Agents for Humans** hackathon, I wanted to build something that didn't just automate a developer's workflow, but actually gave time back to community heroes. I looked at local food banks and pantries, which run almost entirely on volunteer labor. I found that coordinators spend up to 15 hours a week on grinding administrative tasks: logging donations by hand, texting volunteers to fill shifts, and writing tax receipts. 

Enter **PantryPilot**: an autonomous, multi-agent back-office co-pilot for volunteer-run food banks. It runs silently in the background, handling the heavy lifting, and only pings the human coordinator for high-stakes approvals. 

Here is a look at how I built it using the **Strands Agents SDK**, **Model Context Protocol (MCP)**, and **Qwen LLM**.

## The Architecture: Multi-Agent Orchestration

To solve this, I didn't just build a chatbot; I built a distributed problem-solving network. PantryPilot relies on a multi-agent architecture where specialized agents handle distinct parts of the workflow:

1. **The Intake Agent**: Receives raw SMS, email, or voice messages, uses Qwen ASR (Speech-to-Text) and LLMs to parse the unstructured data into structured inventory items, and drafts them for Human-in-the-Loop approval
2. **The Dispatch Agent**: Automates post-approval communication. It sends proactive SMS engagement to request missing donor emails for tax receipts, and coordinates volunteer drop-offs by drafting personalized shift requests.
3. **The Logistics Agent**: Analyzes incoming donations against current inventory levels to proactively flag shortages or overstock situations, ensuring the pantry maintains optimal food security.
4. **The Orchestrator**: The central brain that manages agent state, triggers automated PDF tax receipt generation, routes tasks, and strictly enforces the Human-in-the-Loop (HITL) approval boundary before any real-world action is taken.

## Why Strands Agents SDK?

I chose the **Strands Agents SDK** because of its model-driven approach and native support for tool calling. Instead of hardcoding complex state machines, I defined my agents with clear system prompts and register our tools. 

Here is a simplified look at how I initialize my Intake Agent with Strands:

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

By leveraging Strands, I was able to focus on the *logic* of the food bank rather than the plumbing of the LLM context window.

## The "Human-First" Factor: Transparency & HITL

The core theme of the **Agents for Humans** hackathon is trust. AI agents shouldn't be black boxes, especially when dealing with real-world actions like sending texts to volunteers or logging financial tax receipts.

I implemented a strict **Human-in-the-Loop (HITL)** gate. Before the Dispatch Agent actually sends an SMS via Twilio, it pauses and pushes a "Decision Card" to my Next.js frontend. This card explicitly shows the **Agent Reasoning**—explaining *why* it chose a specific volunteer and *what* it plans to say. The human coordinator simply clicks "Approve" or "Reject." 

I also implemented strict application-level guardrails. For example, if the agent attempts to hallucinate a monetary value for a tax receipt, the guardrail intercepts it and redacts the value to ensure IRS compliance. This design pattern ensures the agent acts as a co-pilot, not an autopilot, keeping the human firmly in control.

## Cloud Deployment

For production readiness, PantryPilot is built on a lightweight, asynchronous FastAPI backend that offloads heavy AI compute to Qwen's managed APIs. This decoupled, API-driven architecture ensures the core orchestrator remains highly scalable and can be easily containerized for cloud deployment. It allows the platform to effortlessly handle sudden spikes in donation volume during holiday drives, providing food bank coordinators with a reliable, always-on experience without the overhead of managing local AI infrastructure.

## What's Next?

Building PantryPilot for the **Agents for Humans** hackathon was an incredible experience. It proved that when you combine the orchestration power of the Strands Agents SDK with a deeply empathetic, human-centered UX, you can build tools that don't just write code—they feed communities.

If you are building your own agent for the hackathon, I highly recommend leaning into the HITL pattern. Judges and users alike want to see *how* the agent thinks, not just what it outputs. 

Check out my open-source code on [https://github.com/subair99/pantry-pilot](GitHub) and let me know what you think!