"""
Utilities module for Media Reels Generator
Contains helper functions for file handling, logging, and validation
"""

import os
import logging
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supported media formats
AUDIO_FORMATS = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma'}
VIDEO_FORMATS = {'.mp4', '.mkv', '.mov', '.avi', '.flv', '.webm', '.m4v'}
ALL_MEDIA_FORMATS = AUDIO_FORMATS | VIDEO_FORMATS


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path to log file
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("media_reels_generator")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(console_format)
        logger.addHandler(file_handler)
    
    return logger


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config file
    
    Returns:
        Configuration dictionary
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Override with environment variables if present
    if 'api' in config:
        api_key_from_config = config['api'].get('openai_api_key', '').strip()
        if not api_key_from_config:
            # Try to get from environment if not in config
            env_key = os.getenv('OPENAI_API_KEY', '').strip()
            if env_key:
                config['api']['openai_api_key'] = env_key
        else:
            # Use the key from config
            config['api']['openai_api_key'] = api_key_from_config
    
    return config


def get_media_files(input_path: str) -> List[Path]:
    """
    Get all media files from input path (file or directory)
    
    Args:
        input_path: Path to file or directory
    
    Returns:
        List of media file paths
    """
    path = Path(input_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")
    
    media_files = []
    
    if path.is_file():
        if path.suffix.lower() in ALL_MEDIA_FORMATS:
            media_files.append(path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    elif path.is_dir():
        for ext in ALL_MEDIA_FORMATS:
            media_files.extend(path.glob(f"*{ext}"))
            media_files.extend(path.glob(f"*{ext.upper()}"))
    
    if not media_files:
        raise ValueError(f"No media files found in: {input_path}")
    
    return sorted(media_files)


def is_audio_file(file_path: Path) -> bool:
    """Check if file is audio-only"""
    return file_path.suffix.lower() in AUDIO_FORMATS


def is_video_file(file_path: Path) -> bool:
    """Check if file is video"""
    return file_path.suffix.lower() in VIDEO_FORMATS


def get_file_duration(file_path: Path) -> float:
    """
    Get duration of media file using ffprobe
    
    Args:
        file_path: Path to media file
    
    Returns:
        Duration in seconds
    """
    import subprocess
    
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
            str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        return duration
    except (subprocess.CalledProcessError, ValueError) as e:
        raise RuntimeError(f"Failed to get file duration: {e}")


def create_output_structure(base_output_dir: str, original_filename: str) -> Dict[str, Path]:
    """
    Create output directory structure for a media file
    
    Args:
        base_output_dir: Base output directory
        original_filename: Original media file name (without extension)
    
    Returns:
        Dictionary with paths to output directories and files
    """
    base_path = Path(base_output_dir) / original_filename
    base_path.mkdir(parents=True, exist_ok=True)
    
    return {
        'base': base_path,
        'highlights_json': base_path / 'highlights.json'
    }


def create_highlight_folder(base_path: Path, highlight_num: int) -> Path:
    """
    Create folder for a specific highlight
    
    Args:
        base_path: Base output path
        highlight_num: Highlight number (1-indexed)
    
    Returns:
        Path to highlight folder
    """
    highlight_folder = base_path / f"highlight_{highlight_num:02d}"
    highlight_folder.mkdir(parents=True, exist_ok=True)
    return highlight_folder


def save_highlights_json(output_path: Path, highlights: List[Dict[str, Any]]) -> None:
    """
    Save highlights to JSON file
    
    Args:
        output_path: Path to output JSON file
        highlights: List of highlight dictionaries
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(highlights, f, indent=2, ensure_ascii=False)


def save_caption_file(output_path: Path, caption: str, summary: str) -> None:
    """
    Save caption and summary to text file
    
    Args:
        output_path: Path to output text file
        caption: One-sentence hook
        summary: 2-3 line summary
    """
    content = f"Caption (Hook):\n{caption}\n\nSummary:\n{summary}"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def validate_file(file_path: Path, min_duration: float = 5.0) -> bool:
    """
    Validate media file (check duration, format, etc.)
    
    Args:
        file_path: Path to media file
        min_duration: Minimum required duration in seconds
    
    Returns:
        True if file is valid
    """
    if not file_path.exists():
        return False
    
    if file_path.suffix.lower() not in ALL_MEDIA_FORMATS:
        return False
    
    try:
        duration = get_file_duration(file_path)
        if duration < min_duration:
            return False
    except Exception:
        return False
    
    return True


def format_timestamp(seconds: float) -> str:
    """
    Format timestamp as HH:MM:SS.mmm
    
    Args:
        seconds: Time in seconds
    
    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

