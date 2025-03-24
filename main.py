#!/usr/bin/env python3
"""
Main Pipeline for Chinese-to-Indonesian Video Dubbing

This script integrates all components of the Chinese-to-Indonesian video dubbing pipeline:
1. Audio extraction from Chinese video
2. Chinese speech-to-text transcription
3. Chinese to Indonesian translation
4. Indonesian text-to-speech generation
5. Audio-video alignment for final dubbed video
6. Output validation

Usage:
    python main.py input_video.mp4 --output-dir /path/to/output --model-size base
"""

import os
import argparse
import time
import json
from audio_extractor import extract_audio
from transcriber import transcribe_audio
from translator import translate_segments
from tts_generator import generate_speech_from_segments
from video_aligner import align_audio_with_video
from validator import validate_output

def create_output_dirs(base_dir):
    """Create output directories for intermediate files"""
    os.makedirs(base_dir, exist_ok=True)
    dirs = {
        "audio": os.path.join(base_dir, "audio"),
        "transcript": os.path.join(base_dir, "transcript"),
        "translation": os.path.join(base_dir, "translation"),
        "speech": os.path.join(base_dir, "speech"),
        "output": os.path.join(base_dir, "output"),
        "validation": os.path.join(base_dir, "validation")
    }
    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    return dirs

def run_pipeline(video_path, output_dir=None, model_size="base", 
                audio_method="ffmpeg", video_method="ffmpeg",
                audio_volume=1.0, background_volume=0.1):
    """
    Run the complete Chinese-to-Indonesian video dubbing pipeline
    
    Args:
        video_path (str): Path to input Chinese video file
        output_dir (str): Directory to save all output files
        model_size (str): Model size for transcription (tiny, base, small, medium, large)
        audio_method (str): Method for audio extraction (ffmpeg or moviepy)
        video_method (str): Method for video alignment (ffmpeg or moviepy)
        audio_volume (float): Volume level for dubbed audio (0.0-1.0)
        background_volume (float): Volume level for original audio (0.0-1.0)
    
    Returns:
        dict: Paths to all output files
    """
    start_time = time.time()
    
    # Validate input file
    if not os.path.exists(video_path):
        print(f"Error: Input video file {video_path} does not exist")
        return None
    
    # Create output directory if needed
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(video_path), "dubbing_output")
    
    # Create output directories
    dirs = create_output_dirs(output_dir)
    
    # Generate base filename
    video_basename = os.path.basename(video_path)
    video_name = os.path.splitext(video_basename)[0]
    
    # Dictionary to store output paths
    output_paths = {
        "input_video": video_path,
        "output_dir": output_dir
    }
    
    try:
        # Step 1: Extract audio from video
        print("\n=== Step 1: Extracting audio from video ===")
        audio_path = extract_audio(video_path, dirs["audio"], audio_method)
        if not audio_path:
            raise Exception("Audio extraction failed")
        output_paths["extracted_audio"] = audio_path
        
        # Step 2: Transcribe Chinese audio to text
        print("\n=== Step 2: Transcribing Chinese audio to text ===")
        transcript_path, segments = transcribe_audio(audio_path, dirs["transcript"], model_size, "zh")
        if not transcript_path or not segments:
            raise Exception("Transcription failed")
        output_paths["transcript"] = transcript_path
        
        # Step 3: Translate Chinese text to Indonesian
        print("\n=== Step 3: Translating Chinese text to Indonesian ===")
        translation_path, translated_segments = translate_segments(segments, dirs["translation"], transcript_path)
        if not translation_path or not translated_segments:
            raise Exception("Translation failed")
        output_paths["translation"] = translation_path
        
        # Step 4: Generate Indonesian speech
        print("\n=== Step 4: Generating Indonesian speech ===")
        speech_path, segment_files = generate_speech_from_segments(translated_segments, dirs["speech"], translation_path)
        if not speech_path:
            raise Exception("Speech generation failed")
        output_paths["indonesian_speech"] = speech_path
        output_paths["speech_segments"] = segment_files
        
        # Step 5: Align audio with video
        print("\n=== Step 5: Aligning audio with video ===")
        output_video_path = align_audio_with_video(
            video_path, speech_path, dirs["output"], video_method, 
            audio_volume, background_volume
        )
        if not output_video_path:
            raise Exception("Audio-video alignment failed")
        output_paths["output_video"] = output_video_path
        
        # Step 6: Validate output
        print("\n=== Step 6: Validating output ===")
        validation_path = validate_output(output_video_path, translation_path, dirs["validation"])
        if validation_path:
            output_paths["validation_report"] = validation_path
        
        # Save pipeline metadata
        metadata = {
            "pipeline_version": "1.0.0",
            "processing_time": time.time() - start_time,
            "input_video": video_path,
            "output_paths": output_paths,
            "parameters": {
                "model_size": model_size,
                "audio_method": audio_method,
                "video_method": video_method,
                "audio_volume": audio_volume,
                "background_volume": background_volume
            },
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        metadata_path = os.path.join(output_dir, f"{video_name}_pipeline_metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        output_paths["metadata"] = metadata_path
        
        print("\n=== Pipeline completed successfully! ===")
        print(f"Total processing time: {time.time() - start_time:.2f} seconds")
        print(f"Output video: {output_video_path}")
        print(f"Metadata: {metadata_path}")
        
        return output_paths
    
    except Exception as e:
        print(f"\nError in dubbing pipeline: {e}")
        
        # Save error log
        error_log = {
            "error": str(e),
            "stage": "unknown",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_steps": output_paths
        }
        
        error_log_path = os.path.join(output_dir, f"{video_name}_error_log.json")
        with open(error_log_path, "w", encoding="utf-8") as f:
            json.dump(error_log, f, ensure_ascii=False, indent=2)
        
        print(f"Error log saved to {error_log_path}")
        return None

def main():
    """Command line interface for the complete pipeline"""
    parser = argparse.ArgumentParser(
        description="Chinese-to-Indonesian Video Dubbing Pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("video_path", help="Path to input Chinese video file")
    parser.add_argument("--output-dir", help="Directory to save all output files")
    parser.add_argument("--model-size", choices=["tiny", "base", "small", "medium", "large"], 
                        default="base", help="Model size for transcription")
    parser.add_argument("--audio-method", choices=["ffmpeg", "moviepy"], default="ffmpeg",
                        help="Method for audio extraction")
    parser.add_argument("--video-method", choices=["ffmpeg", "moviepy"], default="ffmpeg",
                        help="Method for video alignment")
    parser.add_argument("--audio-volume", type=float, default=1.0,
                        help="Volume level for dubbed audio (0.0-1.0)")
    parser.add_argument("--background-volume", type=float, default=0.1,
                        help="Volume level for original audio (0.0-1.0)")
    args = parser.parse_args()
    
    run_pipeline(
        args.video_path, args.output_dir, args.model_size,
        args.audio_method, args.video_method,
        args.audio_volume, args.background_volume
    )

if __name__ == "__main__":
    main()
