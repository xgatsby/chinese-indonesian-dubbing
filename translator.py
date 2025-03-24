#!/usr/bin/env python3
"""
Translation Module for Chinese-to-Indonesian Video Dubbing Pipeline

This module translates Chinese text to Indonesian using the transformers library
with the Helsinki-NLP/opus-mt-zh-id model.
"""

import os
import argparse
import json
from transformers import MarianMTModel, MarianTokenizer

def translate_text(text, model_name="Helsinki-NLP/opus-mt-zh-id"):
    """
    Translate Chinese text to Indonesian
    
    Args:
        text (str): Chinese text to translate
        model_name (str): Model name for translation
    
    Returns:
        str: Translated Indonesian text
    """
    try:
        # Load tokenizer and model
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        
        # Tokenize and translate
        inputs = tokenizer(text, return_tensors="pt", padding=True)
        translated = model.generate(**inputs)
        
        # Decode the translated text
        translated_text = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
        return translated_text
    
    except Exception as e:
        print(f"Error translating text: {e}")
        return None

def translate_segments(segments, output_dir=None, input_file=None):
    """
    Translate transcript segments from Chinese to Indonesian
    
    Args:
        segments (list): List of transcript segments with start, end, and text
        output_dir (str): Directory to save output translation file
        input_file (str): Path to input transcript file (for naming output)
    
    Returns:
        tuple: (Path to translation file, Translated segments)
    """
    # Create output directory if needed
    if output_dir is None and input_file is not None:
        output_dir = os.path.dirname(input_file)
    if output_dir is None:
        output_dir = os.getcwd()
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename
    if input_file is not None:
        input_basename = os.path.basename(input_file)
        input_name = os.path.splitext(input_basename)[0]
        output_path = os.path.join(output_dir, f"{input_name}_translated.json")
    else:
        output_path = os.path.join(output_dir, "translated_segments.json")
    
    try:
        # Translate each segment
        translated_segments = []
        
        print(f"Translating {len(segments)} segments from Chinese to Indonesian...")
        for i, segment in enumerate(segments):
            print(f"Translating segment {i+1}/{len(segments)}...")
            
            # Extract text and translate
            chinese_text = segment["text"]
            indonesian_text = translate_text(chinese_text)
            
            # Create translated segment
            translated_segment = {
                "start": segment["start"],
                "end": segment["end"],
                "original": chinese_text,
                "translated": indonesian_text
            }
            translated_segments.append(translated_segment)
        
        # Save translated segments to file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(translated_segments, f, ensure_ascii=False, indent=2)
        
        print(f"Translation completed and saved to {output_path}")
        return output_path, translated_segments
    
    except Exception as e:
        print(f"Error translating segments: {e}")
        return None, None

def translate_from_file(transcript_path, output_dir=None):
    """
    Translate transcript from file
    
    Args:
        transcript_path (str): Path to input transcript file
        output_dir (str): Directory to save output translation file
    
    Returns:
        tuple: (Path to translation file, Translated segments)
    """
    # Validate input file
    if not os.path.exists(transcript_path):
        print(f"Error: Input transcript file {transcript_path} does not exist")
        return None, None
    
    try:
        # Read transcript file and parse segments
        segments = []
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Parse timestamp and text
                parts = line.split(": ", 1)
                if len(parts) != 2:
                    continue
                
                timestamp, text = parts
                start_end = timestamp.split(" --> ")
                if len(start_end) != 2:
                    continue
                
                start, end = float(start_end[0]), float(start_end[1])
                segments.append({
                    "start": start,
                    "end": end,
                    "text": text
                })
        
        # Translate segments
        return translate_segments(segments, output_dir, transcript_path)
    
    except Exception as e:
        print(f"Error reading transcript file: {e}")
        return None, None

def main():
    """Command line interface for translation"""
    parser = argparse.ArgumentParser(description="Translate Chinese transcript to Indonesian")
    parser.add_argument("transcript_path", help="Path to input transcript file")
    parser.add_argument("--output-dir", help="Directory to save output translation file")
    args = parser.parse_args()
    
    translate_from_file(args.transcript_path, args.output_dir)

if __name__ == "__main__":
    main()
