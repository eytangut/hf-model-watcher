import requests
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retry_request(url, params=None, headers=None, max_retries=3):
    backoff = [2, 8, 30]
    for i in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            return response
        except Exception as e:
            if i == max_retries - 1:
                logger.error(f"Failed to fetch {url} after {max_retries} attempts: {e}")
                raise
            time.sleep(backoff[i])

def fetch_new_models(org, limit=50):
    url = f"https://huggingface.co/api/models"
    params = {
        "author": org,
        "sort": "createdAt",
        "direction": "-1",
        "limit": limit
    }
    try:
        response = retry_request(url, params=params)
        return response.json()
    except Exception:
        return []

def get_model_card(model_id):
    url = f"https://huggingface.co/{model_id}/raw/main/README.md"
    try:
        response = retry_request(url)
        return response.text
    except Exception:
        return ""

def get_model_config(model_id):
    url = f"https://huggingface.co/{model_id}/raw/main/config.json"
    try:
        response = retry_request(url)
        return response.json()
    except Exception:
        return {}

def check_gguf_exists(model_id):
    # Search for sibling repo with -GGUF suffix
    org, name = model_id.split('/')
    gguf_id = f"{org}/{name}-GGUF"
    url = f"https://huggingface.co/api/models/{gguf_id}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return gguf_id
    except:
        pass
    
    # Also search for community uploads (this is a simplified search)
    search_url = "https://huggingface.co/api/models"
    search_params = {"search": f"{name} GGUF", "limit": 5}
    try:
        response = requests.get(search_url, params=search_params, timeout=5)
        if response.status_code == 200:
            results = response.json()
            for r in results:
                if "gguf" in r['modelId'].lower():
                    return r['modelId']
    except:
        pass
    
    return None
