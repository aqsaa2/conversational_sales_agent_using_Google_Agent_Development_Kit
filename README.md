
# Sales Agent Conversational System using Google ADK

This project implements a **conversational AI sales agent** using the [Google ADK](https://google.github.io/adk-docs/get-started/quickstart/#run-your-agent) that interacts with leads, collects essential information, follows up on unresponsive users, and stores everything in structured CSV files.

---

## 🚀 Features

- Handles multi-step lead conversations (consent → age → country → interest).
- Tracks lead status (`initiated`, `in_progress`, `secured`, `follow_up_sent`, etc.).
- Sends follow-up messages to unresponsive leads after a specified timeout.
- Manages multiple leads simultaneously via in-memory sessions.
- CSV logging of all lead data (manual and test inputs).
- Works via command line simulation and also with the ADK web interface.

---

## 📁 Project Structure

```
Sales_Agent/
│
├── conversational_agent/
│   ├── agent.py           # Core agent logic using ADK
│   ├── simulation.py      # Test cases + manual lead simulation
│   ├── __init__.py
│   └── .env               # Optional environment variables
│── leads.csv          # CSV file for storing all lead data
└── README.md              # This file
```

---

## 📹 Demo Video


Full demo of the project:

Note: Edited with capcut, as the screen recorder didnt record voice.

[▶️ Click here to view the demo](https://drive.google.com/file/d/16zbsCnbjhimLrW3a_nUdClUToQ0jfnnJ/view?usp=sharing)



---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/sales-agent-adk.git
cd sales-agent-adk/conversational_agent
```

### 2. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate   # or `venv\Scripts\activate` on Windows
```

### 3. Install dependencies
Install `google-adk` and any other needed packages:
```bash
pip install google-adk
```

### 4. Setup `.env` file (optional, current implementation doesn't use python-dotenv)
Get your Gemini API key, place them in `.env`.

---

## 🧠 Agent Overview

The agent:
- Starts a conversation only after Lead ID and Name are entered as part of the form.
- Progresses through consent → age → country → interest.
- Uses `lead_sessions` dictionary to track each conversation.
- Stores each lead's details in `leads.csv`.
- Sends a follow-up message after 60 seconds if no reply is received.

---

## 🧪 Testing the Agent Locally

### Manual + Simulated Testing (via CLI)
To simulate conversations (including unresponsive leads and delayed inputs):

```bash
python simulation.py
```

You will see:
- Manual input prompts
- Automated test cases in parallel threads
- Console-based agent responses
- CSV (`leads.csv`) updated in real time

---

## 🌐 Running with Google ADK (Web Interface)

You can run the same agent using ADK’s web interface:

### Step 1: Install ADK globally (if not done)
```bash
pip install google-adk
```

### Step 2: Navigate to your agent directory
```bash
# move to your parent folder.
cd parentfolder
```

### Step 3: Run the ADK agent server
```bash
adk web
```

This will host your agent locally at:

```
http://127.0.0.1:8000
```

You can now send messages and interact with your agent via the **ADK web interface**.

---

## 📦 CSV Logging

All interactions (manual and simulated) are saved to:

- `leads.csv`

Columns:
```
lead_id, name, age, country, interest, status
```

Statuses include:
- `initiated`: Session started
- `in_progress`: Consent given, collecting data
- `secured`: All data collected
- `follow_up_sent`: Lead was silent, reminder sent
- `no_response`: Lead declined or dropped

---

