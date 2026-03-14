# Running CarbonSense AI Locally (Without AI API Keys)

This guide explains how to configure and run the CarbonSense AI project using local, open-source models. By following these steps, you can run the entire platform **without needing a Groq, OpenAI, or any other paid API key**.

We will use **Ollama**, an open-source framework that makes it easy to run large language models locally on your machine.

---

## Prerequisites

1.  **Ollama**: Ensure you have Ollama installed on your system.
    *   Download from: [https://ollama.com/download](https://ollama.com/download)
    *   Install and run the application.
2.  **Hardware**: Running local LLMs requires a decent amount of RAM (at least 8GB for small models, 16GB+ recommended).

---

## Step 1: Download Local Models

Open your terminal and pull the models you want to use. We recommend the `llama3` (8B parameters) or `mistral` model for general queries, as they offer an excellent balance of speed and quality.

To download and run Llama 3, use this command:
```bash
ollama run llama3
```
*Wait for the download to finish. You can type `/bye` to exit the Ollama prompt once it's done.*

---

## Step 2: Update Backend Dependencies

CarbonSense AI uses Langchain. To integrate Ollama, ensure you have the `langchain-community` package installed in your backend environment.

Navigate to your `backend` directory and activate your virtual environment:

```bash
cd backend
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install langchain-community
```

---

## Step 3: Modify the LLM Services Code

You need to update the AI integration code to route requests to your local Ollama instance instead of the Groq API.

Locate your primary LLM integration file (e.g., `backend/app/modules/model_selector/api_integrations.py` or your main service file) and make the following replacements:

**Before (Using Groq API):**
```python
from langchain_groq import ChatGroq
import os

def get_llm():
    return ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-8b-8192"
    )
```

**After (Using Local Ollama):**
```python
from langchain_community.chat_models import ChatOllama

def get_llm():
    # This connects to the Ollama server running locally on your machine
    return ChatOllama(
        model="llama3",
        temperature=0.7,
        base_url="http://localhost:11434" # Default Ollama port
    )
```

Apply this change wherever you instantiate the chat model in your backend architecture.

---

## Step 4: Update Environment Variables

Since you are no longer relying on external APIs for your core LLM generation, you can safely remove or comment out the `GROQ_API_KEY` in your backend `.env` file to ensure no cloud APIs are hit.

```env
# Comment out or remove the API key
# GROQ_API_KEY=your_api_key_here

# Ensure your database and other local settings remain intact
DATABASE_URL=postgresql://user:password@localhost:5432/carbonsense
REDIS_URL=redis://localhost:6379/0
```

*Note: If you are using API keys for specific environmental APIs (like Electricity Maps or Climatiq), keep those intact.*

---

## Step 5: Start the Application

With Ollama running in the background and your code pointing to `http://localhost:11434`, start your backend and frontend servers normally:

**Terminal 1 (Backend):**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

## Advanced: How Local "Model Detection" Works

CarbonSense AI includes an **Adaptive Model Selector** that automatically determines which model size (tier) is best for a given query. When running locally, you can map these tiers to specific Ollama models to maintain carbon efficiency.

### 1. The Logic: Complexity-Based Routing
The system analyzes every query before sending it to the LLM. It looks for:
*   **Query Type**: Is it factual, reasoning-heavy, or code-related?
*   **Complexity**: Estimated based on keywords and length.
*   **Capabilities**: Does the query require "Expert Reasoning" or just a "Simple Explanation"?

### 2. Local Model Mapping (Conceptual)
In a cloud-free setup, you would download multiple models and map them to the system tiers like this:

| Tier | Cloud Baseline | Recommended Local (Ollama) | Why? |
| :--- | :--- | :--- | :--- |
| **Small** | Llama 3.1 8B | `llama3:8b` | Balanced for reasoning and complex answers. |
| **Tiny** | Llama 3 8B (Instant) | `phi3` or `gemma:2b` | Extremely fast and low carbon for simple facts. |

### 3. Routing Example
If a user asks: *"What is 2+2?"*
1.  **Detector** flags this as "Simple Factual" (Complexity: 0.1).
2.  **Selector** chooses the **Tiny** tier.
3.  **Local Integrator** routes the request to `phi3`.

If a user asks: *"Write a Python script for a carbon-neutral blockchain."*
1.  **Detector** flags this as "Code Advanced" (Complexity: 0.9).
2.  **Selector** chooses the **Small/Medium** tier.
3.  **Local Integrator** routes the request to `llama3`.

### 4. Implementation Strategy
To implement this, you would modify `backend/app/modules/model_selector/adaptive_selector.py` to change the `DEFAULT_MODEL_TIERS` to use your local model names and set the `endpoint` to `local` (or use a custom Ollama endpoint).

---

## Summary
By combining **Ollama** with CarbonSense's **Adaptive Selector**, you create a system that is not only private and free but also intelligently saves energy by using the smallest possible local model required for the task.

