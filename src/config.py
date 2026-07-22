# Configuration for Hugging Face New-Model Watcher

# List of Hugging Face org/namespace names to track
TRACKED_ORGS = [
    "meta-llama",
    "mistralai",
    "google",
    "Qwen",
    "deepseek-ai",
    "microsoft",
    "openai",
    "01-ai",
    "nvidia",
    "ai21labs",
    "stabilityai",
    "allenai",
]

# Hardware profile (Windows 11, i7 11th gen, 16GB RAM)
HARDWARE_PROFILE = {
    "usable_ram_gb": 10.0,
    "overhead_gb": 1.5,
    "cpu_only": True
}

# Similarity threshold for filtering near-duplicate model cards
SIMILARITY_THRESHOLD = 0.85

# Max length for model card excerpt to store in state
CARD_EXCERPT_LENGTH = 2000

# Email cadence (not used in code, but for reference)
# Polling: Daily
# Digest: Every 14 days
