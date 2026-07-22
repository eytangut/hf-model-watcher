from .config import HARDWARE_PROFILE

def calculate_fit(params_count):
    if not params_count:
        return None
    
    # Convert to Billions if it's large (params_count might be like 7000000000)
    # The spec says safetensors.total which is usually the raw count
    params_b = params_count / 1e9
    
    # Estimates in GB
    # FP16: params * 2 bytes
    fp16_size = params_b * 2
    # Q8: params * 1 byte
    q8_size = params_b * 1
    # Q4: params * 0.5 bytes
    q4_size = params_b * 0.5
    
    budget = HARDWARE_PROFILE["usable_ram_gb"]
    overhead = HARDWARE_PROFILE["overhead_gb"]
    
    def fits(size):
        return (size + overhead) <= budget

    return {
        "fits_q4": fits(q4_size),
        "fits_q8": fits(q8_size),
        "fits_fp16": fits(fp16_size),
        "min_ram_needed_gb": round(q4_size + overhead, 2),
        "params_b": round(params_b, 2)
    }

def get_params_from_config(config):
    # Try common fields
    if not config:
        return None
    
    # safetensors metadata often has total
    if "safetensors" in config and "total" in config["safetensors"]:
        return config["safetensors"]["total"]
    
    # Some configs have num_parameters
    if "num_parameters" in config:
        return config["num_parameters"]
    
    return None
