#!/usr/bin/env python3
"""
Validation Module for Chinese-to-Indonesian Video Dubbing Pipeline

This module validates the quality of the dubbed video output.
"""

import os
import argparse
import json
import time
import subprocess
import numpy as np
from moviepy.editor import VideoFileClip
from faster_whisper import WhisperModel

def calculate_bleu_score(reference, hypothesis):
    """
    Calculate a simplified BLEU score for translation quality
    
    Args:
        reference (str): Reference text (original translation)
        hypothesis (str): Hypothesis text (transcribed from dubbed audio)
    
    Returns:
        float: BLEU score (0.0-1.0)
    """
    # Simple word-level BLEU calculation
    ref_words = reference.lower().split()
    hyp_words = hypothesis.lower().split()
    
    # Count matching words
    matches = sum(1 for w in hyp_words if w in ref_words)
    
    # Calculate precision
    precision = matches / len(hyp_words) if len(hyp_words) > 0 else 0
    
    # Calculate brevity penalty
    bp = min(1.0, len(hyp_words) / len(ref_words)) if len(ref_words) > 0 else 0
    
    # Calculate BLEU score
    bleu = bp * precision
    return bleu

def measure_audio_sync(original_segments, dubbed_audio_path, language="id"):
    """
    Measure audio synchronization by comparing segment timings
    
    Args:
        original_segments (list): Original timing segments
        dubbed_audio_path (str): Path to dubbed audio file
        language (str): Language code for transcription (default: id for Indonesian)
    
    Returns:
        dict: Synchronization metrics
    """
    try:
        # Transcribe the dubbed audio to get timing
        print("Transcribing dubbed audio to measure synchronization...")
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(dubbed_audio_path, language=language, beam_size=5)
        
        # Convert segments to list
        dubbed_segments = []
        for segment in segments:
            dubbed_segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })
        
        # Calculate timing differences
        timing_diffs = []
        for i, orig in enumerate(original_segments):
            if i < len(dubbed_segments):
                # Calculate start and end time differences
                start_diff = abs(orig["start"] - dubbed_segments[i]["start"])
                end_diff = abs(orig["end"] - dubbed_segments[i]["end"])
                timing_diffs.append((start_diff + end_diff) / 2)
        
        # Calculate metrics
        if timing_diffs:
            avg_diff = sum(timing_diffs) / len(timing_diffs)
            max_diff = max(timing_diffs)
            min_diff = min(timing_diffs)
            
            return {
                "average_sync_diff_seconds": avg_diff,
                "max_sync_diff_seconds": max_diff,
                "min_sync_diff_seconds": min_diff,
                "segments_compared": len(timing_diffs)
            }
        else:
            return {
                "error": "No segments could be compared"
            }
    
    except Exception as e:
        print(f"Error measuring audio sync: {e}")
        return {"error": str(e)}

def validate_output(dubbed_video_path, translation_path, output_dir=None):
    """
    Validate the quality of the dubbed video output
    
    Args:
        dubbed_video_path (str): Path to dubbed video file
        translation_path (str): Path to translation file with original segments
        output_dir (str): Directory to save validation report
    
    Returns:
        str: Path to validation report file
    """
    # Validate input files
    if not os.path.exists(dubbed_video_path):
        print(f"Error: Dubbed video file {dubbed_video_path} does not exist")
        return None
    if not os.path.exists(translation_path):
        print(f"Error: Translation file {translation_path} does not exist")
        return None
    
    # Create output directory if needed
    if output_dir is None:
        output_dir = os.path.dirname(dubbed_video_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename
    video_basename = os.path.basename(dubbed_video_path)
    video_name = os.path.splitext(video_basename)[0]
    report_path = os.path.join(output_dir, f"{video_name}_validation.json")
    
    try:
        # Load translation data
        with open(translation_path, "r", encoding="utf-8") as f:
            translated_segments = json.load(f)
        
        # Extract audio from dubbed video for analysis
        video = VideoFileClip(dubbed_video_path)
        temp_audio_path = os.path.join(output_dir, "temp_dubbed_audio.wav")
        video.audio.write_audiofile(temp_audio_path, fps=16000, nbytes=2, codec='pcm_s16le')
        video.close()
        
        # Start validation
        validation_results = {
            "video_path": dubbed_video_path,
            "translation_path": translation_path,
            "validation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "metrics": {}
        }
        
        # 1. Video integrity check
        try:
            cmd = ["ffmpeg", "-v", "error", "-i", dubbed_video_path, "-f", "null", "-"]
            result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
            validation_results["metrics"]["video_integrity"] = {
                "status": "pass" if not result.stderr else "fail",
                "errors": result.stderr if result.stderr else "None"
            }
        except Exception as e:
            validation_results["metrics"]["video_integrity"] = {
                "status": "error",
                "errors": str(e)
            }
        
        # 2. Audio sync measurement
        sync_metrics = measure_audio_sync(translated_segments, temp_audio_path)
        validation_results["metrics"]["audio_sync"] = sync_metrics
        
        # 3. Duration comparison
        original_duration = translated_segments[-1]["end"] if translated_segments else 0
        dubbed_duration = video.duration if hasattr(video, "duration") else 0
        validation_results["metrics"]["duration"] = {
            "original_duration": original_duration,
            "dubbed_duration": dubbed_duration,
            "difference": abs(original_duration - dubbed_duration)
        }
        
        # 4. File size and bitrate
        video_size_bytes = os.path.getsize(dubbed_video_path)
        validation_results["metrics"]["file_info"] = {
            "size_bytes": video_size_bytes,
            "size_mb": video_size_bytes / (1024 * 1024),
            "bitrate_kbps": (video_size_bytes * 8) / (dubbed_duration * 1000) if dubbed_duration > 0 else 0
        }
        
        # Save validation report
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(validation_results, f, ensure_ascii=False, indent=2)
        
        # Clean up temporary files
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        
        print(f"Validation completed and report saved to {report_path}")
        return report_path
    
    except Exception as e:
        print(f"Error validating output: {e}")
        return None

def main():
    """Command line interface for output validation"""
    parser = argparse.ArgumentParser(description="Validate Chinese-to-Indonesian dubbed video")
    parser.add_argument("dubbed_video_path", help="Path to dubbed video file")
    parser.add_argument("translation_path", help="Path to translation file with original segments")
    parser.add_argument("--output-dir", help="Directory to save validation report")
    args = parser.parse_args()
    
    validate_output(args.dubbed_video_path, args.translation_path, args.output_dir)

if __name__ == "__main__":
    main()
