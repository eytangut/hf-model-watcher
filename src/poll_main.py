import logging
from datetime import datetime
from .config import TRACKED_ORGS, CARD_EXCERPT_LENGTH
from .hf_client import fetch_new_models, get_model_card, get_model_config, check_gguf_exists
from .filters import should_skip_model
from .hardware_fit import calculate_fit, get_params_from_config
from .ai_client import AIClient
from .state import load_seen_models, save_seen_models, add_to_pending_digest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    seen_models = load_seen_models()
    ai = AIClient()
    
    for org in TRACKED_ORGS:
        logger.info(f"Polling org: {org}")
        models = fetch_new_models(org)
        
        # Get existing cards for this org for similarity check
        existing_cards = [
            m["card_text_excerpt"] for mid, m in seen_models.items() 
            if mid.startswith(f"{org}/") and "card_text_excerpt" in m
        ]
        
        for m_meta in models:
            model_id = m_meta["modelId"]
            if model_id in seen_models:
                continue
            
            logger.info(f"Processing new model: {model_id}")
            card_text = get_model_card(model_id)
            
            # Basic info
            license_str = m_meta.get("siblings", []) # Not always there, check tags
            tags = m_meta.get("tags", [])
            license_val = next((t.replace("license:", "") for t in tags if t.startswith("license:")), "Unknown")
            
            # Filtering
            skip, reason = should_skip_model(model_id, card_text, existing_cards)
            
            model_entry = {
                "seen_at": datetime.now().isoformat(),
                "card_text_excerpt": card_text[:CARD_EXCERPT_LENGTH],
                "was_alerted": not skip,
                "skip_reason": reason,
                "license": license_val
            }
            
            if not skip:
                logger.info(f"Model {model_id} passed filters. Running AI evaluation.")
                # Hardware fit
                config = get_model_config(model_id)
                params = get_params_from_config(config)
                fit_data = calculate_fit(params)
                
                # GGUF check
                gguf_id = check_gguf_exists(model_id)
                if gguf_id:
                    model_entry["gguf_repo"] = gguf_id
                
                # AI calls
                try:
                    verdict = ai.get_hardware_verdict(fit_data, license_val)
                    summary = ai.get_model_summary(card_text)
                    
                    model_entry["hardware_verdict"] = verdict
                    model_entry["summary"] = summary
                    model_entry["params_b"] = fit_data["params_b"] if fit_data else None
                    
                    # Add to pending digest
                    add_to_pending_digest({"id": model_id, **model_entry})
                except Exception as e:
                    logger.error(f"AI processing failed for {model_id}: {e}")
                    # Don't mark as seen if AI failed, so we retry next time
                    continue

            seen_models[model_id] = model_entry
            save_seen_models(seen_models)
    

if __name__ == "__main__":
    main()
