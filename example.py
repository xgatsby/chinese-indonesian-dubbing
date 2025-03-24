#!/usr/bin/env python3
"""
Example script to demonstrate the Chinese-to-Indonesian video dubbing pipeline.

This script provides a simple example of how to use the pipeline with a sample video.
"""

import os
import argparse
from main import run_pipeline

def main():
    """Run an example of the Chinese-to-Indonesian video dubbing pipeline"""
    parser = argparse.ArgumentParser(
        description="Example of Chinese-to-Indonesian Video Dubbing Pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("video_path", help="Path to input Chinese video file")
    parser.add_argument("--output-dir", default="./dubbing_output", 
                        help="Directory to save all output files")
    parser.add_argument("--model-size", choices=["tiny", "base"], default="tiny",
                        help="Model size for transcription (tiny is faster, base is more accurate)")
    args = parser.parse_args()
    
    print("=" * 80)
    print("Chinese to Indonesian Video Dubbing Example")
    print("=" * 80)
    print(f"Input video: {args.video_path}")
    print(f"Output directory: {args.output_dir}")
    print(f"Model size: {args.model_size}")
    print("=" * 80)
    
    # Run the pipeline with default settings
    output_paths = run_pipeline(
        args.video_path,
        args.output_dir,
        model_size=args.model_size,
        audio_method="ffmpeg",
        video_method="ffmpeg",
        audio_volume=1.0,
        background_volume=0.1
    )
    
    if output_paths:
        print("\nSuccess! Here's what was generated:")
        print(f"- Dubbed video: {output_paths['output_video']}")
        print(f"- Validation report: {output_paths.get('validation_report', 'Not available')}")
        print("\nTo customize the dubbing process, use the main.py script directly with additional options.")
    else:
        print("\nThe dubbing process encountered errors. Check the error logs in the output directory.")

if __name__ == "__main__":
    main()
