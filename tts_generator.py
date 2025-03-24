#!/usr/bin/env python3
"""
Text-to-Speech Module for Chinese-to-Indonesian Video Dubbing Pipeline

This module generates Indonesian speech from translated text using gTTS.
"""

import os
import argparse
import json
import time
from gtts import gTTS
from pydub import AudioSegment

def generate_speech(text, output_path, language="id", slow=False):
    """
    Generate speech from text using gTTS
    
    Args:
        text (str): Text to convert to speech
        output_path (str): Path to output audio file
        language (str): Language code (default: id for Indonesian)
        slow (bool): Whether to speak slowly (default: False)
    
    Returns:
        str: Path to generated audio file
    """
    try:
        # Generate speech using gTTS
        tts = gTTS(text=text, lang=language, slow=slow)
        tts.save(output_path)
        return output_path
    
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None

def generate_speech_from_segments(translated_segments, output_dir=None, input_file=None):
    """
    Generate speech for translated segments
    
    Args:
        translated_segments (list): List of translated segments with timing and text
        output_dir (str): Directory to save output audio files
        input_file (str): Path to input translation file (for naming output)
    
    Returns:
        tuple: (Path to combined audio file, List of segment audio files)
    """
    # Create output directory if needed
    if output_dir is None and input_file is not None:
        output_dir = os.path.dirname(input_file)
    if output_dir is None:
        output_dir = os.getcwd()
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename for combined audio
    if input_file is not None:
        input_basename = os.path.basename(input_file)
        input_name = os.path.splitext(input_basename)[0]
        combined_output_path = os.path.join(output_dir, f"{input_name}_indonesian.mp3")
    else:
        combined_output_path = os.path.join(output_dir, "indonesian_speech.mp3")
    
    try:
        # Create segments directory
        segments_dir = os.path.join(output_dir, "segments")
        os.makedirs(segments_dir, exist_ok=True)
        
        # Generate speech for each segment
        segment_files = []
        combined_audio = AudioSegment.silent(duration=0)
        
        print(f"Generating speech for {len(translated_segments)} segments...")
        for i, segment in enumerate(translated_segments):
            print(f"Processing segment {i+1}/{len(translated_segments)}...")
            
            # Extract text and timing
            indonesian_text = segment["translated"]
            start_time = segment["start"] * 1000  # Convert to milliseconds
            end_time = segment["end"] * 1000
            original_duration = end_time - start_time
            
            # Generate segment filename
            segment_filename = f"segment_{i:04d}.mp3"
            segment_path = os.path.join(segments_dir, segment_filename)
            
            # Generate speech for segment
            generate_speech(indonesian_text, segment_path)
            segment_files.append(segment_path)
            
            # Load generated audio and adjust timing
            segment_audio = AudioSegment.from_file(segment_path)
            
            # Add silence at the beginning to match original timing
            if i > 0:
                previous_end = translated_segments[i-1]["end"] * 1000
                silence_duration = max(0, start_time - previous_end)
                silence = AudioSegment.silent(duration=silence_duration)
                combined_audio += silence
            elif i == 0 and start_time > 0:
                silence = AudioSegment.silent(duration=start_time)
                combined_audio += silence
            
            # Add the segment audio
            combined_audio += segment_audio
        
        # Export combined audio
        combined_audio.export(combined_output_path, format="mp3")
        print(f"Combined Indonesian speech saved to {combined_output_path}")
        
        return combined_output_path, segment_files
    
    except Exception as e:
        print(f"Error generating speech from segments: {e}")
        return None, None

def generate_speech_from_file(translation_path, output_dir=None):
    """
    Generate speech from translation file
    
    Args:
        translation_path (str): Path to input translation file (JSON)
        output_dir (str): Directory to save output audio files
    
    Returns:
        tuple: (Path to combined audio file, List of segment audio files)
    """
    # Validate input file
    if not os.path.exists(translation_path):
        print(f"Error: Input translation file {translation_path} does not exist")
        return None, None
    
    try:
        # Read translation file
        with open(translation_path, "r", encoding="utf-8") as f:
            translated_segments = json.load(f)
        
        # Generate speech
        return generate_speech_from_segments(translated_segments, output_dir, translation_path)
    
    except Exception as e:
        print(f"Error reading translation file: {e}")
        return None, None

def main():
    """Command line interface for speech generation"""
    parser = argparse.ArgumentParser(description="Generate Indonesian speech from translated text")
    parser.add_argument("translation_path", help="Path to input translation file (JSON)")
    parser.add_argument("--output-dir", help="Directory to save output audio files")
    args = parser.parse_args()
    
    generate_speech_from_file(args.translation_path, args.output_dir)

if __name__ == "__main__":
    main()
