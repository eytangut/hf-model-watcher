# Hugging Face New-Model Watcher

This project is a Python-based watcher that tracks new AI model releases from a curated list of AI labs on Hugging Face. It filters out non-innovative models (fine-tunes, quantizations, re-uploads), evaluates their plausible hardware fit on a specific low-end machine profile, and sends a biweekly digest email summarizing new findings.

## Features

- **Hugging Face API Integration**: Fetches new models from specified organizations.
- **Intelligent Filtering**: Identifies and skips derivative models (fine-tunes, quantizations) using metadata, naming conventions, and text similarity.
- **Hardware Feasibility Assessment**: Programmatically estimates if a model can run on a CPU-only machine with limited RAM, providing a structured verdict.
- **AI-Powered Summaries**: Uses Groq (with Gemini as a fallback) to generate human-readable hardware verdicts and concise summaries of new models, including use cases, key innovations, and benchmark notes.
- **Priority Ranking**: Ranks new models within a digest based on hardware fit and innovation to present the most relevant information first.
- **State Persistence**: Stores seen models and pending digest entries in JSON files, committed back to the repository.
- **Biweekly Email Digest**: Sends a formatted HTML email with new model summaries.
- **GitHub Actions Workflows**: Automates polling for new models and sending biweekly digests.

## Project Structure

```
/
├── .github/workflows/
│   ├── poll.yml          # Frequent polling workflow (e.g., daily)
│   └── digest.yml        # Biweekly digest workflow
├── src/
│   ├── config.py         # TRACKED_ORGS, hardware profile constants, thresholds
│   ├── hf_client.py       # HF API fetch + model card retrieval
│   ├── filters.py         # base_model check, suffix heuristic, similarity fallback
│   ├── hardware_fit.py    # Programmatic feasibility computation
│   ├── ai_client.py       # Groq/Gemini call wrapper with retry logic
│   ├── digest.py          # Priority ranking + email composition/sending
│   ├── state.py           # Load/save state JSON, git commit helper
│   ├── poll_main.py       # Main script for the polling workflow
│   └── digest_main.py     # Main script for the digest workflow
├── state/
│   ├── seen_models.json   # Persisted state of all seen models
│   └── pending_digest.json# Models awaiting inclusion in the next digest
├── requirements.txt
└── README.md
```

## Detailed Setup Instructions

Follow these steps to set up and run the Hugging Face New-Model Watcher project in your GitHub repository.

### 1. Create a New GitHub Repository

Start by creating a new, empty GitHub repository. You can name it `hf-model-watcher` or anything you prefer.

### 2. Clone the Repository and Add Project Files

Clone your newly created repository to your local machine:

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

Now, copy all the project files (the `src/`, `.github/workflows/`, `state/` directories, `requirements.txt`, `.gitignore`, and `README.md` from the provided ZIP archive) into the root of your cloned repository.

### 3. Install Dependencies (for local testing/development)

While the GitHub Actions workflows will handle dependency installation automatically, you might want to install them locally for testing or further development:

```bash
pip install -r requirements.txt
```

### 4. Configure GitHub Secrets

This project relies on GitHub Secrets to securely store sensitive information like API keys and email credentials. You **must** configure these in your GitHub repository settings.

1.  Navigate to your GitHub repository on the web.
2.  Go to `Settings` -> `Secrets and variables` -> `Actions`.
3.  Click on `New repository secret` and add the following secrets:

    -   `GROQ_API_KEY`: Your API key for Groq. You can obtain one from [Groq Cloud](https://console.groq.com/keys).
    -   `GEMINI_API_KEY`: (Optional) Your API key for Google Gemini. This is used as a fallback if Groq fails or is unavailable. Obtain it from [Google AI Studio](https://aistudio.google.com/app/apikey).
    -   `SMTP_HOST`: The hostname of your SMTP server (e.g., `smtp.gmail.com`, `smtp.mailgun.org`).
    -   `SMTP_PORT`: The port for your SMTP server (commonly `587` for TLS or `465` for SSL).
    -   `SMTP_USER`: The email address you want to send digests *from*.
    -   `SMTP_PASSWORD`: The password or an application-specific password for the `SMTP_USER` email account. For Gmail, you'll need to generate an [App Password](https://support.google.com/accounts/answer/185833).
    -   `DIGEST_TO_EMAIL`: The email address where you want to *receive* the biweekly digests.

### 5. Commit and Push Initial Files

After adding all the project files and configuring secrets, commit and push them to your GitHub repository:

```bash
git add .
git commit -m "Initial project setup"
git push origin main
```

### 6. Adjust `TRACKED_ORGS` (Optional)

Edit the `src/config.py` file to modify the `TRACKED_ORGS` list. This list defines which Hugging Face organizations you wish to monitor for new model releases. You can add or remove entries as needed.

```python
# src/config.py
TRACKED_ORGS = [
    "meta-llama",
    "mistralai",
    "google",
    "Qwen",
    # Add or remove organizations here
]
```

Commit and push any changes to `src/config.py`.

### 7. Monitor GitHub Actions Workflows

Once the files are pushed, GitHub Actions will automatically detect the workflows:

-   **Daily Polling (`poll.yml`)**: This workflow runs daily (at midnight UTC by default) to fetch new models, apply filters, evaluate hardware fit, generate AI summaries, update the `state/seen_models.json` file, and add new alert-worthy models to `state/pending_digest.json`.
-   **Biweekly Digest (`digest.yml`)**: This workflow runs every 14 days (at midnight UTC by default). It reads `state/pending_digest.json`, ranks models, sends an HTML email digest to `DIGEST_TO_EMAIL`, and then clears `state/pending_digest.json`.

You can manually trigger these workflows from the "Actions" tab in your GitHub repository to test them immediately.

## Hardware Profile

The project is configured to evaluate models against a low-end machine profile:

-   **OS**: Windows 11
-   **CPU**: Intel i7, 11th gen
-   **iGPU**: Intel Iris Xe (not used for LLM inference)
-   **RAM**: ~10 GB realistically available for model + inference overhead.

The hardware fit calculation is programmatic and estimates model size at FP16, Q8, and Q4 quantization levels against this RAM budget. It also checks for GGUF versions for CPU-only inference via `llama.cpp`.

## Example Email Digest

Below is an example of what a biweekly email digest might look like. This is a simulated output based on potential new model releases and their analysis.

```html
<!-- Example HTML Email Content -->
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .model-card { border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-left: 5px solid #007bff; }
        .model-title { font-size: 1.2em; font-weight: bold; color: #007bff; }
        .label { font-weight: bold; color: #555; }
        .ranking-section { background: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>Biweekly AI Model Digest</h1>
    <div class="ranking-section">
        <h3>Priority Ranking & Insight</h3>
        <p>1. **mistralai/Mixtral-8x22B-v0.1**: Highly relevant due to its innovative Mixture-of-Experts architecture and potential for efficient inference even on constrained hardware with quantization.<br>
        2. **google/gemma-2-9b**: Important for its strong performance in a smaller footprint, making it a good candidate for local deployment.<br>
        3. **meta-llama/Llama-3.1-8B**: A solid update to a popular family, offering improved capabilities for general tasks.</p>
    </div>

    <div class="model-card">
        <div class="model-title"><a href="https://huggingface.co/mistralai/Mixtral-8x22B-v0.1">mistralai/Mixtral-8x22B-v0.1</a></div>
        <p><span class="label">License:</span> Apache-2.0</p>
        <p><span class="label">Hardware Verdict:</span> Runs well quantized (Q4) on CPU, expect moderate generation speed. GGUF version available.</p>
        <p><span class="label">Summary:</span> A powerful sparse Mixture-of-Experts model, offering high performance with efficient inference.</p>
        <p><span class="label">Use Case:</span> Advanced text generation, complex reasoning, code generation.</p>
        <p><span class="label">Key Innovation:</span> Scalable MoE architecture enabling high quality with reduced computational cost compared to dense models of similar capacity.</p>
        <p><span class="label">Benchmark Note:</span> Outperforms previous Mistral models on several benchmarks, showing significant gains in reasoning and coding tasks.</p>
    </div>

    <div class="model-card">
        <div class="model-title"><a href="https://huggingface.co/google/gemma-2-9b">google/gemma-2-9b</a></div>
        <p><span class="label">License:</span> Gemma-2</p>
        <p><span class="label">Hardware Verdict:</span> Fits Q4 on CPU, suitable for local experimentation. GGUF version available.</p>
        <p><span class="label">Summary:</span> A lightweight yet powerful open model from Google, designed for responsible AI development.</p>
        <p><span class="label">Use Case:</span> Research, experimentation, fine-tuning for specific tasks, educational purposes.</p>
        <p><span class="label">Key Innovation:</span> Built with Google's latest research, offering strong performance in a compact size, emphasizing safety and responsible deployment.</p>
        <p><span class="label">Benchmark Note:</span> Shows competitive performance against models in its size class, particularly strong in reasoning and language understanding.</p>
    </div>

    <div class="model-card">
        <div class="model-title"><a href="https://huggingface.co/meta-llama/Llama-3.1-8B">meta-llama/Llama-3.1-8B</a></div>
        <p><span class="label">License:</span> Llama-3.1</p>
        <p><span class="label">Hardware Verdict:</span> Fits Q4 on CPU, good for general use. GGUF version available.</p>
        <p><span class="label">Summary:</span> An updated version of the Llama 3 series, offering enhanced capabilities and stability.</p>
        <p><span class="label">Use Case:</span> General purpose chatbot, content creation, summarization, coding assistance.</p>
        <p><span class="label">Key Innovation:</span> Incremental improvements over Llama 3, focusing on robustness and broader applicability across various tasks.</p>
        <p><span class="label">Benchmark Note:</span> Maintains strong performance across a wide range of benchmarks, with slight improvements in instruction following and safety.</p>
    </div>

</body>
</html>
```
