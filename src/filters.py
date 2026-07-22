import re
from difflib import SequenceMatcher
from .config import SIMILARITY_THRESHOLD

DERIVATIVE_SUFFIXES = [
    r"-gguf$", r"-awq$", r"-gptq$", r"-int4$", r"-int8$", r"-4bit$", r"-8bit$",
    r"-bnb$", r"-exl2$", r"-mlx$", r"-instruct-tune$", r"-lora$", r"-ft$", r"-quantized$"
]

def is_derivative_by_name(model_id):
    name = model_id.split('/')[-1].lower()
    for suffix in DERIVATIVE_SUFFIXES:
        if re.search(suffix, name):
            return True
    return False

def has_base_model_tag(model_card_text):
    # Check YAML front matter for base_model
    # This is a simple regex check
    match = re.search(r"^base_model:\s*.+", model_card_text, re.MULTILINE)
    return bool(match)

def check_text_similarity(new_text, existing_texts):
    if not existing_texts:
        return 0.0
    
    max_ratio = 0.0
    for existing in existing_texts:
        ratio = SequenceMatcher(None, new_text, existing).ratio()
        if ratio > max_ratio:
            max_ratio = ratio
    return max_ratio

def should_skip_model(model_id, model_card_text, existing_cards_for_org):
    # 1. Filename/suffix heuristic
    if is_derivative_by_name(model_id):
        return True, "derivative_suffix"
    
    # 2. base_model tag check
    if has_base_model_tag(model_card_text):
        return True, "base_model_tag"
    
    # 3. Text-similarity fallback
    similarity = check_text_similarity(model_card_text, existing_cards_for_org)
    if similarity > SIMILARITY_THRESHOLD:
        return True, f"similarity_{similarity:.2f}"
    
    return False, None
