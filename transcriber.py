#!/usr/bin/env python3
"""
Transcription Module for Chinese-to-Indonesian Video Dubbing Pipeline

This module transcribes Chinese audio to text using faster-whisper.
"""

import os
import argparse
import time
from faster_whisper import WhisperModel

def transcribe_audio(audio_path, output_dir=None, model_size="base", language="zh"):
    """
    Transcribe audio using faster-whisper
    
    Args:
        audio_path (str): Path to input audio file
        output_dir (str): Directory to save output transcript file
        model_size (str): Model size to use (tiny, base, small, medium, large)
        language (str): Language code for transcription (default: zh for Chinese)
    
    Returns:
        tuple: (Path to transcript file, Transcript segments)
    """
    # Validate input file
    if not os.path.exists(audio_path):
        print(f"Error: Input audio file {audio_path} does not exist")
        return None, None
    
    # Create output directory if needed
    if output_dir is None:
        output_dir = os.path.dirname(audio_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename
    audio_basename = os.path.basename(audio_path)
    audio_name = os.path.splitext(audio_basename)[0]
    output_path = os.path.join(output_dir, f"{audio_name}_transcript.txt")
    
    try:
        # Load model - use CPU for compatibility
        print(f"Loading {model_size} model...")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
        # Transcribe audio
        print(f"Transcribing {audio_path}...")
        start_time = time.time()
        segments, info = model.transcribe(audio_path, language=language, beam_size=5)
        
        # Process segments
        transcript_text = ""
        segments_list = []
        
        for segment in segments:
            transcript_text += f"{segment.start:.2f} --> {segment.end:.2f}: {segment.text}\n"
            segments_list.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })
        
        # Save transcript to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcript_text)
        
        elapsed_time = time.time() - start_time
        print(f"Transcription completed in {elapsed_time:.2f} seconds")
        print(f"Detected language: {info.language} with probability {info.language_probability:.2f}")
        print(f"Transcript saved to {output_path}")
        
        return output_path, segments_list
    
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None, None

def main():
    """Command line interface for audio transcription"""
    parser = argparse.ArgumentParser(description="Transcribe Chinese audio to text")
    parser.add_argument("audio_path", help="Path to input audio file")
    parser.add_argument("--output-dir", help="Directory to save output transcript file")
    parser.add_argument("--model-size", choices=["tiny", "base", "small", "medium", "large"], 
                        default="base", help="Model size to use (default: base)")
    parser.add_argument("--language", default="zh", help="Language code (default: zh for Chinese)")
    args = parser.parse_args()
    
    transcribe_audio(args.audio_path, args.output_dir, args.model_size, args.language)

if __name__ == "__main__":
    main()
