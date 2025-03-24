# Chinese to Indonesian Video Dubbing Pipeline

A Python-based solution for converting Chinese-language videos into Indonesian-dubbed versions with natural voice acting.

## Features

- **Free/Open-Source**: Uses only libraries with permissive licenses (MIT, Apache)
- **High-Quality**: Prioritizes translation accuracy, voice naturalness, and lip-sync alignment
- **Scalable**: Optimized for short videos but works for longer content
- **Modular Design**: Each component can be used independently or as part of the pipeline

## Requirements

- Python 3.10+
- FFmpeg (installed system-wide)
- Internet connection (for TTS and model downloads)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/chinese-indonesian-dubbing.git
   cd chinese-indonesian-dubbing
   ```

2. Install dependencies:
   ```
   pip install ffmpeg-python moviepy faster-whisper transformers sentencepiece torch==1.13.1+cpu torchvision==0.14.1+cpu torchaudio==0.13.1 -f https://download.pytorch.org/whl/cpu/torch_stable.html gTTS
   ```

   Note: We use CPU-only PyTorch to reduce installation size. For GPU acceleration, install the appropriate CUDA-enabled version.

## Usage

### Complete Pipeline

To process a video through the entire pipeline:

```bash
python main.py input_video.mp4 --output-dir ./output --model-size base
```

Options:
- `--model-size`: Transcription model size (tiny, base, small, medium, large)
- `--audio-method`: Audio extraction method (ffmpeg, moviepy)
- `--video-method`: Video alignment method (ffmpeg, moviepy)
- `--audio-volume`: Volume level for dubbed audio (0.0-1.0)
- `--background-volume`: Volume level for original audio (0.0-1.0)

### Individual Components

Each component can be used independently:

#### 1. Audio Extraction

```bash
python audio_extractor.py input_video.mp4 --output-dir ./audio --method ffmpeg
```

#### 2. Transcription

```bash
python transcriber.py audio_file.wav --output-dir ./transcript --model-size base --language zh
```

#### 3. Translation

```bash
python translator.py transcript_file.txt --output-dir ./translation
```

#### 4. Text-to-Speech

```bash
python tts_generator.py translation_file.json --output-dir ./speech
```

#### 5. Audio-Video Alignment

```bash
python video_aligner.py input_video.mp4 indonesian_speech.mp3 --output-dir ./output --method ffmpeg --audio-volume 1.0 --background-volume 0.1
```

#### 6. Validation

```bash
python validator.py dubbed_video.mp4 translation_file.json --output-dir ./validation
```

## Pipeline Architecture

1. **Audio Extraction**: Isolates Chinese speech from the video using FFmpeg
2. **Transcription**: Converts audio to text using faster-whisper (a more efficient alternative to OpenAI Whisper)
3. **Translation**: Uses transformers with Helsinki-NLP/opus-mt-zh-id model for Chinese to Indonesian translation
4. **Speech Synthesis**: Generates Indonesian speech with Google Text-to-Speech (gTTS)
5. **Video Remixing**: Aligns dubbed audio with the original video, preserving background audio at reduced volume
6. **Validation**: Assesses output quality with metrics for translation accuracy, audio sync, and technical quality

## Output Structure

The pipeline creates the following directory structure:

```
output_dir/
├── audio/              # Extracted audio files
├── transcript/         # Chinese transcription files
├── translation/        # Indonesian translation files
├── speech/             # Generated Indonesian speech files
│   └── segments/       # Individual speech segments
├── output/             # Final dubbed videos
├── validation/         # Validation reports
└── *_pipeline_metadata.json  # Pipeline execution metadata
```

## Performance Considerations

- **Processing Time**: Depends on video length and model size
- **Disk Space**: Intermediate files require approximately 5x the original video size
- **Memory Usage**: Base model requires ~2GB RAM, larger models need more

## Limitations

- Best results with clear speech and minimal background noise
- Translation quality depends on the domain and complexity of the content
- Lip-sync is approximate and may not be perfect for close-up shots
- Indonesian TTS uses Google's service which requires internet connectivity

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FFmpeg for audio/video processing
- Faster Whisper for efficient speech recognition
- Hugging Face Transformers for translation models
- Google Text-to-Speech for Indonesian voice synthesis
