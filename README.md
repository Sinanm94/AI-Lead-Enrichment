# AI Lead Enrichment Pipeline

A local, privacy-first AI pipeline designed to automatically qualify, score, and strategize real estate leads.

This project demonstrates a Hybrid AI Architecture, deliberately decoupling deterministic mathematical logic from Large Language Model (LLM) text generation to eliminate hallucinations, maximize computational efficiency, and run entirely locally on edge hardware.

## Architecture

Standard LLM implementations often force neural networks to perform basic arithmetic, leading to high latency and numerical hallucinations. This system solves that bottleneck by splitting the workload:

1. **Deterministic Logic Engine:** A Python backend calculates strict market baselines (e.g., Downtown Dubai vs. Deira) and outputs a precise, mathematically sound 1-10 Quality Score.
2. **LLM Synthesizer:** With the computation securely handled, a lightweight, locally hosted LLM reads the calculated metrics to generate nuanced agent strategies and property recommendations.

**Result:** 100% mathematical accuracy, zero price hallucinations, and the ability to run high-quality NLP inferences on constrained hardware (optimized for 4GB VRAM).

## Key Features

* **Deterministic Scoring:** Hardcoded market logic evaluates client budgets against dynamic property types and area tiers.
* **Local NLP Generation:** Utilizes Ollama to run Llama 3.2 locally, ensuring zero data leakage of sensitive client contact information.
* **Responsive Dashboard:** A minimalist Tailwind CSS front-end featuring dynamic DOM sorting (by Score, Budget) and real-time metric calculations.
* **Defensive Fallbacks:** Robust Python error handling ensures the pipeline completes execution even during unexpected LLM formatting anomalies.

## Tech Stack

* **Backend:** Python 3 (CSV parsing, logic routing, REST API requests)
* **AI Engine:** Ollama (Local Llama 3.2 / Qwen models)
* **Frontend:** HTML5, Vanilla JavaScript, Tailwind CSS (via CDN)

## Quick Start

### 1. Prerequisites
Install Python 3.x and Ollama. Pull the required model:
```bash
ollama pull llama3.2

## Screenshots
<img width="1897" height="914" alt="image" src="https://github.com/user-attachments/assets/45ec3fd1-beb6-4427-b79e-cedae10a18fe" />
<img width="1888" height="906" alt="image" src="https://github.com/user-attachments/assets/7d60d8e1-bc10-4e88-9b62-2b19f18fb452" />
<img width="1887" height="874" alt="image" src="https://github.com/user-attachments/assets/45ade4ef-6c79-4a1c-9a65-4ba08f359f39" />
<img width="1901" height="922" alt="image" src="https://github.com/user-attachments/assets/4e825d27-4a02-46f4-9720-eac4fde6d05d" />



