import os
import time
import json
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.use_fallback = False

    def _retry_call(self, func, *args, **kwargs):
        backoff = [2, 8, 30]
        for i in range(3):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"AI call failed (attempt {i+1}): {e}")
                if i == 2: raise
                time.sleep(backoff[i])

    def call_groq(self, prompt, system_prompt="You are a helpful assistant.", json_mode=False):
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }
        if json_mode:
            data["response_format"] = {"type": "json_object"}

        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content) if json_mode else content

    def call_gemini(self, prompt, system_prompt="", json_mode=False):
        # Stub for Gemini fallback
        # In a real implementation, this would use the Gemini API
        logger.info("Gemini fallback triggered (stub)")
        raise NotImplementedError("Gemini fallback not fully implemented in this version")

    def get_hardware_verdict(self, fit_data, license_str):
        if not fit_data:
            return "Hardware fit could not be determined due to missing parameter count."
        
        prompt = f"""
        Pre-computed feasibility for a low-end machine (10GB usable RAM):
        - Fits Q4: {fit_data['fits_q4']}
        - Fits Q8: {fit_data['fits_q8']}
        - Fits FP16: {fit_data['fits_fp16']}
        - Min RAM needed (Q4): {fit_data['min_ram_needed_gb']} GB
        - License: {license_str}

        Phrase a human-readable one-line verdict for this model on this machine. 
        Example: "Runs well quantized (Q4) on CPU, expect slow generation."
        Do not independently judge feasibility, only phrase the numbers provided.
        """
        return self._retry_call(self.call_groq, prompt)

    def get_model_summary(self, model_card_text):
        system_prompt = "You are an AI model analyst. Return only valid JSON."
        prompt = f"""
        Analyze this Hugging Face model card and provide a summary.
        Model Card Text:
        {model_card_text[:4000]}

        Return a JSON object with:
        {{
          "one_line_summary": "...",
          "use_case": "...",
          "key_innovation": "...",
          "benchmark_note": "short comparison vs. this org's previous model if present; else empty string"
        }}
        """
        return self._retry_call(self.call_groq, prompt, system_prompt=system_prompt, json_mode=True)

    def rank_models(self, models_data):
        if not models_data: return []
        
        prompt = "Rank these new AI models by relevance and interest for a user with a low-end machine. "
        prompt += "Consider hardware fit and innovation. Return an ordered list of model IDs with a one-line reason each.\n\n"
        for m in models_data:
            prompt += f"ID: {m['id']}, Fit: {m.get('hardware_verdict')}, Innovation: {m.get('summary', {}).get('key_innovation')}\n"
        
        # This returns a ranked list as text
        return self._retry_call(self.call_groq, prompt)
