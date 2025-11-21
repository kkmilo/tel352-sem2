import sys
import os
import cv2
import numpy as np
from pathlib import Path

# Add parent directory to path to import ColorInsight
sys.path.insert(0, str(Path(__file__).parent.parent))

from ColorInsight_tflite_only import (
    analyze_feature,
    SEASON_NAMES,
    SEASON_DESCRIPTIONS
)


def run_colorinsight_from_image(pil_image, method='simple', verbose=False):
    """
    Receives a PIL image and returns color analysis results.
    
    Args:
        pil_image: PIL Image object
        method: 'simple', 'mediapipe', or 'facer_tflite'
        verbose: bool for detailed output
    
    Returns:
        dict with analysis results and annotated masks
    """
    
    # Save PIL image temporarily
    temp_path = "/tmp/colorinsight_temp.jpg"
    pil_image.save(temp_path)
    
    # Analyze features
    tasks = [("Piel", "skin"), ("Pelo", "hair"), ("Labios", "lips")]
    results = {}
    masks = {}
    
    for name, mtype in tasks:
        result = analyze_feature(temp_path, name, mtype, method, verbose)
        
        if "error" not in result:
            results[name] = {
                "season": result["season_name"],
                "description": result["description"]
            }
            
            # Load mask image
            if "mask_file" in result and os.path.exists(result["mask_file"]):
                mask_img = cv2.imread(result["mask_file"])
                masks[name] = mask_img
                # Clean up temporary mask file
                os.remove(result["mask_file"])
        else:
            results[name] = {"error": result["error"]}
    
    # Clean up temp image
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    return {
        "results": results,
        "masks": masks
    }
