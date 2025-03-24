#!/usr/bin/env python3
"""
Video Dubbing Module for Chinese-to-Indonesian Video Dubbing Pipeline

This module aligns Indonesian audio with the original Chinese video.
"""

import os
import argparse
import ffmpeg
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

def align_audio_with_video_ffmpeg(video_path, audio_path, output_path, 
                                  audio_volume=1.0, background_volume=0.1):
    """
    Align audio with video using ffmpeg-python
    
    Args:
        video_path (str): Path to input video file
        audio_path (str): Path to input audio file (Indonesian speech)
        output_path (str): Path to output video file
        audio_volume (float): Volume level for dubbed audio (0.0-1.0)
        background_volume (float): Volume level for original audio (0.0-1.0)
    
    Returns:
        str: Path to output video file
    """
    try:
        # Extract original audio at reduced volume for background
        if background_volume > 0:
            # Input video
            video = ffmpeg.input(video_path)
            # Extract original audio and adjust volume
            original_audio = video.audio.filter('volume', background_volume)
            # Input dubbed audio and adjust volume
            dubbed_audio = ffmpeg.input(audio_path).audio.filter('volume', audio_volume)
            # Mix the two audio streams
            mixed_audio = ffmpeg.filter([original_audio, dubbed_audio], 'amix', inputs=2, normalize=0)
            # Create output with original video and mixed audio
            output = ffmpeg.output(video.video, mixed_audio, output_path, 
                                  vcodec='copy', acodec='aac', strict='experimental')
        else:
            # If background_volume is 0, just use the dubbed audio
            video = ffmpeg.input(video_path)
            dubbed_audio = ffmpeg.input(audio_path).audio.filter('volume', audio_volume)
            output = ffmpeg.output(video.video, dubbed_audio, output_path, 
                                  vcodec='copy', acodec='aac', strict='experimental')
        
        # Run the ffmpeg command
        output.run(quiet=True, overwrite_output=True)
        print(f"Video with aligned audio saved to {output_path}")
        return output_path
    
    except ffmpeg.Error as e:
        print(f"Error aligning audio with video using ffmpeg: {e.stderr.decode()}")
        return None

def align_audio_with_video_moviepy(video_path, audio_path, output_path, 
                                  audio_volume=1.0, background_volume=0.1):
    """
    Align audio with video using moviepy
    
    Args:
        video_path (str): Path to input video file
        audio_path (str): Path to input audio file (Indonesian speech)
        output_path (str): Path to output video file
        audio_volume (float): Volume level for dubbed audio (0.0-1.0)
        background_volume (float): Volume level for original audio (0.0-1.0)
    
    Returns:
        str: Path to output video file
    """
    try:
        # Load video and audio clips
        video = VideoFileClip(video_path)
        dubbed_audio = AudioFileClip(audio_path).volumex(audio_volume)
        
        # Create composite audio if background audio is needed
        if background_volume > 0:
            original_audio = video.audio.volumex(background_volume)
            new_audio = CompositeAudioClip([original_audio, dubbed_audio])
        else:
            new_audio = dubbed_audio
        
        # Set the new audio to the video
        output_video = video.set_audio(new_audio)
        
        # Write the result to file
        output_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
        
        # Close the clips to free resources
        video.close()
        dubbed_audio.close()
        if background_volume > 0:
            original_audio.close()
        
        print(f"Video with aligned audio saved to {output_path}")
        return output_path
    
    except Exception as e:
        print(f"Error aligning audio with video using moviepy: {e}")
        return None

def align_audio_with_video(video_path, audio_path, output_dir=None, method="ffmpeg",
                          audio_volume=1.0, background_volume=0.1):
    """
    Align audio with video
    
    Args:
        video_path (str): Path to input video file
        audio_path (str): Path to input audio file (Indonesian speech)
        output_dir (str): Directory to save output video file
        method (str): Method to use for alignment (ffmpeg or moviepy)
        audio_volume (float): Volume level for dubbed audio (0.0-1.0)
        background_volume (float): Volume level for original audio (0.0-1.0)
    
    Returns:
        str: Path to output video file
    """
    # Validate input files
    if not os.path.exists(video_path):
        print(f"Error: Input video file {video_path} does not exist")
        return None
    if not os.path.exists(audio_path):
        print(f"Error: Input audio file {audio_path} does not exist")
        return None
    
    # Create output directory if needed
    if output_dir is None:
        output_dir = os.path.dirname(video_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename
    video_basename = os.path.basename(video_path)
    video_name, video_ext = os.path.splitext(video_basename)
    output_path = os.path.join(output_dir, f"{video_name}_indonesian{video_ext}")
    
    # Align audio with video using selected method
    if method.lower() == "ffmpeg":
        return align_audio_with_video_ffmpeg(video_path, audio_path, output_path, 
                                           audio_volume, background_volume)
    elif method.lower() == "moviepy":
        return align_audio_with_video_moviepy(video_path, audio_path, output_path, 
                                            audio_volume, background_volume)
    else:
        print(f"Error: Unknown alignment method '{method}'. Use 'ffmpeg' or 'moviepy'")
        return None

def main():
    """Command line interface for audio-video alignment"""
    parser = argparse.ArgumentParser(description="Align Indonesian audio with Chinese video")
    parser.add_argument("video_path", help="Path to input video file")
    parser.add_argument("audio_path", help="Path to input audio file (Indonesian speech)")
    parser.add_argument("--output-dir", help="Directory to save output video file")
    parser.add_argument("--method", choices=["ffmpeg", "moviepy"], default="ffmpeg",
                        help="Method to use for alignment (default: ffmpeg)")
    parser.add_argument("--audio-volume", type=float, default=1.0,
                        help="Volume level for dubbed audio (0.0-1.0, default: 1.0)")
    parser.add_argument("--background-volume", type=float, default=0.1,
                        help="Volume level for original audio (0.0-1.0, default: 0.1)")
    args = parser.parse_args()
    
    align_audio_with_video(args.video_path, args.audio_path, args.output_dir, 
                          args.method, args.audio_volume, args.background_volume)

if __name__ == "__main__":
    main()
