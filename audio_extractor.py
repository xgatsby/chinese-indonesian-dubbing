#!/usr/bin/env python3
"""
Audio Extraction Module for Chinese-to-Indonesian Video Dubbing Pipeline

This module extracts audio from a Chinese-language video file using ffmpeg-python.
"""

import os
import argparse
import ffmpeg
from moviepy.editor import VideoFileClip

def extract_audio_ffmpeg(video_path, output_path, sample_rate=16000):
    """
    Extract audio from video using ffmpeg-python
    
    Args:
        video_path (str): Path to input video file
        output_path (str): Path to output audio file
        sample_rate (int): Audio sample rate (default: 16000 Hz for STT)
    
    Returns:
        str: Path to extracted audio file
    """
    try:
        # Extract audio using ffmpeg
        (
            ffmpeg
            .input(video_path)
            .output(output_path, acodec='pcm_s16le', ar=sample_rate, ac=1)
            .run(quiet=True, overwrite_output=True)
        )
        print(f"Audio extracted successfully to {output_path}")
        return output_path
    except ffmpeg.Error as e:
        print(f"Error extracting audio: {e.stderr.decode()}")
        return None

def extract_audio_moviepy(video_path, output_path):
    """
    Alternative method to extract audio using moviepy
    
    Args:
        video_path (str): Path to input video file
        output_path (str): Path to output audio file
    
    Returns:
        str: Path to extracted audio file
    """
    try:
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(output_path, fps=16000, nbytes=2, codec='pcm_s16le')
        video.close()
        print(f"Audio extracted successfully to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error extracting audio with moviepy: {e}")
        return None

def extract_audio(video_path, output_dir=None, method="ffmpeg"):
    """
    Extract audio from video file
    
    Args:
        video_path (str): Path to input video file
        output_dir (str): Directory to save output audio file (default: same as video)
        method (str): Extraction method, either "ffmpeg" or "moviepy"
    
    Returns:
        str: Path to extracted audio file
    """
    # Validate input file
    if not os.path.exists(video_path):
        print(f"Error: Input video file {video_path} does not exist")
        return None
    
    # Create output directory if needed
    if output_dir is None:
        output_dir = os.path.dirname(video_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename
    video_basename = os.path.basename(video_path)
    video_name = os.path.splitext(video_basename)[0]
    output_path = os.path.join(output_dir, f"{video_name}_audio.wav")
    
    # Extract audio using selected method
    if method.lower() == "ffmpeg":
        return extract_audio_ffmpeg(video_path, output_path)
    elif method.lower() == "moviepy":
        return extract_audio_moviepy(video_path, output_path)
    else:
        print(f"Error: Unknown extraction method '{method}'. Use 'ffmpeg' or 'moviepy'")
        return None

def main():
    """Command line interface for audio extraction"""
    parser = argparse.ArgumentParser(description="Extract audio from video file")
    parser.add_argument("video_path", help="Path to input video file")
    parser.add_argument("--output-dir", help="Directory to save output audio file")
    parser.add_argument("--method", choices=["ffmpeg", "moviepy"], default="ffmpeg",
                        help="Audio extraction method (default: ffmpeg)")
    args = parser.parse_args()
    
    extract_audio(args.video_path, args.output_dir, args.method)

if __name__ == "__main__":
    main()
