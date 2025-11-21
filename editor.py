"""
Video/Audio editing module for Media Reels Generator
Handles clipping, resizing, subtitle burning, and format conversion using ffmpeg
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
import tempfile
import os

logger = logging.getLogger("media_reels_generator")


class VideoEditor:
    """Handle video/audio editing operations using ffmpeg"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize video editor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.video_config = config.get('video', {})
        self._check_ffmpeg()
    
    def _check_ffmpeg(self) -> None:
        """Check if ffmpeg is available"""
        try:
            subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                check=True
            )
            logger.info("ffmpeg is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "ffmpeg not found. Please install ffmpeg:\n"
                "Windows: https://ffmpeg.org/download.html\n"
                "Linux: sudo apt-get install ffmpeg\n"
                "macOS: brew install ffmpeg"
            )
    
    def extract_clip(
        self,
        input_path: Path,
        output_path: Path,
        start_time: float,
        end_time: float,
        is_audio_only: bool = False
    ) -> Path:
        """
        Extract a clip from media file
        
        Args:
            input_path: Path to input media file
            output_path: Path to output clip
            start_time: Start time in seconds
            end_time: End time in seconds
            is_audio_only: Whether input is audio-only
        
        Returns:
            Path to created clip
        """
        logger.info(f"Extracting clip: {start_time:.2f}s - {end_time:.2f}s from {input_path.name}")
        
        duration = end_time - start_time
        
        if is_audio_only:
            # For audio-only, create a simple waveform video
            return self._create_audio_visualization(input_path, output_path, start_time, end_time)
        
        # Video clip extraction
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-ss', str(start_time),
            '-t', str(duration),
            '-c:v', self.video_config.get('codec', 'libx264'),
            '-preset', self.video_config.get('preset', 'medium'),
            '-crf', str(self.video_config.get('crf', 23)),
            '-c:a', self.video_config.get('audio_codec', 'aac'),
            '-b:a', self.video_config.get('audio_bitrate', '128k'),
            '-avoid_negative_ts', 'make_zero',
            '-y',  # Overwrite output
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Clip extracted: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg error: {e.stderr.decode()}")
            raise RuntimeError(f"Failed to extract clip: {e}")
    
    def _create_audio_visualization(
        self,
        input_path: Path,
        output_path: Path,
        start_time: float,
        end_time: float
    ) -> Path:
        """
        Create video with waveform visualization for audio-only files
        
        Args:
            input_path: Path to audio file
            output_path: Path to output video
            start_time: Start time in seconds
            end_time: End time in seconds
        
        Returns:
            Path to created video
        """
        duration = end_time - start_time
        
        # Extract audio segment first
        temp_audio = output_path.parent / f"temp_audio_{output_path.stem}.wav"
        
        cmd_extract = [
            'ffmpeg',
            '-i', str(input_path),
            '-ss', str(start_time),
            '-t', str(duration),
            '-y',
            str(temp_audio)
        ]
        
        try:
            subprocess.run(cmd_extract, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to extract audio segment: {e}")
        
        # Create waveform video
        width = 1080
        height = 1080
        
        cmd_waveform = [
            'ffmpeg',
            '-i', str(temp_audio),
            '-filter_complex',
            f"[0:a]showwaves=s={width}x{height}:mode=line:colors=0xFFFFFF:scale=sqrt[waves];"
            f"color=c=black:s={width}x{height}[bg];"
            f"[bg][waves]overlay=shortest=1",
            '-c:v', self.video_config.get('codec', 'libx264'),
            '-preset', self.video_config.get('preset', 'medium'),
            '-crf', str(self.video_config.get('crf', 23)),
            '-c:a', self.video_config.get('audio_codec', 'aac'),
            '-b:a', self.video_config.get('audio_bitrate', '128k'),
            '-pix_fmt', 'yuv420p',
            '-y',
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd_waveform, check=True, capture_output=True)
            # Clean up temp audio
            if temp_audio.exists():
                temp_audio.unlink()
            logger.info(f"Audio visualization created: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            if temp_audio.exists():
                temp_audio.unlink()
            logger.error(f"ffmpeg error: {e.stderr.decode()}")
            raise RuntimeError(f"Failed to create audio visualization: {e}")
    
    def resize_video(
        self,
        input_path: Path,
        output_path: Path,
        width: int,
        height: int,
        format_name: str = "custom"
    ) -> Path:
        """
        Resize video to specific dimensions with proper cropping/padding
        
        Args:
            input_path: Path to input video
            output_path: Path to output video
            width: Target width
            height: Target height
            format_name: Format name for logging
        
        Returns:
            Path to resized video
        """
        logger.info(f"Resizing video to {width}x{height} ({format_name})")
        
        # Calculate scale and crop/pad to maintain aspect ratio
        # Use scale and pad to fit target dimensions
        filter_complex = (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black"
        )
        
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-vf', filter_complex,
            '-c:v', self.video_config.get('codec', 'libx264'),
            '-preset', self.video_config.get('preset', 'medium'),
            '-crf', str(self.video_config.get('crf', 23)),
            '-c:a', 'copy',  # Copy audio without re-encoding
            '-y',
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Video resized: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg error: {e.stderr.decode()}")
            raise RuntimeError(f"Failed to resize video: {e}")
    
    def create_subtitle_file(
        self,
        output_path: Path,
        segments: List[Dict[str, Any]],
        start_offset: float = 0.0
    ) -> Path:
        """
        Create SRT subtitle file from segments
        
        Args:
            output_path: Path to output SRT file
            segments: List of segments with 'start', 'end', 'text'
            start_offset: Offset to subtract from timestamps (for clips)
        
        Returns:
            Path to created SRT file
        """
        logger.info(f"Creating subtitle file: {output_path}")
        
        from utils import format_timestamp
        
        srt_content = []
        for i, seg in enumerate(segments, 1):
            start = max(0, seg['start'] - start_offset)
            end = max(0, seg['end'] - start_offset)
            
            start_str = format_timestamp(start)
            end_str = format_timestamp(end)
            
            text = seg['text'].strip()
            
            srt_content.append(f"{i}\n{start_str} --> {end_str}\n{text}\n\n")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(srt_content))
        
        logger.info(f"Subtitle file created: {output_path}")
        return output_path
    
    def burn_subtitles(
        self,
        input_path: Path,
        output_path: Path,
        srt_path: Path
    ) -> Path:
        """
        Burn subtitles into video
        
        Args:
            input_path: Path to input video
            output_path: Path to output video
            srt_path: Path to SRT subtitle file
        
        Returns:
            Path to video with burned subtitles
        """
        logger.info(f"Burning subtitles into video: {output_path}")
        
        font_size = self.video_config.get('subtitle_font_size', 24)
        font_color = self.video_config.get('subtitle_font_color', 'white')
        background = self.video_config.get('subtitle_background', 'black@0.5')
        
        # Subtitles filter (Windows compatibility)
        # On Windows, use forward slashes and escape properly
        srt_path_str = str(srt_path).replace('\\', '/').replace(':', '\\:')
        subtitle_filter = (
            f"subtitles={srt_path_str}:"
            f"force_style='FontSize={font_size},PrimaryColour={font_color},"
            f"BackColour={background},BorderStyle=3,Outline=2'"
        )
        
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-vf', subtitle_filter,
            '-c:v', self.video_config.get('codec', 'libx264'),
            '-preset', self.video_config.get('preset', 'medium'),
            '-crf', str(self.video_config.get('crf', 23)),
            '-c:a', 'copy',
            '-y',
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Subtitles burned: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg error: {e.stderr.decode()}")
            raise RuntimeError(f"Failed to burn subtitles: {e}")
    
    def process_highlight(
        self,
        input_path: Path,
        highlight: Dict[str, Any],
        output_folder: Path,
        is_audio_only: bool = False,
        segments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Path]:
        """
        Process a single highlight: extract clip, resize, create subtitles
        
        Args:
            input_path: Path to original media file
            highlight: Highlight dictionary with start_time, end_time, etc.
            output_folder: Folder to save outputs
            is_audio_only: Whether input is audio-only
            segments: Transcript segments for subtitles
        
        Returns:
            Dictionary with paths to created files
        """
        start_time = highlight['start_time']
        end_time = highlight['end_time']
        
        # Extract base clip
        base_clip_path = output_folder / 'clip.mp4'
        self.extract_clip(input_path, base_clip_path, start_time, end_time, is_audio_only)
        
        # Get segments for this clip
        clip_segments = []
        if segments:
            for seg in segments:
                if seg['start'] >= start_time and seg['end'] <= end_time:
                    clip_segments.append({
                        'start': seg['start'],
                        'end': seg['end'],
                        'text': seg['text']
                    })
        
        # Create subtitle file
        srt_path = None
        if segments and clip_segments:
            srt_path = output_folder / 'clip.srt'
            self.create_subtitle_file(srt_path, clip_segments, start_offset=start_time)
        
        # Resize to different formats
        formats = self.video_config.get('formats', [])
        resized_paths = {}
        
        for fmt in formats:
            fmt_name = fmt.get('name', 'custom')
            width = fmt.get('width', 1080)
            height = fmt.get('height', 1080)
            
            output_name = f"clip_{fmt_name.replace(':', 'x')}.mp4"
            output_path = output_folder / output_name
            
            self.resize_video(base_clip_path, output_path, width, height, fmt_name)
            resized_paths[fmt_name] = output_path
        
        # Burn subtitles if requested
        final_clip_path = base_clip_path
        if self.video_config.get('burn_subtitles', False) and srt_path:
            final_clip_path = output_folder / 'clip_with_subs.mp4'
            self.burn_subtitles(base_clip_path, final_clip_path, srt_path)
        
        return {
            'base_clip': base_clip_path,
            'srt': srt_path,
            'resized': resized_paths,
            'final': final_clip_path
        }

